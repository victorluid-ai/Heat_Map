import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..dependencies import get_coordinator
from ...utils.image_utils import frame_to_jpeg_bytes

router = APIRouter(prefix="/stream", tags=["stream"])
logger = logging.getLogger(__name__)


async def _mjpeg_generator(coordinator, camera_id: str):
    while True:
        runner = coordinator.get_runner(camera_id)
        if runner is None:
            break
        frame = runner.get_annotated_frame()
        if frame is not None:
            jpg = frame_to_jpeg_bytes(frame)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")
        await asyncio.sleep(0.04)  # ~25 fps ceiling


@router.get("/{camera_id}")
async def stream_camera(camera_id: str, coordinator=Depends(get_coordinator)):
    if camera_id not in coordinator.camera_ids:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id!r} not found")
    return StreamingResponse(
        _mjpeg_generator(coordinator, camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
