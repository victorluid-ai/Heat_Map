from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import get_session_factory, require_admin
from ..schemas import (
    CameraAdminResponse,
    CameraAssignRequest,
    ShopAdminResponse,
    ShopCreateRequest,
    UserAdminResponse,
    UserPatchRequest,
)
from ...storage.database import get_session
from ...storage.repository import (
    create_shop,
    delete_shop,
    get_all_cameras,
    get_all_shops,
    get_all_users,
    get_camera,
    get_user_by_id,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserAdminResponse])
async def list_users(
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        users = get_all_users(session)
        return [
            UserAdminResponse(
                id=u.id,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                shop_count=len(u.shops),
            )
            for u in users
        ]


@router.patch("/users/{user_id}", response_model=UserAdminResponse)
async def patch_user(
    user_id: int,
    body: UserPatchRequest,
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        user = get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.is_active = body.is_active
        return UserAdminResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            shop_count=len(user.shops),
        )


@router.get("/shops", response_model=list[ShopAdminResponse])
async def list_shops(
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        shops = get_all_shops(session)
        return [
            ShopAdminResponse(
                id=s.id,
                name=s.name,
                address=s.address,
                owner_id=s.owner_id,
                owner_email=s.owner.email,
                camera_count=len(s.cameras),
            )
            for s in shops
        ]


@router.post("/shops", response_model=ShopAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_shop_endpoint(
    body: ShopCreateRequest,
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        owner = get_user_by_id(session, body.owner_id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")
        shop = create_shop(session, body.name, body.address, body.owner_id)
        return ShopAdminResponse(
            id=shop.id,
            name=shop.name,
            address=shop.address,
            owner_id=shop.owner_id,
            owner_email=owner.email,
            camera_count=0,
        )


@router.delete("/shops/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_shop(
    shop_id: int,
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        from ...storage.models import Shop
        shop = session.get(Shop, shop_id)
        if not shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
        delete_shop(session, shop_id)


@router.get("/cameras", response_model=list[CameraAdminResponse])
async def list_cameras(
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        cameras = get_all_cameras(session)
        return [
            CameraAdminResponse(
                id=c.id,
                name=c.name,
                is_active=c.is_active,
                shop_id=c.shop_id,
                shop_name=c.shop.name if c.shop else None,
            )
            for c in cameras
        ]


@router.patch("/cameras/{camera_id}", response_model=CameraAdminResponse)
async def patch_camera(
    camera_id: str,
    body: CameraAssignRequest,
    _admin=Depends(require_admin),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        camera = get_camera(session, camera_id)
        if not camera:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
        camera.shop_id = body.shop_id
        shop_name = None
        if body.shop_id is not None:
            from ...storage.models import Shop
            shop = session.get(Shop, body.shop_id)
            if shop is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found")
            shop_name = shop.name
        return CameraAdminResponse(
            id=camera.id,
            name=camera.name,
            is_active=camera.is_active,
            shop_id=camera.shop_id,
            shop_name=shop_name,
        )
