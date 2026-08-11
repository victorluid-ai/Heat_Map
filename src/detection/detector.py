import logging
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int = 0


class Detector:
    """Person detector backed by a configurable model (e.g. YOLOv8)."""

    def __init__(self, model_path: str, confidence_threshold: float = 0.4,
                 device: str = "cpu"):
        self._model_path = model_path
        self._confidence_threshold = confidence_threshold
        self._device = device
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO  # type: ignore
            self._model = YOLO(self._model_path)
            logger.info("Loaded detection model: %s on %s", self._model_path, self._device)
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not load model %s: %s — detector will return empty results", self._model_path, exc)
            self._model = None

    @classmethod
    def from_config_dict(cls, config: dict) -> "Detector":
        return cls(
            model_path=config.get("model", "yolov8n.pt"),
            confidence_threshold=config.get("confidence_threshold", 0.4),
            device=config.get("device", "cpu"),
        )

    def detect(self, frame: np.ndarray) -> list[Detection]:
        if self._model is None or frame is None:
            return []
        try:
            results = self._model(frame, device=self._device, verbose=False)
            detections: list[Detection] = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    if cls_id != 0:  # 0 = person in COCO
                        continue
                    conf = float(box.conf[0])
                    if conf < self._confidence_threshold:
                        continue
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detections.append(Detection(x1=x1, y1=y1, x2=x2, y2=y2,
                                                confidence=conf, class_id=cls_id))
            return detections
        except Exception as exc:  # pragma: no cover
            logger.error("Detection error: %s", exc)
            return []
