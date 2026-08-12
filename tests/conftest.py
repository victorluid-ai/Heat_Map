import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.storage.database import get_session
from src.storage.models import Base
from src.heatmap.floor_plan import FloorPlan
from src.heatmap.accumulator import HeatmapAccumulator


@pytest.fixture(scope="session")
def db_components():
    # StaticPool forces all sessions to share the same in-memory SQLite connection
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    yield engine, factory
    engine.dispose()


@pytest.fixture
def session_factory(db_components):
    _, factory = db_components
    return factory


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def small_floor_plan():
    return FloorPlan("nonexistent_path_for_tests", (100, 80))


@pytest.fixture
def accumulator(small_floor_plan):
    return HeatmapAccumulator(small_floor_plan, blur_kernel=5, decay_factor=0.99)


@pytest.fixture
def api_client(session_factory, small_floor_plan):
    from starlette.testclient import TestClient
    from src.api.app import app
    from src.api.dependencies import get_coordinator, get_session_factory

    acc = HeatmapAccumulator(small_floor_plan, blur_kernel=5, decay_factor=0.99)
    mock_coord = MagicMock()
    mock_coord.camera_ids = ["cam_0"]
    mock_coord._event_bus.qsize.return_value = 0
    mock_coord.get_accumulator.return_value = acc

    app.dependency_overrides[get_coordinator] = lambda: mock_coord
    app.dependency_overrides[get_session_factory] = lambda: session_factory

    minimal_cfg = {
        "storage": {"db_url": "sqlite:///:memory:", "batch_write_interval_seconds": 1,
                    "batch_write_max_events": 500},
        "cameras": [],
        "detection": {"model": "yolov8n.pt", "confidence_threshold": 0.4, "device": "cpu"},
        "tracking": {"max_age": 30, "min_hits": 3},
        "heatmap": {"floor_plan_path": "nonexistent", "resolution": [100, 80],
                    "blur_kernel_size": 5, "decay_factor": 0.995},
        "api": {"host": "0.0.0.0", "port": 8000},
        "dashboard": {"api_base_url": "http://localhost:8000", "refresh_interval_ms": 1000},
        "auth": {"secret_key": "test-secret", "token_expire_minutes": 60},
    }

    with patch("src.utils.config.load_config", return_value=minimal_cfg), \
         patch("src.api.app.init_db", return_value=(MagicMock(), session_factory)), \
         patch("src.api.app.PipelineCoordinator", return_value=mock_coord):
        with TestClient(app) as client:
            yield client

    app.dependency_overrides.clear()
