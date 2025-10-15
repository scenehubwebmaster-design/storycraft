# Structured Outputs Implementation Guide

## Overview

This document provides a complete implementation plan for adding structured outputs to character and world generation, ensuring complete, robust profiles without cutoffs.

## Problem

Currently, character generation using free-form text can result in:

- **Incomplete outputs** (like "Unique Qualities" getting cut off)
- **Inconsistent formatting**
- **Missing fields**
- **Difficulty parsing results**

## Solution: Structured Outputs

Use provider-native structured output capabilities to guarantee complete, well-formatted responses that match a predefined schema.

## Implementation Plan

### Phase 1: Schema Definition ✅

**File:** `backend/schemas.py`

Added two new Pydantic models:

1. **CharacterProfile** - 10-section comprehensive character schema:
   - Name and Age
   - Physical Appearance (height, build, hair, eyes, distinctive features)
   - Personality (traits, demeanor, humor)
   - Background (birthplace, upbringing, formative events)
   - Motivations and Goals
   - Fears and Weaknesses
   - Strengths and Abilities
   - Relationships
   - Character Arc Potential
   - Unique Qualities (quirks, habits)

2. **WorldProfile** - Comprehensive world-building schema:
   - Overview (name, type, tagline)
   - History (age, origin, major events, current era)
   - Geography (size, climate zones, regions, natural wonders)
   - Culture and Society (species, population, civilizations, languages, religions)
   - Magic/Technology (power system, level, limitations, artifacts)
   - Conflicts and Themes
   - Lore and Mysteries (legends, unsolved mysteries, prophecies)
   - Story Potential (adventure hooks, notable locations, unique aspects)

### Phase 2: Utility Functions ✅

**File:** `backend/structured_output_utils.py`

Created helper functions:

```python
# Convert Pydantic to provider formats
pydantic_to_json_schema(model)
pydantic_to_openai_schema(model)
pydantic_to_groq_schema(model)
pydantic_to_google_schema(model)
get_schema_for_provider(model, provider)

# Parse and validate responses
parse_structured_response(response_content, model)

# Check provider support
supports_structured_outputs(provider)

# Fallback for unsupported providers
get_structured_output_prompt(model)
```

### Phase 3: LLM Provider Updates (TO DO)

Update each provider's client to support structured outputs:

#### 3.1 Groq Client

**File:** `backend/routers/llm.py` (LLMProvider.generate_groq)

```python
@staticmethod
async def generate_groq(
    prompt: str,
    model: str = "llama-3.3-70b-versatile",
    response_format: dict = None  # NEW PARAMETER
) -> str:
    """Generate using Groq with optional structured output"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)

    # Build request
    request_params = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    # Add structured output if provided
    if response_format:
        request_params["response_format"] = response_format

    response = client.chat.completions.create(**request_params)
    return response.choices[0].message.content
```

**Supported Models:**

- `openai/gpt-oss-20b`
- `openai/gpt-oss-120b`
- `moonshotai/kimi-k2-instruct-0905`
- `meta-llama/llama-4-maverick-17b-128e-instruct`
- `meta-llama/llama-4-scout-17b-16e-instruct`

#### 3.2 OpenAI Client

**File:** `backend/routers/llm.py` (LLMProvider.generate_openai)

```python
@staticmethod
async def generate_openai(
    prompt: str,
    model: str = "gpt-4",
    response_format: dict = None  # NEW PARAMETER
) -> str:
    """Generate using OpenAI with optional structured output"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    request_params = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    if response_format:
        request_params["response_format"] = response_format

    response = client.chat.completions.create(**request_params)
    return response.choices[0].message.content
```

**Supported Models:** All GPT-4 and GPT-3.5 models

#### 3.3 Google Gemini Client

**File:** `backend/routers/llm.py` (LLMProvider.generate_google)

```python
@staticmethod
async def generate_google(
    prompt: str,
    model: str = "gemini-2.0-flash",
    response_schema: dict = None  # NEW PARAMETER
) -> str:
    """Generate using Google Gemini with optional structured output"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)

    # Build generation config
    generation_config = {"temperature": 0.7}

    if response_schema:
        generation_config["response_mime_type"] = "application/json"
        generation_config["response_schema"] = response_schema

    response = model_instance.generate_content(
        prompt,
        generation_config=generation_config
    )

    return response.text
```

**Supported Models:** Gemini 2.0 Flash, Gemini 2.5 Flash, Gemini Pro

### Phase 4: Generation Endpoint Updates (TO DO)

#### 4.1 Create Structured Character Generation Endpoint

**File:** `backend/routers/generation.py`

