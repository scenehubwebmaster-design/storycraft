from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_generate_character_structured_and_save_persists_structured_data():
    # Patch call_llm_structured to return a minimal CharacterProfile-like dict
    def fake_call_llm_structured(prompt, provider, schema_model, model=None, max_tokens=None, temperature=None):
        # Return a fake pydantic-like object with model_dump
        class FakeModel:
            def model_dump(self):
                return {
                    "name": "Test Character",
                    "age": 30,
                    "height": "6ft",
                    "build": "athletic",
                    "hair": "black, short",
                    "eyes": "brown",
                    "distinctive_features": ["scar on chin"],
                    "physical_description": "Tall and lean",
                    "personality_traits": ["brave", "curious"],
                    "demeanor": "calm",
                    "sense_of_humor": "dry",
                    "personality_description": "Curious adventurer",
                    "birthplace": "Unknown",
                    "upbringing": "Orphaned",
                    "formative_events": ["lost home"],
                    "backstory": "A simple backstory",
                    "primary_motivation": "Explore",
                    "goals": ["Find treasure"],
                    "values": ["honor"],
                    "greatest_fear": "Heights",
                    "emotional_weaknesses": ["trust issues"],
                    "physical_weaknesses": ["asthma"],
                    "skills": ["swordsmanship"],
                    "special_abilities": ["keen sight"],
                    "combat_style": "adaptive",
                    "strengths_description": "Skilled fighter",
                    "key_relationships": [{"name": "Ally", "relationship": "friend", "description": "Trusted"}],
                    "character_arc_potential": "Growth into leader",
                    "unique_qualities": ["resilient"],
                    "quirks_and_habits": ["taps foot"],
                }

        return FakeModel(), {"provider": provider, "model": model}

    # Patch the call into the generation module
    import backend.routers.generation as gen_mod
    gen_mod.call_llm_structured = fake_call_llm_structured

    # Call the structured generation endpoint
    payload = {
        "themes": ["adventure"],
        "personality_traits": ["brave"],
        "physical_traits": ["athletic"],
        "archetype": "adventurer",
        "provider": "test",
        "model": "test-model",
    }

    resp = client.post("/api/generate/character/structured", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    # Ensure required fields present in response
    assert data.get("name") == "Test Character"
    assert data.get("hair") == "black, short"

    # Now test save endpoint: construct CharacterSaveRequest payload
    save_payload = {
        "character_profile": data,
        "portrait_image": None,
        "image_prompt": None
    }

    save_resp = client.post("/api/generate/character/structured/save/", json=save_payload)
    assert save_resp.status_code == 200, save_resp.text
    save_data = save_resp.json()
    char_id = save_data.get("id")
    assert isinstance(char_id, int)

    # Fetch the character via characters router to confirm structured_data persisted
    get_resp = client.get(f"/api/characters/{char_id}")
    assert get_resp.status_code == 200, get_resp.text
    fetched = get_resp.json()
    sd = fetched.get("structured_data")
    assert sd is not None, "structured_data should be present"
    assert sd.get("name") == "Test Character"
    assert sd.get("hair") == "black, short"
