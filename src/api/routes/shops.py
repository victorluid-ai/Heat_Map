from fastapi import APIRouter, Depends
from ..dependencies import get_current_user, get_session_factory
from ..schemas import ShopResponse
from ...storage.database import get_session
from ...storage.repository import get_shops_by_owner

router = APIRouter(prefix="/shops", tags=["shops"])


@router.get("", response_model=list[ShopResponse])
async def list_shops(
    current_user=Depends(get_current_user),
    session_factory=Depends(get_session_factory),
):
    with get_session(session_factory) as session:
        shops = get_shops_by_owner(session, current_user.id)
        return [
            ShopResponse(
                id=s.id,
                name=s.name,
                address=s.address,
                camera_ids=[c.id for c in s.cameras if c.is_active],
            )
            for s in shops
        ]