```python
@router.post("/character/structured", response_model=CharacterProfile)
async def generate_character_structured(request: CharacterGenerationRequest):
    """
    Generate a complete, structured character profile.
    Returns a CharacterProfile with all fields guaranteed to be present.
    """
    try:
        # Build enhanced prompt for structured output
        prompt = PromptTemplates.character_structured_prompt(
            themes=request.themes,
            personality_traits=request.personality_traits,
            physical_traits=request.physical_traits,
            archetype=request.archetype,
            custom_details=request.custom_details
        )

        # Get provider-specific schema
        schema = get_schema_for_provider(CharacterProfile, request.provider)

        # Generate with structured output
        if request.provider.lower() == "groq":
            response_text = await LLMProvider.generate_groq(
                prompt,
                request.model or "openai/gpt-oss-120b",
                response_format=schema
            )
        elif request.provider.lower() == "openai":
            response_text = await LLMProvider.generate_openai(
                prompt,
                request.model or "gpt-4",
                response_format=schema
            )
        elif request.provider.lower() == "google":
            google_schema = get_schema_for_provider(CharacterProfile, "google")
            response_text = await LLMProvider.generate_google(
                prompt,
                request.model or "gemini-2.0-flash",
                response_schema=google_schema
            )
        else:
            # Fallback: Add schema to prompt
            schema_prompt = get_structured_output_prompt(CharacterProfile)
            full_prompt = f"{prompt}\n\n{schema_prompt}"
            response_text, _ = await call_llm(full_prompt, request.provider, request.model)

        # Parse and validate response
        character_profile = parse_structured_response(response_text, CharacterProfile)

        return character_profile

    except Exception as e:
        logger.error(f"Structured character generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate structured character: {str(e)}"
        )
```

#### 4.2 Create Structured World Generation Endpoint

**File:** `backend/routers/generation.py`

```python
@router.post("/world/structured", response_model=WorldProfile)
async def generate_world_structured(request: WorldGenerationRequest):
    """
    Generate a complete, structured world profile.
    Returns a WorldProfile with all fields guaranteed to be present.
    """
    try:
        # Build enhanced prompt
        prompt = PromptTemplates.world_structured_prompt(
            themes=request.themes,
            setting=request.setting,
            elements=request.elements,
            custom_details=request.custom_details
        )

        # Get provider-specific schema
        schema = get_schema_for_provider(WorldProfile, request.provider)

        # Generate with structured output
        if request.provider.lower() == "groq":
            response_text = await LLMProvider.generate_groq(
                prompt,
                request.model or "openai/gpt-oss-120b",
                response_format=schema
            )
        elif request.provider.lower() == "openai":
            response_text = await LLMProvider.generate_openai(
                prompt,
                request.model or "gpt-4",
                response_format=schema
            )
        elif request.provider.lower() == "google":
            google_schema = get_schema_for_provider(WorldProfile, "google")
            response_text = await LLMProvider.generate_google(
                prompt,
                request.model or "gemini-2.0-flash",
                response_schema=google_schema
            )
        else:
            # Fallback
            schema_prompt = get_structured_output_prompt(WorldProfile)
            full_prompt = f"{prompt}\n\n{schema_prompt}"
            response_text, _ = await call_llm(full_prompt, request.provider, request.model)

        # Parse and validate
        world_profile = parse_structured_response(response_text, WorldProfile)

        return world_profile

    except Exception as e:
        logger.error(f"Structured world generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate structured world: {str(e)}"
        )
```

### Phase 5: Enhanced Prompts (TO DO)

**File:** `backend/prompts.py`

Add new prompt templates optimized for structured outputs:

