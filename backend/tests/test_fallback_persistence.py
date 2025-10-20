from fastapi.testclient import TestClient
from backend.main import app
import sys
import types

client = TestClient(app)


def test_generate_dnd_persists_fallback_traits():
    # Inject fake dnd_generator module (imported as top-level by the router)
    fake_dnd = types.ModuleType("dnd_generator")

    def generate_dnd_character(class_key, species_key, background_key, alignment=None, ability_score_method=None, name=None, level=1):
        # Return a minimal character dict the router expects
        return {
            "name": name or "Generated",
            "class": class_key.capitalize(),
            "species": species_key.capitalize(),
            "level": level,
            "class_description": f"A {class_key}",
            "species_description": f"A {species_key}",
            "background_description": f"Background {background_key}",
            "alignment": alignment or "Neutral",
            "ability_scores": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
            "hit_points": 10,
            "armor_class": 10,
            "initiative": "+0",
            "speed": 30,
            "proficiency_bonus": "+2",
            "skill_proficiencies": [],
            "saving_throws": [],
            "armor_proficiencies": [],
            "weapon_proficiencies": [],
            "tool_proficiencies": [],
            "racial_traits": [],
            "class_features": [],
            "background_feature": "",
            "background_feature_description": "",
            "equipment": {},
            "languages": [],
        }

    def format_character_sheet(d):
        return "CHAR SHEET"

    fake_dnd.generate_dnd_character = generate_dnd_character
    fake_dnd.format_character_sheet = format_character_sheet
    sys.modules["dnd_generator"] = fake_dnd

    # Inject fake backend.generation.call_llm_with_retries_and_clarifier
    fake_gen = types.ModuleType("backend.generation")

    def call_llm_with_retries_and_clarifier(base_prompt, provider, schema_model=None, model=None, max_attempts=3, initial_temperature=0.95, retry_temperature=0.6, authoritative_fields=None):
        # Simulate failure for structured schema_model (raise) and return fallback JSON text for schema_model=None
        if schema_model is not None:
            raise Exception("Simulated structured generation failure")
        # Return a JSON string with physical traits and metadata dict
        fallback_text = '{"skin":"Simulated skin","eyes":"Simulated eyes","hair":"Simulated hair"}'
        metadata = {"provider": "test"}
        return fallback_text, metadata

    fake_gen.call_llm_with_retries_and_clarifier = call_llm_with_retries_and_clarifier
    sys.modules["backend.generation"] = fake_gen

    # Provide a simple dnd_narrative_prompts.build_dnd_narrative_prompt used by the router
    fake_prompts = types.ModuleType("dnd_narrative_prompts")

    def build_dnd_narrative_prompt(dnd_character, style=None, additional_context=None):
        return "Please produce a narrative"

    fake_prompts.build_dnd_narrative_prompt = build_dnd_narrative_prompt
    sys.modules["dnd_narrative_prompts"] = fake_prompts

    # Provide a minimal 'schemas' module with DnDCharacterNarrative placeholder
    fake_schemas = types.ModuleType("schemas")
    fake_schemas.DnDCharacterNarrative = None
    sys.modules["schemas"] = fake_schemas

    payload = {
        "provider": "groq",
        "model": "",
        "cultural_origin": "generic",
        "archetype": "adventurer",
        "themes": ["exploration"],
        "personality_traits": ["brave"],
        "physical_traits": ["athletic"],
        "emotional_traits": ["stoic"],
        "dnd_level": 3,
        "dnd_class": "fighter",
        "dnd_species": "human",
        "dnd_background": "soldier",
        "name": "Test Fighter",
        "generate_narrative": True,
        "narrative_provider": "groq",
        "narrative_model": "",
        "use_structured": True,
        "custom_details": "Testing narrative + fallback for physical traits and names"
    }

    # Call the generate endpoint
    resp = client.post("/api/characters/dnd/generate/", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Ensure structured_data contains fallback physical traits when ai_narrative had them
    sd = data.get("structured_data")
    # structured_data should be either None or a dict; in fallback case we expect a dict
    assert sd is not None, "structured_data should be present when fallback produced traits"
    for key in ("skin", "eyes", "hair"):
        assert key in sd and sd.get(key), f"Expected '{key}' in structured_data"

    # Also confirm the saved character GET endpoint returns the same structured_data
    char_id = data.get("id")
    get_resp = client.get(f"/api/characters/{char_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    fetched_sd = fetched.get("structured_data")
    assert fetched_sd is not None
    for key in ("skin", "eyes", "hair"):
        assert key in fetched_sd and fetched_sd.get(key)
