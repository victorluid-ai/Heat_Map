import pytest

from src.detection.detector import Detection
from src.tracking.dwell_calculator import DwellCalculator
from src.tracking.track_record import TrackUpdate
from src.tracking.tracker import ByteTrackPersonTracker, PersonTracker


def _det(x1, y1, x2, y2, conf=0.9):
    return Detection(x1=x1, y1=y1, x2=x2, y2=y2, confidence=conf)


def test_tracker_creates_track_from_single_detection():
    tracker = PersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1
    assert tracks[0].cx == pytest.approx(5.0)
    assert tracks[0].cy == pytest.approx(10.0)
    assert tracks[0].x1 == pytest.approx(0.0)
    assert tracks[0].y1 == pytest.approx(0.0)
    assert tracks[0].x2 == pytest.approx(10.0)
    assert tracks[0].y2 == pytest.approx(20.0)


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


def test_from_config_dict_bytetrack():
    cfg = {
        "method": "bytetrack",
        "max_age": 45,
        "min_hits": 3,
        "frame_rate": 25.0,
        "track_activation_threshold": 0.4,
        "minimum_consecutive_frames": 2,
        "minimum_iou_threshold": 0.15,
        "high_conf_det_threshold": 0.5,
    }
    tracker = PersonTracker.from_config_dict(cfg)
    assert isinstance(tracker, ByteTrackPersonTracker)
    assert tracker._max_age == 45
    assert tracker._min_hits == 3
    assert tracker._frame_rate == pytest.approx(25.0)
    assert tracker._track_activation_threshold == pytest.approx(0.4)
    assert tracker._minimum_consecutive_frames == 2
    assert tracker._minimum_iou_threshold == pytest.approx(0.15)
    assert tracker._high_conf_det_threshold == pytest.approx(0.5)


def test_byte_tracker_creates_track_from_single_detection():
    tracker = ByteTrackPersonTracker(
        max_age=5,
        min_hits=1,
        minimum_consecutive_frames=1,
        track_activation_threshold=0.0,
        high_conf_det_threshold=0.0,
    )
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1
    assert tracks[0].cx == pytest.approx(5.0)
    assert tracks[0].cy == pytest.approx(10.0)
    assert tracks[0].x2 > tracks[0].x1
    assert tracks[0].y2 > tracks[0].y1


def test_byte_tracker_returns_empty_with_no_detections():
    tracker = ByteTrackPersonTracker(max_age=5, min_hits=1)
    tracks = tracker.update([])
    assert tracks == []


def test_byte_tracker_requires_min_hits():
    tracker = ByteTrackPersonTracker(
        max_age=5,
        min_hits=3,
        minimum_consecutive_frames=1,
        track_activation_threshold=0.0,
        high_conf_det_threshold=0.0,
    )
    for _ in range(2):
        tracks = tracker.update([_det(0, 0, 10, 20)])
        assert tracks == []
    tracks = tracker.update([_det(0, 0, 10, 20)])
    assert len(tracks) == 1


def test_byte_tracker_prunes_stale_tracks():
    tracker = ByteTrackPersonTracker(
        max_age=2,
        min_hits=1,
        frame_rate=30.0,
        minimum_consecutive_frames=1,
        track_activation_threshold=0.0,
        high_conf_det_threshold=0.0,
    )
    # Two frames with detection so the track is stable.
    tracker.update([_det(0, 0, 10, 20)])
    tracker.update([_det(0, 0, 10, 20)])

    # Within max_age: still active.
    assert len(tracker.update([])) == 1
    assert len(tracker.update([])) == 1

    # Beyond max_age: pruned.
    assert tracker.update([]) == []


def test_byte_tracker_keeps_id_through_brief_occlusion():
    """Brief missed frames should not fragment the ID (better dwell continuity)."""
    tracker = ByteTrackPersonTracker(
        max_age=45,
        min_hits=3,
        frame_rate=25.0,
        track_activation_threshold=0.4,
        minimum_consecutive_frames=2,
        minimum_iou_threshold=0.15,
        high_conf_det_threshold=0.5,
    )
    # Warm-up until the track is exported (min_hits=3).
    for _ in range(3):
        tracks = tracker.update([_det(100, 100, 140, 220, conf=0.85)])
    assert len(tracks) == 1
    track_id = tracks[0].track_id

    # Brief occlusion (5 frames at 25 FPS ≈ 0.2 s).
    for _ in range(5):
        tracks = tracker.update([])
        assert len(tracks) == 1
        assert tracks[0].track_id == track_id

    # Reappear nearby — same ID.
    tracks = tracker.update([_det(108, 104, 148, 224, conf=0.8)])
    assert len(tracks) == 1
    assert tracks[0].track_id == track_id


def test_byte_tracker_rejects_low_confidence_noise():
    """Detections below track_activation / high_conf band should not spawn tracks."""
    tracker = ByteTrackPersonTracker(
        max_age=45,
        min_hits=1,
        frame_rate=25.0,
        track_activation_threshold=0.4,
        minimum_consecutive_frames=2,
        minimum_iou_threshold=0.15,
        high_conf_det_threshold=0.5,
    )
    tracks = tracker.update([_det(0, 0, 10, 20, conf=0.2)])
    assert tracks == []


def test_byte_tracker_dwell_not_fragmented_by_occlusion():
    """Same track_id across a gap → one continuous dwell visit, not two."""
    tracker = ByteTrackPersonTracker(
        max_age=45,
        min_hits=3,
        frame_rate=25.0,
        track_activation_threshold=0.4,
        minimum_consecutive_frames=2,
        minimum_iou_threshold=0.15,
        high_conf_det_threshold=0.5,
    )
    dwell = DwellCalculator()
    active: set[int] = set()
    completed_visits = 0
    t = 0.0

    def step(dets, dt=0.04):
        nonlocal t, completed_visits
        t += dt
        tracks = tracker.update(dets)
        current = {tr.track_id for tr in tracks}
        for lost in active - current:
            assert dwell.record_exit("cam_0", lost, timestamp=t) is not None
            completed_visits += 1
        for tr in tracks:
            dwell.record_entry("cam_0", tr.track_id, timestamp=t)
        active.clear()
        active.update(current)
        return tracks

    for _ in range(4):
        step([_det(50, 50, 90, 170, conf=0.9)])
    for _ in range(8):
        step([])
    for _ in range(4):
        step([_det(55, 52, 95, 172, conf=0.85)])

    # Still one active visit; no premature exit during the occlusion gap.
    assert completed_visits == 0
    assert len(active) == 1
    assert len(dwell.active_tracks()) == 1
