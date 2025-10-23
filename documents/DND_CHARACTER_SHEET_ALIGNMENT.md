# D&D 5e Character Sheet Alignment Analysis

## Executive Summary

This document reviews the current D&D 5e character generation system and identifies gaps between what we generate and what a proper D&D 5e character sheet requires for actual gameplay, especially for combat integration.

## Current System Review

### ✅ What We Generate Correctly

**Ability Scores & Modifiers:**

- ✅ All 6 ability scores (STR, DEX, CON, INT, WIS, CHA)
- ✅ Ability modifiers calculated correctly
- ✅ Racial ability bonuses applied
- ✅ Intelligent score assignment based on class

**Combat Stats:**

- ✅ Hit Points (HP) - Level 1 only currently
- ✅ Armor Class (AC) - Basic calculation
- ✅ Initiative modifier
- ✅ Speed
- ✅ Proficiency bonus

**Proficiencies:**

- ✅ Saving throw proficiencies
- ✅ Skill proficiencies
- ✅ Armor proficiencies
- ✅ Weapon proficiencies
- ✅ Tool proficiencies
- ✅ Languages

**Features:**

- ✅ Racial traits
- ✅ Class features (level 1)
- ✅ Background feature

**Equipment:**

- ✅ Starting equipment by class
- ✅ Equipment packs
- ✅ Starting gold option

**Spellcasting (for casters):**

- ✅ Spellcasting ability
- ✅ Spell save DC
- ✅ Spell attack bonus
- ✅ Known cantrips
- ✅ Spell slots

**Narrative Elements:**

- ✅ Character name
- ✅ Physical description
- ✅ Backstory
- ✅ Personality traits (2)
- ✅ Ideals (1)
- ✅ Bonds (1)
- ✅ Flaws (1)

---

## ⚠️ Critical Gaps for Combat System

### 1. **Attack Bonuses NOT Stored**

**Problem:** Combat system needs these, but we don't store them in the character model.

```python
# Combat system expects (from combat_manager.py):
combatant = Combatant(
    melee_attack_bonus=7,      # ❌ NOT IN CHARACTER MODEL
    ranged_attack_bonus=5,     # ❌ NOT IN CHARACTER MODEL
    spell_attack_bonus=6,      # ✅ Calculated but not stored
    spell_save_dc=14           # ✅ Calculated but not stored
)
```

**What's Missing:**

- Melee weapon attack bonus: STR/DEX + Proficiency
- Ranged weapon attack bonus: DEX + Proficiency
- Spell attack bonus: Spellcasting Ability + Proficiency
- Spell save DC: 8 + Proficiency + Spellcasting Ability

**Current Workaround:** Combat API calculates on-the-fly in `/combat/encounters/{id}/players/{cid}` endpoint.

**Solution:** Add these fields to Character model:

```python
# In models.py Character class
dnd_melee_attack_bonus: int | None = None
dnd_ranged_attack_bonus: int | None = None
dnd_spell_attack_bonus: int | None = None  # Already have dnd_spellcasting with this
dnd_spell_save_dc: int | None = None       # Already have dnd_spellcasting with this
```

### 2. **Weapon Damage Dice NOT Stored**

**Problem:** AI DM needs to know what damage dice to roll for attacks.

```python
# Combat system expects:
result = encounter.make_attack(
    damage_dice="1d8",     # ❌ How do we know this?
    damage_modifier=4      # ❌ Which modifier (STR or DEX)?
)
```

**What's Missing:**

- Primary weapon damage dice (e.g., "1d8" for longsword)
- Damage ability modifier (STR or DEX for finesse weapons)
- Two-handed damage (e.g., longsword versatile "1d10")

**Current State:** Equipment is stored as strings:

```python
"equipment": {
    "weapons": ["Longsword", "Shield"],  # ❌ No dice info
    "armor": ["Chain Mail"]
}
```

**Solution:** Enhance equipment storage:

```python
"equipment": {
    "weapons": [
        {
            "name": "Longsword",
            "damage_dice": "1d8",
            "damage_type": "slashing",
            "properties": ["versatile"],
            "versatile_damage": "1d10",
            "ability": "strength"
        }
    ],
    "armor": [
        {
            "name": "Chain Mail",
            "ac": 16,
            "type": "heavy",
            "stealth_disadvantage": true
        }
    ]
}
```

