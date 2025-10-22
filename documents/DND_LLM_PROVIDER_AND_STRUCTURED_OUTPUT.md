# D&D Character Creation: LLM Provider Selection & Structured Output

## Overview

Enhanced the D&D character creation workflow to include:

1. **LLM Provider Selection** - Users can now choose which AI model to use for narrative generation
2. **Structured Output** - Comprehensive D&D-specific narrative schema that produces consistent, rich character narratives
3. **Species-Aware Prompts** - Special handling for Dragonborn and other D&D species traits

## Changes Made

### Frontend Changes

#### 1. DnDCharacterCreator Component (`frontend/src/components/DnDCharacterCreator.jsx`)

**Added State Variables:**

```javascript
// LLM Provider Selection for narrative generation
const [provider, setProvider] = useState("groq");
const [model, setModel] = useState("");

// Structured Output Toggle
const [useStructured, setUseStructured] = useState(true);
```

**Added UI Components:**

- **ModelSelector** - Allows users to select LLM provider (Groq, OpenAI, Google, Claude, etc.) and specific model
- **Structured Output Toggle** - Switch to enable/disable structured output (default: enabled, recommended)
- **Tooltips** - Helpful information about structured output benefits

**Updated Generation Flow:**

- Now sends provider, model, and structured output preferences to backend
- Backend handles all narrative generation with structured output
- Removed frontend-side narrative aspect generation (moved to backend for better consistency)

**Request Parameters Sent to Backend:**

```javascript
{
  // ... D&D stats params
  generate_narrative: useAINarrative,
  narrative_provider: provider,           // User's selected provider
  narrative_model: model || null,         // Optional specific model
  use_structured: useStructured,          // Enable structured output
  narrative_style: narrativeStyle,        // concise, detailed, dramatic
  narrative_context: narrativePrompt,     // Additional user context
}
```

### Backend Changes

#### 2. New Schema: DnDCharacterNarrative (`backend/schemas.py`)

Created a comprehensive Pydantic schema specifically for D&D character narratives with **21 structured fields**:

**Physical Appearance:**

- `physical_appearance`: Detailed description incorporating species traits
- `height_and_build`: Based on species and ability scores
- `distinctive_features`: Unique characteristics (e.g., Dragonborn scale patterns, horns)

**Personality:**

- `personality_summary`: Rich profile based on alignment and background
- `personality_traits`: Core traits (3-5)
- `ideals`: Personal beliefs
- `bonds`: Important connections
- `flaws`: Character weaknesses

**Backstory:**

- `backstory`: Comprehensive origin story (4-7 sentences)
- `formative_events`: Key shaping events (2-4)

**Motivations:**

- `primary_motivation`: Main driving force
- `short_term_goals`: Immediate objectives (2-3)
- `long_term_goals`: Overarching ambitions (1-2)
- `fears`: What they worry about

**Unique Qualities:**

- `quirks`: Memorable habits (2-4, species-aware)
- `speech_pattern`: How they communicate
- `combat_style_narrative`: Fighting style description
- `signature_abilities`: Distinctive abilities (MUST include racial features like breath weapon)

**Social:**

- `reputation`: How others perceive them
- `allies_and_enemies`: Key relationships

**Development:**

- `character_arc_potential`: Growth opportunities

**Special Features:**

- Dragonborn-specific prompts (scales, horns, breath weapon, draconic ancestry, etc.)
- Validators to handle LLM output variations

#### 3. Enhanced Prompt Builder (`backend/dnd_narrative_prompts.py`)

**New Function: `build_dnd_narrative_prompt()`**

Creates comprehensive prompts tailored to D&D species and classes:

```python
def build_dnd_narrative_prompt(
    dnd_character: Dict[str, Any],
    style: str = "detailed",
    additional_context: Optional[str] = None
) -> str:
```

**Features:**

