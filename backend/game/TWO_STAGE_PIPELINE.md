# Two-Stage LLM Pipeline for Narrative Generation

## Overview

The narrative engine now uses a **two-stage pipeline** for scene generation:

1. **Stage 1 (Local LM Studio)**: Creative narrative generation
2. **Stage 2 (Groq 120B)**: Structured parsing and formatting

## Why Two Stages?

### Problem We Solved

- LLMs kept generating markdown tables in narrative despite instructions
- Single prompt couldn't balance creativity AND strict formatting
- Large cloud models are expensive for pure creative writing

### Solution Benefits

1. **Cost Efficiency**: Local LM Studio is free for creative generation
2. **Quality Control**: Groq excels at following strict JSON schemas
3. **Better Structured Output**: Separation of concerns leads to cleaner results
4. **No More Markdown Tables**: Stage 2 strips them out completely

## Architecture

```
User Action
    ↓
Generate Scene Request
    ↓
┌─────────────────────────────────────────┐
│ STAGE 1: Creative Generation            │
│ (Local LM Studio)                        │
│                                          │
│ Input: "Generate a tavern scene..."     │
│ Output: Rich narrative with atmosphere, │
│         NPCs, and suggested actions      │
│         (any format - prose, tables, etc)│
└─────────────────────────────────────────┘
    ↓
Raw Creative Narrative
    ↓
┌─────────────────────────────────────────┐
│ STAGE 2: Structured Parsing              │
│ (Groq llama-3.3-70b-versatile)          │
│                                          │
│ Input: Raw narrative from Stage 1        │
│ Output: Clean JSON with:                 │
│   - description (prose only)             │
│   - suggested_actions (structured array) │
│   - npcs_present, location, atmosphere   │
│   - NO markdown tables                   │
└─────────────────────────────────────────┘
    ↓
Structured Scene Data
    ↓
Frontend Renders:
- Narrative prose
- Action chips (clickable)
- NPC list
```

## Implementation Details

### Stage 1: Creative Generation Prompt

```
**STAGE 1: CREATIVE GENERATION**

Your task is to write a vivid, immersive D&D narrative. Focus on:

1. Rich Descriptions: Use all five senses
2. Atmosphere & Mood: Create tension, mystery, excitement
3. Character Presence: Describe NPCs with personality
4. Player Options: Suggest 3-5 things players could do

Write naturally and creatively. Any format is fine.
Just tell a great story and give players interesting choices.
```

**Goal**: Get creative, immersive storytelling without constraints

### Stage 2: Structured Parsing Prompt

```
You are a JSON parser for a D&D game system.

**PARSING INSTRUCTIONS:**

1. Extract main narrative as FLOWING PROSE ONLY
   - Remove markdown tables
   - Remove bullet point lists of actions
   - Keep descriptive storytelling

2. Extract player actions as structured JSON:
   - action, roll, dc, type fields
   - Parse "Investigation DC 15" → structured format

3. Extract NPCs, location, atmosphere

**OUTPUT**: Valid JSON only with strict schema
```

**Goal**: Convert creative output to clean structured data

## Error Handling & Fallbacks

The implementation includes multiple fallback layers:

### Level 1: Two-Stage Success

Both stages complete successfully → Perfect structured output

### Level 2: JSON Extraction

Stage 2 returns markdown code blocks → Extract JSON from ```json blocks

### Level 3: Fallback Scene Creation

Parsing fails → Create basic structure from raw narrative:

- Strip markdown tables from description
- Extract actions using regex patterns
- Return functional scene data

### Level 4: Single-Stage Fallback

Two-stage pipeline completely fails → Use Groq directly with strict prompt

### Level 5: Empty Fallback

All LLM calls fail → Return basic scene structure with empty choices

## Configuration

```python
narrative_engine = NarrativeEngine(
    db=db,
    local_llm_url="http://100.120.44.114:1234/v1",  # LM Studio
    groq_model="llama-3.3-70b-versatile"             # Groq parser
)

