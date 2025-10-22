# Google Safety Blocking - Quick Reference

## What's Happening?

When you see: **"Content was blocked by Google's safety filters"**

This means Google Gemini refused to generate content, even though we set safety settings to the most permissive level (`BLOCK_NONE`).

## Why Is This Happening?

Google blocks content at **2 different levels**:

### 1. Prompt-Level Blocking (Most Common) 🚫

- **When**: Before generation even starts
- **What**: Google analyzes YOUR input prompt
- **Why**: Detects "unsafe" keywords, themes, or patterns
- **Can't Be Disabled**: Safety settings don't prevent this
- **Triggers**: Character conflicts, violence, weapons, dark themes, moral ambiguity

### 2. Response-Level Blocking

- **When**: During or after generation
- **What**: Google blocks its own generated content
- **Why**: Generated text violates safety policies
- **Partially Controllable**: `BLOCK_NONE` helps but doesn't eliminate

## What Triggers Google's Filters?

Common storytelling elements that get blocked:

### ❌ Frequently Blocked

- **Combat/Battles**: "warrior with sword", "fighting skills"
- **Weapons**: "gun", "blade", "explosive", "poison"
- **Conflict**: "revenge", "betrayal", "assassination"
- **Dark Themes**: "trauma", "abuse", "death", "murder"
- **Power Dynamics**: "control", "domination", "subjugation"
- **Criminal Activity**: "thief", "smuggler", "mercenary"
- **Violence**: "blood", "injury", "torture", "suffering"

### ✅ Usually Allowed

- Peaceful characters
- Slice-of-life stories
- Lighthearted adventures
- Educational content
- Historical information

## Error Messages Explained

### "Your prompt was blocked by Google before generation: SAFETY"

- **Meaning**: Your input contained flagged content
- **What to do**: Rephrase or switch providers
- **Note**: May show safety ratings like "Dangerous Content: MEDIUM"

### "Your prompt was blocked: BLOCKLIST"

- **Meaning**: Contains specific blocked words/phrases
- **What to do**: Use different terminology or switch providers

### "Your prompt was blocked: PROHIBITED_CONTENT"

- **Meaning**: Violates Google's content policies
- **What to do**: Switch providers (rewriting won't help)

### "Content generation was blocked after prompt was accepted"

- **Meaning**: Prompt was OK, but generated content violated policies
- **What to do**: Try again (might get different generation) or switch providers

## Solutions

### ✅ Solution 1: Use Groq (Recommended)

**Best for**: All creative fiction, fantasy, sci-fi, action

- ✅ Free tier available
- ✅ Fastest generation (30 req/min)
- ✅ No content restrictions for fiction
- ✅ Excellent quality (Llama 4 models)
- ✅ Perfect for storytelling

**How**: Already the default provider in the app!

### ✅ Solution 2: Use Anthropic Claude

**Best for**: Complex narratives, character psychology, literary fiction

- ✅ Excellent quality
- ✅ Minimal content restrictions
- ✅ Best for nuanced storytelling
- 💰 Requires paid API key

### ⚠️ Solution 3: Rephrase for Google (Not Recommended)

Only if you must use Google:

**Before**: "A battle-hardened warrior with a dark past"
**After**: "An experienced guardian with a mysterious background"

**Before**: "Revenge-driven assassin"
**After**: "Determined investigator seeking justice"

**Before**: "Dangerous weapon"
**After**: "Specialized tool"

**Note**: This sanitizes your creative vision and may still fail unpredictably.

## Why We Don't Recommend Google for Fiction

| Issue                      | Impact                                     | Solution           |
| -------------------------- | ------------------------------------------ | ------------------ |
| **Unpredictable Blocking** | Same prompt works one day, fails the next  | Use Groq/Anthropic |
| **Creative Limitation**    | Can't write action, conflict, dark themes  | Use Groq/Anthropic |
| **Two-Level Filtering**    | Blocks prompts AND responses               | Use Groq/Anthropic |
| **No True Bypass**         | `BLOCK_NONE` doesn't fully disable filters | Use Groq/Anthropic |
| **Poor User Experience**   | Frustrating trial-and-error                | Use Groq/Anthropic |

## Technical Details

### Our Safety Configuration

```python
# backend/routers/llm.py
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
```

**This is the MOST permissive setting possible** (short of `OFF` which violates TOS).

### Block Reason Codes

- `0`: No block (OK)
- `1`: SAFETY - Content safety violation
- `2`: OTHER - Unknown issue
- `3`: BLOCKLIST - Specific blocked terms
- `4`: PROHIBITED_CONTENT - Policy violation

### Safety Rating Levels

- `NEGLIGIBLE`: Almost certainly safe
- `LOW`: Unlikely to be harmful
- `MEDIUM`: Possibly harmful → **Often triggers blocks**
- `HIGH`: Likely harmful → **Always triggers blocks**

## What We've Done to Help

### 1. Enhanced Error Messages ✅

- Show exact block reason (SAFETY, BLOCKLIST, etc.)
- Display which safety categories triggered
- Show probability levels (LOW, MEDIUM, HIGH)
- Recommend switching to Groq/Anthropic

### 2. Set Permissive Defaults ✅

- All safety thresholds set to `BLOCK_NONE`
- Allow MEDIUM and LOW probability content
- Most permissive configuration possible

### 3. Changed Default Provider ✅

- Frontend now defaults to **Groq** instead of Google
- Users can still choose Google if they want
- Clear warnings in UI about Google limitations

### 4. Detection & Logging ✅

- Detect prompt-level blocks (before generation)
- Detect response-level blocks (during generation)
- Log safety ratings for debugging
- Helpful error messages with actionable guidance

## For Developers

### Checking Block Details

```python
# Check prompt feedback
if response.prompt_feedback.block_reason:
    print(f"Blocked at prompt level: {response.prompt_feedback.block_reason}")
    for rating in response.prompt_feedback.safety_ratings:
        print(f"{rating.category}: {rating.probability}")

# Check response candidates
if not response.candidates:
    print("No candidates returned - blocked during generation")
```

### Testing Different Providers

```python
# Test same prompt across providers
providers = ["groq", "anthropic", "google"]
for provider in providers:
    try:
        result = await call_llm(prompt, provider)
        print(f"{provider}: SUCCESS")
    except Exception as e:
        print(f"{provider}: FAILED - {e}")
```

## Summary

**Bottom Line**: Google Gemini's safety filters are **too aggressive for creative fiction**, even at the most permissive settings.

**Recommendation**: Use **Groq** (free, fast, no restrictions) or **Anthropic** (paid, excellent quality) for all storytelling.

**Current Status**: App defaults to Groq ✅

**User Action Required**: None! Just keep using Groq (default) and you won't see these errors.