### 3. **Prepared Spells NOT Managed**

**Problem:** Spellcasters can prepare different spells each day.

**Current State:**

```python
"spellcasting": {
    "cantrips_known": 3,
    "spells_known_or_prepared": 4,  # ❌ Which 4 spells?
    "spell_slots": {"level_1": 2}
}
```

**What's Missing:**

- List of known spells (for classes that know spells)
- List of currently prepared spells (for classes that prepare)
- Spell details (level, school, components, etc.)

**Solution:** Add spell management:

```python
"spellcasting": {
    "ability": "intelligence",
    "spell_save_dc": 13,
    "spell_attack_bonus": 5,
    "cantrips_known": ["fire_bolt", "mage_hand", "prestidigitation"],
    "spells_known": ["fireball", "shield", "magic_missile", "detect_magic", "identify"],
    "spells_prepared": ["fireball", "shield", "magic_missile", "detect_magic"],
    "spell_slots": {
        "level_1": {"max": 4, "current": 2},
        "level_2": {"max": 3, "current": 3}
    }
}
```

### 4. **Current HP Tracking**

**Problem:** Characters take damage in combat.

**Current State:**

```python
dnd_hit_points: int | None = None  # ❌ Max HP only
```

**What's Missing:**

- Current HP (separate from max HP)
- Temporary HP
- Death saves tracking

**Solution:** Update model:

```python
dnd_hit_points_max: int | None = None
dnd_hit_points_current: int | None = None
dnd_temporary_hp: int | None = None
dnd_death_saves: Dict[str, Any] | None = None  # {"successes": 0, "failures": 0}
```

### 5. **Ability Modifiers NOT Stored**

**Problem:** Combat needs quick access to modifiers for saving throws and checks.

**Current State:**

```python
dnd_ability_scores: Dict[str, int] | None = None  # {"strength": 16, ...}
# ❌ Modifiers calculated on-the-fly everywhere
```

**What's Missing:**

- Pre-calculated modifiers for faster access
- Saves confusion in code (no more `(score - 10) // 2` everywhere)

**Solution:** Add modifiers field:

```python
dnd_ability_modifiers: Dict[str, int] | None = None  # {"strength": 3, ...}
```

### 6. **Conditions NOT Tracked**

**Problem:** Combat applies conditions (blinded, stunned, etc.).

**What's Missing:**

- Active conditions list
- Condition durations
- Condition effects

**Solution:** Add to model:

```python
dnd_conditions: List[str] | None = None  # ["poisoned", "prone"]
```

### 7. **Resources NOT Tracked**

**Problem:** Many features have limited uses.

**What's Missing:**

- Class feature uses (Rage, Action Surge, etc.)
- Hit dice remaining
- Spell slots used

**Solution:** Add resource tracking:

```python
dnd_resources: Dict[str, Any] | None = None
# {
#   "rage": {"max": 2, "current": 1},
#   "action_surge": {"max": 1, "current": 0},
#   "hit_dice": {"max": 3, "current": 2}
# }
```

---

## 📝 Database Schema Changes Needed

### Character Model Updates

```python
# In backend/models.py

class Character(Base):
    __tablename__ = "characters"

    # ... existing fields ...

    # === NEW FIELDS FOR COMBAT ===

    # Attack Bonuses (calculated at generation, stored for quick access)
    dnd_melee_attack_bonus: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dnd_ranged_attack_bonus: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Ability Modifiers (pre-calculated)
    dnd_ability_modifiers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # HP Tracking
    dnd_hit_points_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dnd_hit_points_current: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dnd_temporary_hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)

    # Combat State
    dnd_conditions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=[])
    dnd_death_saves: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Resources (spell slots, feature uses, hit dice)
    dnd_resources: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Enhanced Equipment (with damage dice and properties)
    # NOTE: dnd_equipment already exists, needs structure change

    # Enhanced Spellcasting (with prepared spells)
    # NOTE: dnd_spellcasting already exists, needs structure enhancement
```

### Migration Required

