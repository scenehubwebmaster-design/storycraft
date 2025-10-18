# Stable Diffusion Integration - Phase 1

## Overview
Initial integration of local Stable Diffusion server for character portrait generation.

## Components Created

### Backend
- **stablediffusion_client.py**: Client for Gradio-based SD WebUI
  - `StableDiffusionClient` class with connection testing
  - `generate_portrait_with_sd()` function for styled portrait generation
  - Quality presets: draft (fast), standard, high
  - Style presets: photorealistic, fantasy, anime, oil_painting, digital_art

- **test_stablediffusion.py**: Test suite for SD integration
  - Connection testing
  - Portrait generation testing

### Frontend (CreateCharacter.jsx)
- Added "Stable Diffusion (Local)" as provider option
- Added SD model selector ("Local SD Model")
- Added SD quality selector (Draft/Standard/High)
- Available in both regular character and D&D character edit views

### Integration Points
- Updated `openai_image_client.py`:
  - Added `stablediffusion` provider to `generate_portrait_with_provider()`
  - Maps style presets to SD-compatible styles
  - Extracts safe appearance descriptions

## Configuration
Add to `.env`:
```
STABLEDIFFUSION_API_URL=http://192.168.250.14:7861
```

## Current Status
✅ Backend client created
✅ Frontend UI updated with SD options
✅ Integration into portrait generation pipeline
⚠️  **API endpoint mapping needs refinement** - Current Gradio interface differs from standard SD WebUI API

## Next Steps
1. **Identify correct Gradio endpoint** for text-to-image generation
   - Current endpoint #2 just echoes inputs, doesn't generate
   - Need to find the actual generation endpoint in the Gradio interface
   
2. **Test actual image generation** once endpoint is identified

3. **Add model selection** from available SD models:
   - chilloutmix_NiPrunedFp32Fix
   - dreamshaper_8
   - epicphotogasm_ultimateFidelity
   - goddessOfRealism_gorV6ilxlVAE
   - juggernautXL_ragnarokBy
   - kreaUltimateRealism_v10
   - realismByStableYogi variants
   - And more...

4. **Optional enhancements**:
   - Add negative prompt customization
   - Add CFG scale control
   - Add aspect ratio selection
   - Show generation progress
   - Cache generated images locally

## Technical Notes
- Server running at `http://192.168.250.14:7861`
- Uses Gradio API format (not standard SD WebUI `/sdapi/v1/` endpoints)
- Connection test successful ✅
- Need to map Gradio interface to actual generation functions

## Usage Example (when complete)
```python
from stablediffusion_client import generate_portrait_with_sd

image_base64, prompt = generate_portrait_with_sd(
    character_description="a young elf warrior with blonde hair and blue eyes",
    style="fantasy",
    quality="standard"
)
```

Frontend usage:
1. Select "Stable Diffusion (Local)" as provider
2. Choose "Local SD Model"
3. Pick art style (Realistic, Fantasy Art, Anime, etc.)
4. Select quality (Draft/Standard/High)
5. Click "Generate Portrait"

## Files Modified
- `backend/stablediffusion_client.py` (new)
- `backend/openai_image_client.py` (updated)
- `backend/test_stablediffusion.py` (new)
- `frontend/src/pages/CreateCharacter.jsx` (updated - 2 locations for regular and D&D)

## Testing
```bash
cd backend
python test_stablediffusion.py
```

Current test status:
- ✅ Connection test passes
- ⚠️  Generation test needs correct endpoint mapping
