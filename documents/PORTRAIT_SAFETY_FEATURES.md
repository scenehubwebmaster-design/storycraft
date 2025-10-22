# Portrait Generation Safety Features

## Overview

Enhanced OpenAI DALL-E portrait generation with content safety filtering and intelligent fallback mechanisms to handle OpenAI's strict content policies.

## Problem Solved

OpenAI DALL-E has strict content safety policies that can reject character descriptions containing:

- Violence or weapons
- Sensitive content
- Certain character archetypes
- Complex personality descriptions

**Error Example:**

```
Error code: 400 - Your request was rejected as a result of our safety system.
```

## Solution Implemented

### 1. Safe Appearance Extraction (`extract_safe_appearance`)

Intelligently extracts only physical appearance details from character descriptions.

**Features:**

- Searches for appearance sections in character text
- Filters for safe physical descriptors only
- Removes potentially problematic content
- Keeps only sentences with appearance keywords

**Safe Keywords:**

- Physical: hair, eyes, skin, face, features, complexion, build
- Clothing: wearing, dressed, clothing, attire, garment, armor
- Age: young, middle-aged, elderly, adult, years old

**Filtered Out:**

- Violence-related: weapon, blood, gore, death, kill, murder
- Inappropriate: sexual, nude, naked
- Other sensitive content

### 2. Enhanced Prompt Building (`build_styled_prompt`)

Creates safe, professional prompts for image generation.

**Changes:**

- Uses `extract_safe_appearance()` to filter content
- Adds professional framing: "A portrait of a character: [description]"
- Includes style presets safely
- Logs prompts for debugging

### 3. Automatic Fallback System

If content policy violation occurs, automatically retries with ultra-safe prompt.

**Fallback Process:**

1. Detects content policy violation error
2. Generates generic safe prompt: "A professional portrait photograph of a person, [style]"
3. Retries generation with safe prompt
4. Returns image with note about modification
5. If fallback also fails, provides helpful error message

**Helpful Error Messages:**

```
Content policy violation. The character description contains content
that doesn't meet OpenAI's safety guidelines. Please try:
1) Using Google Imagen instead
2) Simplifying the character description
3) Focusing only on visual appearance details
```

## Default Model Change

**Previous Default:** `gpt-4.1-mini` (GPT Image)

- Requires organization verification
- Takes up to 15 minutes after verification
- Error: 403 - Organization must be verified

**New Default:** `dall-e-3`

- Available immediately for verified accounts
- High quality image generation
- More widely accessible

**UI Updates:**

- DALL-E 3 shown as "DALL-E 3 (Recommended)"
- GPT Image labeled "GPT Image (Requires Verification)"
- Model order: DALL-E 3 > DALL-E 2 > GPT Image

## Code Changes

### Backend: `openai_image_client.py`

#### New Function: `extract_safe_appearance()`

```python
def extract_safe_appearance(text: str) -> str:
    """
    Extract only safe, physical appearance details.
    Removes potentially sensitive content.
    """
    # Finds appearance section
    # Filters for safe keywords
    # Removes sensitive words
    # Returns sanitized description
```

#### Enhanced: `build_styled_prompt()`

```python
def build_styled_prompt(character_name, appearance, style_preset):
    """Build safe prompt with filtered appearance"""
    safe_appearance = extract_safe_appearance(appearance)
    prompt = f"A portrait of a character: {safe_appearance}. {style_suffix}"
    return prompt
```

#### Enhanced: `generate_character_portrait_openai()`

```python
try:
    # Generate with original prompt
    response = client.images.generate(...)
except Exception as e:
    if "safety system" in str(e) or "content_policy_violation" in str(e):
        # Automatic fallback
        safe_prompt = "A professional portrait photograph of a person..."
        response = client.images.generate(prompt=safe_prompt, ...)
        return with note about modification
```

### Frontend: `character.jsx`

#### Default Model Changed

```javascript
// Before
const [imageModel, setImageModel] = useState("gpt-4.1-mini");

// After
const [imageModel, setImageModel] = useState("dall-e-3");
```

#### Provider Change Handler

```javascript
if (newProvider === "openai") {
  setImageModel("dall-e-3"); // DALL-E 3 as default
}
```

#### Model Menu Order

```javascript
<MenuItem value="dall-e-3">DALL-E 3 (Recommended)</MenuItem>
<MenuItem value="dall-e-2">DALL-E 2</MenuItem>
<MenuItem value="gpt-4.1-mini">GPT Image (Requires Verification)</MenuItem>
```

