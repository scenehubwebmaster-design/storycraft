# D&D 5e Narrative Prompts Review & Recommendations

## Executive Summary

This document reviews the current D&D character narrative generation prompts in `backend/dnd_narrative_prompts.py` and identifies areas for improvement to ensure alignment with official D&D 5e lore, mechanics, and character sheet standards.

## Current System Overview

### ✅ Strong Points

1. **Context-Aware Prompts**: Prompts intelligently use ability scores to infer physical, mental, and social traits
2. **Species-Specific Guidance**: Detailed guidance for Dragonborn, Elf, Dwarf, Halfling, Tiefling
3. **Class Integration**: Prompts consider class features and training background
4. **Alignment Influence**: Personality traits driven by alignment
5. **Modular Design**: Can generate specific aspects (appearance, backstory, etc.) independently
6. **D&D 5e Format**: Output matches official character sheet sections (traits, ideals, bonds, flaws)
7. **Variety Enforcement**: Strong warnings against repetitive descriptions

### ⚠️ Areas for Improvement

1. **Incomplete Species Coverage**: Missing many PHB species
2. **Class Guidance Too Brief**: Could be more specific about class identity
3. **Background Integration Weak**: Generic treatment of backgrounds
4. **No Subclass Awareness**: Prompts don't account for subclass differences
5. **Missing Cultural Details**: Lacks specific cultural naming patterns
6. **No Equipment Context**: Doesn't mention starting equipment in appearance
7. **Limited Spell References**: Casters could reference signature spells
8. **No Feat Integration**: Level 1+ feats not mentioned

---

## Missing Species Guidance

### Current Coverage (5 species)

- ✅ Dragonborn
- ✅ Elf (including Eladrin)
- ✅ Dwarf
- ✅ Halfling
- ✅ Tiefling

### Missing from PHB (6+ species)

#### 1. **Human** - Most Versatile and Numerous

```python
"""
👤 HUMAN - Diverse and Ambitious
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Highly varied: all heights, builds, skin tones, hair colors
  - No universal human "look" - emphasize diversity
  - Adaptable to any climate or region
  - Average lifespan but accomplish much in short time

Cultural Elements:
  - Most culturally diverse species
  - Driven, ambitious, quick to action
  - Found in all walks of life
  - Tend to be generalists rather than specialists
  - Strong sense of individuality

Naming Conventions:
  - Vary by culture/region (use diverse Earth-inspired patterns)
  - Examples: Calimshan (Middle Eastern), Chondathan (Western European),
    Damaran (Slavic), Illuskan (Nordic), Mulan (Egyptian),
    Rashemi (Eastern European), Shou (East Asian), Turami (African)
"""
```

#### 2. **Half-Elf** - Between Two Worlds

```python
"""
🌓 HALF-ELF - Bridge Between Cultures
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Blend of human and elven features
  - Slightly pointed ears (not fully elven)
  - Graceful but not ethereal
  - Ages slower than humans (up to 180 years)
  - Height between humans and elves (5-6 feet)

Cultural Elements:
  - Often feel like outsiders in both cultures
  - Charismatic and diplomatic due to navigating two worlds
  - Inherit human ambition + elven grace
  - May embrace one heritage, both, or neither
  - Excellent mediators and ambassadors

Special Traits to Reference:
  - Skill versatility (jack-of-all-trades)
  - Natural diplomats (extra skills from human versatility)
  - Darkvision from elven heritage
"""
```

#### 3. **Half-Orc** - Strength and Struggle

```python
"""
💪 HALF-ORC - Power and Resilience
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Powerfully built, muscular frame (6-7 feet tall)
  - Grayish skin tones (gray, green-gray, brown-gray)
  - Prominent lower canines (small tusks)
  - Heavy brow, strong jaw
  - Coarse dark hair

Cultural Elements:
  - Face prejudice from both human and orc communities
  - Prove themselves through strength and action
  - Often have something to prove
  - Value personal honor and respect
  - Fierce loyalty to those who accept them
  - May embrace orc heritage, human upbringing, or forge own path

Special Abilities to Reference:
  - Relentless Endurance (drop to 1 HP instead of 0 once per long rest)
  - Savage Attacks (extra damage die on critical hits)
  - Intimidating presence
"""
```

