# D&D 5e Combat System Integration

## Overview

The AI DM now has full D&D 5e combat capabilities including:

✅ **Monster Stat Blocks** - Access to official D&D monsters via MCP
✅ **Dice Rolling** - Complete dice mechanics (attacks, damage, saves)
✅ **Player Character Stats** - Parse and use player stats from database
✅ **Combat Encounters** - Full initiative tracking and turn management
✅ **Combat Rules** - Advantage/disadvantage, critical hits, conditions
✅ **Area Effects** - Handle spells like Fireball with saving throws

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AI DM Chat                           │
│  (Uses combat rules from documents/reference/combat_rules.md)│
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> Combat API (/api/combat/encounters)
             │    - Create/manage encounters
             │    - Add players/monsters
             │    - Resolve attacks/saves
             │
             ├──> Character API (/api/characters)
             │    - Fetch player stats
             │    - D&D 5e character sheets
             │
             ├──> D&D MCP Client (services/dnd_mcp_client.py)
             │    - Monster stat blocks
             │    - Spell descriptions
             │    - Equipment data
             │
             └──> Dice Roller (game/dice_roller.py)
                  - D20 rolls with advantage
                  - Attack vs AC
                  - Damage (with critical hits)
                  - Saving throws
```

## Core Components

### 1. Dice Roller (`backend/game/dice_roller.py`)

Complete D&D dice system:

```python
from backend.game.dice_roller import DiceRoller, AdvantageType

roller = DiceRoller()

# Basic rolls
result = roller.roll("2d6+3")  # Roll 2d6, add 3

# Attack rolls
attack = roller.roll_attack(
    attack_bonus=5,     # +5 to hit
    target_ac=15,       # Target AC 15
    advantage=AdvantageType.ADVANTAGE
)
# Returns: AttackResult(hit=True, critical=False, total=18, ...)

# Damage rolls
damage = roller.roll_damage("1d8+3", critical=True)
# Returns: DamageResult(total=14, rolls=[5, 6], ...)

# Saving throws
save = roller.roll_ability_check(
    modifier=2,  # +2 DEX modifier
    dc=15,       # DC 15
    advantage=AdvantageType.NORMAL
)
# Returns: CheckResult(success=True, total=16, ...)
```

### 2. Combat Manager (`backend/game/combat_manager.py`)

Orchestrates combat encounters:

```python
from backend.game.combat_manager import (
    combat_manager,
    Combatant,
    CombatantType
)

# Create encounter
encounter = combat_manager.create_encounter("enc_1", session_id=1)

# Add combatants
fighter = Combatant(
    id="player_1",
    name="Grok the Fighter",
    type=CombatantType.PLAYER,
    max_hp=45,
    current_hp=45,
    ac=18,
    initiative=14,
    dex_modifier=1,
    melee_attack_bonus=7
)
encounter.add_combatant(fighter)

# Start combat (sorts initiative)
encounter.start_combat()

# Make attack
result = encounter.make_attack(
    attacker_id="player_1",
    target_id="monster_1",
    attack_type="melee",
    damage_dice="1d8",
    damage_modifier=4
)

# Apply area damage (Fireball!)
result = encounter.apply_area_damage(
    target_ids=["monster_1", "monster_2", "monster_3"],
    damage_dice="8d6",
    damage_type="fire",
    save_dc=15,
    save_ability="dex",
    half_on_save=True
)

# Advance turn
encounter.next_turn()
```

### 3. Combat API (`backend/routers/combat.py`)

REST endpoints for combat operations:

#### Create Encounter

```bash
POST /api/combat/encounters
{
  "session_id": 1,
  "encounter_name": "Kobold Ambush"
}
```

#### Add Player from Database

```bash
POST /api/combat/encounters/{encounter_id}/players/{character_id}
{
  "initiative_roll": 14  # Optional, will roll if not provided
}
```

#### Add Monsters (from D&D MCP)

```bash
POST /api/combat/encounters/{encounter_id}/monsters
{
  "monster_name": "kobold",
  "count": 4
}
```

#### Start Combat

```bash
POST /api/combat/encounters/{encounter_id}/start
```

#### Make Attack

```bash
POST /api/combat/encounters/{encounter_id}/attack
{
  "attacker_id": "player_1",
  "target_id": "monster_kobold_1",
  "attack_type": "melee",
  "advantage": "advantage",
  "damage_dice": "1d8",
  "damage_modifier": 4
}
```

#### Apply Area Damage (Fireball!)

```bash
POST /api/combat/encounters/{encounter_id}/area-damage
{
  "target_ids": ["monster_kobold_1", "monster_kobold_2", "monster_kobold_3"],
  "damage_dice": "8d6",
  "damage_type": "fire",
  "save_dc": 15,
  "save_ability": "dex",
  "half_on_save": true
}
```

#### Make Saving Throw

```bash
POST /api/combat/encounters/{encounter_id}/save
{
  "combatant_id": "monster_kobold_1",
  "dc": 15,
  "ability": "dex",
  "advantage": null
}
```

#### Next Turn

```bash
POST /api/combat/encounters/{encounter_id}/next-turn
```

#### Get Combat State

```bash
GET /api/combat/encounters/{encounter_id}

