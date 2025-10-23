# D&D Character Generation Workflow - Complete Review

## Overview

This document provides a comprehensive analysis of the current D&D character generation system, from frontend UI through backend processing to database storage.

**Review Date**: October 22, 2025  
**Purpose**: Understand complete workflow before implementing combat system enhancements

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  CreateCharacter.jsx                                                    │
│    ├─ D&D Mode Toggle (isDnDMode state)                               │
│    ├─ Imports: DnDCharacterCreator component                           │
│    └─ Handles: Character saving, portrait generation, edit mode        │
│                                                                         │
│  DnDCharacterCreator.jsx (1100 lines)                                  │
│    ├─ Form: Class, Species, Background, Alignment, Level               │
│    ├─ Ability Scores: Standard Array / Point Buy / Random              │
│    ├─ AI Narrative: Toggle + Provider/Model selection                  │
│    ├─ Portrait: Optional generation                                    │
│    ├─ Equipment: Class default / Pack / Buy with gold                  │
│    └─ Calls: POST /api/characters/dnd/generate/                        │
│                                                                         │
│  DnDCharacterSheet.jsx                                                  │
│    └─ Display: Full character sheet with D&D 5e layout                 │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                            BACKEND API                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  routers/characters.py                                                  │
│    POST /api/characters/dnd/generate/                                  │
│      ├─ Validates: DnDCharacterGenerateRequest schema                  │
│      ├─ Calls: dnd_generator.generate_dnd_character()                  │
│      ├─ Optional: Narrative generation with LLM                         │
│      │   ├─ Prompt: dnd_narrative_prompts.build_dnd_narrative_prompt() │
│      │   ├─ Schema: DnDCharacterNarrative (Pydantic model)             │
│      │   └─ Provider: Groq/OpenAI/Claude/Gemini                        │
│      ├─ Maps: Narrative → Character fields                             │
│      ├─ Creates: Character database record                             │
│      └─ Returns: CharacterResponse with full D&D data                  │
│                                                                         │
│    GET /api/characters/dnd/classes/                                    │
│    GET /api/characters/dnd/species/                                    │
│    GET /api/characters/dnd/backgrounds/                                │
│    GET /api/characters/dnd/alignments/                                 │
│    GET /api/characters/dnd/equipment/                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          GENERATION LOGIC                               │
├─────────────────────────────────────────────────────────────────────────┤
│  dnd_generator.py (618 lines)                                          │
│    generate_dnd_character(                                             │
│      class_key, species_key, background_key,                           │
│      alignment, ability_score_method, name, level                      │
│    ) -> Dict[str, Any]                                                 │
│                                                                         │
│    Returns:                                                             │
│      {                                                                  │
│        "name": str,                                                     │
│        "class": str,                                                    │
│        "level": int,                                                    │
│        "species": str,                                                  │
│        "background": str,                                               │
│        "alignment": str,                                                │
│        "ability_scores": {"strength": 15, ...},  # 6 scores            │
│        "hit_points": int,                                               │
│        "armor_class": int,                                              │
│        "initiative": "+2",                                              │
│        "speed": 30,                                                     │
│        "proficiency_bonus": "+2",                                       │
│        "saving_throws": ["dexterity", "intelligence"],                 │
│        "skill_proficiencies": ["arcana", "history"],                   │
│        "armor_proficiencies": ["light"],                                │
│        "weapon_proficiencies": ["simple", "crossbow"],                  │
│        "tool_proficiencies": [],                                        │
│        "racial_traits": ["Darkvision", "Fey Ancestry"],                │
│        "class_features": ["Spellcasting", "Arcane Recovery"],          │
│        "background_feature": "Researcher",                              │
│        "background_feature_description": "...",                         │
│        "equipment": {"weapons": [...], "armor": [...]},                 │
│        "spellcasting": {                                                │
│          "spellcasting_ability": "intelligence",                        │
│          "spell_save_dc": 13,                                           │
│          "spell_attack_bonus": 5,                                       │
│          "cantrips_known": 3,                                           │
│          "spells_known_or_prepared": 6,                                 │
│          "spell_slots": {"level_1": 2}                                  │
│        },                                                               │
│        "languages": ["Common", "Elvish"]                                │
│      }                                                                  │
│                                                                         │
│  dnd_narrative_prompts.py (600+ lines)                                 │
│    build_dnd_narrative_prompt(dnd_character, style, context)           │
│      ├─ Builds: Context-aware prompt from ability scores               │
│      ├─ Includes: Species/class/background guidance                    │
│      ├─ Infers: Physical/mental/social traits from stats               │
│      └─ Returns: Comprehensive prompt for LLM                           │
│                                                                         │
│  schemas.py - DnDCharacterNarrative (Pydantic)                         │
│    {                                                                    │
│      "character_name": str,                                             │
│      "age": str,                                                        │
│      "height": str,                                                     │
│      "weight": str,                                                     │
│      "eyes": str,                                                       │
│      "skin": str,                                                       │
│      "hair": str,                                                       │
│      "character_appearance": str,  # Rich description                  │
│      "allies_and_organizations": str,                                   │
│      "character_backstory": str,                                        │
│      "additional_features_and_traits": str,                             │
│      "personality_traits": List[str],  # Exactly 2                     │
│      "ideals": str,  # 1                                                │
│      "bonds": str,   # 1                                                │
│      "flaws": str    # 1                                                │
│    }                                                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATABASE                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  models.py - Character (SQLAlchemy)                                    │
│    ✅ EXISTING FIELDS:                                                  │
│      • name: String(255)                                                │
│      • description: Text                                                │
│      • background: Text                                                 │
│      • personality: Text                                                │
│      • appearance: Text                                                 │
│      • portrait_image: Text (base64)                                    │
│      • image_prompt: Text                                               │
│      • generation_log: JSON                                             │
│      • structured_data: JSON (DnDCharacterNarrative)                    │
│                                                                         │
│    ✅ D&D FIELDS (EXISTING):                                            │
│      • is_dnd: Boolean                                                  │
│      • dnd_class: String(100)                                           │
│      • dnd_level: Integer                                               │
│      • dnd_species: String(100)                                         │
│      • dnd_background: String(100)                                      │
│      • dnd_alignment: String(50)                                        │
│      • dnd_ability_scores: JSON  # {"strength": 15, ...}               │
│      • dnd_hit_points: Integer   # MAX HP ONLY                         │
│      • dnd_armor_class: Integer                                         │
│      • dnd_initiative: String(10)  # "+2"                               │
│      • dnd_speed: Integer                                               │
│      • dnd_proficiency_bonus: String(10)  # "+2"                        │
│      • dnd_skills: JSON  # ["Arcana", "History"]                       │
│      • dnd_proficiencies: JSON  # {saves, armor, weapons, tools}       │
│      • dnd_features: JSON  # {racial, class, background}               │
│      • dnd_equipment: JSON  # {weapons, armor, gear}                   │
│      • dnd_spellcasting: JSON  # {ability, dc, attack, slots}          │
│      • dnd_languages: JSON  # ["Common", "Elvish"]                     │
│                                                                         │
│    ❌ MISSING FOR COMBAT (PHASE A):                                     │
│      • dnd_ability_modifiers: JSON  # Pre-calculated                   │
│      • dnd_melee_attack_bonus: Integer                                  │
│      • dnd_ranged_attack_bonus: Integer                                 │
│      • dnd_hit_points_max: Integer                                      │
│      • dnd_hit_points_current: Integer                                  │
│      • dnd_temporary_hp: Integer                                        │
│      • dnd_conditions: JSON  # ["poisoned", "prone"]                   │
│      • dnd_death_saves: JSON  # {successes: 0, failures: 0}            │
│      • dnd_resources: JSON  # {rage, action_surge, spell_slots}        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Current Workflow Steps

