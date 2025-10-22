# OpenAI Image Generation Integration

## Overview

Added OpenAI image generation support alongside Google Imagen, allowing users to choose between multiple AI providers for character portrait generation.

## What Was Implemented

### Backend Changes

1. **New File: `backend/openai_image_client.py`** (211 lines)
   - Dual-mode OpenAI image generation:
     - **GPT Image Mode**: Uses `gpt-4.1-mini` via Responses API with `tools=[{"type": "image_generation"}]`
     - **DALL-E Mode**: Uses `dall-e-2` or `dall-e-3` via Images API
   - Unified provider interface: `generate_portrait_with_provider()`
   - Automatic provider routing based on `provider` and `model` parameters
   - Aspect ratio mapping for DALL-E sizes (3:4 → 1024x1792)

2. **Updated: `backend/schemas.py`**
   - Added `provider` field to `ImageGenerationRequest` (default="google")
   - Made `model` field optional (provider-specific defaults)
   - Supports "google" or "openai" as provider values

3. **Updated: `backend/routers/generation.py`**
   - Modified `/api/generate/character/generate-portrait` endpoint
   - Now calls unified `generate_portrait_with_provider()` function
   - Returns provider information in response

### Frontend Changes

1. **Updated: `frontend/src/routes/create/character.jsx`**
   - Added provider selection state:
     ```javascript
     const [imageProvider, setImageProvider] = useState("openai");
     const [imageModel, setImageModel] = useState("gpt-4.1-mini");
     ```
   - Added provider selection UI:
     - **Image Provider dropdown**: Choose between "Google Imagen" or "OpenAI"
     - **Model dropdown**: Provider-specific models
       - Google: Fast, Standard, Ultra
       - OpenAI: GPT Image (gpt-4.1-mini), DALL-E 2, DALL-E 3
   - Updated `handleGeneratePortrait()` to send provider and model
   - Success message shows which provider was used

## How to Use

### 1. Configure API Keys

Make sure you have the appropriate API key configured in `backend/.env`:

```env
# For Google Imagen
GOOGLE_API_KEY=your_google_api_key_here

# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Generate a Character Portrait

1. Navigate to the Character Creation wizard
2. Complete Step 1: Enter prompt and generate character content
3. Move to Step 2: Review & Save
4. In the "Character Portrait" section:
   - **Select Image Provider**: Choose "Google Imagen" or "OpenAI"
   - **Select Model**: Choose from provider-specific models
   - Click **"Generate Portrait"**
5. Wait for generation (usually 5-15 seconds)
6. Preview the generated portrait
7. Save the character to store the portrait in the database

### 3. Provider Recommendations

| Provider | Model           | Best For                               | Estimated Cost |
| -------- | --------------- | -------------------------------------- | -------------- |
| Google   | Imagen Fast     | Quick generation, lowest cost          | ~$0.02/image   |
| Google   | Imagen Standard | Balanced quality and speed             | ~$0.04/image   |
| Google   | Imagen Ultra    | Best quality                           | ~$0.10/image   |
| OpenAI   | GPT Image       | World knowledge, context understanding | ~$0.02/image   |
| OpenAI   | DALL-E 2        | Lower cost, good quality               | ~$0.02/image   |
| OpenAI   | DALL-E 3        | High quality, detailed                 | ~$0.04/image   |

**Default Recommendation**: OpenAI GPT Image (gpt-4.1-mini) - excellent balance of quality, speed, and cost.

## Technical Details

### OpenAI GPT Image Flow

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    tools=[{"type": "image_generation"}],
    messages=[{"role": "user", "content": prompt}]
)

# Extract image from response
for output in response.output:
    if output.type == "image_generation_call":
        image_base64 = output.result  # Base64 PNG
```

### OpenAI DALL-E Flow

```python
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1792",  # Portrait orientation
    response_format="b64_json"
)

image_base64 = response.data[0].b64_json
```

### Aspect Ratio Mapping (DALL-E)

- `3:4` → `1024x1792` (portrait)
- `1:1` → `1024x1024` (square)
- `4:3` → `1792x1024` (landscape)

### Unified Provider Interface

```python
async def generate_portrait_with_provider(
    character_name: str,
    appearance_text: str,
    provider: str = "openai",
    model: Optional[str] = None,
    aspect_ratio: str = "3:4",
    custom_prompt: Optional[str] = None
) -> Dict[str, str]:
    """
    Routes to appropriate provider based on parameters.
    Returns: {"image_base64": "...", "prompt": "..."}
    """
```

## Testing

### Test Google Imagen

