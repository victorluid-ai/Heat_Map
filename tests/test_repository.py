import time
import pytest

from src.storage.repository import (
    upsert_camera,
    bulk_insert_tracking_events,
    bulk_insert_dwell_records,
    insert_dwell_record,
    get_events_by_timerange,
    get_xy_points,
    get_zone_dwell_summary,
)
from src.tracking.track_record import DwellUpdate, TrackUpdate


def test_upsert_camera_creates_new(db_session):
    cam = upsert_camera(db_session, "cam_test_1", "Test Camera", "0")
    db_session.flush()
    assert cam.id == "cam_test_1"
    assert cam.name == "Test Camera"


def test_upsert_camera_is_idempotent(db_session):
    upsert_camera(db_session, "cam_idem", "Cam A", "1")
    db_session.flush()
    upsert_camera(db_session, "cam_idem", "Cam A Updated", "1")
    db_session.flush()
    from src.storage.models import Camera
    from sqlalchemy import select
    count = db_session.execute(select(Camera).where(Camera.id == "cam_idem")).all()
    assert len(count) == 1


def test_bulk_insert_tracking_events(db_session):
    now = time.time()
    updates = [
        TrackUpdate(camera_id="cam_repo", track_id=i, x=float(i * 10),
                    y=float(i * 5), timestamp=now + i, confidence=0.9)
        for i in range(5)
    ]
    count = bulk_insert_tracking_events(db_session, updates)
    db_session.flush()
    assert count == 5


def test_bulk_insert_empty_list(db_session):
    count = bulk_insert_tracking_events(db_session, [])
    assert count == 0


def test_get_events_by_timerange(db_session):
    t0 = time.time()
    updates = [
        TrackUpdate(camera_id="cam_range", track_id=0, x=1.0, y=2.0,
                    timestamp=t0, confidence=0.8),
        TrackUpdate(camera_id="cam_range", track_id=1, x=3.0, y=4.0,
                    timestamp=t0 + 1, confidence=0.8),
    ]
    bulk_insert_tracking_events(db_session, updates)
    db_session.flush()

    events = get_events_by_timerange(db_session, t0 - 1, t0 + 10)
    assert any(e.camera_id == "cam_range" for e in events)


def test_get_xy_points(db_session):
    t0 = time.time()
    updates = [
        TrackUpdate(camera_id="cam_xy", track_id=0, x=11.0, y=22.0,
                    timestamp=t0, confidence=0.9),
    ]
    bulk_insert_tracking_events(db_session, updates)
    db_session.flush()

    points = get_xy_points(db_session, t0 - 1, t0 + 10, "cam_xy")
    assert (11.0, 22.0) in points


def test_bulk_insert_dwell_records(db_session):
    t0 = time.time()
    updates = [
        DwellUpdate(camera_id="cam_bulk", track_id=1, zone_id="entrance",
                    entry_time=t0, exit_time=t0 + 5),
        DwellUpdate(camera_id="cam_bulk", track_id=2, zone_id="entrance",
                    entry_time=t0, exit_time=t0 + 12),
    ]
    count = bulk_insert_dwell_records(db_session, updates)
    db_session.flush()
    assert count == 2


def test_insert_and_query_dwell_record(db_session):
    t0 = time.time()
    record = insert_dwell_record(db_session, "cam_dwell", 99, "zone_a", t0, t0 + 30)
    db_session.flush()
    assert record.dwell_seconds == pytest.approx(30.0)


def test_get_zone_dwell_summary(db_session):
    t0 = time.time()
    insert_dwell_record(db_session, "cam_sum", 1, "zone_sum", t0, t0 + 10)
    insert_dwell_record(db_session, "cam_sum", 2, "zone_sum", t0, t0 + 20)
    db_session.flush()

    summary = get_zone_dwell_summary(db_session, "zone_sum", t0 - 1, t0 + 100)
    assert summary["visits"] == 2
    assert summary["avg_dwell_seconds"] == pytest.approx(15.0)
    assert summary["max_dwell_seconds"] == pytest.approx(20.0)
