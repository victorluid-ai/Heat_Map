"""Tests for customer shop/camera rename endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import pytest
from jose import jwt

from src.storage.database import get_session
from src.storage.models import Camera, Shop, User
from src.storage.repository import upsert_camera

AUTH_SECRET = "test-secret"


@pytest.fixture
def auth_config(api_client):
    from src.api.app import app

    cfg = {
        "storage": {
            "db_url": "sqlite:///:memory:",
            "batch_write_interval_seconds": 1,
            "batch_write_max_events": 500,
        },
        "cameras": [],
        "detection": {"model": "yolov8n.pt", "confidence_threshold": 0.4, "device": "cpu"},
        "tracking": {"max_age": 30, "min_hits": 3},
        "heatmap": {
            "floor_plan_path": "nonexistent",
            "resolution": [100, 80],
            "blur_kernel_size": 5,
            "decay_factor": 0.995,
        },
        "api": {"host": "0.0.0.0", "port": 8000},
        "dashboard": {"api_base_url": "http://localhost:8000", "refresh_interval_ms": 1000},
        "auth": {"secret_key": AUTH_SECRET, "token_expire_minutes": 60},
    }
    app.state.config = cfg
    return cfg


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode({"sub": str(user_id), "exp": exp}, AUTH_SECRET, algorithm="HS256")


def _seed_owner_with_shop(session_factory):
    suffix = uuid.uuid4().hex[:8]
    with get_session(session_factory) as session:
        owner = User(
            email=f"owner-{suffix}@example.com",
            password_hash=_hash("secret123"),
            role="customer",
        )
        other = User(
            email=f"other-{suffix}@example.com",
            password_hash=_hash("secret123"),
            role="customer",
        )
        session.add_all([owner, other])
        session.flush()
        shop = Shop(name="Original Shop", address="Main St", owner_id=owner.id)
        session.add(shop)
        session.flush()
        cam = Camera(
            id=f"cam_{suffix}",
            name="Entrance Cam",
            source_url="0",
            shop_id=shop.id,
        )
        session.add(cam)
        session.flush()
        return owner.id, other.id, shop.id, cam.id


def test_list_shops_includes_cameras(api_client, session_factory, auth_config):
    owner_id, _, _, _ = _seed_owner_with_shop(session_factory)
    resp = api_client.get("/shops", headers={"Authorization": f"Bearer {_token(owner_id)}"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["name"] == "Original Shop"
    assert body[0]["cameras"][0]["name"] == "Entrance Cam"


def test_rename_shop(api_client, session_factory, auth_config):
    owner_id, _, shop_id, _ = _seed_owner_with_shop(session_factory)
    resp = api_client.patch(
        f"/shops/{shop_id}",
        headers={"Authorization": f"Bearer {_token(owner_id)}"},
        json={"name": "  Nueva Tienda  "},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Nueva Tienda"


def test_rename_shop_forbidden_for_other_user(api_client, session_factory, auth_config):
    _, other_id, shop_id, _ = _seed_owner_with_shop(session_factory)
    resp = api_client.patch(
        f"/shops/{shop_id}",
        headers={"Authorization": f"Bearer {_token(other_id)}"},
        json={"name": "Hacked"},
    )
    assert resp.status_code == 403


def test_rename_camera(api_client, session_factory, auth_config):
    owner_id, _, shop_id, camera_id = _seed_owner_with_shop(session_factory)
    resp = api_client.patch(
        f"/shops/{shop_id}/cameras/{camera_id}",
        headers={"Authorization": f"Bearer {_token(owner_id)}"},
        json={"name": "Puerta Principal"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Puerta Principal"
    assert resp.json()["id"] == camera_id


def test_rename_camera_rejects_empty_name(api_client, session_factory, auth_config):
    owner_id, _, shop_id, camera_id = _seed_owner_with_shop(session_factory)
    resp = api_client.patch(
        f"/shops/{shop_id}/cameras/{camera_id}",
        headers={"Authorization": f"Bearer {_token(owner_id)}"},
        json={"name": "   "},
    )
    assert resp.status_code == 400


def test_upsert_camera_preserves_custom_name(db_session):
    cam = upsert_camera(db_session, "cam_keep", "Config Name", "0")
    db_session.flush()
    cam.name = "Nombre personalizado"
    db_session.flush()
    upsert_camera(db_session, "cam_keep", "Config Name Again", "rtsp://example")
    db_session.flush()
    refreshed = db_session.get(Camera, "cam_keep")
    assert refreshed is not None
    assert refreshed.name == "Nombre personalizado"
    assert refreshed.source_url == "rtsp://example"
