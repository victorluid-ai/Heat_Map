import pytest
from src.detection.detector import Detection
from src.tracking.tracker import ByteTrackPersonTracker, PersonTracker
from src.tracking.track_record import TrackUpdate


def _det(x1, y1, x2, y2, conf=0.9):
    return Detection(x1=x1, y1=y1, x2=x2, y2=y2, confidence=conf)


def test_tracker_creates_track_from_single_detection():
    tracker = PersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1
    assert tracks[0].cx == pytest.approx(5.0)
    assert tracks[0].cy == pytest.approx(10.0)


def test_tracker_returns_empty_with_no_detections():
    tracker = PersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([])
    assert tracks == []


def test_tracker_requires_min_hits():
    tracker = PersonTracker(max_age=5, min_hits=3)
    for _ in range(2):
        tracks = tracker.update([_det(0, 0, 10, 20)])
    assert tracks == []  # not enough hits yet
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1


def test_tracker_prunes_stale_tracks():
    tracker = PersonTracker(max_age=2, min_hits=1)
    tracker.update([_det(0, 0, 10, 20)])
    tracker.update([])
    tracker.update([])
    tracker.update([])  # age > max_age
    tracks = tracker.update([])
    assert tracks == []


def test_make_track_updates():
    tracker = PersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([_det(0, 0, 10, 20)])
    updates = tracker.make_track_updates("cam_0", tracks)
    assert len(updates) == 1
    assert isinstance(updates[0], TrackUpdate)
    assert updates[0].camera_id == "cam_0"
    assert updates[0].x == pytest.approx(5.0)


def test_from_config_dict():
    cfg = {"max_age": 15, "min_hits": 2}
    tracker = PersonTracker.from_config_dict(cfg)
    assert tracker._max_age == 15
    assert tracker._min_hits == 2


def test_byte_tracker_creates_track_from_single_detection():
    tracker = ByteTrackPersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1
    assert tracks[0].cx == pytest.approx(5.0)
    assert tracks[0].cy == pytest.approx(10.0)


def test_byte_tracker_returns_empty_with_no_detections():
    tracker = ByteTrackPersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([])
    assert tracks == []


def test_byte_tracker_requires_min_hits():
    tracker = ByteTrackPersonTracker(max_age=5, min_hits=3)
    for _ in range(2):
        tracks = tracker.update([_det(0, 0, 10, 20)])
        assert tracks == []
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1


def test_byte_tracker_prunes_stale_tracks():
    tracker = ByteTrackPersonTracker(max_age=2, min_hits=1)
    # Dos frames con detección para que el track sea estable.
    tracker.update([_det(0, 0, 10, 20)])
    tracker.update([_det(0, 0, 10, 20)])

    # Dentro de max_age: sigue activo.
    assert len(tracker.update([])) == 1
    assert len(tracker.update([])) == 1

    # Por encima de max_age: prunear.
    assert tracker.update([]) == []