- **Species-Specific Guidance**: Special instructions for Dragonborn (draconic features, breath weapon, ancestry), Elves, Dwarves, Halflings, etc.
- **Class-Specific Guidance**: Tailored prompts for Wizards, Fighters, Rogues, Clerics, etc.
- **Ability Score Interpretation**: Translates STR, DEX, CON, INT, WIS, CHA into narrative traits
- **Comprehensive Requirements**: Detailed specifications for each narrative element

**Example Dragonborn-Specific Prompt:**

```
- DRAGONBORN: This character is a wingless, bipedal dragon with draconic features
- Describe their scale coloration matching their draconic ancestry
- Mention their horns, thick-boned structure, bright eyes, and imposing presence
- Include how their breath weapon (Cone or Line attack) manifests in combat
- Reference their damage resistance to their ancestry's element
- At level 5+: Describe how they manifest spectral draconic wings for flight
- Consider draconic behaviors: formal speech, territorial instincts, honor-bound nature
```

#### 4. Updated D&D Generation Endpoint (`backend/routers/characters.py`)

**Enhanced Request Schema:**

```python
class DnDCharacterGenerateRequest(BaseModel):
    # ... existing D&D params

    # NEW: AI Narrative Generation
    generate_narrative: bool = False
    narrative_provider: str = "groq"         # LLM provider
    narrative_model: str | None = None       # Optional specific model
    use_structured: bool = True              # Use structured output
    narrative_style: str = "detailed"        # concise, detailed, dramatic
    narrative_context: str | None = None     # Additional context
```

**Updated Generation Flow:**

```python
@router.post("/dnd/generate")
async def generate_dnd_character(request: DnDCharacterGenerateRequest, ...):
    # 1. Generate D&D stats (ability scores, HP, AC, equipment, etc.)
    dnd_char = generate_dnd_character(...)

    # 2. If narrative requested, use structured generation
    if request.generate_narrative:
        if request.use_structured:
            # Use DnDCharacterNarrative schema
            narrative_data = await generate_structured_content(
                prompt=build_dnd_narrative_prompt(dnd_char, ...),
                schema_class=DnDCharacterNarrative,
                provider=request.narrative_provider,
                model=request.narrative_model
            )
        else:
            # Fallback to simple text generation
            narrative_text = await LLMProvider.generate_text(...)

    # 3. Store character with narrative in database
    db_character = Character(...)
    db_character.generation_log = {
        "character_sheet": format_character_sheet(dnd_char),
        "ai_narrative": narrative_dict,  # Structured narrative data
        ...
    }
```

## Benefits

### 1. **Consistent Narrative Quality**

- Structured output ensures all narrative aspects are covered
- No missing fields or incomplete descriptions
- Predictable, parseable format

### 2. **Species-Aware Generation**

- Dragonborn get proper draconic features (scales, horns, breath weapon, ancestry)
- Each species receives appropriate trait descriptions
- Racial abilities are incorporated into narrative

### 3. **User Control**

- Choose preferred LLM provider (Groq for speed, Claude for quality, etc.)
- Select specific models for different needs
- Adjust narrative style (concise, detailed, dramatic)
- Add custom context for personalization

### 4. **Integration with D&D Mechanics**

- Ability scores influence physical/mental/social traits
- Class features woven into combat style and personality
- Background informs backstory and relationships
- Alignment shapes ideals and motivations

## Example Output

For a **Level 3 Dragonborn Fighter** with Red Dragon ancestry:

