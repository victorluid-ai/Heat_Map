from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import bcrypt as _bcrypt
from jose import jwt
from ..dependencies import get_config, get_current_user, get_session_factory
from ..schemas import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from ...storage.database import get_session
from ...storage.repository import create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


def _make_token(user_id: int, secret: str, expire_minutes: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, secret, algorithm="HS256")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    session_factory=Depends(get_session_factory),
    config=Depends(get_config),
):
    with get_session(session_factory) as session:
        if get_user_by_email(session, body.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        user = create_user(session, body.email, _hash(body.password))
        user_id = user.id
    token = _make_token(user_id, config["auth"]["secret_key"], config["auth"]["token_expire_minutes"])
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session_factory=Depends(get_session_factory),
    config=Depends(get_config),
):
    with get_session(session_factory) as session:
        user = get_user_by_email(session, body.email)
        if not user or not _verify(body.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        user_id = user.id
    token = _make_token(user_id, config["auth"]["secret_key"], config["auth"]["token_expire_minutes"])
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def me(current_user=Depends(get_current_user)):
    return MeResponse(email=current_user.email, role=current_user.role)