### 1. **User Interface (Frontend)**

**File**: `frontend/src/pages/CreateCharacter.jsx`

```javascript
// User toggles D&D mode
const [isDnDMode, setIsDnDMode] = useState(false);
const [dndCharacter, setDndCharacter] = useState(null);

// Renders DnDCharacterCreator component
{
  isDnDMode && (
    <DnDCharacterCreator
      onCharacterGenerated={(char) => {
        setDndCharacter(char);
        setCharacterName(char.name);
        setActiveStep(2); // Go to review step
      }}
      onError={(err) => setError(err)}
    />
  );
}
```

### 2. **Character Creation Form**

**File**: `frontend/src/components/DnDCharacterCreator.jsx`

```javascript
// User selects:
- Class (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)
- Species (Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling)
- Background (Acolyte, Charlatan, Criminal, Entertainer, Folk Hero, etc.)
- Alignment (Lawful Good, Neutral Good, etc.)
- Level (1-20, default 1)
- Ability Score Method (Standard Array, Point Buy, Random Roll)

// Optional AI Narrative Generation:
- Toggle: useAINarrative
- Provider: Groq, OpenAI, Claude, Gemini
- Model: Provider-specific model
- Style: Detailed, Concise, Dramatic
- Custom Context: User-provided backstory hints

// Optional Portrait Generation:
- Toggle: generatePortrait
- Style: Fantasy Art, Realistic, etc.

// Equipment:
- Method: Class Default, Buy with Gold, Equipment Pack
- Pack: Dungeoneer, Explorer, Priest, etc.
```