```python
# backend/migrations/add_combat_fields.py

def upgrade():
    # Add new columns
    op.add_column('characters', sa.Column('dnd_melee_attack_bonus', sa.Integer(), nullable=True))
    op.add_column('characters', sa.Column('dnd_ranged_attack_bonus', sa.Integer(), nullable=True))
    op.add_column('characters', sa.Column('dnd_ability_modifiers', sa.JSON(), nullable=True))
    op.add_column('characters', sa.Column('dnd_hit_points_max', sa.Integer(), nullable=True))
    op.add_column('characters', sa.Column('dnd_hit_points_current', sa.Integer(), nullable=True))
    op.add_column('characters', sa.Column('dnd_temporary_hp', sa.Integer(), nullable=True))
    op.add_column('characters', sa.Column('dnd_conditions', sa.JSON(), nullable=True))
    op.add_column('characters', sa.Column('dnd_death_saves', sa.JSON(), nullable=True))
    op.add_column('characters', sa.Column('dnd_resources', sa.JSON(), nullable=True))

    # Migrate existing data
    # - Copy dnd_hit_points -> dnd_hit_points_max AND dnd_hit_points_current
    # - Calculate ability modifiers from ability scores
    # - Calculate attack bonuses
```

---

## 🔧 Generator Updates Needed

### 1. Update `dnd_generator.py`

```python
def generate_dnd_character(...) -> Dict:
    # ... existing generation ...

    # Calculate ability modifiers
    ability_modifiers = {
        ability: calculate_ability_modifier(score)
        for ability, score in ability_scores.items()
    }

    # Calculate attack bonuses
    prof_bonus = get_proficiency_bonus(level)

    # Melee: STR + prof (or DEX + prof if finesse weapon)
    melee_attack_bonus = ability_modifiers['strength'] + prof_bonus

    # Ranged: DEX + prof
    ranged_attack_bonus = ability_modifiers['dexterity'] + prof_bonus

    # Spell attack: Casting ability + prof (if caster)
    spell_attack_bonus = 0
    spell_save_dc = 8
    if spellcasting:
        casting_mod = ability_modifiers[spellcasting['spellcasting_ability']]
        spell_attack_bonus = casting_mod + prof_bonus
        spell_save_dc = 8 + prof_bonus + casting_mod

    # Enhanced equipment with damage dice
    equipment = generate_enhanced_equipment(class_key, starting_gold)

    # Initialize resources
    resources = {
        "hit_dice": {"max": level, "current": level},
        "spell_slots": spellcasting["spell_slots"] if spellcasting else {}
    }

    # Add class-specific resources
    if class_key == "barbarian":
        resources["rage"] = {"max": 2, "current": 2}
    elif class_key == "fighter":
        resources["action_surge"] = {"max": 1, "current": 1}
        resources["second_wind"] = {"max": 1, "current": 1}
    # ... etc for other classes

    character = {
        # ... existing fields ...
        "ability_modifiers": ability_modifiers,
        "melee_attack_bonus": melee_attack_bonus,
        "ranged_attack_bonus": ranged_attack_bonus,
        "spell_attack_bonus": spell_attack_bonus,
        "spell_save_dc": spell_save_dc,
        "hit_points_max": hit_points,
        "hit_points_current": hit_points,
        "temporary_hp": 0,
        "conditions": [],
        "death_saves": {"successes": 0, "failures": 0},
        "resources": resources,
        "equipment": equipment  # Enhanced structure
    }

    return character
```

### 2. Equipment Enhancement

Create `backend/dnd_equipment_enhanced.py`:

```python
WEAPON_DATA = {
    "longsword": {
        "name": "Longsword",
        "type": "martial melee",
        "damage_dice": "1d8",
        "damage_type": "slashing",
        "properties": ["versatile"],
        "versatile_damage": "1d10",
        "weight": 3,
        "cost": {"amount": 15, "unit": "gp"}
    },
    "shortsword": {
        "name": "Shortsword",
        "type": "martial melee",
        "damage_dice": "1d6",
        "damage_type": "piercing",
        "properties": ["finesse", "light"],
        "weight": 2,
        "cost": {"amount": 10, "unit": "gp"}
    },
    # ... all PHB weapons
}

ARMOR_DATA = {
    "chain_mail": {
        "name": "Chain Mail",
        "type": "heavy",
        "ac": 16,
        "strength_required": 13,
        "stealth_disadvantage": True,
        "weight": 55,
        "cost": {"amount": 75, "unit": "gp"}
    },
    # ... all PHB armor
}
```

---

## 📋 Character Sheet Parity Checklist

### Official D&D 5e Character Sheet Sections

