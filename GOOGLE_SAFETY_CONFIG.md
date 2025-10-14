# Google Gemini Safety Configuration Guide

## ⚠️ CRITICAL RECOMMENDATION

**For Creative Fiction/Storytelling**: **Use Groq or Anthropic instead of Google Gemini**

### Why Avoid Google for Fiction?

Even with safety settings set to `BLOCK_NONE` (most permissive), Google Gemini **still blocks content** at multiple levels:

1. **Prompt-Level Blocking**: Blocks your input before generation even starts
2. **Response-Level Blocking**: Blocks generated content mid-stream
3. **Overly Aggressive**: Flags common storytelling elements as "dangerous" or "harassment"
4. **Unpredictable**: Same prompt may work one day, fail the next
5. **Creative Limitations**: Restricts character conflicts, action scenes, dark themes

### ✅ Recommended Providers for Fiction

| Provider | Cost | Speed | Creative Freedom | Best For |
|----------|------|-------|------------------|----------|
| **Groq (Llama)** | ✅ Free | ⚡ Fastest | 🎯 Excellent | Fantasy, Sci-Fi, Action |
| **Anthropic (Claude)** | 💰 Paid | 🐇 Fast | 🎯 Excellent | Complex narratives, Character depth |
| **OpenAI (GPT)** | 💰 Paid | 🐇 Fast | ⚠️ Moderate | General fiction |
| **Google (Gemini)** | ✅ Free | 🐢 Medium | ❌ Poor | ❌ Not recommended for fiction |

---

## Overview

Google Gemini has built-in safety filters that can block content during generation. This guide explains how safety settings work and how they're configured in StoryCraft.

## Current Configuration

**File**: `backend/routers/llm.py` → `generate_google()` function

**Settings**: All 4 harm categories set to **`BLOCK_NONE`** (most permissive)

```python
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"  # Most permissive setting
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"  # Most permissive setting
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"  # Most permissive setting
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"  # Most permissive setting
    },
]
```

**Despite these permissive settings, Google still blocks many creative fiction prompts.**

## Harm Categories

| Category                            | Description                                                          | Examples                                     |
| ----------------------------------- | -------------------------------------------------------------------- | -------------------------------------------- |
| **HARM_CATEGORY_HARASSMENT**        | Negative or harmful comments targeting identity/protected attributes | Bullying, threats, insults based on identity |
| **HARM_CATEGORY_HATE_SPEECH**       | Content that is rude, disrespectful, or profane                      | Slurs, derogatory language, profanity        |
| **HARM_CATEGORY_SEXUALLY_EXPLICIT** | References to sexual acts or lewd content                            | Adult content, sexual descriptions           |
| **HARM_CATEGORY_DANGEROUS_CONTENT** | Promotes, facilitates, or encourages harmful acts                    | Violence, weapons, illegal activities        |

**Note**: There's also `HARM_CATEGORY_CIVIC_INTEGRITY` (election-related), but it's not configurable via API and defaults to BLOCK_NONE for gemini-2.0-flash.

## Block Thresholds

| Threshold      | API Value                | Behavior                                              | When to Use                                |
| -------------- | ------------------------ | ----------------------------------------------------- | ------------------------------------------ |
| **Off**        | `OFF`                    | Turn off safety filter completely                     | Not recommended (violates TOS)             |
| **Block none** | `BLOCK_NONE`             | ✅ Show content regardless of probability             | ✅ **Creative storytelling (our setting)** |
| **Block few**  | `BLOCK_ONLY_HIGH`        | Block only high probability unsafe content            | Moderate content filtering                 |
| **Block some** | `BLOCK_MEDIUM_AND_ABOVE` | Block medium or high probability unsafe content       | Default for older models                   |
| **Block most** | `BLOCK_LOW_AND_ABOVE`    | Block low, medium, or high probability unsafe content | Very restrictive                           |

### Probability Levels

Content is rated on **probability of being unsafe** (not severity):

- **HIGH**: Very likely to be unsafe
- **MEDIUM**: Somewhat likely to be unsafe
- **LOW**: Unlikely to be unsafe
- **NEGLIGIBLE**: Not unsafe

**Important**: Google blocks based on **probability**, not **severity**. A sentence like "The robot punched me" might have higher probability than "The robot slashed me up" even though the second is more severe.

## Why BLOCK_NONE for StoryCraft?

### Creative Storytelling Needs

1. **Fantasy Violence**: Battles, combat, warfare (common in fantasy stories)
2. **Dark Themes**: Horror, thriller, dystopian content
3. **Mature Characters**: Adult protagonists in adult situations
4. **Fictional Danger**: Villains, threats, dangerous scenarios
5. **Realistic Dialogue**: Characters may use strong language

### Default Behavior (BLOCK_MEDIUM_AND_ABOVE)

