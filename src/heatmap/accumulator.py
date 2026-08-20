import logging
import threading
import numpy as np
import cv2
from .floor_plan import FloorPlan

logger = logging.getLogger(__name__)


class HeatmapAccumulator:
    """Thread-safe accumulator that builds a live heatmap overlay."""

    def __init__(self, floor_plan: FloorPlan, blur_kernel: int = 51,
                 decay_factor: float = 0.995):
        self._floor_plan = floor_plan
        self._blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        self._decay_factor = decay_factor
        self._lock = threading.Lock()
        h, w = floor_plan.height, floor_plan.width
        self._heat: np.ndarray = np.zeros((h, w), dtype=np.float32)
        self._frame_heat: np.ndarray | None = None
        self._total_updates: int = 0

    def add_point(
        self,
        x: float,
        y: float,
        weight: float = 1.0,
        frame_shape: tuple[int, ...] | None = None,
    ) -> None:
        xi = int(np.clip(x, 0, self._floor_plan.width - 1))
        yi = int(np.clip(y, 0, self._floor_plan.height - 1))
        with self._lock:
            self._heat[yi, xi] += weight
            self._total_updates += 1
            if frame_shape is not None and len(frame_shape) >= 2:
                self._add_frame_point_locked(x, y, weight, int(frame_shape[0]), int(frame_shape[1]))

    def _add_frame_point_locked(
        self, x: float, y: float, weight: float, frame_h: int, frame_w: int
    ) -> None:
        if frame_h < 1 or frame_w < 1:
            return
        if self._frame_heat is None or self._frame_heat.shape != (frame_h, frame_w):
            if self._frame_heat is None:
                self._frame_heat = np.zeros((frame_h, frame_w), dtype=np.float32)
            else:
                self._frame_heat = cv2.resize(
                    self._frame_heat, (frame_w, frame_h), interpolation=cv2.INTER_LINEAR
                )
        fx = int(np.clip(x, 0, frame_w - 1))
        fy = int(np.clip(y, 0, frame_h - 1))
        self._frame_heat[fy, fx] += weight

    def decay(self) -> None:
        with self._lock:
            self._heat *= self._decay_factor
            if self._frame_heat is not None:
                self._frame_heat *= self._decay_factor

    def get_heatmap_image(self) -> np.ndarray:
        base = self._floor_plan.image
        with self._lock:
            heat = self._heat.copy()
        blurred = cv2.GaussianBlur(heat, (self._blur_kernel, self._blur_kernel), 0)
        max_val = blurred.max()
        if max_val > 0:
            normalized = (blurred / max_val * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(blurred, dtype=np.uint8)
        colormap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        alpha = (normalized / 255.0 * 0.6).reshape(
            normalized.shape[0], normalized.shape[1], 1
        )
        overlay = (base.astype(np.float32) * (1 - alpha) +
                   colormap.astype(np.float32) * alpha).astype(np.uint8)
        return overlay

    def overlay_on_frame(self, frame: np.ndarray, max_alpha: float = 0.45) -> np.ndarray:
        """Blend camera-space heat onto a BGR video frame (aligned with people)."""
        out = frame.copy()
        with self._lock:
            heat = None if self._frame_heat is None else self._frame_heat.copy()
        if heat is None or float(heat.max()) <= 0:
            return out

        fh, fw = out.shape[:2]
        if heat.shape != (fh, fw):
            heat = cv2.resize(heat, (fw, fh), interpolation=cv2.INTER_LINEAR)

        k = min(self._blur_kernel, (min(fh, fw) // 2) * 2 + 1)
        if k < 3:
            k = 3
        if k % 2 == 0:
            k += 1
        blurred = cv2.GaussianBlur(heat, (k, k), 0)
        max_val = float(blurred.max())
        if max_val <= 0:
            return out
        normalized = (blurred / max_val * 255).astype(np.uint8)
        colormap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        alpha = (normalized.astype(np.float32) / 255.0 * max_alpha).reshape(fh, fw, 1)
        blended = out.astype(np.float32) * (1.0 - alpha) + colormap.astype(np.float32) * alpha
        return blended.astype(np.uint8)

    @property
    def floor_plan(self) -> FloorPlan:
        return self._floor_plan

    @property
    def total_updates(self) -> int:
        with self._lock:
            return self._total_updates
