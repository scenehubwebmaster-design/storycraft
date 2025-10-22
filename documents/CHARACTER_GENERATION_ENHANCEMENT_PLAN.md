# Character Generation Enhancement Plan

## Overview

Transform the character generation system into a robust, modular framework that creates unique, diverse, and authentic characters with rich cultural backgrounds, abilities, and optional D&D 5E integration.

---

## Phase 1: Modular Prompt System Architecture

### 1.1 Core Prompt Modules

Create reusable, composable prompt components:

**Cultural Background Module**

- Geographic origins (50+ diverse regions)
- Cultural traditions and values
- Language and dialects
- Religious/spiritual beliefs
- Social customs and taboos
- Historical context

**Personality Archetype Module**

- 20+ base archetypes (Hero, Trickster, Sage, Rebel, etc.)
- Psychological depth (motivations, fears, desires)
- Moral alignment spectrums
- Character development arcs
- Internal conflicts

**Physical Diversity Module**

- Body types and builds (athletic, stocky, willowy, etc.)
- Ethnic features and variations
- Age representation (child, teen, adult, elder)
- Unique identifiers (scars, tattoos, mutations)
- Disability representation

**Professional/Class Module**

- 50+ occupations and roles
- Skill sets and expertise
- Career progression paths
- Professional relationships
- Tools and equipment

**Backstory Generator Module**

- Family dynamics (orphan, noble house, commoner, etc.)
- Formative events (trauma, triumph, revelation)
- Relationships and connections
- Educational background
- Life-changing moments

### 1.2 Diversity & Authenticity Guidelines

- Cultural consultation references
- Avoiding stereotypes checklist
- Representation best practices
- Historical accuracy considerations
- Sensitivity guidelines

---

## Phase 2: Enhanced Character Schema

### 2.1 Extended Structured Output Schema

```python
class EnhancedCharacterProfile(BaseModel):
    # Core Identity
    name: str
    age: int
    pronouns: str  # NEW
    species_race: str  # NEW (human, elf, dwarf, custom)

    # Cultural Background (NEW SECTION)
    cultural_origin: str
    primary_language: str
    additional_languages: List[str]
    cultural_traditions: List[str]
    religious_beliefs: Optional[str]

    # Physical Attributes (ENHANCED)
    height: str
    build: str
    body_type: str  # NEW
    skin_tone: str  # NEW
    hair: str
    eyes: str
    distinctive_features: List[str]
    disabilities_conditions: Optional[List[str]]  # NEW
    physical_description: str

    # Personality (ENHANCED)
    personality_archetype: str  # NEW
    core_traits: List[str]
    demeanor: str
    communication_style: str  # NEW
    sense_of_humor: str
    personality_description: str

    # Background (ENHANCED)
    birthplace: str
    socioeconomic_background: str  # NEW
    family_structure: str  # NEW
    upbringing: str
    education_training: List[str]  # NEW
    formative_events: List[str]
    backstory: str

    # Abilities & Skills (NEW SECTION)
    professional_skills: List[str]
    combat_abilities: Optional[List[str]]
    magical_abilities: Optional[List[str]]
    special_talents: List[str]
    weaknesses_limitations: List[str]

    # Motivations & Psychology
    primary_motivation: str
    secondary_motivations: List[str]  # NEW
    goals: List[str]
    values: List[str]
    greatest_fear: str
    internal_conflicts: List[str]  # NEW

    # Relationships (ENHANCED)
    relationship_style: str  # NEW
    key_relationships: List[Dict]  # ENHANCED with more structure
    allies_enemies: Dict[str, List[str]]  # NEW

    # Character Arc
    starting_point: str
    potential_growth: str
    arc_trajectory: str

    # Unique Elements
    quirks_habits: List[str]
    speech_patterns: List[str]  # NEW
    mannerisms: List[str]  # NEW
    what_makes_unique: str

    # Optional D&D 5E Data
    dnd_data: Optional[DnDCharacterData]  # NEW
```

### 2.2 D&D 5E Integration Schema

