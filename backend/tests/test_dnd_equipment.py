import sys
from pathlib import Path

# Ensure backend package path is available when tests are run from the backend folder
HERE = Path(__file__).resolve().parent
BACKEND_DIR = HERE.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import dnd_equipment


def test_roll_dice_basic():
    # Basic formula parsing should return within expected bounds for 1d4
    for _ in range(10):
        val = dnd_equipment.roll_dice("1d4")
        assert 1 <= val <= 4


def test_roll_starting_gold_ranges():
    # Starting gold should be positive for known classes
    g = dnd_equipment.roll_starting_gold("fighter")
    assert g >= 10


def test_get_pack_returns_structure():
    pack = dnd_equipment.get_pack("dungeoneer")
    assert pack is not None
    assert "items" in pack
    assert isinstance(pack["items"], list)
    # items may now be objects with name/price/weight
    first = pack["items"][0]
    assert isinstance(first, (str, dict))