**Generation Request**:

```javascript
const dndRequest = {
  name: characterName || null,
  dnd_class: selectedClass,
  dnd_species: selectedSpecies,
  dnd_background: selectedBackground,
  dnd_alignment: selectedAlignment || null,
  dnd_level: characterLevel,
  ability_score_method: abilityScoreMethod,
  generate_narrative: useAINarrative,
  narrative_provider: provider,
  narrative_model: model || null,
  use_structured: useStructured,
  narrative_style: narrativeStyle,
  narrative_context: narrativePrompt || null,
  starting_equipment_method: startingEquipmentMethod,
  starting_pack: startingPack,
  starting_gold_override: null,
};

const response = await axios.post(
  `${API_URL}/api/characters/dnd/generate/`,
  dndRequest
);
```

### 3. **Backend Processing**

**File**: `backend/routers/characters.py`

```python
@router.post("/dnd/generate/", response_model=CharacterResponse)
async def generate_dnd_character(
    request: DnDCharacterGenerateRequest,
    db: Session = Depends(get_db)
):
    # Step 1: Generate D&D stats
    dnd_char = generate_dnd_character(
        class_key=request.dnd_class,
        species_key=request.dnd_species,
        background_key=request.dnd_background,
        alignment=request.dnd_alignment,
        ability_score_method=request.ability_score_method,
        name=request.name,
        level=request.dnd_level,
    )

    # Step 2: Generate narrative (if requested)
    narrative_dict = None
    if request.generate_narrative:
        narrative_prompt = build_dnd_narrative_prompt(
            dnd_character=dnd_char,
            style=request.narrative_style,
            additional_context=request.narrative_context,
        )

        if request.use_structured:
            narrative_obj, metadata = await call_llm_with_retries_and_clarifier(
                base_prompt=narrative_prompt,
                provider=request.narrative_provider,
                schema_model=DnDCharacterNarrative,
                model=request.narrative_model,
                max_attempts=3,
            )
            narrative_dict = narrative_obj.model_dump()

    # Step 3: Map to database model
    db_character = Character(
        name=character_name,
        description=description,
        background=background_text,
        personality=personality,
        appearance=appearance,
        # D&D fields
        is_dnd=True,
        dnd_class=dnd_char.get("class"),
        dnd_level=dnd_char.get("level"),
        dnd_species=dnd_char.get("species"),
        dnd_background=dnd_char.get("background"),
        dnd_alignment=dnd_char.get("alignment"),
        dnd_ability_scores=dnd_char.get("ability_scores"),
        dnd_hit_points=dnd_char.get("hit_points"),  # MAX HP
        dnd_armor_class=dnd_char.get("armor_class"),
        dnd_initiative=dnd_char.get("initiative"),
        dnd_speed=dnd_char.get("speed"),
        dnd_proficiency_bonus=dnd_char.get("proficiency_bonus"),
        dnd_skills=dnd_char.get("skill_proficiencies"),
        dnd_proficiencies={
            "saves": dnd_char.get("saving_throws"),
            "armor": dnd_char.get("armor_proficiencies"),
            "weapons": dnd_char.get("weapon_proficiencies"),
            "tools": dnd_char.get("tool_proficiencies"),
        },
        dnd_features={
            "racial": dnd_char.get("racial_traits"),
            "class": dnd_char.get("class_features"),
            "background": {
                "feature": dnd_char.get("background_feature"),
                "description": dnd_char.get("background_feature_description"),
            },
        },
        dnd_equipment=dnd_char.get("equipment"),
        dnd_spellcasting=dnd_char.get("spellcasting"),
        dnd_languages=dnd_char.get("languages"),
        structured_data=narrative_dict,
        generation_log={...},
    )

    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character
```

