import pytest
from fastapi.testclient import TestClient

from backend.main import app


class FakeSDClient:
    def __init__(self):
        pass

    def generate_image(self, **kwargs):
        # Return deterministic fake image and echo prompt for validation
        return {"image": "fake_landscape_base64", "info": {"received": kwargs}}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_generate_world_landscape_endpoint_monkeypatched(monkeypatch, client):
    # Patch the StableDiffusionClient to avoid external calls
    import backend.stablediffusion_client as sdmod

    monkeypatch.setattr(sdmod, "StableDiffusionClient", FakeSDClient)

    payload = {
        "world_name": "Test World",
        "description": "A test world for landscape generation, rolling hills and dramatic sky.",
        "landscape_type": "overview",
        "provider": "stablediffusion",
        "model": None,
        "style_preset": "cinematic",
    }

    # The router expects these as query/form parameters rather than a JSON body
    resp = client.post("/api/generate/world/generate-landscape/", params=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "image_base64" in data and data["image_base64"]
    assert "prompt" in data and data["prompt"]
    # Ensure the chosen style appears in the prompt
    assert "cinematic" in data["prompt"].lower()