# Toggle pipeline on/off for testing
narrative_engine.use_two_stage_pipeline = True  # Default
```

## Performance Characteristics

### Latency

- **Stage 1 (Local)**: ~2-5 seconds (depending on local hardware)
- **Stage 2 (Groq)**: ~1-2 seconds (fast JSON parsing)
- **Total**: ~3-7 seconds for complete scene generation

### Cost

- **Stage 1**: FREE (local)
- **Stage 2**: ~$0.0001 per scene (Groq pricing)
- **Total**: Essentially free compared to using GPT-4 for both stages

### Quality

- **Creativity**: High (local models can be very creative)
- **Structure**: Excellent (Groq 70B+ excels at JSON extraction)
- **Consistency**: Very good (Stage 2 enforces rules)

## Testing

### Test Basic Generation

```python
from backend.game.narrative_engine import NarrativeEngine
from backend.database import get_db

db = next(get_db())
engine = NarrativeEngine(db)

# Test opening scene
scene = await engine.generate_opening_scene(
    game_session=session,
    adventure_type="fantasy_adventure",
    starting_location="The Crossroads Tavern"
)

print(scene.description)  # Should be clean prose
print(scene.suggested_actions)  # Should be structured list
```

### Test Fallback Behavior

```python
# Disable two-stage pipeline
engine.use_two_stage_pipeline = False

# Should fall back to single-stage generation
scene = await engine.generate_opening_scene(...)
```

### Test Error Recovery

```python
# Use invalid LM Studio URL
engine.local_llm_url = "http://invalid:9999/v1"

# Should gracefully fall back through error handling chain
scene = await engine.generate_opening_scene(...)
# Scene should still be generated, just with fallback method
```

## Monitoring & Debugging

All stages log their operations:

```python
import logging
logging.basicConfig(level=logging.INFO)

# You'll see:
# [Narrative Engine] Stage 1: Generating creative narrative with Local LM Studio...
# [Stage 1] Generated 1234 chars of narrative
# [Narrative Engine] Stage 2: Parsing into structured format with Groq...
# [Stage 2] Parsed structured output: 567 chars
# [Narrative Engine] Successfully parsed JSON from Stage 2
```

## Integration with Existing Systems

The two-stage pipeline is **transparent** to existing code:

```python
# Old code (placeholder):
scene_data = await self._generate_scene_with_llm(prompt)

# New code (two-stage pipeline):
scene_data = await self._generate_scene_with_llm(prompt)
# ↑ Same interface, much better results!
```

No changes needed in:

- `dm_chat_handler.py`
- `chat.py` router
- Frontend components

## Future Enhancements

1. **Caching Stage 1 Output**: Cache creative narratives for reuse
2. **Model Selection**: Allow different local models based on scene type
3. **Parallel Generation**: Generate multiple scene variations and pick best
4. **Quality Scoring**: Rate Stage 1 output before sending to Stage 2
5. **Dynamic Fallback**: Automatically switch to single-stage if Stage 1 is slow

## Troubleshooting

### "Stage 1 timeout"

- **Cause**: Local LM Studio not responding
- **Fix**: Check LM Studio is running on `http://100.120.44.114:1234`
- **Fallback**: Automatically switches to single-stage Groq generation

### "Stage 2 JSON parsing failed"

- **Cause**: Groq returned invalid JSON or markdown
- **Fix**: Automatically extracts JSON from code blocks
- **Fallback**: Creates scene structure from raw narrative

### "Two-stage pipeline failed"

- **Cause**: Both stages encountered errors
- **Fix**: Automatically falls back to single-stage generation
- **Fallback**: Returns basic scene structure if all fails

### "Markdown tables still appearing"

- **Cause**: Stage 2 parsing missed some tables
- **Fix**: Check `_strip_markdown_tables()` regex patterns
- **Workaround**: Add post-processing in frontend

## Comparison: Before vs After

### Before (Single Prompt)

```
LLM Response:
"You enter the tavern...

| Action | Roll | DC |
|--------|------|-----|
| Talk to bartender | Persuasion | 12 |

What do you do?"
```

❌ Markdown table in narrative  
❌ Wrong items clickable  
❌ Inconsistent format

### After (Two-Stage Pipeline)

```json
{
  "description": "You enter the tavern. The warm glow of firelight dances across weathered wooden beams. A burly bartender polishes glasses behind the bar, while a hooded figure sits alone in the corner, watching.",
  "suggested_actions": [
    {
      "action": "Approach the bartender and order a drink",
      "roll": "Persuasion (d20 + 3)",
      "dc": "12",
      "type": "dialogue"
    }
  ]
}
```

✅ Clean prose narrative  
✅ Structured actions  
✅ Consistent format  
✅ No markdown tables