### 4. **Combat System Integration**

**File**: `backend/routers/combat.py`

```python
@router.post("/encounters/{encounter_id}/players/{character_id}")
def add_player_from_character(
    encounter_id: str,
    character_id: int,
    db: Session = Depends(get_db)
):
    # Fetch character
    character = db.query(Character).filter(Character.id == character_id).first()

    # ⚠️ ISSUE: Need to calculate modifiers on-the-fly
    ability_scores = character.dnd_ability_scores or {}
    dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
    str_mod = (ability_scores.get("strength", 10) - 10) // 2
    con_mod = (ability_scores.get("constitution", 10) - 10) // 2

    prof_bonus = int(character.dnd_proficiency_bonus.replace("+", ""))

    # ⚠️ ISSUE: Assume STR for melee, DEX for ranged
    melee_attack = str_mod + prof_bonus
    ranged_attack = dex_mod + prof_bonus

    # ⚠️ ISSUE: Current HP not tracked, use max HP
    max_hp = character.dnd_hit_points
    current_hp = max_hp

    # Add to combat
    encounter.add_combatant(
        combatant_id=f"player_{character_id}",
        name=character.name,
        combatant_type="player",
        max_hp=max_hp,
        current_hp=current_hp,
        ac=character.dnd_armor_class,
        initiative_bonus=dex_mod,
        dex_modifier=dex_mod,
        str_modifier=str_mod,
        con_modifier=con_mod,
        melee_attack_bonus=melee_attack,
        ranged_attack_bonus=ranged_attack,
    )
```

**⚠️ PROBLEMS**:

