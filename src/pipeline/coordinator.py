import logging
import threading
import time
from sqlalchemy.orm import sessionmaker
from ..ingestion.source_manager import SourceManager
from ..detection.detector import Detector
from ..tracking.tracker import PersonTracker
from ..tracking.dwell_calculator import DwellCalculator
from ..heatmap.accumulator import HeatmapAccumulator
from ..heatmap.floor_plan import FloorPlan
from ..storage.repository import (
    bulk_insert_dwell_records,
    bulk_insert_tracking_events,
    upsert_camera,
)
from ..storage.database import get_session
from .runner import PipelineRunner
from .events import EventBus, PipelineEvent

logger = logging.getLogger(__name__)


class PipelineCoordinator:
    def __init__(self, config: dict, session_factory: sessionmaker):
        self._config = config
        self._session_factory = session_factory
        self._event_bus = EventBus()
        self._floor_plan = FloorPlan(
            config["heatmap"]["floor_plan_path"],
            tuple(config["heatmap"]["resolution"]),
        )
        self._accumulators: dict[str, HeatmapAccumulator] = {}
        self._runners: dict[str, PipelineRunner] = {}
        self._source_manager = SourceManager(config["cameras"])
        self._writer_thread: threading.Thread | None = None
        self._running = False
        self._detector = Detector.from_config_dict(config["detection"])
        self._dwell_calc = DwellCalculator()
        self._default_zone_id = config.get("tracking", {}).get("default_zone_id", "entrance")

    def start(self) -> None:
        with get_session(self._session_factory) as session:
            for cam in self._config["cameras"]:
                if cam.get("enabled", True):
                    upsert_camera(session, cam["id"], cam["name"], str(cam["source"]))
        self._source_manager.start_all()
        for cam_id in self._source_manager.camera_ids:
            acc = HeatmapAccumulator(
                self._floor_plan,
                blur_kernel=self._config["heatmap"]["blur_kernel_size"],
                decay_factor=self._config["heatmap"]["decay_factor"],
            )
            self._accumulators[cam_id] = acc
            tracker = PersonTracker.from_config_dict(self._config["tracking"])
            reader = self._source_manager.get_reader(cam_id)
            runner = PipelineRunner(
                cam_id, reader, self._detector, tracker,
                acc, self._event_bus, self._dwell_calc,
                zone_id=self._default_zone_id,
            )
            self._runners[cam_id] = runner
            runner.start()
        self._running = True
        self._writer_thread = threading.Thread(
            target=self._writer_loop, daemon=True, name="db-writer"
        )
        self._writer_thread.start()
        logger.info("PipelineCoordinator started with %d cameras", len(self._runners))

    def stop(self) -> None:
        self._running = False
        for runner in self._runners.values():
            runner.stop()
        self._source_manager.stop_all()
        if self._writer_thread:
            self._writer_thread.join(timeout=5.0)
        logger.info("PipelineCoordinator stopped")

    def get_accumulator(self, camera_id: str) -> HeatmapAccumulator | None:
        return self._accumulators.get(camera_id)

    def get_runner(self, camera_id: str) -> PipelineRunner | None:
        return self._runners.get(camera_id)

    @property
    def camera_ids(self) -> list[str]:
        return list(self._runners.keys())

    def _writer_loop(self) -> None:
        pending_tracks: list = []
        pending_dwells: list = []
        last_flush = time.time()
        batch_interval = self._config["storage"]["batch_write_interval_seconds"]
        batch_max = self._config["storage"]["batch_write_max_events"]
        while self._running or pending_tracks or pending_dwells:
            event: PipelineEvent | None = self._event_bus.get(timeout=0.5)
            if event:
                if event.event_type == "track":
                    pending_tracks.append(event.payload)
                elif event.event_type == "dwell":
                    pending_dwells.append(event.payload)
            now = time.time()
            should_flush = (
                len(pending_tracks) >= batch_max
                or (now - last_flush >= batch_interval and (pending_tracks or pending_dwells))
                or (not self._running and (pending_tracks or pending_dwells))
            )
            if should_flush:
                try:
                    with get_session(self._session_factory) as session:
                        if pending_tracks:
                            bulk_insert_tracking_events(session, pending_tracks)
                            pending_tracks.clear()
                        if pending_dwells:
                            bulk_insert_dwell_records(session, pending_dwells)
                            pending_dwells.clear()
                    last_flush = now
                except Exception as exc:
                    logger.error("DB write error: %s", exc)