#### 4. **Gnome** - Curious Tinkerers

```python
"""
🔧 GNOME - Bright-Eyed Innovators
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Small stature (3-4 feet tall), lighter than halflings
  - Vibrant hair colors (common: white, blonde; rare: pink, green, blue)
  - Tan or brown skin tones
  - Large eyes, expressive faces
  - Prominent noses

SUBRACE DIFFERENCES:
  Forest Gnome:
    - More earthy tones
    - Wiry, nimble build
    - Connection to small animals
    - Natural illusionist

  Rock Gnome:
    - Sturdier build
    - Stained with soot or grease from tinkering
    - Pockets full of gadgets and tools
    - Inventor's mindset

Cultural Elements:
  - Insatiably curious about everything
  - Love of jokes, pranks, and wordplay
  - Optimistic even in danger
  - Tight-knit communities
  - Respect for knowledge and craft

Special Abilities to Reference:
  - Gnome Cunning (advantage vs magic mental effects)
  - Rock Gnome: Tinker trait (create clockwork devices)
  - Forest Gnome: Speak with Small Beasts
"""
```

#### 5. **Drow (Dark Elf)** - Exiled and Conflicted

```python
"""
🕷️ DROW - Shadow Elves
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Obsidian-black or deep purple-blue skin
  - White, pale yellow, or silver hair
  - Pale eyes (often lavender, silver, red)
  - Slender, graceful elven build
  - Exotic, striking appearance

Cultural Elements:
  - Surface drow often exiles or refugees from Underdark
  - Carry stigma of evil drow society (Lolth worship)
  - Must constantly prove they're different
  - Struggle with heritage vs. personal morality
  - Superior darkvision (120 ft)
  - Sunlight sensitivity (disadvantage in direct sunlight)

Special Abilities to Reference:
  - Innate drow magic (dancing lights, faerie fire, darkness)
  - Weapon training (rapiers, shortswords, hand crossbows)
  - Trance instead of sleep (like all elves)

CRITICAL: If Drow character is Good/Neutral, address:
  - How they escaped/rejected Lolth and evil drow ways
  - Constant suspicion from others
  - Internal struggle with dark heritage
"""
```

#### 6. **Aarakocra** - Winged Wanderers

```python
"""
🦅 AARAKOCRA - Children of the Sky
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Bird-like humanoid (head, legs, feathers of bird)
  - Wings span about 20 feet
  - Hollow bones, lightweight (80-100 lbs)
  - Taloned hands and feet
  - Plumage varies (eagle, parrot, owl patterns)

Cultural Elements:
  - Claustrophobic in enclosed spaces
  - Prefer high places and open skies
  - Short-lived (about 30 years max)
  - See world from aerial perspective
  - Often scouts or messengers
  - Uncomfortable with ground-dwelling life

Special Abilities to Reference:
  - Flight (50 ft. fly speed)
  - Talons as natural weapons
  - Cannot fly in heavy armor
  - May have difficulty with heavy weapons (talons, not hands)
"""
```

---

## Class Guidance Enhancement

### Current Issue

Class guidance is 2-3 bullet points. Needs more detail about:

- Class identity and role
- Typical personality archetypes
- Training and mentorship
- Subclass differences (at level 3+)

### Recommended Additions

#### Example: **Wizard** (Enhanced)

**Current:**

```python
# Simple 3-line guidance
```

**Proposed:**