- Blocks too much creative content
- False positives on fantasy combat
- Restricts character development
- Limits storytelling freedom

### BLOCK_NONE Behavior

- ✅ Allows creative freedom for storytelling
- ✅ Permits fantasy violence and combat
- ✅ Enables mature themes in fiction
- ✅ Still respects Google's core safety (child safety always protected)
- ⚠️ Application must handle any inappropriate content responsibly

## Model-Specific Defaults

| Model                     | Default Threshold      | Notes                        |
| ------------------------- | ---------------------- | ---------------------------- |
| **gemini-2.0-flash**      | BLOCK_NONE             | Newer model, most permissive |
| **gemini-2.0-flash-lite** | BLOCK_NONE             | Lightweight version          |
| **gemini-2.5-flash**      | BLOCK_NONE             | Latest model                 |
| **Older models**          | BLOCK_MEDIUM_AND_ABOVE | More restrictive             |

**Our Choice**: We explicitly set `BLOCK_NONE` even though it's the default for gemini-2.0-flash to ensure consistency if we switch models.

## Safety Filtering Flow

```
User Prompt
     ↓
[Safety Check: Prompt]
     ↓
  Blocked? → Return promptFeedback.blockReason
     ↓ No
[Model Generation]
     ↓
[Safety Check: Response]
     ↓
  Blocked? → Return candidate.finishReason = SAFETY
     ↓ No
Return Generated Content
```

## Handling Safety Blocks

### 1. Prompt Blocked (Before Generation)

```python
if response.prompt_feedback.block_reason:
    # Prompt was blocked
    # Check: response.prompt_feedback.safety_ratings
```

**Our Implementation**: We check if `response.candidates` is empty and provide feedback.

### 2. Response Blocked (After Generation)

```python
if candidate.finish_reason == 2:  # SAFETY
    # Response was blocked
    # Check: candidate.safety_ratings
```

**Our Implementation**: We parse `finish_reason` and extract triggered safety categories with their probability levels.

### 3. Error Messages

**Before** (cryptic):

```
Invalid operation: The `response.text` quick accessor requires
the response to contain a valid `Part`, but none were returned.
```

**After** (clear):

```
Content was blocked by Google's safety filters.
Triggered categories: Dangerous Content: MEDIUM.
Try rephrasing your prompt or use a different provider (Groq or Anthropic).
```

## Alternative: If Content Still Gets Blocked

### Option 1: Switch to Groq (Recommended)

- **Default provider**: Groq is now the default in StoryCraft
- **Less restrictive**: Groq has fewer safety restrictions
- **Faster**: 2x faster rate limits (30 RPM vs 10-15 RPM)
- **Free**: Generous free tier

### Option 2: Rephrase Prompt

- Remove specific words that might trigger filters
- Use euphemisms for violence/conflict
- Focus on story structure over specific content
- Example: "battle" → "confrontation", "kill" → "defeat"

### Option 3: Use Anthropic Claude

- **Balanced**: Good safety settings for creative content
- **High quality**: Excellent for long-form narrative
- **Paid**: Requires API key with credits

## Terms of Service Compliance

