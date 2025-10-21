import random
from typing import Dict, Any

# Minimal curated data for starting wealth and equipment packs.
# Keep this intentionally small and conservative — it's a helper for
# the DnD generator to provide deterministic pack contents and a
# simple buy-with-gold flow.

STARTING_WEALTH_BY_CLASS: Dict[str, str] = {
    "fighter": "5d4*10",
    "cleric": "5d4*10",
    "paladin": "5d4*10",
    "ranger": "5d4*10",
    "rogue": "4d4*10",
    "bard": "5d4*10",
    "wizard": "4d4*10",
    "sorcerer": "4d4*10",
    "warlock": "4d4*10",
    "monk": "5d4*10",
    "barbarian": "5d4*10",
    "default": "4d4*10",
}


EQUIPMENT_PACKS: Dict[str, Dict[str, Any]] = {
    "dungeoneer": {
        "id": "dungeoneer",
        "name": "Dungeoneer's Pack",
        "price_gp": 12,
        "items": [
            {"name": "backpack", "price_gp": 2, "weight": 5},
            {"name": "crowbar", "price_gp": 2, "weight": 5},
            {"name": "hammer", "price_gp": 1, "weight": 3},
            {"name": "10 pitons", "price_gp": 0.1, "weight": 2},
            {"name": "10 torches", "price_gp": 0.01, "weight": 2},
            {"name": "tinderbox", "price_gp": 0.1, "weight": 1},
            {"name": "10 days rations", "price_gp": 5, "weight": 20},
            {"name": "waterskin", "price_gp": 0.2, "weight": 5},
            {"name": "50 ft hempen rope", "price_gp": 1, "weight": 10},
        ],
    },
    "burglar": {
        "id": "burglar",
        "name": "Burglar's Pack",
        "price_gp": 16,
        "items": [
            {"name": "backpack", "price_gp": 2, "weight": 5},
            {"name": "bag of 1,000 ball bearings", "price_gp": 1, "weight": 2},
            {"name": "10 ft string", "price_gp": 0.01, "weight": 0.1},
            {"name": "bell", "price_gp": 0.01, "weight": 0.2},
            {"name": "5 candles", "price_gp": 0.05, "weight": 0.2},
            {"name": "crowbar", "price_gp": 2, "weight": 5},
            {"name": "hammer", "price_gp": 1, "weight": 3},
            {"name": "10 pitons", "price_gp": 0.1, "weight": 2},
            {"name": "hooded lantern", "price_gp": 5, "weight": 3},
            {"name": "2 flasks of oil", "price_gp": 0.02, "weight": 2},
            {"name": "5 days rations", "price_gp": 2.5, "weight": 10},
            {"name": "tinderbox", "price_gp": 0.1, "weight": 1},
            {"name": "waterskin", "price_gp": 0.2, "weight": 5},
            {"name": "50 ft hempen rope", "price_gp": 1, "weight": 10},
        ],
    },
    "explorer": {
        "id": "explorer",
        "name": "Explorer's Pack",
        "price_gp": 10,
        "items": [
            {"name": "backpack", "price_gp": 2, "weight": 5},
            {"name": "bedroll", "price_gp": 1, "weight": 7},
            {"name": "mess kit", "price_gp": 0.2, "weight": 1},
            {"name": "tinderbox", "price_gp": 0.1, "weight": 1},
            {"name": "10 torches", "price_gp": 0.01, "weight": 2},
            {"name": "10 days rations", "price_gp": 5, "weight": 20},
            {"name": "waterskin", "price_gp": 0.2, "weight": 5},
            {"name": "50 ft rope", "price_gp": 1, "weight": 10},
        ],
    },
}


def roll_dice(formula: str) -> int:
    """Very small dice roller for formulas like '5d4*10' or '4d6'.

    This intentionally supports only the subset we need for starting gold.
    """
    if not formula:
        return 0
    mult = 1
    base = formula
    if "*" in formula:
        parts = formula.split("*", 1)
        base = parts[0]
        try:
            mult = int(parts[1])
        except Exception:
            mult = 1

    if "d" not in base:
        try:
            return int(base) * mult
        except Exception:
            return 0

    try:
        n_str, m_str = base.split("d", 1)
        n = int(n_str)
        m = int(m_str)
    except Exception:
        return 0

    total = 0
    for _ in range(max(0, n)):
        total += random.randint(1, m)

    return total * mult


def roll_starting_gold(class_key: str) -> int:
    key = (class_key or "").lower()
    formula = STARTING_WEALTH_BY_CLASS.get(key, STARTING_WEALTH_BY_CLASS.get("default"))
    return roll_dice(formula)


def get_pack(pack_id: str) -> Dict[str, Any] | None:
    if not pack_id:
        return None
    return EQUIPMENT_PACKS.get(pack_id)


def choose_equipment_for_class(class_key: str) -> Dict[str, Any]:
    """Return a simple default equipment object for a class.

    This function is intentionally simple: prefer a sensible pack and an
    empty gold_remaining slot (backend may compute gold separately).
    """
    cls = (class_key or "").lower()
    # Fighters, rangers, barbarians -> heavier packs
    if cls in ("fighter", "ranger", "barbarian"):
        return {"pack": EQUIPMENT_PACKS.get("dungeoneer"), "gold_remaining": 0}
    # Rogues -> burglar pack
    if cls == "rogue":
        return {"pack": EQUIPMENT_PACKS.get("burglar"), "gold_remaining": 0}
    # Default -> explorer
    return {"pack": EQUIPMENT_PACKS.get("explorer"), "gold_remaining": 0}