## Usage

### For Users

1. **Default Experience** - Just click "Generate Portrait"
   - Uses DALL-E 3 by default
   - Safe prompts automatically generated
   - Fallback handling is transparent

2. **If Content Policy Error Occurs:**
   - System automatically retries with safer prompt
   - If successful, you'll see: "(Note: Original prompt was modified for safety)"
   - If still fails, clear error message with alternatives

3. **Alternative Providers:**
   - Switch to Google Imagen (more permissive policies)
   - Simplify character description before generating
   - Focus on visual details only

### For Developers

**Testing Content Filtering:**

```python
from openai_image_client import extract_safe_appearance

# Test with problematic content
text = """
**Appearance:** A warrior with battle scars, wielding a sword.
Blood-stained armor from countless battles.
"""

safe = extract_safe_appearance(text)
# Result: Filters out "blood-stained", "battles", "wielding", "sword"
# Keeps: "A warrior with battle scars", "armor"
```

**Logging:**

```python
# Enable detailed logging to see filtering in action
import logging
logging.basicConfig(level=logging.INFO)

# Logs will show:
# "Built safe prompt: A portrait of a character: [filtered description]..."
# "Content policy violation detected. Trying with generic safe prompt..."
# "Successfully generated portrait with safe fallback prompt"
```

## Content Policy Guidelines

### ✅ Safe Content

- Physical appearance (hair, eyes, skin, build)
- Clothing and attire descriptions
- Age and general appearance
- Facial features and expressions
- Professional/occupational descriptions
- Fantasy elements (elf, dwarf, mage)

### ⚠️ Filtered Content

- Weapons and combat equipment
- Violence or injury descriptions
- Blood, gore, or battle damage
- Overly aggressive descriptions
- Inappropriate or suggestive content
- Real public figures

### 💡 Best Practices

1. **Focus on Visual Details:**

   ```
   Good: "A tall woman with silver hair and green eyes, wearing elegant robes"
   Avoid: "A deadly assassin with blood-stained daggers"
   ```

2. **Use Professional Language:**

   ```
   Good: "A warrior in ceremonial armor"
   Avoid: "A violent fighter covered in battle scars"
   ```

3. **Emphasize Artistic Style:**
   ```
   Good: "Fantasy art style, dramatic lighting"
   Avoid: "Dark and violent scene"
   ```

## Error Handling

### Error Types

1. **Content Policy Violation (400)**
   - Automatic fallback to safe prompt
   - User-friendly error message
   - Suggestions for alternatives

2. **Organization Not Verified (403)**
   - Clear message about verification
   - Link to verification page
   - Recommendation to use DALL-E instead

3. **Rate Limits (429)**
   - Standard error message
   - Suggestion to wait and retry

## Testing

### Test Cases

1. **Basic Character (Should Pass):**

   ```
   Lyra: A young elf with silver hair and emerald eyes, wearing elegant robes
   ```

2. **Problematic Content (Triggers Fallback):**

   ```
   Warrior: Covered in blood, wielding deadly weapons, violent demeanor
   ```

3. **Fantasy Content (Should Pass):**
   ```
   Wizard: An elderly mage with a long white beard, wearing star-covered robes
   ```

### Manual Testing Steps

1. Generate character with standard description
2. Click "Generate Portrait" with DALL-E 3
3. Verify image generates successfully
4. Try with complex/problematic character
5. Verify fallback system activates if needed
6. Check error messages are helpful

## Future Enhancements

### Potential Improvements

1. **Pre-Generation Preview:**
   - Show filtered prompt before generating
   - Allow user to edit before submission

2. **Smart Content Rewriting:**
   - Use LLM to rewrite problematic content
   - Example: "blood-stained armor" → "weathered armor"

3. **Multi-Provider Fallback:**
   - If OpenAI fails, automatically try Google Imagen
   - Seamless provider switching

4. **Content Analysis:**
   - Show safety score before generation
   - Highlight potentially problematic phrases
   - Suggest safer alternatives

5. **User Preferences:**
   - Save preferred provider
   - Remember safety filtering preferences
   - Custom safety thresholds

## Conclusion

The enhanced safety system provides:

- ✅ Robust content filtering
- ✅ Automatic fallback mechanisms
- ✅ User-friendly error handling
- ✅ Clear guidance for users
- ✅ Logging for debugging
- ✅ Compatible with all providers

Users can now generate character portraits with confidence, knowing the system will handle content policy issues gracefully.
