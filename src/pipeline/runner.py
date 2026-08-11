import logging
import threading
import time
from typing import Optional
import numpy as np
from ..detection.detector import Detector
from ..tracking.tracker import PersonTracker
from ..tracking.dwell_calculator import DwellCalculator
from ..tracking.track_record import DwellUpdate
from ..heatmap.accumulator import HeatmapAccumulator
from ..ingestion.camera_reader import CameraReader
from .events import EventBus, PipelineEvent

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Per-camera thread that reads frames, detects, tracks, and accumulates."""

    def __init__(
        self,
        camera_id: str,
        reader: CameraReader,
        detector: Detector,
        tracker: PersonTracker,
        accumulator: HeatmapAccumulator,
        event_bus: EventBus,
        dwell_calc: DwellCalculator,
        zone_id: str = "entrance",
    ):
        self._camera_id = camera_id
        self._reader = reader
        self._detector = detector
        self._tracker = tracker
        self._accumulator = accumulator
        self._event_bus = event_bus
        self._dwell_calc = dwell_calc
        self._zone_id = zone_id
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._annotated_frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()
        self._active_track_ids: set[int] = set()

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True,
            name=f"runner-{self._camera_id}",
        )
        self._thread.start()
        logger.info("PipelineRunner started for %s", self._camera_id)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self._flush_remaining_dwells(time.time())
        logger.info("PipelineRunner stopped for %s", self._camera_id)

    def get_annotated_frame(self) -> Optional[np.ndarray]:
        with self._frame_lock:
            return self._annotated_frame.copy() if self._annotated_frame is not None else None

    def _run_loop(self) -> None:
        while self._running:
            result = self._reader.get_frame()
            if result is None:
                time.sleep(0.01)
                continue

            ts, frame = result
            detections = self._detector.detect(frame)
            active_tracks = self._tracker.update(detections)
            current_ids = {t.track_id for t in active_tracks}
            lost_ids = self._active_track_ids - current_ids
            for track_id in lost_ids:
                self._publish_dwell_exit(track_id, ts)
            self._active_track_ids = current_ids

            for track in active_tracks:
                self._accumulator.add_point(track.cx, track.cy)
                self._dwell_calc.record_entry(self._camera_id, track.track_id, ts)

            # Decay heatmap periodically (every frame is fine, it's per-frame factor)
            self._accumulator.decay()

            # Publish track events for the DB writer
            updates = self._tracker.make_track_updates(self._camera_id, active_tracks)
            for update in updates:
                self._event_bus.put(PipelineEvent(
                    event_type="track",
                    camera_id=self._camera_id,
                    payload=update,
                    timestamp=ts,
                ))

            # Store latest annotated frame for MJPEG streaming
            annotated = self._annotate_frame(frame, active_tracks)
            with self._frame_lock:
                self._annotated_frame = annotated

    def _publish_dwell_exit(self, track_id: int, timestamp: float) -> None:
        times = self._dwell_calc.record_exit(self._camera_id, track_id, timestamp)
        if times is None:
            return
        entry_time, exit_time = times
        self._event_bus.put(PipelineEvent(
            event_type="dwell",
            camera_id=self._camera_id,
            payload=DwellUpdate(
                camera_id=self._camera_id,
                track_id=track_id,
                zone_id=self._zone_id,
                entry_time=entry_time,
                exit_time=exit_time,
            ),
            timestamp=exit_time,
        ))

    def _flush_remaining_dwells(self, timestamp: float) -> None:
        for track_id in list(self._active_track_ids):
            self._publish_dwell_exit(track_id, timestamp)
        self._active_track_ids.clear()

    def _annotate_frame(self, frame: np.ndarray, tracks) -> np.ndarray:
        import cv2
        out = frame.copy()
        for track in tracks:
            cx, cy = int(track.cx), int(track.cy)
            cv2.circle(out, (cx, cy), 6, (0, 255, 0), -1)
            cv2.putText(out, str(track.track_id), (cx + 8, cy - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return out