| Section                    | Subsection           | Current Status            | Notes                |
| -------------------------- | -------------------- | ------------------------- | -------------------- |
| **Character Information**  |                      |                           |                      |
|                            | Character Name       | ✅ Generated              |                      |
|                            | Class & Level        | ✅ Stored                 |                      |
|                            | Background           | ✅ Stored                 |                      |
|                            | Player Name          | ❌ Missing                | Not applicable (NPC) |
|                            | Race                 | ✅ Stored (as species)    |                      |
|                            | Alignment            | ✅ Stored                 |                      |
|                            | Experience Points    | ❌ Missing                | For leveling         |
| **Ability Scores**         |                      |                           |                      |
|                            | Score                | ✅ Stored                 |                      |
|                            | Modifier             | ⚠️ Calculated             | Should be stored     |
|                            | Saving Throws        | ✅ Stored (proficiencies) |                      |
| **Combat Stats**           |                      |                           |                      |
|                            | Armor Class          | ✅ Calculated             |                      |
|                            | Initiative           | ✅ Calculated             |                      |
|                            | Speed                | ✅ Stored                 |                      |
|                            | Hit Point Maximum    | ✅ Stored                 |                      |
|                            | Current Hit Points   | ❌ Missing                | For tracking damage  |
|                            | Temporary Hit Points | ❌ Missing                |                      |
|                            | Hit Dice             | ✅ Stored (type)          | ❌ Missing (current) |
|                            | Death Saves          | ❌ Missing                |                      |
| **Attacks & Spellcasting** |                      |                           |                      |
|                            | Attack Name          | ⚠️ Equipment list         | ❌ Not structured    |
|                            | Attack Bonus         | ❌ Missing                | Critical gap         |
|                            | Damage/Type          | ❌ Missing                | Critical gap         |
| **Skills**                 |                      |                           |                      |
|                            | Proficiency          | ✅ Stored                 |                      |
|                            | Bonuses              | ⚠️ Calculated             |                      |
| **Features & Traits**      |                      |                           |                      |
|                            | Racial Traits        | ✅ Stored                 |                      |
|                            | Class Features       | ✅ Stored                 |                      |
|                            | Feature Uses         | ❌ Missing                | (Rage, etc.)         |
| **Equipment**              |                      |                           |                      |
|                            | Item List            | ✅ Stored                 | ❌ No properties     |
|                            | Currency             | ⚠️ Starting gold          | ❌ Not tracked       |
| **Personality**            |                      |                           |                      |
|                            | Traits               | ✅ Stored (2)             |                      |
|                            | Ideals               | ✅ Stored (1)             |                      |
|                            | Bonds                | ✅ Stored (1)             |                      |
|                            | Flaws                | ✅ Stored (1)             |                      |
| **Spellcasting**           |                      |                           |                      |
|                            | Spellcasting Ability | ✅ Stored                 |                      |
|                            | Spell Save DC        | ✅ Calculated             | ⚠️ Not stored        |
|                            | Spell Attack Bonus   | ✅ Calculated             | ⚠️ Not stored        |
|                            | Spell Slots          | ✅ Stored (max)           | ❌ Missing (current) |
|                            | Prepared Spells      | ❌ Missing                | Critical for casters |

**Legend:**

- ✅ Fully implemented
- ⚠️ Partially implemented
- ❌ Missing/not implemented

---

## 🎯 Priority Recommendations

### **Phase 1: Critical Combat Fields** (HIGHEST PRIORITY)

1. ✅ Add attack bonuses to Character model
2. ✅ Add ability modifiers to Character model
3. ✅ Add current HP tracking
4. ✅ Update `dnd_generator.py` to calculate and store these

**Impact:** Enables combat system without workarounds.

### **Phase 2: Equipment Enhancement** (HIGH PRIORITY)

1. Create weapon/armor data with dice and properties
2. Update equipment generation to use enhanced structure
3. Update Character model equipment field structure

**Impact:** AI DM can properly resolve attacks and damage.

### **Phase 3: Spell Management** (HIGH PRIORITY)

1. Add spell list data (from D&D MCP)
2. Implement spell selection for casters
3. Add prepared spells tracking
4. Track current spell slots

**Impact:** Spellcasters can use their spells in combat.

### **Phase 4: Resource Tracking** (MEDIUM PRIORITY)

1. Add resources field to Character model
2. Initialize class-specific resources
3. Create API endpoints for resource management
4. Build frontend resource tracker

