import logging
import time
from dataclasses import dataclass
from typing import Optional
import numpy as np
from .track_record import TrackUpdate
from ..detection.detector import Detection

logger = logging.getLogger(__name__)


@dataclass
class _Track:
    track_id: int
    cx: float
    cy: float
    hits: int = 1
    age: int = 0
    confidence: float = 1.0


class PersonTracker:
    """Simple IoU-based multi-object tracker."""

    def __init__(self, max_age: int = 30, min_hits: int = 3):
        self._max_age = max_age
        self._min_hits = min_hits
        self._tracks: dict[int, _Track] = {}
        self._next_id = 0

    @classmethod
    def from_config_dict(cls, config: dict) -> "PersonTracker":
        return cls(
            max_age=config.get("max_age", 30),
            min_hits=config.get("min_hits", 3),
        )

    def update(self, detections: list[Detection]) -> list[_Track]:
        for track in self._tracks.values():
            track.age += 1

        unmatched_dets = list(detections)
        for det in unmatched_dets:
            cx = (det.x1 + det.x2) / 2.0
            cy = (det.y1 + det.y2) / 2.0
            matched = self._match_closest(cx, cy)
            if matched is not None:
                matched.cx = cx
                matched.cy = cy
                matched.hits += 1
                matched.age = 0
                matched.confidence = det.confidence
            else:
                self._tracks[self._next_id] = _Track(
                    track_id=self._next_id, cx=cx, cy=cy,
                    confidence=det.confidence,
                )
                self._next_id += 1

        # Prune stale tracks
        self._tracks = {tid: t for tid, t in self._tracks.items()
                        if t.age <= self._max_age}

        return [t for t in self._tracks.values() if t.hits >= self._min_hits]

    def _match_closest(self, cx: float, cy: float,
                        dist_threshold: float = 80.0) -> Optional[_Track]:
        best: Optional[_Track] = None
        best_dist = dist_threshold
        for track in self._tracks.values():
            d = ((track.cx - cx) ** 2 + (track.cy - cy) ** 2) ** 0.5
            if d < best_dist:
                best_dist = d
                best = track
        return best

    def make_track_updates(self, camera_id: str,
                           tracks: list[_Track]) -> list[TrackUpdate]:
        now = time.time()
        return [
            TrackUpdate(camera_id=camera_id, track_id=t.track_id,
                        x=t.cx, y=t.cy, timestamp=now, confidence=t.confidence)
            for t in tracks
        ]
