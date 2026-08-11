import numpy as np
import cv2
from typing import Optional


class CoordinateTransform:
    def __init__(self, homography: Optional[np.ndarray] = None):
        self._H = homography

    def set_homography(self, src_points: np.ndarray, dst_points: np.ndarray) -> None:
        self._H, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC)

    def transform(self, x: float, y: float) -> tuple[float, float]:
        if self._H is None:
            return x, y
        pt = np.array([[[x, y]]], dtype=np.float32)
        result = cv2.perspectiveTransform(pt, self._H)
        return float(result[0][0][0]), float(result[0][0][1])

    def is_calibrated(self) -> bool:
        return self._H is not None
