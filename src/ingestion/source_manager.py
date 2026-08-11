import logging
from typing import Iterator
import numpy as np
from .camera_reader import CameraReader

logger = logging.getLogger(__name__)


class SourceManager:
    def __init__(self, camera_configs: list[dict]):
        self._readers: dict[str, CameraReader] = {}
        for cam in camera_configs:
            if cam.get("enabled", True):
                self._readers[cam["id"]] = CameraReader(
                    camera_id=cam["id"],
                    source=cam["source"],
                )

    def start_all(self) -> None:
        for reader in self._readers.values():
            reader.start()

    def stop_all(self) -> None:
        for reader in self._readers.values():
            reader.stop()

    def get_reader(self, camera_id: str) -> CameraReader | None:
        return self._readers.get(camera_id)

    def iter_frames(self) -> Iterator[tuple[str, float, np.ndarray]]:
        for camera_id, reader in self._readers.items():
            result = reader.get_frame()
            if result is not None:
                ts, frame = result
                yield camera_id, ts, frame

    @property
    def camera_ids(self) -> list[str]:
        return list(self._readers.keys())
