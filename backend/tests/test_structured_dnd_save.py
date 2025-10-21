from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_structured_save_persists_dnd_fields():
    # Construct a full CharacterProfile-shaped dict (schema requires many fields)
    character_profile = {
        "name": "DndTest",
        "age": 120,
        "height": "5ft 8in",
        "build": "slender",
        "hair": "silver",
        "eyes": "green",
        "distinctive_features": ["tattoo on arm"],
        "physical_description": "Slender elf with silver hair and green eyes.",
        "personality_traits": ["curious", "reserved"],
        "demeanor": "calm",
        "sense_of_humor": "dry",
        "personality_description": "A thoughtful and studious elf.",
        "birthplace": "Elvenwood",
        "upbringing": "Scholarly",
        "formative_events": ["lost a mentor"],
        "backstory": "Raised among scholars, sought arcane knowledge.",
        "primary_motivation": "Pursue knowledge",
        "goals": ["Master a spell"],
        "values": ["knowledge", "honor"],
        "greatest_fear": "failure",
        "emotional_weaknesses": ["stoicism"],
        "physical_weaknesses": ["frail"],
        "skills": ["arcana", "history"],
        "special_abilities": ["minor_fey_insight"],
        "combat_style": "ranged_spellcaster",
        "strengths_description": "Highly intelligent and perceptive.",
        "key_relationships": [{"name": "Mentor", "relationship": "teacher", "description": "Taught magic."}],
        "character_arc_potential": "From scholar to archmage",
        "unique_qualities": ["spellcraft prodigy"],
        "quirks_and_habits": ["collects feathers"],
        # D&D fields (these are extra keys accepted by our fallback mapping)
        "dnd_species": "elf",
        "dnd_background": "sage",
        "dnd_class": "wizard",
        "dnd_level": 3,
        "dnd_ability_scores": {"strength": 8, "dexterity": 14, "constitution": 12, "intelligence": 16, "wisdom": 10, "charisma": 11}
    }

    payload = {
        "character_profile": character_profile,
        "portrait_image": None,
        "image_prompt": None
    }

    resp = client.post("/api/generate/character/structured/save/", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    char_id = data.get("id")
    assert isinstance(char_id, int)

    # Fetch the saved character
    get_resp = client.get(f"/api/characters/{char_id}")
    assert get_resp.status_code == 200, get_resp.text
    fetched = get_resp.json()

    # Assert that D&D legacy columns were populated
    assert fetched.get("dnd_species") in ("elf", "Elf"), f"unexpected species: {fetched.get('dnd_species')}"
    assert fetched.get("dnd_background") in ("sage", "Sage"), f"unexpected background: {fetched.get('dnd_background')}"
    assert fetched.get("dnd_class") in ("wizard", "Wizard"), f"unexpected class: {fetched.get('dnd_class')}"
    # Assert structured_data also contains the ability scores
    sd = fetched.get("structured_data") or {}
    assert sd.get("dnd_ability_scores") == character_profile["dnd_ability_scores"]
