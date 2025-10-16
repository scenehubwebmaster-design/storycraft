# D&D 5E Integration - Phase 4 Implementation Plan

**Status**: 🔄 **IN PROGRESS**  
**Date**: October 16, 2025  
**Prerequisites**: ✅ Phase 1-3 Complete

---

## Overview

Integrate D&D 5th Edition character creation into StoryCraft, allowing users to generate complete D&D character sheets with stats, classes, races, backgrounds, and equipment.

---

## Goals

1. **Generate D&D-Compatible Characters** - Full stat blocks, classes, races
2. **Seamless Integration** - Works with existing genre/culture system
3. **Authentic D&D Experience** - Follows 5E rules and conventions
4. **Export Capability** - Export to common D&D formats
5. **User-Friendly** - Simple toggle for D&D mode

---

## D&D Character Components

### 1. Core Stats (Ability Scores)
- **STR** (Strength) - Physical power
- **DEX** (Dexterity) - Agility and reflexes
- **CON** (Constitution) - Endurance and health
- **INT** (Intelligence) - Reasoning and memory
- **WIS** (Wisdom) - Awareness and insight
- **CHA** (Charisma) - Force of personality

**Methods**:
- Standard Array: [15, 14, 13, 12, 10, 8]
- Point Buy: 27 points to distribute
- Random Roll: 4d6 drop lowest (×6)
- AI-Generated: Based on class and character concept

### 2. Classes (13 Core Classes)
- **Barbarian** - Fierce warrior, rage-fueled combat
- **Bard** - Musician, inspiration, jack-of-all-trades
- **Cleric** - Divine caster, healer, warrior-priest
- **Druid** - Nature magic, wild shape, elemental power
- **Fighter** - Master of weapons and armor
- **Monk** - Martial artist, ki powers, unarmed combat
- **Paladin** - Holy warrior, divine smite, oath-bound
- **Ranger** - Wilderness expert, hunter, tracker
- **Rogue** - Stealth, sneak attack, skills
- **Sorcerer** - Innate magic, metamagic, bloodline power
- **Warlock** - Pact magic, eldritch invocations, patron
- **Wizard** - Arcane scholar, spell versatility, ritual caster
- **Artificer** - Magical inventor, infusions, tool expertise

### 3. Races (Core + Popular)
**Core Races**:
- Human, Elf (High, Wood, Dark), Dwarf (Mountain, Hill)
- Halfling (Lightfoot, Stout), Dragonborn, Gnome (Forest, Rock)
- Half-Elf, Half-Orc, Tiefling

**Popular Additions**:
- Aasimar, Genasi, Tabaxi, Firbolg, Goliath, Kenku, Lizardfolk

### 4. Backgrounds (Common)
- Acolyte, Charlatan, Criminal, Entertainer, Folk Hero
- Guild Artisan, Hermit, Noble, Outlander, Sage
- Sailor, Soldier, Urchin

### 5. Alignment
- **Lawful Good** - Crusader, paladin, righteous hero
- **Neutral Good** - Kind soul, helpful, balanced
- **Chaotic Good** - Free spirit, rebel hero, individual
- **Lawful Neutral** - Judge, soldier, follower of law
- **True Neutral** - Balanced, pragmatic, nature-focused
- **Chaotic Neutral** - Free spirit, unpredictable, self-interested
- **Lawful Evil** - Tyrant, organized villain, dominator
- **Neutral Evil** - Villain, selfish, no qualms
- **Chaotic Evil** - Destroyer, anarchist, pure evil

### 6. Skills & Proficiencies
**Skills** (18 total):
- Acrobatics, Animal Handling, Arcana, Athletics
- Deception, History, Insight, Intimidation
- Investigation, Medicine, Nature, Perception
- Performance, Persuasion, Religion, Sleight of Hand
- Stealth, Survival