Response:
{
  "encounter_id": "combat_1_123456",
  "status": "in_progress",
  "current_round": 2,
  "current_combatant": "Grok the Fighter",
  "combatants": {...},
  "turn_order": ["player_1", "monster_kobold_1", ...],
  "combat_log": [
    "Combat started! Round 1 begins.",
    "Grok the Fighter's turn.",
    "Grok attacks Kobold 1: 1d20 (18) +7 = 25 vs AC 12",
    "Damage: 5 + 4 = 9 - Kobold 1 has 0/5 HP remaining",
    "Kobold 1 has fallen!"
  ]
}
```

## Example: Fireball Combat Flow

### User Message:

> "I cast Fireball at the 3 Kobolds! DC 15 Dexterity save."

### AI DM Response Flow:

1. **Fetch Spell** (via MCP):

```python
spell = await dnd_mcp_client.get_spell("fireball")
# Returns: damage dice, save DC, area of effect
```

2. **Identify Targets** (from active encounter):

```python
encounter = combat_manager.get_session_encounter(session_id)
kobold_ids = [c.id for c in encounter.combatants.values()
              if "kobold" in c.name.lower()]
```

3. **Apply Area Damage**:

```python
result = encounter.apply_area_damage(
    target_ids=kobold_ids,
    damage_dice="8d6",
    damage_type="fire",
    save_dc=15,
    save_ability="dex",
    half_on_save=True
)
```

4. **Generate Narrative Response**:

```
A bright streak of flame flashes from your pointing finger, blossoming
into a 20-foot-radius sphere of explosive fire!

**Damage Roll:** 8d6 = 4 + 6 + 3 + 5 + 2 + 6 + 1 + 5 = **32 fire damage**

**Kobold 1:** DEX save 1d20 (8) +2 = 10 vs DC 15 - FAILURE
  Takes 32 fire damage - **DEFEATED!**

**Kobold 2:** DEX save 1d20 (14) +2 = 16 vs DC 15 - SUCCESS
  Takes 16 fire damage (half) - 1/5 HP remaining

**Kobold 3:** DEX save 1d20 (7) +2 = 9 vs DC 15 - FAILURE
  Takes 32 fire damage - **DEFEATED!**

**2 Kobolds defeated! 1 Kobold remains with 1 HP.**
```

## Integration with AI DM

The AI DM can now:

1. **Access Combat Rules** from `documents/reference/dnd_mechanics/combat_rules.md`
2. **Fetch Monster Stats** via D&D MCP client
3. **Parse Player Stats** from character database
4. **Execute Combat Actions** via Combat API
5. **Generate Narrative** based on dice results

### Example AI DM System Prompt Addition:

```
You are an expert D&D 5e Dungeon Master with access to combat systems.

When combat begins:
1. Create encounter: POST /api/combat/encounters
2. Add players: POST /api/combat/encounters/{id}/players/{char_id}
3. Add monsters: POST /api/combat/encounters/{id}/monsters
4. Start combat: POST /api/combat/encounters/{id}/start

During combat:
- Use /api/combat/encounters/{id}/attack for attacks
- Use /api/combat/encounters/{id}/area-damage for AoE spells
- Use /api/combat/encounters/{id}/save for saving throws
- Use /api/combat/encounters/{id}/next-turn to advance

Always narrate results dramatically using the combat log and dice breakdowns.
```

## Testing the System

### 1. Test Dice Roller

```bash
cd backend
python -m pytest tests/test_dice_roller.py -v
```

### 2. Test Combat Manager

```python
# backend/tests/test_combat_manager.py
from backend.game.combat_manager import combat_manager, Combatant, CombatantType

