import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, update
from .models import Camera, DwellRecord, Shop, TrackingEvent, User
from ..tracking.track_record import DwellUpdate, TrackUpdate

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.scalars(select(User).where(User.email == email)).first()


def create_user(session: Session, email: str, password_hash: str) -> User:
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    session.flush()
    return user


def get_shops_by_owner(session: Session, owner_id: int) -> list[Shop]:
    return list(
        session.scalars(
            select(Shop).where(Shop.owner_id == owner_id).options(joinedload(Shop.cameras))
        ).all()
    )


def upsert_camera(session: Session, camera_id: str, name: str, source_url: str) -> Camera:
    cam = session.get(Camera, camera_id)
    if cam is None:
        cam = Camera(id=camera_id, name=name, source_url=str(source_url))
        session.add(cam)
    else:
        cam.name = name
        cam.source_url = str(source_url)
    return cam


def bulk_insert_tracking_events(session: Session, updates: list[TrackUpdate]) -> int:
    if not updates:
        return 0
    rows = [
        TrackingEvent(camera_id=u.camera_id, track_id=u.track_id,
                      x=u.x, y=u.y, timestamp=u.timestamp, confidence=u.confidence)
        for u in updates
    ]
    session.add_all(rows)
    return len(rows)


def bulk_insert_dwell_records(session: Session, updates: list[DwellUpdate]) -> int:
    if not updates:
        return 0
    rows = [
        DwellRecord(
            camera_id=u.camera_id,
            track_id=u.track_id,
            zone_id=u.zone_id,
            entry_time=u.entry_time,
            exit_time=u.exit_time,
            dwell_seconds=u.exit_time - u.entry_time,
        )
        for u in updates
    ]
    session.add_all(rows)
    return len(rows)


def insert_dwell_record(session: Session, camera_id: str, track_id: int, zone_id: str,
                        entry_time: float, exit_time: float) -> DwellRecord:
    record = DwellRecord(
        camera_id=camera_id, track_id=track_id, zone_id=zone_id,
        entry_time=entry_time, exit_time=exit_time,
        dwell_seconds=exit_time - entry_time,
    )
    session.add(record)
    return record


def get_events_by_timerange(session: Session, start: float, end: float,
                             camera_id: str | None = None) -> list[TrackingEvent]:
    q = select(TrackingEvent).where(
        TrackingEvent.timestamp >= start,
        TrackingEvent.timestamp <= end,
    )
    if camera_id:
        q = q.where(TrackingEvent.camera_id == camera_id)
    return list(session.scalars(q).all())


def get_xy_points(session: Session, start: float, end: float,
                  camera_id: str | None = None) -> list[tuple[float, float]]:
    events = get_events_by_timerange(session, start, end, camera_id)
    return [(e.x, e.y) for e in events]


def get_hourly_counts(session: Session, start: float, end: float,
                      camera_id: str | None = None) -> list[dict]:
    q = (
        select(
            func.cast(func.floor(TrackingEvent.timestamp / 3600) * 3600, TrackingEvent.timestamp.type).label("hour"),
            func.count(TrackingEvent.id).label("count"),
        )
        .where(TrackingEvent.timestamp >= start, TrackingEvent.timestamp <= end)
        .group_by("hour")
        .order_by("hour")
    )
    if camera_id:
        q = q.where(TrackingEvent.camera_id == camera_id)
    rows = session.execute(q).all()
    return [{"hour": r.hour, "count": r.count} for r in rows]


def get_zone_dwell_summary(session: Session, zone_id: str, start: float, end: float) -> dict:
    q = select(
        func.count(DwellRecord.id).label("visits"),
        func.avg(DwellRecord.dwell_seconds).label("avg_dwell"),
        func.max(DwellRecord.dwell_seconds).label("max_dwell"),
    ).where(
        DwellRecord.zone_id == zone_id,
        DwellRecord.entry_time >= start,
        DwellRecord.exit_time <= end,
    )
    row = session.execute(q).one()
    return {
        "zone_id": zone_id,
        "visits": row.visits or 0,
        "avg_dwell_seconds": float(row.avg_dwell or 0),
        "max_dwell_seconds": float(row.max_dwell or 0),
    }


def get_all_users(session: Session) -> list[User]:
    return list(session.scalars(select(User).options(joinedload(User.shops))).unique().all())


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_all_shops(session: Session) -> list[Shop]:
    return list(
        session.scalars(
            select(Shop).options(joinedload(Shop.owner), joinedload(Shop.cameras))
        ).unique().all()
    )


def create_shop(session: Session, name: str, address: str | None, owner_id: int) -> Shop:
    shop = Shop(name=name, address=address, owner_id=owner_id)
    session.add(shop)
    session.flush()
    return shop


def delete_shop(session: Session, shop_id: int) -> None:
    session.execute(update(Camera).where(Camera.shop_id == shop_id).values(shop_id=None))
    shop = session.get(Shop, shop_id)
    if shop:
        session.delete(shop)


def get_all_cameras(session: Session) -> list[Camera]:
    return list(session.scalars(select(Camera).options(joinedload(Camera.shop))).unique().all())


def get_camera(session: Session, camera_id: str) -> Camera | None:
    return session.get(Camera, camera_id)