**Proficiencies**:
- Armor (Light, Medium, Heavy, Shields)
- Weapons (Simple, Martial, Specific)
- Tools (Artisan's tools, musical instruments, etc.)
- Saving Throws (2 per class)

### 7. Combat Stats
- **Hit Points** (HP) - Based on class + CON modifier
- **Armor Class** (AC) - 10 + DEX + armor + shield
- **Initiative** - DEX modifier
- **Speed** - Typically 30 ft (race-dependent)
- **Hit Dice** - For healing during short rests
- **Proficiency Bonus** - Starts at +2 (levels 1-4)

### 8. Equipment & Wealth
- Starting equipment by class
- Starting gold (varies by class)
- Weapons, armor, tools
- Adventuring gear
- Spell components (for casters)

### 9. Spells (For Spellcasters)
- Spell slots by level
- Spells known/prepared
- Cantrips
- Spell save DC
- Spell attack bonus

### 10. Features & Traits
- Racial traits
- Class features (level 1)
- Background feature
- Personality traits, ideals, bonds, flaws

---

## Implementation Plan

### Step 1: Backend Schema Extension ✅ TODO

**File**: `backend/models.py`

Add D&D fields to Character model:
```python
class Character(Base):
    # Existing fields...
    
    # D&D 5E Fields
    is_dnd = Column(Boolean, default=False)
    dnd_class = Column(String, nullable=True)  # "Fighter", "Wizard", etc.
    dnd_level = Column(Integer, default=1)
    dnd_race = Column(String, nullable=True)  # "Human", "Elf", etc.
    dnd_background = Column(String, nullable=True)
    dnd_alignment = Column(String, nullable=True)  # "Lawful Good", etc.
    
    # Ability Scores
    strength = Column(Integer, nullable=True)
    dexterity = Column(Integer, nullable=True)
    constitution = Column(Integer, nullable=True)
    intelligence = Column(Integer, nullable=True)
    wisdom = Column(Integer, nullable=True)
    charisma = Column(Integer, nullable=True)
    
    # Combat Stats
    hit_points = Column(Integer, nullable=True)
    armor_class = Column(Integer, nullable=True)
    initiative = Column(Integer, nullable=True)
    speed = Column(Integer, default=30)
    
    # Skills & Proficiencies (JSON)
    skills = Column(JSON, nullable=True)  # {"Perception": true, "Stealth": true}
    proficiencies = Column(JSON, nullable=True)  # {"armor": ["light"], "weapons": ["simple"]}
    
    # Equipment & Spells (JSON)
    equipment = Column(JSON, nullable=True)
    spells = Column(JSON, nullable=True)
    
    # Features & Traits (JSON)
    features = Column(JSON, nullable=True)
```

**Migration Script**: `backend/migrate_add_dnd_stats.py`

### Step 2: D&D Data Modules ✅ TODO

**File**: `backend/dnd_data.py`

Create comprehensive D&D reference data:
- Class definitions (hit dice, proficiencies, features)
- Race definitions (ability bonuses, traits, languages)
- Background definitions (skills, tools, features)
- Equipment lists and costs
- Spell lists by class
- Skill descriptions

### Step 3: D&D Character Generator ✅ TODO

**File**: `backend/dnd_generator.py`

Functions:
- `generate_ability_scores()` - Standard array, point buy, or AI-generated
- `calculate_modifiers()` - Convert scores to modifiers
- `select_class_features()` - Get level 1 class features
- `select_racial_traits()` - Get racial abilities
- `calculate_combat_stats()` - HP, AC, initiative
- `select_starting_equipment()` - By class/background
- `select_spells()` - For spellcasters
- `build_dnd_character()` - Main orchestrator function

### Step 4: Prompt Enhancement for D&D ✅ TODO

**File**: `backend/prompts.py`

Add D&D-specific prompt sections:
```python
def dnd_character_prompt(class_name, race, background, alignment, stats):
    return f"""
    Generate a D&D 5E character with the following specifications:
    
    CLASS: {class_name}
    RACE: {race}
    BACKGROUND: {background}
    ALIGNMENT: {alignment}
    
    ABILITY SCORES:
    - Strength: {stats['strength']} ({modifier(stats['strength'])})
    - Dexterity: {stats['dexterity']} ({modifier(stats['dexterity'])})
    - Constitution: {stats['constitution']} ({modifier(stats['constitution'])})
    - Intelligence: {stats['intelligence']} ({modifier(stats['intelligence'])})
    - Wisdom: {stats['wisdom']} ({modifier(stats['wisdom'])})
    - Charisma: {stats['charisma']} ({modifier(stats['charisma'])})
    
    Create a backstory that explains:
    - How they became a {class_name}
    - Their connection to their {race} heritage
    - Their {background} background experiences
    - Their {alignment} moral compass
    - Their personality, ideals, bonds, and flaws
    - Their appearance and mannerisms
    """
```

### Step 5: API Endpoints ✅ TODO

**File**: `backend/routers/characters.py`

New endpoints:
```python
@router.post("/characters/dnd")
async def generate_dnd_character(request: DnDCharacterRequest):
    """Generate a complete D&D 5E character"""
    pass

@router.get("/dnd/classes")
async def get_dnd_classes():
    """Get all D&D classes with descriptions"""
    pass

@router.get("/dnd/races")
async def get_dnd_races():
    """Get all D&D races with traits"""
    pass

@router.get("/dnd/backgrounds")
async def get_dnd_backgrounds():
    """Get all D&D backgrounds"""
    pass

@router.get("/characters/{id}/sheet")
async def get_character_sheet(id: int):
    """Get formatted D&D character sheet"""
    pass

@router.get("/characters/{id}/export/dnd-beyond")
async def export_to_dnd_beyond(id: int):
    """Export character in D&D Beyond compatible format"""
    pass
```

### Step 6: Frontend UI Components ✅ TODO

**New Component**: `frontend/src/components/DnDCharacterCreator.jsx`
- D&D mode toggle
- Class selector with descriptions
- Race selector with traits
- Ability score allocation UI
- Background selector
- Alignment picker
- Equipment selection

**New Component**: `frontend/src/components/DnDCharacterSheet.jsx`
- Standard D&D character sheet layout
- Editable stat blocks
- Spell slot tracking
- Equipment management
- Export buttons

### Step 7: Integration with Existing System ✅ TODO

**File**: `frontend/src/routes/create/character.jsx`

Add D&D toggle:
```jsx
<FormControlLabel
  control={
    <Switch
      checked={isDndCharacter}
      onChange={(e) => setIsDndCharacter(e.target.checked)}
    />
  }
  label="D&D 5E Character"
/>

{isDndCharacter && (
  <DnDCharacterCreator
    onGenerate={handleDnDGeneration}
  />
)}
```

---

## Sample D&D Character Output

```json
{
  "name": "Thoren Ironforge",
  "is_dnd": true,
  "dnd_class": "Fighter",
  "dnd_level": 1,
  "dnd_race": "Dwarf (Mountain)",
  "dnd_background": "Soldier",
  "dnd_alignment": "Lawful Good",
  
  "ability_scores": {
    "strength": 16,
    "dexterity": 12,
    "constitution": 15,
    "intelligence": 10,
    "wisdom": 13,
    "charisma": 8
  },
  
  "combat_stats": {
    "hit_points": 13,
    "armor_class": 18,
    "initiative": 1,
    "speed": 25,
    "hit_dice": "1d10",
    "proficiency_bonus": 2
  },
  
  "skills": {
    "Athletics": true,
    "Intimidation": true,
    "Perception": true
  },
  
  "proficiencies": {
    "armor": ["light", "medium", "heavy", "shields"],
    "weapons": ["simple", "martial"],
    "tools": ["smith's tools"],
    "saving_throws": ["strength", "constitution"]
  },
  
  "features": {
    "racial": [
      "Darkvision (60 ft)",
      "Dwarven Resilience",
      "Dwarven Combat Training",
      "Stonecunning"
    ],
    "class": [
      "Fighting Style: Defense",
      "Second Wind"
    ],
    "background": [
      "Military Rank"
    ]
  },
  
  "equipment": [
    "Chain mail",
    "Longsword",
    "Shield",
    "Two handaxes",
    "Explorer's pack",
    "Military insignia"
  ],
  
  "personality": {
    "traits": ["I face problems head-on", "I enjoy being strong"],
    "ideal": "Responsibility - I will protect those who cannot protect themselves",
    "bond": "I owe my life to my shield-brother who saved me in battle",
    "flaw": "I have little patience for book learning"
  }
}
```

---

## Timeline

**Estimated Time**: 4-6 hours

1. **Backend Setup** (1-2 hours)
   - Database schema
   - Migration script
   - D&D data module

2. **Generator Logic** (2-3 hours)
   - Ability score generation
   - Combat stat calculations
   - Feature selection
   - Equipment assignment

3. **API & Prompts** (30-60 min)
   - Endpoints
   - D&D-specific prompts

4. **Frontend UI** (1-2 hours)
   - D&D toggle
   - Class/race/background selectors
   - Character sheet display
   - Export functionality

---

## Success Criteria

✅ Generate complete D&D 5E characters with all required stats  
✅ Support all core classes and races  
✅ Calculate combat stats correctly (HP, AC, modifiers)  
✅ Select appropriate starting equipment  
✅ Generate backstory that fits D&D class/race/background  
✅ Display character sheet in standard D&D format  
✅ Export to shareable format  
✅ Integrate seamlessly with existing genre/culture system  

---

## Future Enhancements

- **Level Advancement** - Support characters beyond level 1
- **Subclasses** - Arcane Traditions, Martial Archetypes, etc.
- **Multiclassing** - Rules for combining classes
- **Feats** - Optional character improvements
- **Magic Items** - Enchanted weapons and armor
- **Homebrew Support** - Custom classes, races, items
- **Party Management** - Track full adventuring party
- **Campaign Integration** - Link characters to campaigns

---

## Let's Begin! 🎲

Ready to start implementing? We'll begin with:
1. Database schema updates
2. D&D data module
3. Character generator logic

