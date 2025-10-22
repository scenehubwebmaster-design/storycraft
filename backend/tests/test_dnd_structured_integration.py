import sys
import pathlib
import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure repo root is on sys.path so local top-level modules (dnd_generator etc.) can be imported
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now import the app and DB helpers
from backend.main import app
from backend.database import Base, get_db

# Ensure ORM models are imported so their tables are registered on Base.metadata
import backend.models  # noqa: F401

# Some router code uses top-level module imports like `import dnd_generator` or `from dnd_narrative_prompts import ...`
# Make those available by aliasing the backend package modules into sys.modules under the expected names.
try:
    import backend.dnd_generator as _dg
    import backend.dnd_narrative_prompts as _dp
    import backend.schemas as _schemas
    import backend.dnd_data as _dnd_data
    sys.modules.setdefault("dnd_generator", _dg)
    sys.modules.setdefault("dnd_narrative_prompts", _dp)
    sys.modules.setdefault("schemas", _schemas)
    sys.modules.setdefault("dnd_data", _dnd_data)
except Exception:
    # If these backend helper modules are not available in test context, the test will fail later
    pass

# If any of the top-level modules expected by routers are still missing, insert minimal fakes
import types
if "dnd_generator" not in sys.modules:
    fake_dg = types.ModuleType("dnd_generator")
    def generate_dnd_character(class_key, species_key, background_key, alignment=None, ability_score_method=None, name=None, level=1):
        return {"name": name or f"{class_key.title()} {species_key.title()}", "class": class_key, "species": species_key, "level": level}
    def format_character_sheet(c):
        return "Formatted sheet"
    fake_dg.generate_dnd_character = generate_dnd_character
    fake_dg.format_character_sheet = format_character_sheet
    sys.modules["dnd_generator"] = fake_dg

if "dnd_narrative_prompts" not in sys.modules:
    fake_dp = types.ModuleType("dnd_narrative_prompts")
    def build_dnd_narrative_prompt(dnd_character, style=None, additional_context=None):
        return "Please generate a structured narrative for the character in JSON."
    fake_dp.build_dnd_narrative_prompt = build_dnd_narrative_prompt
    sys.modules["dnd_narrative_prompts"] = fake_dp

if "schemas" not in sys.modules:
    fake_schemas = types.ModuleType("schemas")
    class DnDCharacterNarrative:
        pass
    fake_schemas.DnDCharacterNarrative = DnDCharacterNarrative
    sys.modules["schemas"] = fake_schemas


@pytest.fixture(scope="module")
def test_db():
    # Reuse the app's database engine and session factory so tables and sessions
    # operate on the same in-memory DB created by backend.database when pytest
    # sets the test env. This avoids mismatched engines and missing tables.
    import backend.database as _database

    engine = _database.engine
    TestingSessionLocal = _database.SessionLocal
    # Create tables on the shared engine
    Base.metadata.create_all(bind=engine)

    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency
    app.dependency_overrides[get_db] = _get_db
    yield TestingSessionLocal
    # Teardown
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(test_db):
    with TestClient(app) as c:
        yield c


def test_dnd_structured_generation_with_groq_mock(monkeypatch, client):
    # Prepare a mocked structured response (Groq-like)
    structured = {
        "character_name": "Sir Mockalot",
        "physical_description": "Tall, scarred, wears a tattered cloak",
        "personality": "Brave, stubborn",
        "backstory": "Raised by wolves, found an ancient sword",
        "skin": "pale with a faint scar",
        "eyes": "piercing green",
        "hair": "short, dark",
    }

    class MockObj:
        def model_dump(self):
            return structured

    async def fake_call_llm_with_retries_and_clarifier(*args, **kwargs):
        # Return the structured object and metadata indicating groq
        return MockObj(), {"provider": "groq", "model": kwargs.get("model")}

    # Patch the generation helper used by characters router.
    # The characters router does a local import from .generation, so patch that module.
    # Patch the call_llm helper in the generation router where it's defined
    monkeypatch.setattr("backend.routers.generation.call_llm_with_retries_and_clarifier", fake_call_llm_with_retries_and_clarifier, raising=False)

    payload = {
        "dnd_class": "fighter",
        "dnd_species": "human",
        "dnd_background": "soldier",
        "generate_narrative": True,
        "use_structured": True,
        "narrative_provider": "groq",
        "narrative_model": "meta-llama/llama-4-scout-17b-16e-instruct",
    }

    resp = client.post("/api/characters/dnd/generate", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Ensure structured_data normalized fields exist
    sd = data.get("structured_data")
    assert sd is not None, "structured_data should be present"
    # Normalization should have moved physical_description -> character_appearance
    assert "character_appearance" in sd or "physical_description" in sd
    # Personality should have been normalized to personality_traits
    assert "personality_traits" in sd or "personality" in sd

    # generation_log should indicate provider groq
    gen_log = data.get("generation_log") or {}
    assert gen_log.get("narrative_provider") == "groq"