```json
{
  "physical_appearance": "Kordax stands at an imposing 6'7\", his muscular frame covered in crimson scales that gleam like burnished copper in firelight. Curved horns sweep back from his angular skull, and his bright amber eyes hold an intensity that speaks of draconic heritage. His thick, powerful build marks him as a warrior, with battle-scarred armor that bears the marks of countless fights.",

  "distinctive_features": [
    "Crimson scales with darker red striping along spine",
    "Two prominent curved horns with small chips from combat",
    "Burn scar on left forearm from his own breath weapon training",
    "Small collection of dragon teeth worn as a necklace"
  ],

  "signature_abilities": [
    "Fire Breath: Can exhale a 15-foot cone of searing flame, his most trusted weapon in close combat",
    "Fire Resistance: His draconic blood grants immunity to his own flames and resistance to all fire",
    "Darkvision: Can see perfectly in darkness up to 60 feet",
    "Action Surge: Can push beyond normal limits for explosive combat bursts"
  ],

  "quirks": [
    "Hisses softly when frustrated or concentrating",
    "Hoards small trophies from worthy opponents",
    "Speaks in formal, measured tones - a habit from draconic upbringing"
  ],

  "combat_style_narrative": "Kordax fights with calculated aggression, using his breath weapon to scatter enemies before charging into melee range. His fighting style combines draconic fury with disciplined military training, making him a fearsome opponent who knows exactly when to unleash his most devastating attacks."

  // ... 16 more structured fields
}
```

## Usage Instructions

### For Users:

1. **Toggle D&D Mode** in character creation
2. **Select LLM Provider** - Choose from available providers
3. **Pick Model** (optional) - Use specific model or let system choose default
4. **Enable Structured Output** (recommended) - For consistent, comprehensive narratives
5. **Set Narrative Style** - Concise, Detailed, or Dramatic
6. **Add Custom Context** (optional) - Include specific details you want
7. **Configure D&D Options** - Class, Species, Background, etc.
8. **Generate** - Backend creates character with structured narrative

### For Developers:

**Adding New Species Support:**

1. Update `build_dnd_narrative_prompt()` in `dnd_narrative_prompts.py`
2. Add species-specific guidance similar to Dragonborn example
3. Include racial traits, abilities, and cultural elements

**Adding New Narrative Fields:**

1. Update `DnDCharacterNarrative` schema in `schemas.py`
2. Add field with clear description for LLM
3. Update prompt requirements in `build_dnd_narrative_prompt()`

## Testing

### Backend Tests:

```bash
# Test schema loading
cd backend
python -c "from schemas import DnDCharacterNarrative; print('Schema loaded:', len(DnDCharacterNarrative.model_fields), 'fields')"

# Test prompt generation
python -c "from dnd_narrative_prompts import build_dnd_narrative_prompt; ..."
```

### Frontend Tests:

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to character creation
4. Toggle D&D Mode
5. Verify ModelSelector appears
6. Verify Structured Output toggle appears
7. Test character generation with different providers

## Troubleshooting

### "No LLM provider selection shown"

- **Cause**: ModelSelector not imported or not rendered
- **Fix**: Check DnDCharacterCreator imports and UI section

### "Narrative generation fails"

- **Cause**: Provider API key not set or model not available
- **Fix**: Check backend `.env` file for API keys, verify model exists

### "Incomplete narrative output"

- **Cause**: Structured output disabled or LLM didn't follow schema
- **Fix**: Enable structured output (recommended), or try different provider

### "Dragonborn missing breath weapon"

- **Cause**: Prompt not species-specific enough
- **Fix**: Prompt explicitly requires signature abilities including racial features

## Future Enhancements

1. **More Species Support**: Add detailed prompts for Tieflings, Half-Orcs, Gnomes, etc.
2. **Subrace Handling**: Dragonborn draconic ancestry variations, Elf subraces, etc.
3. **Level-Appropriate Narratives**: Adjust descriptions based on character level
4. **Multiclass Support**: Narratives that reflect multiple class identities
5. **Background Integration**: Deeper integration of background features into narrative
6. **Party Dynamics**: Generate relationship dynamics with other party members

## Related Documentation

- `STRUCTURED_OUTPUTS_IMPLEMENTATION.md` - General structured output system
- `DND_PHASE4_PROGRESS.md` - D&D integration overall progress
- `CHARACTER_GENERATION_ENHANCEMENT_PLAN.md` - Original character generation features
- `CLAUDE_INTEGRATION.md` - Claude LLM provider details

## Credits

- **D&D 5E Species Data**: Based on official D&D Beyond references
- **Dragonborn Traits**: From Player's Handbook and D&D Beyond species page
- **Structured Output Pattern**: Adapted from existing CharacterProfile schema