```python
"""
🎓 WIZARD - Scholar of the Arcane
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Class Identity:
  - Magic through rigorous study and memorization
  - Spellbook is their most prized possession
  - Intelligence-based spellcasting (INT modifier for DC and attacks)
  - Ritual casting specialist

Personality Archetypes:
  - The Scholar: Bookish, curious, seeks knowledge for its own sake
  - The Ambitious: Power through mastery, competitive with other mages
  - The Specialist: Focused on one school of magic obsessively
  - The Practical: Magic as a tool to solve problems

Training & Mentorship:
  - Academy education (formal wizarding school)
  - Apprenticeship under master wizard
  - Self-taught from stolen/found spellbooks
  - War mage training (military background)

Combat Approach:
  - Battlefield control and area effects
  - Prepared spell selection critical to success
  - Fragile but devastating at range
  - Uses INT for spell attack rolls and save DCs

Appearance & Gear:
  - Spellbook always nearby (describe its appearance)
  - Component pouch or arcane focus (staff, wand, orb, rod)
  - Robes or practical traveling clothes
  - May have scholarly accessories (spectacles, ink-stained fingers)

Subclass Hints (Level 3+):
  - Abjuration: Protective magic, wards and shields
  - Conjuration: Summoning, teleportation
  - Divination: Foresight, knowledge, prophecy
  - Enchantment: Mind control, charm magic
  - Evocation: Blasting spells, raw destructive power
  - Illusion: Deception, trickery, phantasms
  - Necromancy: Death magic, undead control
  - Transmutation: Alteration, transformation
"""
```

#### **Similar Detail Needed For:**

- Barbarian (Rage, tribal/savage warrior themes)
- Bard (Performance, versatile support, College choice)
- Cleric (Deity, divine magic vs martial approach, Domain)
- Druid (Nature bond, Wild Shape, Circle)
- Fighter (Martial versatility, fighting style, background matters)
- Monk (Discipline, ki, monastery, tradition)
- Paladin (Oath, divine warrior, tension between codes)
- Ranger (Wilderness survival, favored enemy/terrain, archetype)
- Rogue (Expertise, cunning, various archetypes from thief to spy)
- Sorcerer (Innate magic, bloodline, chaotic power)
- Warlock (Pact, patron relationship, Eldritch Blast identity)

---

## Background Integration Issues

### Current Problem

Backgrounds mentioned but not deeply integrated. Need:

- Background feature in backstory
- Skill proficiencies reflected in personality
- Equipment context (starting gear)
- Relationship templates (contacts from background)

### Recommended Additions

#### Background Integration Template

```python
BACKGROUND_DETAILS = {
    "acolyte": {
        "feature": "Shelter of the Faithful",
        "personality_hints": "Devout, ceremonial knowledge, community-focused",
        "relationships": "Religious order, temple hierarchy, fellow devotees",
        "equipment": "Holy symbol, prayer book, vestments",
        "skills": "Insight, Religion"
    },
    "charlatan": {
        "feature": "False Identity",
        "personality_hints": "Deceptive, charming, quick-thinking",
        "relationships": "Former marks, con artist contacts, fake credentials",
        "equipment": "Disguise kit, forgery kit, fine clothes",
        "skills": "Deception, Sleight of Hand"
    },
    "criminal": {
        "feature": "Criminal Contact",
        "personality_hints": "Streetwise, cautious, loyal to crew",
        "relationships": "Criminal network, fence, old partners",
        "equipment": "Dark common clothes, crowbar, thieves' tools",
        "skills": "Deception, Stealth"
    },
    "entertainer": {
        "feature": "By Popular Demand",
        "personality_hints": "Outgoing, dramatic, loves attention",
        "relationships": "Troupe members, admirers, venue owners",
        "equipment": "Musical instrument, costume, admirer's favor",
        "skills": "Acrobatics, Performance"
    },
    "folk_hero": {
        "feature": "Rustic Hospitality",
        "personality_hints": "Humble, protective, champion of common folk",
        "relationships": "Village saved, common folk network, local legends",
        "equipment": "Artisan's tools, shovel, iron pot, common clothes",
        "skills": "Animal Handling, Survival"
    },
    "guild_artisan": {
        "feature": "Guild Membership",
        "personality_hints": "Proud of craft, business-minded, traditional",
        "relationships": "Guild contacts, master artisan, trade network",
        "equipment": "Artisan's tools, letter of introduction, traveler's clothes",
        "skills": "Insight, Persuasion"
    },
    "hermit": {
        "feature": "Discovery",
        "personality_hints": "Introspective, wise, uncomfortable in crowds",
        "relationships": "Isolated past, rare visitors, spiritual guides",
        "equipment": "Scroll case with notes, blanket, herbalism kit",
        "skills": "Medicine, Religion"
    },
    "noble": {
        "feature": "Position of Privilege",
        "personality_hints": "Commanding, cultured, aware of social hierarchies",
        "relationships": "Noble family, retainers, political connections",
        "equipment": "Fine clothes, signet ring, scroll of pedigree",
        "skills": "History, Persuasion"
    },
    "outlander": {
        "feature": "Wanderer",
        "personality_hints": "Self-reliant, uncomfortable in cities, naturalist",
        "relationships": "Tribal connections, wilderness guides, hermits",
        "equipment": "Staff, hunting trap, trophy from animal",
        "skills": "Athletics, Survival"
    },
    "sage": {
        "feature": "Researcher",
        "personality_hints": "Curious, analytical, values knowledge",
        "relationships": "Library access, fellow scholars, research contacts",
        "equipment": "Ink, quill, small knife, letter with unanswered question",
        "skills": "Arcana, History"
    },
    "sailor": {
        "feature": "Ship's Passage",
        "personality_hints": "Superstitious, practical, loves sea stories",
        "relationships": "Former crew, port contacts, nautical traditions",
        "equipment": "Belaying pin (club), silk rope, lucky charm",
        "skills": "Athletics, Perception"
    },
    "soldier": {
        "feature": "Military Rank",
        "personality_hints": "Disciplined, loyal, hierarchical mindset",
        "relationships": "Military unit, commanding officers, war comrades",
        "equipment": "Insignia of rank, trophy from fallen enemy, dice set",
        "skills": "Athletics, Intimidation"
    },
    "urchin": {
        "feature": "City Secrets",
        "personality_hints": "Street-smart, scrappy, distrustful of authority",
        "relationships": "Street network, old gang, hidden routes",
        "equipment": "Small knife, city map, pet mouse, reminder of parents",
        "skills": "Sleight of Hand, Stealth"
    },
}
```

