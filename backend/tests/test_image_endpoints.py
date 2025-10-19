import pytest
from fastapi.testclient import TestClient

# Import the app from the backend module (backend is a package)
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_get_worlds_has_seeded_world(client):
    resp = client.get("/api/worlds/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # ensure at least one world exists (seed script should have created id=1)
    assert len(data) >= 1


def test_region_crop_returns_image_base64(client):
    # Use seeded world id=1; percent bounds cover a central area
    payload = {
        "world_id": 1,
        "percent_bounds": {"x1": 10, "y1": 10, "x2": 90, "y2": 90},
        "upscale": 1,
    }
    resp = client.post("/api/generate/region/crop/", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "image_base64" in data and data["image_base64"], "image_base64 missing or empty"
    assert "width" in data and "height" in data


def test_crop_and_generate_returns_image_or_fallback(client):
    payload = {
        "world_id": 1,
        "percent_bounds": {"x1": 10, "y1": 10, "x2": 90, "y2": 90},
        "prompt": "A painterly fantasy map segment",
        "provider": "stablediffusion",
        "upscale": 1,
    }
    resp = client.post("/api/generate/region/crop-and-generate/", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    # Either provider returned image_base64, or we got crop_base64 as fallback
    assert ("image_base64" in data and data["image_base64"]) or ("crop_base64" in data and data["crop_base64"]), "No image returned"