```python
class DnDCharacterData(BaseModel):
    # Core Stats
    character_class: str  # Barbarian, Bard, Cleric, etc.
    subclass: Optional[str]  # Path, College, Domain, etc.
    level: int  # 1-20
    race: str  # As per PHB
    subrace: Optional[str]
    background: str  # Acolyte, Criminal, Folk Hero, etc.

    # Ability Scores
    strength: int  # 3-20 (base + racial modifiers)
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    # Modifiers (calculated)
    ability_modifiers: Dict[str, int]

    # Combat Stats
    armor_class: int
    hit_points: int
    hit_dice: str  # e.g., "3d8"
    speed: int
    initiative: int
    proficiency_bonus: int

    # Proficiencies
    saving_throw_proficiencies: List[str]
    skill_proficiencies: List[str]
    tool_proficiencies: List[str]
    weapon_proficiencies: List[str]
    armor_proficiencies: List[str]
    language_proficiencies: List[str]

    # Features & Traits
    racial_traits: List[Dict]  # name, description
    class_features: List[Dict]
    feats: List[Dict]

    # Spellcasting (if applicable)
    spellcasting_ability: Optional[str]
    spell_save_dc: Optional[int]
    spell_attack_bonus: Optional[int]
    spell_slots: Optional[Dict[str, int]]
    cantrips_known: List[str]
    spells_known: List[str]
    spells_prepared: List[str]

    # Equipment
    starting_equipment: List[str]
    armor: Optional[str]
    weapons: List[str]
    tools: List[str]
    treasure: str

    # Background Features
    background_feature: Dict  # name, description
    personality_traits: List[str]  # From background
    ideal: str
    bond: str
    flaw: str

    # Alignment
    alignment: str  # LG, NG, CG, LN, N, CN, LE, NE, CE
```

---

## Phase 3: Prompt Templates & Variations

### 3.1 Base Generation Prompts

Create 10+ variations for each category:

**Fantasy Prompts** (10 variations)

- High Fantasy (classic Tolkien-inspired)
- Dark Fantasy (gritty, morally grey)
- Urban Fantasy (modern world with magic)
- Epic Fantasy (world-saving heroes)
- Cozy Fantasy (low-stakes, slice-of-life)
- Steampunk Fantasy
- Sword & Sorcery
- Mythological Fantasy
- Fairy Tale Fantasy
- Portal Fantasy

**Sci-Fi Prompts** (10 variations)

- Space Opera
- Cyberpunk
- Hard Science Fiction
- Post-Apocalyptic
- Time Travel
- First Contact
- Military Sci-Fi
- Biopunk
- Solar Punk
- Space Western

**Historical Prompts** (10 variations)

- Ancient Civilizations
- Medieval Period
- Renaissance
- Age of Exploration
- Industrial Revolution
- Victorian Era
- World Wars Era
- Cold War
- Ancient Asia
- Pre-Colonial Americas

**Contemporary Prompts** (10 variations)

- Modern Urban
- Rural/Small Town
- Professional/Corporate
- Criminal Underworld
- Academic
- Medical
- Military
- Political
- Arts & Entertainment
- Tech Industry

**Genre Blends** (10 variations)

- Western Fantasy
- Horror Sci-Fi
- Mystery Fantasy
- Romance Adventure
- Comedy Drama
- Thriller Supernatural
- Historical Fantasy
- Noir Cyberpunk
- Martial Arts Fantasy
- Psychological Horror

### 3.2 Diversity Enhancement Prompts

**Geographic Diversity**

- African cultures (North, West, East, South, Central)
- Asian cultures (East, South, Southeast, Central, West)
- European cultures (Nordic, Celtic, Mediterranean, Slavic, Germanic)
- Americas (North, Central, South, Indigenous)
- Middle Eastern cultures
- Pacific Island cultures
- Arctic/Circumpolar cultures
- Mixed/Diaspora backgrounds

**Neurodiversity & Disability**

- Autism spectrum
- ADHD/Executive function
- Physical disabilities
- Chronic illnesses
- Mental health conditions
- Sensory differences
- Learning differences

**Identity Diversity**