**Usage in Prompts:**

```python
def _get_background_context(self) -> str:
    """Get background-specific context for prompts"""
    bg_key = self.background.lower().replace(" ", "_")
    bg_info = BACKGROUND_DETAILS.get(bg_key, {})

    return f"""
Background: {self.background.title()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: {bg_info.get('feature', 'Unknown')}
Personality Influence: {bg_info.get('personality_hints', 'Various')}
Key Relationships: {bg_info.get('relationships', 'To be determined')}
Equipment Theme: {bg_info.get('equipment', 'Standard gear')}
Skill Proficiencies: {bg_info.get('skills', 'Various')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Include the background feature naturally in backstory.
Reflect skill proficiencies in character's expertise and confidence.
"""
```

---

## Equipment in Appearance Descriptions

### Current Issue

Appearance descriptions don't mention specific equipment characters carry.

### Recommendation

Add equipment context to appearance prompts:

```python
def _get_equipment_context(self) -> str:
    """Get equipment for appearance description"""
    equipment = self.character.get("dnd_equipment", {})

    weapons = equipment.get("weapons", [])
    armor = equipment.get("armor", [])

    context = "\nEQUIPMENT TO REFERENCE IN APPEARANCE:\n"

    if armor:
        context += f"  Armor: {', '.join(armor)}\n"
    if weapons:
        context += f"  Weapons: {', '.join(weapons)}\n"

    context += "\nInclude this equipment naturally in appearance description.\n"
    context += "Describe how they wear/carry their gear, battle wear on equipment.\n"

    return context
```

**Example Output Enhancement:**

```
Before: "She has flowing black hair and piercing green eyes."
After: "She has flowing black hair and piercing green eyes. Chain mail
       covers her torso, worn and dented from battles, and a longsword
       hangs at her hip alongside a weathered shield emblazoned with
       a faded family crest."
```

---

## Spellcasting Integration

### Current Issue

Caster prompts mention "relationship with magic" but don't reference actual spells.

### Recommendation

For spellcasters, include spell list in context:

