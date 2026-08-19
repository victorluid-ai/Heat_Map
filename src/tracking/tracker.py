import logging
import time
from dataclasses import dataclass
from typing import Optional
import numpy as np
from .track_record import TrackUpdate
from ..detection.detector import Detection

try:
    import supervision as sv
    from trackers import ByteTrackTracker

    _HAS_SUPERVISION_TRACKERS = True
except ImportError:  # pragma: no cover
    sv = None  # type: ignore[assignment]
    ByteTrackTracker = None  # type: ignore[assignment]
    _HAS_SUPERVISION_TRACKERS = False

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
    """Tracker simple y ligero por distancia de centroides."""

    def __init__(self, max_age: int = 30, min_hits: int = 3):
        self._max_age = max_age
        self._min_hits = min_hits
        self._tracks: dict[int, _Track] = {}
        self._next_id = 0

    @classmethod
    def from_config_dict(cls, config: dict) -> "PersonTracker":
        method = str(config.get("method", config.get("tracker", "iou"))).lower()
        if method == "bytetrack":
            if _HAS_SUPERVISION_TRACKERS:
                return ByteTrackPersonTracker(
                    max_age=config.get("max_age", 30),
                    min_hits=config.get("min_hits", 3),
                    frame_rate=float(config.get("frame_rate", 30.0)),
                )
            logger.warning(
                "ByteTrack requested but supervision/trackers no están instalados; usando fallback IoU."
            )
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


class ByteTrackPersonTracker(PersonTracker):
    """Multi-object tracker motion-only basado en ByteTrack (sin ReID)."""

    def __init__(self, max_age: int = 30, min_hits: int = 3, frame_rate: float = 30.0):
        super().__init__(max_age=max_age, min_hits=min_hits)
        if not _HAS_SUPERVISION_TRACKERS:  # pragma: no cover
            raise RuntimeError("Se requiere supervision y trackers para ByteTrackPersonTracker")

        # lost_track_buffer en ByteTrack está expresado como "nº de frames a 30 FPS".
        # Usamos max_age para mantener la semántica aproximada de 'prune por inactividad'.
        self._byte_tracker = ByteTrackTracker(
            lost_track_buffer=max_age,
            frame_rate=frame_rate,
            track_activation_threshold=0.0,
            minimum_consecutive_frames=1,
            minimum_iou_threshold=0.1,
            high_conf_det_threshold=0.0,
        )
        # Mapeo estable: tracklet (identidad Python) -> track_id que usa el resto del sistema.
        self._tracklet_id_to_track_id: dict[int, int] = {}

    def update(self, detections: list[Detection]) -> list[_Track]:
        if not _HAS_SUPERVISION_TRACKERS:  # pragma: no cover
            return super().update(detections)

        dets_arr = None
        conf_arr = None
        if detections:
            dets_arr = np.array(
                [[d.x1, d.y1, d.x2, d.y2] for d in detections],
                dtype=np.float32,
            )
            conf_arr = np.array([d.confidence for d in detections], dtype=np.float32)

            # Clase esperada: 0 = person (COCO) en nuestro Detector.
            class_arr = np.array([d.class_id for d in detections], dtype=np.int32)
        else:
            dets_arr = np.empty((0, 4), dtype=np.float32)
            conf_arr = np.empty((0,), dtype=np.float32)
            class_arr = np.empty((0,), dtype=np.int32)

        sv_detections = sv.Detections(
            xyxy=dets_arr,
            confidence=conf_arr,
            class_id=class_arr,
        )

        self._byte_tracker.update(sv_detections)

        present_tracklets = {id(t) for t in self._byte_tracker.tracks}

        # Elimina tracks que ByteTrack ya no considera "alive".
        for tracklet_key, track_id in list(self._tracklet_id_to_track_id.items()):
            if tracklet_key not in present_tracklets:
                self._tracklet_id_to_track_id.pop(tracklet_key, None)
                self._tracks.pop(track_id, None)

        # Actualiza/crea tracks basados en tracklets internos.
        for tracklet in self._byte_tracker.tracks:
            tracklet_key = id(tracklet)
            track_id = self._tracklet_id_to_track_id.get(tracklet_key)
            state_bbox = tracklet.get_state_bbox().astype(np.float32)
            x1, y1, x2, y2 = state_bbox.tolist()
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0

            updated_this_frame = int(tracklet.time_since_update) == 0

            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
                self._tracklet_id_to_track_id[tracklet_key] = track_id

                hits = 1 if updated_this_frame else 0
                confidence = float(conf_arr[0]) if hits == 1 and len(conf_arr) else 1.0
                if hits == 1 and len(dets_arr):
                    confidence = float(self._select_best_confidence(state_bbox, dets_arr, conf_arr))

                self._tracks[track_id] = _Track(
                    track_id=track_id,
                    cx=cx,
                    cy=cy,
                    hits=hits,
                    age=int(tracklet.time_since_update),
                    confidence=confidence,
                )
            else:
                track = self._tracks[track_id]
                track.cx = cx
                track.cy = cy
                track.age = int(tracklet.time_since_update)

                if updated_this_frame:
                    track.hits += 1
                    if len(dets_arr):
                        track.confidence = float(self._select_best_confidence(state_bbox, dets_arr, conf_arr))

        # Prune por 'max_age' (semántica equivalente a PersonTracker).
        self._tracks = {tid: t for tid, t in self._tracks.items() if t.age <= self._max_age}

        return [t for t in self._tracks.values() if t.hits >= self._min_hits]

    @staticmethod
    def _select_best_confidence(state_bbox: np.ndarray, det_xyxy: np.ndarray, det_conf: np.ndarray) -> float:
        """Elige la confianza del box de detección con mayor IoU vs estado estimado."""
        if len(det_xyxy) == 0:
            return 1.0

        # IoU vectorizado: estado_bbox (4,) vs det_xyxy (N,4)
        xA = np.maximum(det_xyxy[:, 0], state_bbox[0])
        yA = np.maximum(det_xyxy[:, 1], state_bbox[1])
        xB = np.minimum(det_xyxy[:, 2], state_bbox[2])
        yB = np.minimum(det_xyxy[:, 3], state_bbox[3])

        inter_w = np.maximum(0.0, xB - xA)
        inter_h = np.maximum(0.0, yB - yA)
        inter_area = inter_w * inter_h

        box_area = (state_bbox[2] - state_bbox[0]) * (state_bbox[3] - state_bbox[1])
        det_area = (det_xyxy[:, 2] - det_xyxy[:, 0]) * (det_xyxy[:, 3] - det_xyxy[:, 1])
        union_area = box_area + det_area - inter_area
        iou = np.where(union_area > 0.0, inter_area / union_area, 0.0)

        best_idx = int(np.argmax(iou))
        return float(det_conf[best_idx])
