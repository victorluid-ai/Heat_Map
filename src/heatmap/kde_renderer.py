import logging
import numpy as np
import cv2
from .floor_plan import FloorPlan

logger = logging.getLogger(__name__)


class KDERenderer:
    """Renders a historical heatmap from a list of (x, y) points using KDE."""

    def __init__(self, floor_plan: FloorPlan, bandwidth: int = 31):
        self._floor_plan = floor_plan
        self._bandwidth = bandwidth if bandwidth % 2 == 1 else bandwidth + 1

    def render(self, points: list[tuple[float, float]]) -> np.ndarray:
        base = self._floor_plan.image
        h, w = self._floor_plan.height, self._floor_plan.width
        density = np.zeros((h, w), dtype=np.float32)

        for x, y in points:
            xi = int(np.clip(x, 0, w - 1))
            yi = int(np.clip(y, 0, h - 1))
            density[yi, xi] += 1.0

        blurred = cv2.GaussianBlur(density, (self._bandwidth, self._bandwidth), 0)
        max_val = blurred.max()
        if max_val > 0:
            normalized = (blurred / max_val * 255).astype(np.uint8)
        else:
            normalized = np.zeros((h, w), dtype=np.uint8)

        colormap = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        alpha = (normalized / 255.0 * 0.6).reshape(h, w, 1)
        overlay = (base.astype(np.float32) * (1 - alpha) +
                   colormap.astype(np.float32) * alpha).astype(np.uint8)
        return overlay