```python
def _get_spellcasting_context(self) -> str:
    """Get spellcasting context for caster classes"""
    spellcasting = self.character.get("dnd_spellcasting")

    if not spellcasting:
        return ""

    cantrips = spellcasting.get("cantrips_known", [])
    spells = spellcasting.get("spells_known_or_prepared", [])
    ability = spellcasting.get("spellcasting_ability", "").title()

    context = f"""
SPELLCASTING DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spellcasting Ability: {ability}
Cantrips Known: {', '.join(cantrips) if cantrips else 'None yet'}
Spells: {len(spells)} spell(s) known/prepared
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

In backstory and combat style, reference signature spells they favor.
Mention their relationship with {ability}-based magic.
"""

    return context
```

---

## Feat Integration (Level 1 Variant Human / Custom Origin)

### Current Issue

Feats not mentioned if character has them.

### Recommendation

Check for feats and integrate:

```python
def _get_feat_context(self) -> str:
    """Get feat context if character has feats"""
    features = self.character.get("dnd_features", [])

    # Check if any features are actually feats
    feat_keywords = ["feat", "magic initiate", "tough", "alert", "lucky"]
    feats = [f for f in features if any(kw in f.lower() for kw in feat_keywords)]

    if not feats:
        return ""

    context = f"""
FEATS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{', '.join(feats)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Incorporate this feat into their training, abilities, or personality.
"""

    return context
```

---

## Prompt Alignment with D&D 5e Mechanics

### ✅ Already Correct

1. **Ability Score Modifiers**: Correctly calculates `(score - 10) // 2`
2. **Personality Traits**: Requires exactly 2 (matches character sheet)
3. **Ideals**: Requires exactly 1
4. **Bonds**: Requires exactly 1
5. **Flaws**: Requires exactly 1
6. **Alignment Influence**: Properly maps alignment to personality
7. **Species Traits**: Accurately describes species features

### ⚠️ Needs Verification