```python
@staticmethod
def character_structured_prompt(
    themes: List[str] = None,
    personality_traits: List[str] = None,
    physical_traits: List[str] = None,
    archetype: str = None,
    custom_details: str = None
) -> str:
    """
    Generate prompt for structured character profile.
    Optimized to work with JSON schema constraints.
    """
    prompt = """Create a detailed, complete character profile with ALL fields filled out.

This character will be used in a story, so make them:
- Compelling and multi-dimensional
- Internally consistent
- Ready to use in narrative contexts
- Complete with specific, concrete details (not vague descriptions)

Include specific examples, numbers, and details. For example:
- Don't say "tall" - say "6'5\" (196cm)"
- Don't say "several scars" - list them: "scar across left cheek, burn mark on right forearm"
- Don't say "loyal friend" - name them and describe the relationship

"""

    if themes:
        prompt += f"\nThemes to incorporate: {', '.join(themes)}"
    if personality_traits:
        prompt += f"\nPersonality traits: {', '.join(personality_traits)}"
    if physical_traits:
        prompt += f"\nPhysical traits: {', '.join(physical_traits)}"
    if archetype:
        prompt += f"\nArchetype: {archetype}"
    if custom_details:
        prompt += f"\n\nAdditional requirements:\n{custom_details}"

    prompt += "\n\nEnsure EVERY field is filled with rich, specific details. No placeholders or generic descriptions."

    return prompt


@staticmethod
def world_structured_prompt(
    themes: List[str] = None,
    setting: List[str] = None,
    elements: List[str] = None,
    custom_details: str = None
) -> str:
    """
    Generate prompt for structured world profile.
    Optimized to work with JSON schema constraints.
    """
    prompt = """Create a rich, detailed world profile with ALL fields completely filled out.

This world will be used for storytelling, so make it:
- Immersive and believable
- Internally consistent
- Full of story possibilities
- Specific with concrete details (avoid vague descriptions)

Provide specific examples, numbers, and vivid details. For example:
- Don't say "ancient" - say "Founded 3,247 years ago during the Age of Dragons"
- Don't say "large population" - say "Estimated 47 million inhabitants across 12 provinces"
- Don't say "magical artifacts" - name them: "The Sundering Blade, Orb of Eternal Night"

"""

    if themes:
        prompt += f"\nThemes to explore: {', '.join(themes)}"
    if setting:
        prompt += f"\nSetting elements: {', '.join(setting)}"
    if elements:
        prompt += f"\nWorld-building elements: {', '.join(elements)}"
    if custom_details:
        prompt += f"\n\nAdditional requirements:\n{custom_details}"

    prompt += "\n\nFill EVERY field with rich, specific, immersive details. Create a world readers can see, smell, and touch."

    return prompt
```

### Phase 6: Frontend Updates (TO DO)

#### 6.1 Update Character Creation Page

**File:** `frontend/src/routes/create/character.jsx`

```javascript
// Add toggle for structured output
const [useStructuredOutput, setUseStructuredOutput] = useState(true);

const handleGenerate = async () => {
  setGenerating(true);
  setError(null);

  try {
    const endpoint = useStructuredOutput
      ? `${API_URL}/api/generate/character/structured`
      : `${API_URL}/api/generate/character`;

    const response = await axios.post(endpoint, {
      themes: selectedThemes.length > 0 ? selectedThemes : null,
      personality_traits:
        selectedPersonalityTraits.length > 0 ? selectedPersonalityTraits : null,
      physical_traits:
        selectedPhysicalTraits.length > 0 ? selectedPhysicalTraits : null,
      archetype: selectedArchetype || null,
      custom_details: customDetails || null,
      provider: provider,
      model: model || null,
    });

    if (useStructuredOutput) {
      // Response is structured JSON object
      setGeneratedProfile(response.data);
      // Format as readable text for display
      setGeneratedContent(formatCharacterProfile(response.data));
    } else {
      // Legacy text response
      setGeneratedContent(response.data.content);
    }

    setActiveStep(2);
  } catch (err) {
    setError(err.response?.data?.detail || "Failed to generate character");
  } finally {
    setGenerating(false);
  }
};

// Helper to format structured profile as readable text
const formatCharacterProfile = (profile) => {
  return `
**${profile.name}** (Age: ${profile.age})

**Physical Appearance:**
Height: ${profile.height}
Build: ${profile.build}
Hair: ${profile.hair}
Eyes: ${profile.eyes}
Distinctive Features: ${profile.distinctive_features.join(", ")}

${profile.physical_description}

**Personality:**
Traits: ${profile.personality_traits.join(", ")}
Demeanor: ${profile.demeanor}
${profile.sense_of_humor ? `Sense of Humor: ${profile.sense_of_humor}` : ""}

${profile.personality_description}

**Background:**
Birthplace: ${profile.birthplace}
Upbringing: ${profile.upbringing}

Key Formative Events:
${profile.formative_events.map((event) => `- ${event}`).join("\n")}

${profile.backstory}

**Motivations and Goals:**
Primary Motivation: ${profile.primary_motivation}

Goals:
${profile.goals.map((goal) => `- ${goal}`).join("\n")}

Values:
${profile.values.map((value) => `- ${value}`).join("\n")}

**Fears and Weaknesses:**
Greatest Fear: ${profile.greatest_fear}

Emotional Weaknesses:
${profile.emotional_weaknesses.map((w) => `- ${w}`).join("\n")}

Physical Weaknesses:
${profile.physical_weaknesses.map((w) => `- ${w}`).join("\n")}

**Strengths and Abilities:**
Skills: ${profile.skills.join(", ")}
Special Abilities: ${profile.special_abilities.join(", ")}
${profile.combat_style ? `Combat Style: ${profile.combat_style}` : ""}

${profile.strengths_description}

**Relationships:**
${profile.key_relationships
  .map((rel) => `- **${rel.name}** (${rel.relationship}): ${rel.description}`)
  .join("\n")}

**Character Arc Potential:**
${profile.character_arc_potential}

**Unique Qualities:**
${profile.unique_qualities.join(", ")}

