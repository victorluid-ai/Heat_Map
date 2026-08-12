from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    email: str
    role: str


class CameraInfo(BaseModel):
    id: str
    name: str
    is_active: bool


class ShopResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    camera_ids: list[str]
    cameras: list[CameraInfo] = []


class ShopUpdateRequest(BaseModel):
    name: str


class CameraUpdateRequest(BaseModel):
    name: str


class HeatmapResponse(BaseModel):
    camera_id: str
    total_updates: int
    image_url: str


class TrafficDataPoint(BaseModel):
    hour: float
    count: int


class DwellSummary(BaseModel):
    zone_id: str
    visits: int
    avg_dwell_seconds: float
    max_dwell_seconds: float


class HealthResponse(BaseModel):
    status: str
    cameras: list[str]
    total_events_queued: int


class UserAdminResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    shop_count: int


class UserPatchRequest(BaseModel):
    is_active: bool


class ShopAdminResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    owner_id: int
    owner_email: str
    camera_count: int


class ShopCreateRequest(BaseModel):
    name: str
    address: Optional[str] = None
    owner_id: int


class CameraAdminResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    shop_id: Optional[int]
    shop_name: Optional[str]


class CameraAssignRequest(BaseModel):
    shop_id: Optional[int]
