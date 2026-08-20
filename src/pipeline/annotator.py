"""Live-frame overlays: heatmap blend, track boxes, and HUD."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

import cv2
import numpy as np

# Design tokens (BGR): accent cyan #00d4ff, HUD text #e8edf5, panel #0a0e17
_CYAN = (255, 212, 0)
_CYAN_DIM = (180, 150, 0)
_TEXT = (245, 237, 232)
_HUD_BG = (23, 14, 10)
_LABEL_BG = (40, 24, 8)

_HUD_H = 28
_BOX_THICKNESS = 2


class TrackLike(Protocol):
    track_id: int
    cx: float
    cy: float
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


def annotate_live_frame(
    frame: np.ndarray,
    tracks: Sequence[TrackLike],
    camera_id: str,
) -> np.ndarray:
    """Return a BGR copy with track boxes, IDs, and a LIVE HUD."""
    out = frame.copy()
    for track in tracks:
        _draw_track(out, track)
    _draw_hud(out, camera_id, len(tracks))
    return out


def _bbox(track: TrackLike, width: int, height: int) -> tuple[int, int, int, int] | None:
    if track.x2 > track.x1 and track.y2 > track.y1:
        x1, y1, x2, y2 = int(track.x1), int(track.y1), int(track.x2), int(track.y2)
    else:
        bw, bh = 48, 96
        cx, cy = int(track.cx), int(track.cy)
        x1, y1 = cx - bw // 2, cy - bh // 2
        x2, y2 = cx + bw // 2, cy + bh // 2
    x1 = int(np.clip(x1, 0, width - 1))
    y1 = int(np.clip(y1, 0, height - 1))
    x2 = int(np.clip(x2, 0, width - 1))
    y2 = int(np.clip(y2, 0, height - 1))
    if x2 - x1 < 4 or y2 - y1 < 4:
        return None
    return x1, y1, x2, y2


def _draw_track(img: np.ndarray, track: TrackLike) -> None:
    h, w = img.shape[:2]
    box = _bbox(track, w, h)
    if box is None:
        return
    x1, y1, x2, y2 = box
    cv2.rectangle(img, (x1, y1), (x2, y2), _CYAN, _BOX_THICKNESS)
    _draw_corners(img, x1, y1, x2, y2, _CYAN)
    label = f"ID {track.track_id:02d}  {track.confidence:.0%}"
    (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    pad = 4
    ly1 = max(0, y1 - th - baseline - pad * 2)
    ly2 = y1
    lx2 = min(w - 1, x1 + tw + pad * 2)
    cv2.rectangle(img, (x1, ly1), (lx2, ly2), _LABEL_BG, -1)
    cv2.rectangle(img, (x1, ly1), (lx2, ly2), _CYAN, 1)
    cv2.putText(
        img,
        label,
        (x1 + pad, ly2 - pad - baseline + 1),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        _TEXT,
        1,
        cv2.LINE_AA,
    )


def _draw_corners(
    img: np.ndarray, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int]
) -> None:
    length = max(10, min(x2 - x1, y2 - y1) // 5)
    t = _BOX_THICKNESS + 1
    cv2.line(img, (x1, y1), (x1 + length, y1), color, t)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, t)
    cv2.line(img, (x2, y1), (x2 - length, y1), color, t)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, t)
    cv2.line(img, (x1, y2), (x1 + length, y2), color, t)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, t)
    cv2.line(img, (x2, y2), (x2 - length, y2), color, t)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, t)


def _draw_hud(img: np.ndarray, camera_id: str, n_tracks: int) -> None:
    h, w = img.shape[:2]
    bar_h = min(_HUD_H, h)
    overlay = img[0:bar_h, 0:w].copy()
    cv2.rectangle(overlay, (0, 0), (w, bar_h), _HUD_BG, -1)
    blended = cv2.addWeighted(overlay, 0.72, img[0:bar_h, 0:w], 0.28, 0)
    img[0:bar_h, 0:w] = blended
    cv2.line(img, (0, bar_h), (w, bar_h), _CYAN_DIM, 1)
    text = f"LIVE  |  {camera_id}  |  TRACKS {n_tracks:02d}"
    cv2.putText(img, text, (10, bar_h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, _CYAN, 1, cv2.LINE_AA)
    cv2.circle(img, (w - 16, bar_h // 2), 5, (60, 60, 220), -1)
