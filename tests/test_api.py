import pytest


def test_health_endpoint(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["cameras"], list)
    assert isinstance(body["total_events_queued"], int)


def test_analytics_traffic_default(api_client):
    response = api_client.get("/analytics/traffic")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analytics_traffic_with_params(api_client):
    response = api_client.get("/analytics/traffic?start=0&end=1000000")
    assert response.status_code == 200


def test_analytics_dwell_default(api_client):
    response = api_client.get("/analytics/dwell")
    assert response.status_code == 200
    body = response.json()
    assert "zone_id" in body
    assert "visits" in body


def test_heatmap_live_returns_png(api_client):
    response = api_client.get("/heatmap/live?camera_id=cam_0")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0


def test_heatmap_live_unknown_camera(api_client):
    from unittest.mock import patch
    from src.api.app import app
    from src.api.dependencies import get_coordinator
    from unittest.mock import MagicMock

    mock_coord = MagicMock()
    mock_coord.get_accumulator.return_value = None
    mock_coord.camera_ids = []

    original_override = app.dependency_overrides.get(get_coordinator)
    app.dependency_overrides[get_coordinator] = lambda: mock_coord
    try:
        response = api_client.get("/heatmap/live?camera_id=unknown_cam")
        assert response.status_code == 404
    finally:
        if original_override is not None:
            app.dependency_overrides[get_coordinator] = original_override


def test_heatmap_historical_returns_png(api_client):
    response = api_client.get("/heatmap/historical?start=0&end=1000000")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_docs_endpoint(api_client):
    response = api_client.get("/docs")
    assert response.status_code == 200


def test_stream_unknown_camera(api_client):
    response = api_client.get("/stream/unknown_cam")
    assert response.status_code == 404
