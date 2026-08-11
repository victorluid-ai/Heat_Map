import time
import logging
from fastapi import APIRouter, Depends, Query
from ..dependencies import get_session_factory
from ..schemas import TrafficDataPoint, DwellSummary
from ...storage.repository import get_hourly_counts, get_zone_dwell_summary
from ...storage.database import get_session

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


@router.get("/traffic", response_model=list[TrafficDataPoint])
async def traffic_data(
    start: float = Query(default=None),
    end: float = Query(default=None),
    camera_id: str = Query(default=None),
    session_factory=Depends(get_session_factory),
):
    now = time.time()
    if end is None:
        end = now
    if start is None:
        start = now - 86400
    with get_session(session_factory) as session:
        rows = get_hourly_counts(session, start, end, camera_id)
    return [TrafficDataPoint(hour=r["hour"], count=r["count"]) for r in rows]


@router.get("/dwell", response_model=DwellSummary)
async def dwell_summary(
    zone_id: str = Query(default="entrance"),
    start: float = Query(default=None),
    end: float = Query(default=None),
    session_factory=Depends(get_session_factory),
):
    now = time.time()
    if end is None:
        end = now
    if start is None:
        start = now - 86400
    with get_session(session_factory) as session:
        summary = get_zone_dwell_summary(session, zone_id, start, end)
    return DwellSummary(**summary)