**Impact:** Classes with limited features work properly.

### **Phase 5: Conditions & Status** (MEDIUM PRIORITY)

1. Add conditions field
2. Create condition application API
3. Build combat condition display

**Impact:** Combat conditions work correctly.

---

## 🔄 Backward Compatibility

### Migration Strategy

1. **Add new fields with defaults**

   - New fields nullable
   - Migration script backfills from existing data

2. **Dual-field support during transition**

   - `dnd_hit_points` → kept for old characters
   - `dnd_hit_points_max` → used for new characters
   - Code checks both fields with fallback

3. **Deprecation timeline**
   - Phase 1: Add new fields, dual support
   - Phase 2: Update generator to use new fields
   - Phase 3: Migrate all old characters
   - Phase 4: Remove old field support

---

## 📊 Data Structure Examples

### Current Character Data

```json
{
  "name": "Thorin Oakenshield",
  "dnd_class": "fighter",
  "dnd_level": 3,
  "dnd_ability_scores": {
    "strength": 16,
    "dexterity": 14,
    "constitution": 15
  },
  "dnd_hit_points": 28,
  "dnd_armor_class": 18,
  "dnd_equipment": {
    "weapons": ["Longsword", "Shield"],
    "armor": ["Plate Armor"]
  }
}
```

### Proposed Enhanced Character Data

```json
{
  "name": "Thorin Oakenshield",
  "dnd_class": "fighter",
  "dnd_level": 3,
  "dnd_ability_scores": {
    "strength": 16,
    "dexterity": 14,
    "constitution": 15
  },
  "dnd_ability_modifiers": {
    "strength": 3,
    "dexterity": 2,
    "constitution": 2
  },
  "dnd_hit_points_max": 28,
  "dnd_hit_points_current": 22,
  "dnd_temporary_hp": 5,
  "dnd_armor_class": 18,
  "dnd_melee_attack_bonus": 5,
  "dnd_ranged_attack_bonus": 4,
  "dnd_equipment": {
    "weapons": [
      {
        "name": "Longsword",
        "damage_dice": "1d8",
        "damage_type": "slashing",
        "properties": ["versatile"],
        "versatile_damage": "1d10",
        "equipped": true
      }
    ],
    "armor": [
      {
        "name": "Plate Armor",
        "ac": 18,
        "type": "heavy",
        "stealth_disadvantage": true,
        "equipped": true
      }
    ],
    "shield": {
      "name": "Shield",
      "ac_bonus": 2,
      "equipped": true
    }
  },
  "dnd_conditions": ["blessed"],
  "dnd_resources": {
    "hit_dice": { "max": 3, "current": 2 },
    "action_surge": { "max": 1, "current": 0 },
    "second_wind": { "max": 1, "current": 1 }
  }
}
```

---

## 🎨 Frontend Implications

### Character Creation Updates Needed

1. **Preview screen should show:**

   - Attack bonuses
   - Damage dice for weapons
   - Current/max HP (both starting at max)
   - Available resources

2. **Combat integration panel:**

   - "Add to Combat" button
   - HP tracker
   - Resource tracker
   - Condition badges

3. **Character sheet view:**
   - Full D&D 5e layout
   - Combat stats prominent
   - Resource management UI
   - Spell management (for casters)

---

## ✅ Action Items

1. [ ] Create migration script for new Character fields
2. [ ] Update `backend/models.py` Character class
3. [ ] Update `backend/dnd_generator.py` to populate new fields
4. [ ] Create `backend/dnd_equipment_enhanced.py` with weapon/armor data
5. [ ] Update `backend/routers/characters.py` CharacterResponse schema
6. [ ] Update frontend CreateCharacter.jsx to display new fields
7. [ ] Update frontend Character detail page with combat stats
8. [ ] Create resource management API endpoints
9. [ ] Create spell management API endpoints
10. [ ] Update combat API to use stored attack bonuses
11. [ ] Write tests for new fields and calculations
12. [ ] Update documentation with new character sheet format

---

## 📚 References

- [D&D 5e SRD Character Sheet](https://www.dndbeyond.com/sources/basic-rules)
- [D&D 5e Player's Handbook](https://www.dndbeyond.com/sources/phb)
- Combat Rules: `documents/reference/dnd_mechanics/combat_rules.md`
- Combat System: `documents/COMBAT_SYSTEM_INTEGRATION.md`
