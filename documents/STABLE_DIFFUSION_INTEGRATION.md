# Stable Diffusion Integration

## Status: ✅ WORKING

Successfully integrated local Stable Diffusion server (Gradio-based WebUI) for character portrait generation.

## Overview

Character portraits can now be generated using:

- **Google Imagen** (cloud)
- **OpenAI DALL-E** (cloud)
- **Stable Diffusion** (local server) ← NEW

## Configuration

Add to `.env` file:

```env
STABLEDIFFUSION_API_URL=http://192.168.250.14:7861
```

## Server Details

- **Type**: Gradio-based Stable Diffusion WebUI
- **API Format**: `/api/predict` with `fn_index` parameter
- **txt2img Endpoint**: fn_index 124 (71 parameters)
- **Available Models**: 16+ models including:
  - ChilloutMix
  - DreamShaper 8
  - EpicPhotoGasm
  - Juggernaut XL
  - And more...

## Implementation

### Backend

**stablediffusion_client.py**:

- `StableDiffusionClient` class for Gradio API communication
- `generate_image()` - Uses endpoint 124 with full 71-parameter array
- `generate_portrait_with_sd()` - Helper function with quality/style presets
- Fetches generated images from server using `/file=` endpoint

**openai_image_client.py**:

- Added `stablediffusion` provider to `generate_portrait_with_provider()`
- Maps style presets to SD-compatible prompts
- Uses `extract_safe_appearance()` for character description

### Frontend

**CreateCharacter.jsx** (2 locations):

- Added "Stable Diffusion (Local)" to provider selector
- Shows "Local SD Model" when SD is selected
- Quality selector: Draft (Fast), Standard, High Quality
- Reuses existing style selector

### Quality Presets

- **Draft**: 20 steps, 512x512 (fast prototyping)
- **Standard**: 30 steps, 768x768 (balanced)
- **High**: 50 steps, 1024x1024 (best quality)

### Style Presets

- Photorealistic
- Fantasy Art
- Anime
- Oil Painting
- Digital Art
- Watercolor
- Comic Book
- Noir

## Technical Notes

### Gradio API Structure

Endpoint 124 requires 71 parameters in specific order:

```python
data = [
    {},              # 0. parameter_47 (Label)
    prompt,          # 1. Prompt
    negative_prompt, # 2. Negative prompt
    [],              # 3. Styles (List[str])
    1,               # 4. Batch count
    1,               # 5. Batch size
    7.0,             # 6. CFG Scale
    height,          # 7. Height
    width,           # 8. Width
    # ... 62 more parameters with proper defaults
]
```

### Response Format

```json
{
  "data": [
    [{ "name": "path/to/image.png", "data": null, "is_file": true }],
    "{\"prompt\": \"...\", \"seed\": 123, ...}",
    "<p>Generation info HTML</p>",
    "<p>Performance stats</p>"
  ]
}
```

Images are saved on server and fetched via `/file=<path>` endpoint.

## Testing

```bash
cd backend
python test_stablediffusion.py
```

Expected output:

```
✅ Successfully connected to Stable Diffusion server
✅ Portrait generated successfully!
   Image size: ~500KB
   Saved to test_portrait.png
```

## Usage

1. Start backend server
2. In character creation/editing:
   - Select "Stable Diffusion (Local)" as provider
   - Choose quality level
   - Select art style
   - Click "Generate Portrait"
3. Image generates in ~2-30 seconds depending on quality
4. Portrait displays and saves to database

## Benefits

✅ No cloud API costs
✅ No rate limiting (local server)
✅ Full control over models and settings
✅ Privacy (all processing local)
✅ High-quality realistic portraits
✅ Supports all 16+ installed models

## Known Issues

- ⚠️ Requires SD server to be running
- ⚠️ First generation may be slower (model loading)
- ⚠️ High quality settings can take 20-30 seconds

## Files Modified/Created

- `backend/stablediffusion_client.py` (new)
- `backend/openai_image_client.py` (updated)
- `backend/test_stablediffusion.py` (new)
- `frontend/src/pages/CreateCharacter.jsx` (updated - 2 locations)

## Next Steps

- [ ] Add model selector (currently uses server default)
- [ ] Add advanced settings (sampler, CFG scale)
- [ ] Implement img2img for portrait refinement
- [ ] Add LoRA support
- [ ] Batch generation support
