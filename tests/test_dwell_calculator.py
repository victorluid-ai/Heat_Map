import time
import pytest

from src.tracking.dwell_calculator import DwellCalculator


def test_record_entry_and_exit():
    calc = DwellCalculator()
    t0 = time.time()
    calc.record_entry("cam_0", 1, timestamp=t0)
    times = calc.record_exit("cam_0", 1, timestamp=t0 + 15.0)
    assert times is not None
    entry, exit_ts = times
    assert exit_ts - entry == pytest.approx(15.0)


def test_exit_without_entry_returns_none():
    calc = DwellCalculator()
    result = calc.record_exit("cam_0", 99)
    assert result is None


def test_entry_is_not_recorded_twice():
    calc = DwellCalculator()
    t0 = time.time()
    calc.record_entry("cam_0", 1, timestamp=t0)
    calc.record_entry("cam_0", 1, timestamp=t0 + 100.0)  # should be ignored
    times = calc.record_exit("cam_0", 1, timestamp=t0 + 10.0)
    assert times is not None
    entry, exit_ts = times
    assert exit_ts - entry == pytest.approx(10.0)


def test_dwell_so_far():
    calc = DwellCalculator()
    t0 = time.time()
    calc.record_entry("cam_0", 1, timestamp=t0)
    elapsed = calc.dwell_so_far("cam_0", 1, now=t0 + 5.0)
    assert elapsed == pytest.approx(5.0)


def test_dwell_so_far_unknown_track():
    calc = DwellCalculator()
    result = calc.dwell_so_far("cam_0", 999)
    assert result is None


def test_active_tracks():
    calc = DwellCalculator()
    calc.record_entry("cam_0", 1)
    calc.record_entry("cam_0", 2)
    active = calc.active_tracks()
    assert ("cam_0", 1) in active
    assert ("cam_0", 2) in active


def test_frame_buffer_basic():
    import numpy as np
    from src.ingestion.frame_buffer import FrameBuffer

    buf = FrameBuffer(maxlen=3)
    assert len(buf) == 0

    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    buf.put(frame)
    assert len(buf) == 1

    result = buf.get()
    assert result is not None
    ts, f = result
    assert f.shape == (10, 10, 3)


def test_frame_buffer_maxlen():
    import numpy as np
    from src.ingestion.frame_buffer import FrameBuffer

    buf = FrameBuffer(maxlen=2)
    for i in range(5):
        buf.put(np.zeros((4, 4, 3), dtype=np.uint8))
    assert len(buf) == 2