1. Attack bonuses calculated on-the-fly (inefficient, assumes proficiency)
2. Current HP not stored (can't persist damage between sessions)
3. Ability modifiers recalculated everywhere (redundant)
4. No weapon damage dice stored (combat can't auto-roll damage)
5. No spell tracking (can't manage spell slots in combat)
6. No resource tracking (Rage, Action Surge, etc.)

---

## Data Flow Diagram

```
User Input (Frontend)
  ↓
[Class, Species, Background, Alignment, Level, Ability Method]
  ↓
POST /api/characters/dnd/generate/
  ↓
dnd_generator.generate_dnd_character()
  ├─ Assign ability scores (standard array / point buy / random)
  ├─ Apply racial bonuses
  ├─ Calculate proficiency bonus
  ├─ Determine HP (class hit die + CON modifier)
  ├─ Calculate AC (armor + DEX modifier)
  ├─ Calculate initiative (+DEX modifier)
  ├─ Assign skill proficiencies (class + background)
  ├─ Assign saving throw proficiencies (class)
  ├─ Assign racial traits (species)
  ├─ Assign class features (level 1)
  ├─ Select starting equipment (class default)
  ├─ Setup spellcasting (if caster class)
  └─ Return character dict
  ↓
Optional: AI Narrative Generation
  ├─ build_dnd_narrative_prompt()
  │   ├─ Include ability scores
  │   ├─ Infer physical traits from STR/DEX/CON
  │   ├─ Infer mental traits from INT/WIS
  │   ├─ Infer social traits from CHA
  │   ├─ Add species-specific guidance
  │   ├─ Add class-specific guidance
  │   └─ Add background context
  ├─ call_llm_with_retries_and_clarifier()
  │   ├─ Provider: Groq/OpenAI/Claude/Gemini
  │   ├─ Schema: DnDCharacterNarrative
  │   └─ Returns: Structured narrative object
  └─ Extract: name, age, appearance, backstory, traits, ideals, bonds, flaws
  ↓
Database Insert (Character table)
  ├─ Basic fields (name, description, personality, appearance, background)
  ├─ D&D stats (class, level, species, alignment, ability scores, HP, AC, etc.)
  ├─ Proficiencies (skills, saves, armor, weapons, tools)
  ├─ Features (racial, class, background)
  ├─ Equipment (weapons, armor, gear)
  ├─ Spellcasting (if applicable)
  ├─ Languages
  ├─ structured_data (AI narrative as JSON)
  └─ generation_log (metadata)
  ↓
Return to Frontend (CharacterResponse)
  ↓
Display in DnDCharacterSheet component
  ├─ Character Info
  ├─ Ability Scores (with modifiers calculated client-side)
  ├─ Combat Stats (HP, AC, Initiative, Speed)
  ├─ Skills & Saves
  ├─ Features & Traits
  ├─ Equipment
  ├─ Spellcasting
  └─ Narrative (Backstory, Personality, Appearance)
```

---

## Current Strengths

### ✅ Comprehensive D&D Generation

- All core D&D 5e mechanics implemented
- Ability score methods (standard array, point buy, random)
- Racial bonuses correctly applied
- Class features assigned
- Background integration
- Spellcasting setup for casters

### ✅ AI Narrative Integration

- Context-aware prompts using ability scores
- Species/class/background-specific guidance
- Structured output with DnDCharacterNarrative schema
- Multiple LLM providers supported
- Physical/mental/social trait inference

### ✅ Database Design

- Comprehensive D&D fields
- Structured data storage (JSON for flexibility)
- Generation log tracking
- Soft delete support

### ✅ API Design

- Clean REST endpoints
- Pydantic validation
- Comprehensive response models
- Reference data endpoints (classes, species, backgrounds)

---

## Critical Gaps for Combat (Phase A)

### 1. **Attack Bonuses NOT Stored**

**Current Behavior**: Calculated on-the-fly in combat API

```python
# In combat.py
prof_bonus = int(character.dnd_proficiency_bonus.replace("+", ""))
melee_attack = str_mod + prof_bonus  # Assumes proficiency
ranged_attack = dex_mod + prof_bonus
```

**Problems**:

- Assumes character has proficiency with all weapons
- Doesn't account for finesse weapons (DEX for melee)
- Doesn't account for class features (Fighting Style, Martial Arts)
- Inefficient recalculation

**Solution**: Store in database

```python
# In models.py (NEW)
dnd_melee_attack_bonus: Integer
dnd_ranged_attack_bonus: Integer

# Calculate once in dnd_generator.py
melee_attack_bonus = str_mod + prof_bonus
ranged_attack_bonus = dex_mod + prof_bonus
```

### 2. **Ability Modifiers NOT Stored**

**Current Behavior**: Calculated repeatedly

```python
# In multiple places
dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
```

**Problems**:

- Redundant calculations
- Code duplication
- Error-prone

**Solution**: Store modifiers alongside scores

```python
# In models.py (NEW)
dnd_ability_modifiers: JSON  # {"strength": 3, "dexterity": 2, ...}

# Calculate once in dnd_generator.py
ability_modifiers = {
    ability: (score - 10) // 2
    for ability, score in ability_scores.items()
}
```

### 3. **Current HP NOT Tracked**

**Current Behavior**: Only max HP stored

```python
dnd_hit_points: Integer  # MAX HP ONLY
```

**Problems**:

- Can't persist damage between combat sessions
- Combat always starts at full HP
- No death save tracking
- No temporary HP

**Solution**: Separate max and current HP

```python
# In models.py (NEW)
dnd_hit_points_max: Integer
dnd_hit_points_current: Integer
dnd_temporary_hp: Integer
dnd_death_saves: JSON  # {"successes": 0, "failures": 0}
```

### 4. **Weapon Damage Dice Missing**

**Current Behavior**: Equipment stored as simple lists

```python
"equipment": {
  "weapons": ["Longsword", "Shield"],
  "armor": ["Chain Mail"]
}
```

**Problems**:

- AI DM doesn't know damage dice
- Can't auto-roll damage
- No weapon properties (versatile, finesse, etc.)

**Solution**: Enhanced equipment structure

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

### 5. **Spell Management Missing**

**Current Behavior**: Only spell counts

```python
"spellcasting": {
  "spells_known_or_prepared": 4,  # How many, but WHICH ones?
  "spell_slots": {"level_1": 2}   # Max slots, not current
}
```

**Problems**:

- Can't track which spells are prepared
- Can't track spell slot usage
- Combat can't validate spell availability

**Solution**: Full spell tracking

```python
"spellcasting": {
  "cantrips_known": ["fire_bolt", "mage_hand", "prestidigitation"],
  "spells_known": ["fireball", "shield", "magic_missile", "detect_magic"],
  "spells_prepared": ["fireball", "shield", "magic_missile"],
  "spell_slots": {
    "level_1": {"max": 4, "current": 2},
    "level_2": {"max": 3, "current": 3}
  }
}
```

### 6. **Resource Tracking Missing**

**Current Behavior**: Class features stored, but uses not tracked

```python
"class_features": ["Rage", "Unarmored Defense"]  # No usage tracking
```

**Problems**:

- Can't track Rage uses (Barbarian)
- Can't track Action Surge (Fighter)
- Can't track Ki points (Monk)
- Can't track Channel Divinity (Cleric/Paladin)

**Solution**: Resource tracking

```python
dnd_resources: JSON  # (NEW)
{
  "rage": {"max": 2, "current": 1},
  "action_surge": {"max": 1, "current": 0},
  "hit_dice": {"max": 3, "current": 2}
}
```

### 7. **Conditions NOT Tracked**

**Current Behavior**: No condition storage

**Problems**:

- Combat applies conditions (poisoned, stunned, etc.)
- No persistence

**Solution**: Condition list

```python
dnd_conditions: JSON  # (NEW)
["poisoned", "prone"]
```

---

## Phase A Implementation Plan

### Step 1: Database Schema Updates

**File**: `backend/models.py`

Add new fields to Character model:

```python
# Attack Bonuses
dnd_melee_attack_bonus = Column(Integer, nullable=True)
dnd_ranged_attack_bonus = Column(Integer, nullable=True)

# Ability Modifiers (pre-calculated)
dnd_ability_modifiers = Column(JSON, nullable=True)

# HP Tracking
dnd_hit_points_max = Column(Integer, nullable=True)
dnd_hit_points_current = Column(Integer, nullable=True)
dnd_temporary_hp = Column(Integer, nullable=True, default=0)

# Combat State
dnd_conditions = Column(JSON, nullable=True, default=[])
dnd_death_saves = Column(JSON, nullable=True)

# Resources
dnd_resources = Column(JSON, nullable=True)
```

### Step 2: Migration Script

**File**: `backend/migrations/add_combat_fields.py`

```python
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

### Step 3: Update dnd_generator.py

Calculate and return new fields:

```python
def generate_dnd_character(...) -> Dict:
    # ... existing generation ...

    # Calculate ability modifiers
    ability_modifiers = {
        ability: (score - 10) // 2
        for ability, score in ability_scores.items()
    }

    # Calculate attack bonuses
    prof_bonus = get_proficiency_bonus(level)
    melee_attack_bonus = ability_modifiers['strength'] + prof_bonus
    ranged_attack_bonus = ability_modifiers['dexterity'] + prof_bonus

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

    character = {
        # ... existing fields ...
        "ability_modifiers": ability_modifiers,
        "melee_attack_bonus": melee_attack_bonus,
        "ranged_attack_bonus": ranged_attack_bonus,
        "hit_points_max": hit_points,
        "hit_points_current": hit_points,
        "temporary_hp": 0,
        "conditions": [],
        "death_saves": {"successes": 0, "failures": 0},
        "resources": resources,
    }

    return character
```

### Step 4: Update characters.py

Map new fields to database:

```python
db_character = Character(
    # ... existing fields ...

    # NEW FIELDS
    dnd_ability_modifiers=dnd_char.get("ability_modifiers"),
    dnd_melee_attack_bonus=dnd_char.get("melee_attack_bonus"),
    dnd_ranged_attack_bonus=dnd_char.get("ranged_attack_bonus"),
    dnd_hit_points_max=dnd_char.get("hit_points_max"),
    dnd_hit_points_current=dnd_char.get("hit_points_current"),
    dnd_temporary_hp=dnd_char.get("temporary_hp"),
    dnd_conditions=dnd_char.get("conditions"),
    dnd_death_saves=dnd_char.get("death_saves"),
    dnd_resources=dnd_char.get("resources"),
)
```

### Step 5: Update CharacterResponse Schema

```python
class CharacterResponse(CharacterBase):
    # ... existing fields ...

    # NEW FIELDS
    dnd_ability_modifiers: Dict[str, int] | None = None
    dnd_melee_attack_bonus: int | None = None
    dnd_ranged_attack_bonus: int | None = None
    dnd_hit_points_max: int | None = None
    dnd_hit_points_current: int | None = None
    dnd_temporary_hp: int | None = None
    dnd_conditions: List[str] | None = None
    dnd_death_saves: Dict[str, int] | None = None
    dnd_resources: Dict[str, Any] | None = None
```

### Step 6: Update Combat API

Simplify by using stored values:

```python
@router.post("/encounters/{encounter_id}/players/{character_id}")
def add_player_from_character(...):
    character = db.query(Character).filter(Character.id == character_id).first()

    # Use stored modifiers
    ability_modifiers = character.dnd_ability_modifiers or {}

    # Use stored attack bonuses
    melee_attack = character.dnd_melee_attack_bonus
    ranged_attack = character.dnd_ranged_attack_bonus

    # Use current HP
    max_hp = character.dnd_hit_points_max
    current_hp = character.dnd_hit_points_current or max_hp

    encounter.add_combatant(
        combatant_id=f"player_{character_id}",
        name=character.name,
        combatant_type="player",
        max_hp=max_hp,
        current_hp=current_hp,
        ac=character.dnd_armor_class,
        initiative_bonus=ability_modifiers.get("dexterity", 0),
        dex_modifier=ability_modifiers.get("dexterity", 0),
        str_modifier=ability_modifiers.get("strength", 0),
        con_modifier=ability_modifiers.get("constitution", 0),
        melee_attack_bonus=melee_attack,
        ranged_attack_bonus=ranged_attack,
    )
```

---

## Testing Checklist

### Unit Tests

- [ ] Test ability modifier calculation
- [ ] Test attack bonus calculation
- [ ] Test resource initialization by class
- [ ] Test HP tracking (max, current, temporary)
- [ ] Test condition application/removal
- [ ] Test death saves

### Integration Tests

- [ ] Generate D&D character with new fields
- [ ] Add character to combat encounter
- [ ] Apply damage and verify HP updates
- [ ] Apply conditions and verify storage
- [ ] Use class resources (Rage, etc.)
- [ ] Test character level-up (update resources)

### Migration Tests

- [ ] Migrate existing characters
- [ ] Verify no data loss
- [ ] Verify backward compatibility

---

## Summary

**Current State**: ✅ Strong foundation for D&D character generation  
**Combat Gap**: ⚠️ Missing critical fields for combat system  
**Next Step**: 🚀 Implement Phase A (Combat Fields)

**Estimated Effort**: 4-6 hours

- Migration script: 1 hour
- Generator updates: 2 hours
- API updates: 1 hour
- Testing: 1-2 hours

**Impact**: 🎯 Combat system can use stored values instead of on-the-fly calculations