def test_fireball_scenario():
    encounter = combat_manager.create_encounter("test_1", 1)

    # Add wizard
    wizard = Combatant(
        id="wizard_1",
        name="Elara",
        type=CombatantType.PLAYER,
        max_hp=30,
        current_hp=30,
        ac=12,
        initiative=15,
        dex_modifier=2,
        spell_save_dc=15
    )
    encounter.add_combatant(wizard)

    # Add 3 kobolds
    for i in range(3):
        kobold = Combatant(
            id=f"kobold_{i+1}",
            name=f"Kobold {i+1}",
            type=CombatantType.MONSTER,
            max_hp=5,
            current_hp=5,
            ac=12,
            initiative=10,
            dex_modifier=2
        )
        encounter.add_combatant(kobold)

    encounter.start_combat()

    # Cast Fireball!
    result = encounter.apply_area_damage(
        target_ids=["kobold_1", "kobold_2", "kobold_3"],
        damage_dice="8d6",
        damage_type="fire",
        save_dc=15,
        save_ability="dex",
        half_on_save=True
    )

    print("\n=== FIREBALL RESULTS ===")
    print(f"Damage: {result['damage_dice']}")
    for target in result['targets']:
        print(f"{target['name']}: {target['damage_dealt']} damage, {target['hp_remaining']} HP remaining")
```

### 3. Test via API

```bash
# Start backend
cd backend
python -m uvicorn main:app --reload

# In another terminal, test API
curl -X POST http://localhost:8000/api/combat/encounters \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'

# Add monsters
curl -X POST http://localhost:8000/api/combat/encounters/combat_1_123/monsters \
  -H "Content-Type: application/json" \
  -d '{"monster_name": "kobold", "count": 3}'

# Start combat
curl -X POST http://localhost:8000/api/combat/encounters/combat_1_123/start

# Fireball!
curl -X POST http://localhost:8000/api/combat/encounters/combat_1_123/area-damage \
  -H "Content-Type: application/json" \
  -d '{
    "target_ids": ["monster_kobold_1", "monster_kobold_2", "monster_kobold_3"],
    "damage_dice": "8d6",
    "damage_type": "fire",
    "save_dc": 15,
    "save_ability": "dex",
    "half_on_save": true
  }'
```

## Frontend Integration

Next steps for frontend:

1. **Combat UI Component** - Display combat state, initiative order, HP bars
2. **Action Buttons** - Attack, Cast Spell, Use Item, End Turn
3. **Dice Animation** - Show dice rolls visually
4. **Combat Log** - Display narrative combat events
5. **Character Sheet Quick View** - Show relevant stats during combat

## Files Created/Modified

### Created:

- `backend/game/combat_manager.py` - Combat orchestration
- `backend/routers/combat.py` - Combat API endpoints
- `documents/COMBAT_SYSTEM_INTEGRATION.md` - This file

### Modified:

- `backend/main.py` - Added combat router registration

### Existing (Used):

- `backend/game/dice_roller.py` - Dice mechanics (already existed)
- `backend/services/dnd_mcp_client.py` - Monster/spell data (already existed)
- `backend/routers/characters.py` - Character stats (already existed)
- `documents/reference/dnd_mechanics/combat_rules.md` - Combat rules reference

## Next Steps

1. ✅ **Combat System Backend** - COMPLETE
2. ✅ **Dice Rolling** - COMPLETE
3. ✅ **Monster Integration** - COMPLETE
4. ✅ **Player Stats Parsing** - COMPLETE
5. ⏳ **AI DM Prompt Enhancement** - Add combat system instructions
6. ⏳ **Frontend Combat UI** - Build React components
7. ⏳ **Combat Testing** - End-to-end tests with AI DM

## Usage Example

```python
# Example: Full combat encounter with AI DM

# 1. User: "We enter the goblin cave"
# AI DM creates encounter
encounter_id = create_encounter(session_id)

# 2. User: "I ready my sword"
# AI DM adds 3 goblins
add_monsters(encounter_id, "goblin", count=3)
add_player(encounter_id, character_id=1)

# 3. Combat starts
start_combat(encounter_id)

# 4. User: "I attack the nearest goblin"
result = make_attack(
    encounter_id,
    attacker_id="player_1",
    target_id="monster_goblin_1",
    attack_type="melee",
    damage_dice="1d8",
    damage_modifier=3
)

# 5. AI DM narrates result
# "You swing your longsword in a mighty arc!
#  Attack: 1d20 (18) +5 = 23 vs AC 15 - HIT!
#  Damage: 1d8 (7) +3 = 10 - The goblin falls!"
```

---

**The AI DM can now run exciting, mechanically-accurate D&D combat! 🎲⚔️🔥**
