import sys
from pathlib import Path
import types
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure backend package on path
HERE = Path(__file__).resolve().parent
BACKEND_DIR = HERE.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.main import app


def _inject_minimal_dnd_generator():
    fake_mod = types.ModuleType("dnd_generator")

    def fake_generate_dnd_character(class_key, species_key, background_key, alignment, ability_score_method, name, level):
        return {
            "name": name or "TestName",
            "class": class_key,
            "level": level,
            "species": species_key,
            "background": background_key,
            "alignment": alignment,
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
            "background_feature": None,
            "background_feature_description": None,
            "equipment": None,
            "spellcasting": None,
            "languages": [],
        }

    def fake_format_character_sheet(d):
        return "TEST SHEET"

    fake_mod.generate_dnd_character = fake_generate_dnd_character
    fake_mod.format_character_sheet = fake_format_character_sheet
    sys.modules["dnd_generator"] = fake_mod


def test_buy_with_gp_calculation():
    _inject_minimal_dnd_generator()
    client = TestClient(app)

    payload = {
        "name": "Buy GP Test",
        "dnd_class": "fighter",
        "dnd_species": "human",
        "dnd_background": "soldier",
        "dnd_alignment": "Neutral",
        "dnd_level": 1,
        "generate_narrative": False,
        "starting_equipment_method": "buy_with_gp",
        "starting_pack": "dungeoneer",
    }

    # Mock roll_starting_gold to always return 100 gp for deterministic test
    with patch("backend.dnd_equipment.roll_starting_gold", return_value=100):
        resp = client.post("/api/characters/dnd/generate/", json=payload)
        assert resp.status_code == 200
        char = resp.json()
        assert char.get("id")

        get_resp = client.get(f"/api/characters/{char['id']}")
        assert get_resp.status_code == 200
        loaded = get_resp.json()
        assert loaded.get("dnd_equipment") is not None
        # gold_remaining should be 100 - pack price (dungeoneer price_gp is 12)
        assert isinstance(loaded["dnd_equipment"].get("gold_remaining"), (int, float))
        assert abs(loaded["dnd_equipment"]["gold_remaining"] - (100 - 12)) < 0.001