1. **Dragonborn Breath Weapon**: ✅ Mentioned
2. **Dragonborn Wings**: ✅ Correctly notes "level 5+" for spectral wings
3. **Drow Sunlight Sensitivity**: ❌ Not mentioned (should warn about surface world challenges)
4. **Aarakocra Flight in Armor**: ❌ Not mentioned (can't fly in medium/heavy armor)
5. **Gnome Cunning**: ❌ Not mentioned (advantage on INT/WIS/CHA saves vs magic)
6. **Half-Orc Relentless Endurance**: ❌ Not mentioned (survives at 1 HP once per long rest)

---

## Name Generation Improvements

### Current Issues

1. **Static Example Lists**: Prompt includes example names that may get reused
2. **Surname Diversity**: "Do not reuse any static example names" is good, but needs enforcement
3. **Cultural Naming**: Good guidance but could be expanded

### Recommendations

#### 1. **Remove Static Names from Main Prompt**

Instead of listing example names, reference cultural patterns:

**Current:**

```
- Dragonborn: Strong consonants + clan names (Balasar, Ghesh, Heskan...)
```

**Proposed:**

```
- Dragonborn: Strong consonants (B, G, K, T, DR, TH) + vowels (A, O, U)
  Clan names: Honor/element theme (Ironscale, Firebreath, Stormclaw)
```

#### 2. **Enhanced Cultural Naming Patterns**

```python
NAMING_PATTERNS = {
    "dragonborn": {
        "style": "Strong consonants, draconic sounds",
        "syllables": ["Bal", "Dar", "Ghes", "Kor", "Nak", "Taz", "Zor", "Kri"],
        "suffixes": ["sar", "dash", "kar", "than", "rin", "ar", "han"],
        "clan_themes": ["element (Flameheart)", "virtue (Truthseeker)",
                       "lineage (Firstborn)", "achievement (Wyrmslayer)"]
    },
    "elf": {
        "style": "Flowing, melodic, uses L, R, TH sounds",
        "syllables": ["Ae", "El", "Gal", "Iver", "Lau", "Qui", "Syl", "Thal"],
        "suffixes": ["lar", "rian", "thil", "indel", "inan", "enor", "alel"],
        "surname_patterns": ["Nature (Greenleaf)", "Star (Starwillow)",
                            "Ancient lineage (Silvershadow)"]
    },
    # ... etc for all species
}
```

#### 3. **Enforce Diversity in Name Prompt**

Add this to name generation prompt:

```
CRITICAL NAME GENERATION RULES:
1. Generate 6 COMPLETELY DIFFERENT names (no shared roots)
2. Use varied syllable structures (2-syllable, 3-syllable, 4-syllable)
3. Mix consonant clusters (avoid repeating patterns like "Th-" in multiple names)
4. Vary vowel sounds across names (not all "a" or "o" heavy)
5. Include both common and rare cultural variations

FORBIDDEN: Do not generate variations of the same name
  ❌ Bad: Theron, Therion, Theris (same root "Ther-")
  ✅ Good: Theron, Kaelith, Voren, Aldric, Silas, Bryndor
```

---

## Prompt Testing & Validation

### Recommended Test Cases

Create test suite to validate prompts produce correct outputs:

```python
def test_personality_traits_count():
    """Ensure exactly 2 personality traits generated"""
    result = generate_narrative(test_character)
    assert len(result["personality_traits"]) == 2

def test_ideals_count():
    """Ensure exactly 1 ideal"""
    result = generate_narrative(test_character)
    assert isinstance(result["ideals"], str)  # Single string, not array

def test_bonds_count():
    """Ensure exactly 1 bond"""
    result = generate_narrative(test_character)
    assert isinstance(result["bonds"], str)

def test_flaws_count():
    """Ensure exactly 1 flaw"""
    result = generate_narrative(test_character)
    assert isinstance(result["flaws"], str)

def test_species_traits_referenced():
    """Ensure species traits mentioned in appearance/backstory"""
    dragonborn_char = {..., "dnd_species": "dragonborn"}
    result = generate_narrative(dragonborn_char)

    # Check for dragonborn keywords
    appearance = result["character_appearance"].lower()
    assert any(word in appearance for word in ["scales", "dragon", "breath"])

def test_class_features_referenced():
    """Ensure class features influence narrative"""
    wizard_char = {..., "dnd_class": "wizard"}
    result = generate_narrative(wizard_char)

    backstory = result["character_backstory"].lower()
    assert any(word in backstory for word in ["study", "magic", "spellbook", "arcane"])

def test_alignment_in_personality():
    """Ensure alignment influences personality/ideals"""
    lawful_good_char = {..., "dnd_alignment": "Lawful Good"}
    result = generate_narrative(lawful_good_char)

    # Check for lawful good themes
    combined_text = (result["personality_traits"] + [result["ideals"]]).lower()
    assert any(word in combined_text for word in ["honor", "justice", "law", "help", "good"])

def test_background_feature_in_backstory():
    """Ensure background feature referenced"""
    sage_char = {..., "dnd_background": "sage"}
    result = generate_narrative(sage_char)

    backstory = result["character_backstory"].lower()
    assert any(word in backstory for word in ["research", "knowledge", "study", "library", "scholar"])
```

---

## Implementation Priority

### Phase 1: Critical Fixes (HIGH PRIORITY)

1. ✅ Add missing species guidance (Human, Half-Elf, Half-Orc, Gnome, Drow, Aarakocra)
2. ✅ Enhance class guidance with detailed archetypes and combat styles
3. ✅ Add background integration context (features, relationships, equipment)
4. ✅ Add equipment context to appearance prompts

**Estimated Effort**: 4-6 hours
**Impact**: Makes prompts comprehensive for all PHB options

### Phase 2: Mechanical Accuracy (HIGH PRIORITY)

1. Add spellcasting context for casters (spell lists, casting ability)
2. Add feat context for variant humans / custom origin
3. Verify all species traits mentioned correctly
4. Add special ability references (Relentless Endurance, Gnome Cunning, etc.)

**Estimated Effort**: 2-3 hours
**Impact**: Ensures mechanical accuracy

### Phase 3: Name Generation (MEDIUM PRIORITY)

1. Replace static example names with pattern descriptions
2. Add cultural naming patterns dictionary
3. Enhance name diversity enforcement

**Estimated Effort**: 2 hours
**Impact**: Reduces name repetition

### Phase 4: Testing & Validation (MEDIUM PRIORITY)

1. Create prompt test suite
2. Validate output format matches D&D 5e character sheet
3. Test with all species/class/background combinations
4. Check for mechanical accuracy in generated narratives

**Estimated Effort**: 3-4 hours
**Impact**: Ensures quality and correctness

---

## Example: Before & After

### Current Wizard Prompt (Simplified)

```
TASK: Generate backstory for this D&D character.

Class: Wizard
Species: Elf
Background: Sage

Generate backstory now:
```

### Enhanced Wizard Prompt

```
TASK: Generate backstory for this D&D character.

🎓 WIZARD - Scholar of the Arcane
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Class Identity: Magic through rigorous study, spellbook is prized possession
Training Options: Academy education, master's apprenticeship, self-taught
Combat Role: Battlefield control, prepared spell selection critical
Personality: Scholarly, curious, analytical, possibly arrogant about intelligence

🍃 ELF - Graceful, Long-Lived Fey-Touched
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Long perspective from centuries of life
Deep connection to magic and ancient traditions
May have studied for decades before adventuring

📚 SAGE BACKGROUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: Researcher (knows where to find information)
Personality: Curious, analytical, values knowledge over gold
Relationships: Fellow scholars, library access, academic contacts
Equipment: Ink, quill, letter with unanswered question

SPELLCASTING DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spellcasting Ability: Intelligence
Cantrips: Fire Bolt, Mage Hand, Prestidigitation
Spells: 6 spells in spellbook (mention favorites in backstory)

REQUIREMENTS:
- Explain how they learned wizardry (academy, apprentice, self-taught?)
- Reference Researcher feature from Sage background
- Mention spellbook acquisition (inherited, purchased, found?)
- Include relationship with mentor or rival wizard
- Explain elven perspective on magic (centuries of study)
- Reference starting spells in magical style
- 4-6 sentences

Generate backstory now:
```

**Result Quality Improvement:**

- Current: Generic "studied magic at academy"
- Enhanced: Specific training path, spell preferences, scholarly relationships, elven longevity context

---

## Action Items

### Immediate (Next Sprint)

1. [ ] Add missing species guidance blocks to `dnd_narrative_prompts.py`
2. [ ] Expand all 13 class guidance sections with detailed archetypes
3. [ ] Create `BACKGROUND_DETAILS` dictionary with all PHB backgrounds
4. [ ] Add `_get_background_context()` method to `DnDNarrativePromptBuilder`
5. [ ] Add `_get_equipment_context()` method for appearance prompts
6. [ ] Add `_get_spellcasting_context()` method for caster classes
7. [ ] Update `build_dnd_narrative_prompt()` to use all new context methods

### Short-term (Within Month)

1. [ ] Create comprehensive prompt test suite
2. [ ] Test all species/class/background combinations
3. [ ] Validate mechanical accuracy of generated narratives
4. [ ] Enhance name generation diversity enforcement
5. [ ] Add feat integration for variant humans

### Long-term (Ongoing)

1. [ ] Add subclass awareness (level 3+)
2. [ ] Create prompt variation templates for different narrative styles
3. [ ] Build feedback loop for prompt quality (track user edits to generated narratives)
4. [ ] Expand to non-PHB species (Genasi, Goliath, Tabaxi, etc.)

---

## Conclusion

The current D&D narrative prompt system is **structurally sound** with excellent context awareness and mechanical alignment. The main gaps are:

1. **Coverage**: Missing 6+ PHB species
2. **Depth**: Class and background guidance too brief
3. **Integration**: Equipment and spells not referenced in narratives
4. **Testing**: No validation that outputs match D&D 5e standards

Implementing Phase 1 (Critical Fixes) will bring the system to full PHB parity. Phases 2-4 will ensure mechanical accuracy, diversity, and quality validation.

Estimated total effort: **12-16 hours** for complete enhancement.

**Recommendation**: Implement Phase 1 immediately, as it addresses the most significant gaps in species and class coverage.