- Gender identities (cis, trans, non-binary, agender, genderfluid)
- Sexual orientations
- Age diversity (children, teens, adults, elderly)
- Body diversity (sizes, types, features)
- Family structures (nuclear, single-parent, chosen family, multigenerational)

---

## Phase 4: D&D 5E Character Generator

### 4.1 Implementation Strategy

**Step 1: Core Rules Database**

- Create JSON files for all PHB content:
  - `dnd_classes.json` - All 13 classes with subclasses
  - `dnd_races.json` - All races and subraces
  - `dnd_backgrounds.json` - All backgrounds
  - `dnd_spells.json` - Spell lists by class
  - `dnd_equipment.json` - Weapons, armor, tools, items
  - `dnd_feats.json` - All feats

**Step 2: Character Creation Pipeline**

1. Generate base character profile (narrative)
2. Map narrative to D&D mechanics:
   - Personality → Class selection
   - Background → D&D Background
   - Physical traits → Race selection
   - Skills → Proficiencies
3. Calculate stats (point buy, standard array, or random)
4. Select appropriate equipment
5. Generate character sheet

**Step 3: AI-Assisted Class Selection**

```python
def suggest_dnd_class(character_profile: EnhancedCharacterProfile) -> List[str]:
    """
    Use AI to suggest appropriate D&D classes based on character narrative.
    Returns ranked list of suitable classes with reasoning.
    """
    prompt = f"""
    Based on this character profile, suggest the 3 most appropriate D&D 5E classes:

    Personality: {character_profile.personality_description}
    Skills: {character_profile.professional_skills}
    Backstory: {character_profile.backstory}
    Motivations: {character_profile.primary_motivation}

    For each class, explain why it fits the character's narrative.
    """
    # Return: [(class_name, subclass, reasoning, confidence_score)]
```

### 4.2 Integration Points

**New Endpoints:**

- `POST /api/generate/character/dnd` - Generate D&D character
- `POST /api/generate/character/convert-to-dnd` - Convert existing character
- `GET /api/dnd/classes` - Get all classes/subclasses
- `GET /api/dnd/races` - Get all races/subraces
- `GET /api/dnd/backgrounds` - Get all backgrounds
- `POST /api/dnd/character-sheet/export` - Export to PDF/JSON

**Frontend Components:**

- `DnDCharacterSheet.jsx` - Full character sheet display
- `DnDStatBlock.jsx` - Combat stat block
- `DnDSpellbook.jsx` - Spellcasting component
- `DnDEquipment.jsx` - Equipment management
- `DnDToggle.jsx` - Toggle D&D mode on/off

---

## Phase 5: Implementation Roadmap

### Sprint 1: Foundation (Week 1)

- [ ] Create modular prompt system architecture
- [ ] Design extended character schema
- [ ] Update database migrations for new fields
- [ ] Create prompt variation library (10 per category)

### Sprint 2: Enhanced Generation (Week 2)

- [ ] Implement cultural background module
- [ ] Implement diversity enhancement prompts
- [ ] Add ability/skill generation
- [ ] Test and refine prompt variations

### Sprint 3: D&D Rules Engine (Week 3)

- [ ] Create D&D data JSON files (classes, races, etc.)
- [ ] Implement stat calculation system
- [ ] Build class/race suggestion AI
- [ ] Create equipment selection logic

### Sprint 4: D&D Integration (Week 4)

- [ ] Implement D&D character generation endpoint
- [ ] Create character sheet component
- [ ] Add stat block display
- [ ] Implement character conversion tool

### Sprint 5: UI/UX Enhancement (Week 5)

- [ ] Update character creation flow
- [ ] Add prompt selection interface
- [ ] Implement D&D toggle feature
- [ ] Create character sheet export functionality

### Sprint 6: Testing & Refinement (Week 6)

- [ ] Generate 100+ test characters
- [ ] Evaluate diversity and quality
- [ ] Refine prompts based on results
- [ ] Performance optimization
- [ ] Documentation

---

## Technical Considerations

### Database Schema Updates

