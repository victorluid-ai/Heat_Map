import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from ..dependencies import get_coordinator, get_session_factory
from ...storage.repository import get_xy_points
from ...storage.database import get_session
from ...heatmap.kde_renderer import KDERenderer
from ...utils.image_utils import frame_to_png_bytes

router = APIRouter(prefix="/heatmap", tags=["heatmap"])
logger = logging.getLogger(__name__)


@router.get("/live")
async def live_heatmap(
    camera_id: str = "cam_0",
    coordinator=Depends(get_coordinator),
):
    acc = coordinator.get_accumulator(camera_id)
    if acc is None:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id!r} not found")
    image = acc.get_heatmap_image()
    return Response(content=frame_to_png_bytes(image), media_type="image/png")


@router.get("/historical")
async def historical_heatmap(
    start: float = Query(default=None),
    end: float = Query(default=None),
    camera_id: str = Query(default=None),
    coordinator=Depends(get_coordinator),
    session_factory=Depends(get_session_factory),
):
    now = time.time()
    if end is None:
        end = now
    if start is None:
        start = now - 86400
    with get_session(session_factory) as session:
        points = get_xy_points(session, start, end, camera_id)
    resolved_cam = camera_id or (coordinator.camera_ids[0] if coordinator.camera_ids else None)
    acc = coordinator.get_accumulator(resolved_cam) if resolved_cam else None
    if acc is None:
        raise HTTPException(status_code=404, detail="No cameras available")
    renderer = KDERenderer(acc.floor_plan)
    image = renderer.render(points)
    return Response(content=frame_to_png_bytes(image), media_type="image/png")