Per [Gemini API Terms](https://ai.google.dev/gemini-api/terms#use-restrictions):

**Allowed with BLOCK_NONE**:

- ✅ Creative fiction and storytelling
- ✅ Fantasy violence and combat
- ✅ Mature themes in appropriate context
- ✅ Character development with flaws
- ✅ Realistic dialogue

**Still Prohibited** (Core Safety):

- ❌ Child safety endangerment (always blocked)
- ❌ Generating actual misinformation
- ❌ Creating real-world harm guides
- ❌ Impersonating real people
- ❌ Bypassing safety for malicious intent

**Note**: Applications using less restrictive settings may be subject to review by Google.

## Testing Recommendations

### 1. Safety Benchmarking

Test with prompts that represent your content:

```python
test_prompts = [
    "Create a fantasy warrior character",
    "Generate a battle scene with orcs",
    "Write a dark thriller opening",
    "Create a villain with dangerous plans",
]
```

### 2. Adversarial Testing

Try edge cases that might trigger filters:

```python
edge_cases = [
    "Character with a troubled violent past",
    "Scene involving weapons and combat",
    "Dark fantasy with horror elements",
]
```

### 3. Monitor Failures

Log when content gets blocked:

```python
if candidate.finish_reason == 2:
    logger.warning(f"Content blocked: {prompt[:100]}")
    logger.warning(f"Safety ratings: {candidate.safety_ratings}")
```

## Troubleshooting

### Problem: Content Still Blocked with BLOCK_NONE

**Possible Causes**:

1. **Core safety violation**: Content endangers child safety (always blocked)
2. **Prompt too explicit**: Even BLOCK_NONE has limits
3. **Recitation**: Content too similar to copyrighted material (finish_reason=3)
4. **Rate limiting**: Not a safety issue, but can look similar

**Solutions**:

1. Check `candidate.finish_reason`:
   - 2 = SAFETY (use Groq instead)
   - 3 = RECITATION (rephrase prompt)
   - 5 = MAX_TOKENS (increase token limit)
2. Review `candidate.safety_ratings` for specific triggers
3. Try Groq or Anthropic as alternatives
4. Rephrase prompt with less explicit language

### Problem: False Positives

**Example**: "The hero defeats the villain" gets blocked as dangerous content.

**Explanation**: Google's probability-based blocking can flag fantasy violence even in heroic contexts.

**Solutions**:

1. **Use Groq** (default): Better for fantasy/adventure content
2. Rephrase: "The hero overcomes the antagonist"
3. Add context: "In this fantasy story, the hero defeats the villain"
4. Use story structure: Focus on plot beats, not specific actions

## Comparison: Groq vs Google Safety

| Feature                   | Google Gemini                           | Groq                  |
| ------------------------- | --------------------------------------- | --------------------- |
| **Safety Filters**        | Very restrictive (even with BLOCK_NONE) | More permissive       |
| **Fantasy Violence**      | Often blocked                           | Usually allowed       |
| **Mature Themes**         | Frequently blocked                      | Generally allowed     |
| **Creative Freedom**      | ⚠️ Moderate                             | ✅ High               |
| **Best For**              | Safe, family-friendly content           | Creative storytelling |
| **Default in StoryCraft** | ❌ Secondary option                     | ✅ Primary provider   |

## Implementation Details

### Current Code (backend/routers/llm.py)

```python
@staticmethod
async def generate_google(prompt: str, model: str = "gemini-2.0-flash", ...):
    # Configure minimally restrictive safety settings
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    model_instance = genai.GenerativeModel(model, safety_settings=safety_settings)
    response = model_instance.generate_content(prompt, ...)

    # Check if blocked
    if not response.candidates:
        raise HTTPException(status_code=400, detail="Content blocked...")

    # Check finish_reason
    if candidate.finish_reason == 2:  # SAFETY
        # Extract safety ratings and provide detailed error
        safety_info = [...]
        raise HTTPException(status_code=400, detail=f"Content blocked: {safety_info}")
```

### Error Response to User

```json
{
  "detail": "Content was blocked by Google's safety filters. Triggered categories: Dangerous Content: MEDIUM. Try rephrasing your prompt or use a different provider (Groq or Anthropic)."
}
```

## Monitoring & Logging

### Log Safety Blocks

```python
if candidate.finish_reason == 2:
    logger.warning(f"Google blocked content for prompt: {prompt[:50]}...")
    logger.warning(f"Safety ratings: {candidate.safety_ratings}")
```

### Track Block Rate

```python
# In your analytics/monitoring
total_requests = 100
blocked_requests = 5
block_rate = 5%  # May indicate need to switch to Groq
```

### User Feedback

```javascript
// Frontend: Show helpful message
if (error.response?.data?.detail?.includes("safety filters")) {
  setError("Google blocked this content. Try Groq instead!");
  // Auto-switch to Groq
  setProvider("groq");
}
```

## Recommendations

### For StoryCraft Users

1. **Default to Groq** ✅
   - Already set as default provider
   - Better for creative storytelling
   - Fewer safety false positives

2. **Google as Fallback**
   - Use for factual, informational content
   - Better for non-fiction summaries
   - More accurate for real-world knowledge

3. **Anthropic for Premium**
   - Best quality long-form content
   - Great for complex narratives
   - Balanced safety settings

### For Developers

1. **Set BLOCK_NONE** for creative apps
2. **Implement detailed error handling** (done ✅)
3. **Provide provider alternatives** (done ✅)
4. **Monitor block rates** via logging
5. **Test with diverse prompts** regularly

## Future Improvements

1. **Automatic Provider Switching**
   - Detect Google safety block
   - Auto-retry with Groq
   - Seamless user experience

2. **Prompt Sanitization**
   - Detect problematic words
   - Suggest rephrasing
   - Show examples of safe alternatives

3. **Safety Analytics Dashboard**
   - Track block rates per provider
   - Identify common trigger words
   - Optimize prompt templates

4. **User Preference**
   - Let users choose safety level
   - "Family-friendly" vs "Mature themes"
   - Adjust provider accordingly

## Conclusion

- ✅ **Current Setting**: BLOCK_NONE for maximum creative freedom
- ✅ **Error Handling**: Clear, actionable user messages
- ✅ **Provider Fallback**: Groq as default, Google as option
- ✅ **TOS Compliant**: Core safety still enforced
- ⚠️ **Monitoring Needed**: Track block rates and adjust if needed

**Bottom Line**: Use Groq for creative storytelling. Use Google for factual content. Both are now properly configured with optimal safety settings.
