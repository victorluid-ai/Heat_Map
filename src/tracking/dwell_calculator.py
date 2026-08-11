import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class DwellCalculator:
    """Tracks entry times per (camera, track) pair to compute dwell duration."""

    def __init__(self):
        # key: (camera_id, track_id) -> entry_timestamp
        self._entries: dict[tuple[str, int], float] = {}

    def record_entry(self, camera_id: str, track_id: int,
                     timestamp: Optional[float] = None) -> None:
        key = (camera_id, track_id)
        if key not in self._entries:
            self._entries[key] = timestamp or time.time()

    def record_exit(self, camera_id: str, track_id: int,
                    timestamp: Optional[float] = None) -> Optional[tuple[float, float]]:
        """Return (entry_time, exit_time) when a track leaves, else None."""
        key = (camera_id, track_id)
        entry = self._entries.pop(key, None)
        if entry is None:
            return None
        exit_ts = timestamp or time.time()
        return (entry, exit_ts)

    def dwell_so_far(self, camera_id: str, track_id: int,
                     now: Optional[float] = None) -> Optional[float]:
        entry = self._entries.get((camera_id, track_id))
        if entry is None:
            return None
        return max(0.0, (now or time.time()) - entry)

    def active_tracks(self) -> list[tuple[str, int]]:
        return list(self._entries.keys())
