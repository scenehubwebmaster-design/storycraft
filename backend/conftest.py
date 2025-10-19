import pytest
import logging
from fastapi.testclient import TestClient

from backend.main import app
import base64
from unittest.mock import patch
from dataclasses import dataclass
from io import BytesIO
try:
    from PIL import Image
except Exception:
    Image = None


# --- Provider mocks ---
@dataclass
class GenerationResult:
    meta: dict

    def __str__(self):
        # Maintain backwards compatibility when callers print or treat the second
        # returned value as a string (prompt).
        return self.meta.get("prompt", "")


def _fake_image_base64_bytes(width=1, height=1, color=(0, 0, 0)):
    """Return a valid 1x1 PNG encoded as base64. Uses Pillow when available.

    Falls back to a deterministic byte sequence if Pillow is not installed.
    """
    if Image is not None:
        img = Image.new("RGBA", (width, height), color)
        buf = BytesIO()
        img.save(buf, format="PNG")
        raw = buf.getvalue()
    else:
        raw = b"PNGDATA" + bytes([width % 256, height % 256, color[0] % 256])
    return base64.b64encode(raw).decode("ascii")


@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient for integration tests against the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def ensure_seeded_world():
    """Ensure there's at least one sample world in the DB for image endpoint tests.

    When tests run against an in-memory DB we need to create minimal seed data that
    some tests rely on (previously created by a separate seed script when using
    an on-disk DB). This fixture runs once per session.
    """
    try:
        # Import DB/session and models from the backend package
        from backend.database import SessionLocal, engine, Base
        from backend.models import World

        # Ensure tables exist on the test engine
        Base.metadata.create_all(bind=engine)

        session = SessionLocal()
        try:
            existing = session.query(World).count()
            if existing == 0:
                # Insert a minimal seeded world with a tiny image so image endpoints can run
                img_b64 = _fake_image_base64_bytes(16, 16)
                w = World(name="Seeded Sample World", description="Auto-seeded for tests", world_image=img_b64, world_map=img_b64, image_prompt="seeded for tests")
                session.add(w)
                session.commit()
        finally:
            session.close()
    except Exception:
        # If anything goes wrong, don't break tests - individual tests can patch or seed as needed
        pass


@pytest.fixture(autouse=True)
def caplog_level(monkeypatch):
    """Ensure logging during tests is visible and at INFO by default.

    This fixture is autouse so all tests get consistent logging capture.
    """
    logging.getLogger().setLevel(logging.INFO)
    yield


@pytest.fixture(autouse=True)
def mock_providers(monkeypatch):
    """Autouse fixture that patches external provider clients to deterministic fakes.

    This prevents CI from calling real external services and provides stable
    image_base64 strings and simple generation metadata.
    """
    # Patch stable diffusion client generate functions
    try:
        import backend.stablediffusion_client as sd_client

        def fake_generate(*args, provider_name="stable-diffusion", model="sd-default", width=512, height=512, **kwargs):
            img_b64 = _fake_image_base64_bytes(1, 1)
            meta = {"prompt": "fake stable diffusion prompt", "provider": provider_name, "model": model, "width": width, "height": height}
            return img_b64, GenerationResult(meta)

        monkeypatch.setattr(sd_client, "generate_image", fake_generate, raising=False)
        monkeypatch.setattr(sd_client, "generate_portrait_with_sd", fake_generate, raising=False)
    except Exception:
        # If client not present, ignore - tests that rely on it can patch explicitly
        pass

    # Patch openai/imagen/groq style clients similarly if present
    for mod_name, func_name in [
        ("backend.openai_image_client", "generate_image"),
        ("backend.imagen_client", "generate_image"),
        ("backend.groq_client", "generate_structured")
    ]:
        try:
            mod = __import__(mod_name, fromlist=["*"])
            if hasattr(mod, func_name):
                def _fake(*a, provider_name=mod_name.split('.')[-1], model="mock-model", **k):
                    img = _fake_image_base64_bytes(1, 1)
                    meta = {"prompt": f"fake prompt from {provider_name}", "provider": provider_name, "model": model, "width": 1, "height": 1}
                    return img, GenerationResult(meta)

                monkeypatch.setattr(mod, func_name, _fake, raising=False)
        except Exception:
            continue

    yield
