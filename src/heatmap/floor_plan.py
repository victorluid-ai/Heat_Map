import logging
from pathlib import Path
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class FloorPlan:
    """Loads and provides the floor-plan image used as a heatmap base."""

    def __init__(self, path: str, resolution: tuple[int, int] = (800, 600)):
        self._path = Path(path)
        self._resolution = resolution  # (width, height)
        self._image: np.ndarray | None = None
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            img = cv2.imread(str(self._path))
            if img is not None:
                self._image = cv2.resize(img, self._resolution)
                logger.info("Floor plan loaded: %s (%dx%d)",
                            self._path, *self._resolution)
                return
        logger.warning("Floor plan not found at %s — using blank canvas", self._path)
        w, h = self._resolution
        self._image = np.zeros((h, w, 3), dtype=np.uint8)

    @property
    def image(self) -> np.ndarray:
        assert self._image is not None
        return self._image.copy()

    @property
    def width(self) -> int:
        return self._resolution[0]

    @property
    def height(self) -> int:
        return self._resolution[1]

    @property
    def resolution(self) -> tuple[int, int]:
        return self._resolution
