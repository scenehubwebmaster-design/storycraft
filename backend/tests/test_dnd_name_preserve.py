import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch
import sys
import types


@pytest.mark.asyncio
async def test_preserve_canonical_name_when_llm_returns_different():
    client = TestClient(app)

    # Prepare payload matching DnDCharacterGenerateRequest
    payload = {
        "name": "Kaelin Valtor",
        "dnd_class": "barbarian",
        "dnd_species": "goliath",
        "dnd_background": "outlander",
        "dnd_alignment": "Neutral Good",
        "dnd_level": 1,
        "generate_narrative": True,
        "narrative_provider": "groq",
        "use_structured": True,
        "narrative_style": "detailed",
    }

    # Create a fake structured response where the model suggests a different name
    fake_structured = {
        "character_name": "Aurelian Thrain",
        "age": "young adult",
        "height": "5'10\"",
        "weight": "150 lbs",
        "eyes": "Hazel with a subtle golden sparkle",
        "skin": "Warm, golden-brown",
        "hair": "Short, dark brown"
    }

    async def fake_call_llm_structured(*args, **kwargs):
        # Return a simple object with model_dump
        class Dummy:
            def model_dump(self):
                return fake_structured

        return Dummy(), {"provider":"groq", "model":"mock"}

    # Patch call_llm_structured (defined in generation) to return fake conflicting name
    # Inject a fake dnd_generator module so the endpoint can import it during the test
    fake_mod = types.ModuleType("dnd_generator")

    def fake_generate_dnd_character(class_key, species_key, background_key, alignment, ability_score_method, name, level):
        # Return minimal dict expected by the handler
        return {
            "name": name or "Generated Name",
            "class": class_key.title(),
            "level": level,
            "species": species_key.title(),
            "background": background_key.title(),
            "alignment": alignment or "Neutral",
                "class_description": f"A {class_key} trained in battle.",
                "species_description": f"A {species_key} of sturdy build.",
                "background_description": f"From the {background_key} background.",
            "ability_scores": {"strength":15, "dexterity":13, "constitution":14, "intelligence":12, "wisdom":10, "charisma":8},
            "hit_points": 14,
            "armor_class": 11,
            "initiative": "+1",
            "speed": 30,
            "proficiency_bonus": "+2",
                "skill_proficiencies": ["Athletics","Survival"],
                "saving_throws": ["Strength","Constitution"],
            "armor_proficiencies": ["Light armor"],
            "weapon_proficiencies": ["Simple weapons"],
            "tool_proficiencies": [],
            "racial_traits": ["Powerful Build"],
            "class_features": ["Rage"],
            "background_feature": "Wanderer",
            "background_feature_description": "Can find food and water",
            "equipment": {"weapons": ["Greataxe"]},
            "spellcasting": None,
            "languages": ["Common","Giant"],
        }

    def fake_format_character_sheet(d):
        return "DUMMY SHEET"

    fake_mod.generate_dnd_character = fake_generate_dnd_character
    fake_mod.format_character_sheet = fake_format_character_sheet
    sys.modules["dnd_generator"] = fake_mod
    # Inject a minimal dnd_narrative_prompts module with build_dnd_narrative_prompt
    fake_prompt_mod = types.ModuleType("dnd_narrative_prompts")
    def fake_build_dnd_narrative_prompt(dnd_character, style="detailed", additional_context=None):
        # Return a short prompt that will be passed to the mocked call_llm_structured
        return "FAKE_PROMPT_FOR_TESTING"
    fake_prompt_mod.build_dnd_narrative_prompt = fake_build_dnd_narrative_prompt
    # Also provide builder classes referenced elsewhere (not used in this test)
    fake_prompt_mod.DnDNarrativePromptBuilder = lambda x: None
    fake_prompt_mod.NarrativeAspect = None
    fake_prompt_mod.NarrativeStyle = None
    sys.modules["dnd_narrative_prompts"] = fake_prompt_mod
    # Inject a minimal schemas module with DnDCharacterNarrative to satisfy imports
    fake_schemas = types.ModuleType("schemas")
    class FakeDnDCharacterNarrative:
        pass
    fake_schemas.DnDCharacterNarrative = FakeDnDCharacterNarrative
    sys.modules["schemas"] = fake_schemas

    with patch("backend.routers.generation.call_llm_structured", new=fake_call_llm_structured):
        resp = client.post("/api/characters/dnd/generate/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Canonical name preserved
        assert data["name"] == "Kaelin Valtor"
    # name_suggestions should include the LLM suggestion either at top-level or inside generation_log.ai_narrative
    top_level_suggestions = data.get("name_suggestions")
    gen_log_ai = data.get("generation_log", {}).get("ai_narrative", {})
    suggestions_in_log = gen_log_ai.get("name_suggestions") if isinstance(gen_log_ai, dict) else None
    assert (top_level_suggestions is not None) or (suggestions_in_log is not None)
