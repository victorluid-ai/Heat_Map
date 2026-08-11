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
        self._total_updates: int = 0

    def add_point(self, x: float, y: float, weight: float = 1.0) -> None:
        xi = int(np.clip(x, 0, self._floor_plan.width - 1))
        yi = int(np.clip(y, 0, self._floor_plan.height - 1))
        with self._lock:
            self._heat[yi, xi] += weight
            self._total_updates += 1

    def decay(self) -> None:
        with self._lock:
            self._heat *= self._decay_factor

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

    @property
    def floor_plan(self) -> FloorPlan:
        return self._floor_plan

    @property
    def total_updates(self) -> int:
        with self._lock:
            return self._total_updates
