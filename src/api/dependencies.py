from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import sessionmaker
from ..pipeline.coordinator import PipelineCoordinator
from ..storage.database import get_session
from ..storage.models import User

_security = HTTPBearer()


def get_coordinator(request: Request) -> PipelineCoordinator:
    return request.app.state.coordinator


def get_session_factory(request: Request) -> sessionmaker:
    return request.app.state.session_factory


def get_config(request: Request) -> dict:
    return request.app.state.config


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> User:
    config = request.app.state.config
    try:
        payload = jwt.decode(credentials.credentials, config["auth"]["secret_key"], algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    session_factory = request.app.state.session_factory
    with get_session(session_factory) as session:
        user = session.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user


def require_admin(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> User:
    user = get_current_user(request, credentials)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
