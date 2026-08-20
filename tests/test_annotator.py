import numpy as np

from src.pipeline.annotator import annotate_live_frame
from src.tracking.tracker import _Track


def test_annotate_live_frame_draws_box_and_id():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    track = _Track(
        track_id=7,
        cx=80,
        cy=90,
        x1=40,
        y1=30,
        x2=120,
        y2=160,
        confidence=0.91,
    )
    out = annotate_live_frame(frame, [track], "cam_0")
    assert out.shape == frame.shape
    assert out.dtype == np.uint8
    assert not np.array_equal(out, frame)


def test_annotate_live_frame_empty_tracks_still_has_hud():
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    out = annotate_live_frame(frame, [], "cam_0")
    assert out.shape == frame.shape
    assert not np.array_equal(out, frame)


def test_annotate_live_frame_does_not_mutate_input():
    frame = np.zeros((80, 100, 3), dtype=np.uint8)
    original = frame.copy()
    annotate_live_frame(frame, [], "cam_0")
    assert np.array_equal(frame, original)
