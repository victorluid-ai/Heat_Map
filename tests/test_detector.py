import numpy as np
import pytest

from src.detection.detector import Detector, Detection


def test_detection_dataclass():
    d = Detection(x1=0.0, y1=0.0, x2=10.0, y2=20.0, confidence=0.9)
    assert d.x1 == 0.0
    assert d.class_id == 0


def test_detector_initialises_without_model():
    det = Detector(model_path="nonexistent_model.pt", confidence_threshold=0.4)
    assert det._model is None


def test_detect_returns_empty_on_none_frame():
    det = Detector(model_path="nonexistent_model.pt")
    result = det.detect(None)
    assert result == []


def test_detect_returns_empty_when_no_model(sample_frame):
    det = Detector(model_path="nonexistent_model.pt")
    result = det.detect(sample_frame)
    assert isinstance(result, list)
    assert len(result) == 0


def test_from_config_dict():
    cfg = {"model": "yolov8n.pt", "confidence_threshold": 0.5, "device": "cpu"}
    det = Detector.from_config_dict(cfg)
    assert det._confidence_threshold == 0.5
    assert det._device == "cpu"