```sql
-- Add new columns to characters table
ALTER TABLE characters ADD COLUMN pronouns VARCHAR(50);
ALTER TABLE characters ADD COLUMN species_race VARCHAR(100);
ALTER TABLE characters ADD COLUMN cultural_origin VARCHAR(200);
ALTER TABLE characters ADD COLUMN dnd_data TEXT; -- JSON
ALTER TABLE characters ADD COLUMN character_type VARCHAR(50) DEFAULT 'narrative'; -- 'narrative', 'dnd', 'both'

-- Create new table for character abilities
CREATE TABLE character_abilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    ability_type VARCHAR(50), -- 'skill', 'combat', 'magic', 'special'
    ability_name VARCHAR(200),
    ability_description TEXT,
    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
);

-- Create table for D&D character data
CREATE TABLE dnd_character_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL UNIQUE,
    class VARCHAR(50),
    subclass VARCHAR(50),
    level INTEGER,
    race VARCHAR(50),
    subrace VARCHAR(50),
    background VARCHAR(50),
    ability_scores TEXT, -- JSON
    combat_stats TEXT, -- JSON
    proficiencies TEXT, -- JSON
    features_traits TEXT, -- JSON
    spellcasting_data TEXT, -- JSON
    equipment TEXT, -- JSON
    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
);
```

### API Structure

```
backend/
├── routers/
│   ├── generation.py (enhanced)
│   ├── dnd.py (NEW)
│   └── characters.py (updated)
├── prompts/
│   ├── base_prompts.py
│   ├── cultural_modules.py (NEW)
│   ├── diversity_modules.py (NEW)
│   ├── dnd_prompts.py (NEW)
│   └── prompt_composer.py (NEW)
├── dnd/
│   ├── rules_engine.py (NEW)
│   ├── class_mapper.py (NEW)
│   ├── stat_calculator.py (NEW)
│   ├── equipment_selector.py (NEW)
│   └── spell_selector.py (NEW)
└── data/
    └── dnd_5e/
        ├── classes.json (NEW)
        ├── races.json (NEW)
        ├── backgrounds.json (NEW)
        ├── spells.json (NEW)
        ├── equipment.json (NEW)
        └── feats.json (NEW)
```

---

## Success Metrics

### Character Quality

- **Diversity Score**: % of characters with non-default cultural backgrounds (Target: >70%)
- **Uniqueness Score**: Character similarity index (Target: <30% overlap)
- **Authenticity Score**: Cultural/disability representation accuracy (Target: >85%)
- **Completeness Score**: % of fields populated meaningfully (Target: >95%)

### D&D Integration

- **Mechanical Validity**: % of D&D characters that follow all rules (Target: 100%)
- **Narrative-Mechanical Fit**: How well mechanics match narrative (Target: >90%)
- **Balance Score**: Character power level appropriateness (Target: Within 10% of standard)

### User Experience

- **Generation Time**: Time to create full character (Target: <15 seconds)
- **User Satisfaction**: Feedback rating (Target: >4.5/5)
- **Regeneration Rate**: % of users who regenerate (Target: <20%)

---

## Next Steps

1. **Review & Approval**: Review this plan and provide feedback
2. **Prioritization**: Decide which phases to tackle first
3. **Resource Gathering**: Collect D&D 5E SRD data and cultural references
4. **Prototype**: Build minimal viable version of enhanced system
5. **Iterate**: Test, gather feedback, refine

---

## Questions for Discussion

1. **Scope**: Do we want to start with just the enhanced prompt system, or tackle D&D integration simultaneously?
2. **D&D Licensing**: Should we restrict to SRD content or include PHB content? (Legal considerations)
3. **Diversity**: Do you want me to research and compile cultural authenticity guidelines?
4. **Prompt Count**: How many variations per category do we want initially? (10? 20? 50?)
5. **Character Types**: Should we support other game systems (Pathfinder, Call of Cthulhu, etc.)?
6. **AI Models**: Continue with Groq (Llama), or explore others for better quality? (GPT-4, Claude, Gemini)

---

**Created:** October 16, 2025  
**Status:** Planning Phase  
**Priority:** High