Quirks and Habits:
${profile.quirks_and_habits.map((q) => `- ${q}`).join("\n")}
  `.trim();
};
```

#### 6.2 Update World Creation Page

**File:** `frontend/src/routes/create/world.jsx`

Similar changes - add structured output toggle and formatting function.

### Phase 7: Database Schema Updates (TO DO)

Consider adding a `structured_data` JSON column to Character and World tables:

```python
# In models.py
class Character(Base):
    __tablename__ = "characters"
    # ... existing fields ...
    structured_data = Column(JSON, nullable=True)  # NEW: Store full structured profile

class World(Base):
    __tablename__ = "worlds"
    # ... existing fields ...
    structured_data = Column(JSON, nullable=True)  # NEW: Store full structured profile
```

Migration:

```python
# migration file
def upgrade():
    op.add_column('characters', sa.Column('structured_data', sa.JSON(), nullable=True))
    op.add_column('worlds', sa.Column('structured_data', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('characters', 'structured_data')
    op.drop_column('worlds', 'structured_data')
```

### Phase 8: Testing Checklist

1. **Schema Validation:**
   - [ ] CharacterProfile validates correctly with all required fields
   - [ ] WorldProfile validates correctly with all required fields
   - [ ] Pydantic catches missing or malformed fields

2. **Provider-Specific Tests:**
   - [ ] Groq: Test with `openai/gpt-oss-120b`
   - [ ] OpenAI: Test with `gpt-4`
   - [ ] Google: Test with `gemini-2.0-flash`
   - [ ] Verify schema conversion works for each provider

3. **End-to-End Generation:**
   - [ ] Generate character with structured output
   - [ ] Verify no fields are cut off or missing
   - [ ] Generate world with structured output
   - [ ] Verify all sections are complete

4. **Edge Cases:**
   - [ ] Test with minimal prompt input
   - [ ] Test with extensive custom details
   - [ ] Test error handling for validation failures
   - [ ] Test fallback for unsupported providers

5. **Performance:**
   - [ ] Compare token usage vs regular generation
   - [ ] Measure response times
   - [ ] Verify rate limiting still works

### Phase 9: Documentation

Create user-facing documentation:

1. **API Documentation:**
   - Document new structured endpoints
   - Provide example requests/responses
   - Explain schema structure

2. **User Guide:**
   - Explain benefits of structured outputs
   - Show how to enable/disable in UI
   - Provide examples of complete profiles

## Benefits of Structured Outputs

1. **Completeness:** No more cut-off sections or incomplete profiles
2. **Consistency:** Every character/world has the same structure
3. **Type Safety:** Automatic validation of field types
4. **Easier Parsing:** Direct JSON access to fields
5. **Better UX:** Users see progress and know what to expect
6. **Database Integration:** Easier to store and query structured data

## Migration Path

1. **Backward Compatibility:** Keep existing endpoints working
2. **Gradual Rollout:** Add structured endpoints alongside existing ones
3. **User Choice:** Let users toggle between modes
4. **Data Preservation:** Continue supporting legacy text-based profiles

## Next Steps

1. Complete Phase 3: Update LLM provider methods ⏳
2. Complete Phase 4: Add structured generation endpoints ⏳
3. Complete Phase 5: Create optimized prompts ⏳
4. Complete Phase 6: Update frontend ⏳
5. Complete Phase 7: Database updates (optional) ⏳
6. Complete Phase 8: Testing ⏳
7. Complete Phase 9: Documentation ⏳

## Estimated Timeline

- **Foundation (Phases 1-2):** ✅ Complete
- **Backend Implementation (Phases 3-5):** 4-6 hours
- **Frontend Integration (Phase 6):** 2-3 hours
- **Database & Testing (Phases 7-8):** 2-3 hours
- **Documentation (Phase 9):** 1-2 hours

**Total:** ~10-15 hours for complete implementation

## Provider Support Summary

| Provider         | Structured Output Support | Models                                                           |
| ---------------- | ------------------------- | ---------------------------------------------------------------- |
| Groq             | ✅ Yes                    | gpt-oss-20b, gpt-oss-120b, kimi, llama-4-maverick, llama-4-scout |
| OpenAI           | ✅ Yes                    | All GPT-4 and GPT-3.5 models                                     |
| Google Gemini    | ✅ Yes                    | Gemini 2.0/2.5 Flash, Pro                                        |
| Anthropic Claude | ❌ No (use prompt-based)  | All Claude models                                                |

## Conclusion

This implementation will solve the character cutoff issue by:

1. Using provider-native structured outputs
2. Enforcing complete schema compliance
3. Validating all required fields are present
4. Providing rich, complete profiles every time

The structured approach is more reliable, maintainable, and provides better user experience than free-form text generation.
