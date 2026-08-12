from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import get_current_user, get_session_factory
from ..schemas import CameraInfo, CameraUpdateRequest, ShopResponse, ShopUpdateRequest
from ...storage.database import get_session
from ...storage.repository import (
    get_camera,
    get_shop_by_id,
    get_shops_by_owner,
    update_camera_name,
    update_shop_name,
)

router = APIRouter(prefix="/shops", tags=["shops"])


def _shop_response(shop) -> ShopResponse:
    active_cameras = [c for c in shop.cameras if c.is_active]
    return ShopResponse(
        id=shop.id,
        name=shop.name,
        address=shop.address,
        camera_ids=[c.id for c in active_cameras],
        cameras=[
            CameraInfo(id=c.id, name=c.name, is_active=c.is_active)
            for c in active_cameras
        ],
    )


def _require_owned_shop(session, shop_id: int, owner_id: int):
    shop = get_shop_by_id(session, shop_id)
    if shop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
    if shop.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your shop")
    return shop


@router.get("", response_model=list[ShopResponse])
async def list_shops(
    current_user=Depends(get_current_user),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        shops = get_shops_by_owner(session, current_user.id)
        return [_shop_response(s) for s in shops]


@router.patch("/{shop_id}", response_model=ShopResponse)
async def rename_shop(
    shop_id: int,
    body: ShopUpdateRequest,
    current_user=Depends(get_current_user),
    session_factory=Depends(get_session_factory),
):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    if len(name) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name too long")

    with get_session(session_factory) as session:
        shop = _require_owned_shop(session, shop_id, current_user.id)
        update_shop_name(session, shop, name)
        return _shop_response(shop)


@router.patch("/{shop_id}/cameras/{camera_id}", response_model=CameraInfo)
async def rename_camera(
    shop_id: int,
    camera_id: str,
    body: CameraUpdateRequest,
    current_user=Depends(get_current_user),
    session_factory=Depends(get_session_factory),
):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required")
    if len(name) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name too long")

    with get_session(session_factory) as session:
        _require_owned_shop(session, shop_id, current_user.id)
        camera = get_camera(session, camera_id)
        if camera is None or camera.shop_id != shop_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
        update_camera_name(session, camera, name)
        return CameraInfo(id=camera.id, name=camera.name, is_active=camera.is_active)