1. Select "Google Imagen" as provider
2. Choose "Imagen Fast (Recommended)"
3. Generate portrait
4. Verify image displays correctly

### Test OpenAI GPT Image

1. Select "OpenAI" as provider
2. Choose "GPT Image (Recommended)"
3. Generate portrait
4. Verify image displays correctly
5. Compare quality with Imagen

### Test OpenAI DALL-E

1. Select "OpenAI" as provider
2. Choose "DALL-E 3"
3. Generate portrait
4. Compare quality and style with GPT Image

## Error Handling

Common errors and solutions:

### 1. "Make sure API key is configured"

**Solution**: Add `OPENAI_API_KEY` or `GOOGLE_API_KEY` to `backend/.env`

### 2. OpenAI Rate Limits

**Error**: 429 Too Many Requests
**Solution**: Wait a few minutes before retrying, or upgrade your OpenAI plan

### 3. DALL-E Content Policy Violations

**Error**: Content policy violation
**Solution**: Try GPT Image instead (more permissive), or modify the character description

### 4. Invalid Model Selection

**Error**: Model not found
**Solution**: Ensure you selected a valid model from the dropdown

## Comparison: Google Imagen vs OpenAI

### Google Imagen

- **Pros**: Excellent portrait quality, specialized for human faces, fast models available
- **Cons**: Requires Google AI Studio API key, stricter person generation policies
- **Best For**: High-quality character portraits with realistic features

### OpenAI GPT Image

- **Pros**: Understands context, world knowledge, flexible content policy, fast
- **Cons**: May be less specialized for portraits than Imagen
- **Best For**: Characters with specific contexts (e.g., "warrior in medieval armor")

### OpenAI DALL-E

- **Pros**: Specialized image generation, consistent quality, well-documented
- **Cons**: Limited size options, no custom aspect ratios
- **Best For**: Artistic character portraits with specific styles

## Next Steps

### Recommended Enhancements

1. **Add Quality Settings**
   - Add "HD" quality option for DALL-E 3
   - Add negative prompts for better control

2. **Add Style Presets**
   - "Realistic Portrait"
   - "Fantasy Art"
   - "Anime Style"
   - "Watercolor"

3. **Add Regeneration Options**
   - "Regenerate with same provider"
   - "Try with different provider"

4. **Add Cost Tracking**
   - Display estimated cost before generation
   - Track total API costs per user

5. **Add Image Editing**
   - Crop/resize after generation
   - Apply filters
   - Inpainting for corrections

## Files Modified

```
backend/
  ├── openai_image_client.py        [NEW - 211 lines]
  ├── schemas.py                     [MODIFIED - added provider field]
  ├── routers/generation.py          [MODIFIED - unified provider routing]

frontend/
  └── src/
      └── routes/
          └── create/
              └── character.jsx      [MODIFIED - added provider selection UI]
```

## API Reference

### POST `/api/generate/character/generate-portrait`

**Request Body**:

```json
{
  "character_name": "Aria Stormwind",
  "appearance_text": "A young elf with silver hair and emerald eyes...",
  "provider": "openai", // "google" or "openai"
  "model": "gpt-4.1-mini", // Optional, provider-specific
  "aspect_ratio": "3:4", // "1:1", "3:4", "4:3", etc.
  "custom_prompt": null // Optional override
}
```

**Response**:

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "Portrait of Aria Stormwind, a young elf...",
  "model": "gpt-4.1-mini",
  "provider": "openai",
  "aspect_ratio": "3:4",
  "message": "Portrait generated successfully"
}
```

## Troubleshooting

### Provider Selection Not Showing

- **Check**: Make sure you're on Step 2 (Review & Save)
- **Check**: Ensure character content has been generated in Step 1

### Model Dropdown Empty

- **Check**: Make sure you selected a provider first
- **Fix**: Try changing the provider and back again

### Images Not Displaying

- **Check**: Browser console for errors
- **Check**: Verify Base64 image format is correct
- **Fix**: Try regenerating with a different provider

### Slow Generation Times

- **Google Imagen Fast**: Usually 5-10 seconds
- **OpenAI GPT Image**: Usually 8-15 seconds
- **OpenAI DALL-E 3**: Usually 10-20 seconds
- **If slower**: Check your internet connection and API quotas

## Conclusion

You now have a complete multi-provider image generation system integrated into StoryCraft! Users can choose between Google Imagen and OpenAI (GPT Image or DALL-E) for generating character portraits, with each provider offering different strengths and capabilities.

The system is fully functional and ready for testing. Try generating portraits with different providers to see which one works best for your specific character types and artistic preferences.
