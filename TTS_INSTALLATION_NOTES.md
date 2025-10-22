# Orpheus TTS Installation Notes

## Current Status: ⚠️ Not Functional on Windows (CUDA Required)

### Issue
Orpheus TTS requires CUDA-enabled PyTorch but the system has CPU-only PyTorch installed.

**Error:**
```
AssertionError: Torch not compiled with CUDA enabled
```

### Why This Happens
- Orpheus TTS automatically tries to move models to CUDA device
- Windows installation of PyTorch defaults to CPU-only version
- The `orpheus_tts` package doesn't support CPU-only operation

### Installation Attempted
```powershell
pip install --user orpheus-speech
```

**Result:** Package installed successfully, but fails on import due to CUDA requirement.

## Options to Enable TTS

### Option 1: Install CUDA PyTorch (Recommended for GPU users)

**Prerequisites:**
- NVIDIA GPU
- CUDA Toolkit 11.8 or 12.1

**Steps:**
```powershell
# Uninstall CPU PyTorch
pip uninstall torch torchvision torchaudio

# Install CUDA 11.8 version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or CUDA 12.1 version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Reinstall orpheus-speech
pip install --user orpheus-speech
```

**Verification:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

import orpheus_tts
print("Orpheus TTS imported successfully!")
```

### Option 2: Use Alternative TTS Service

Consider these alternatives that work on CPU:

1. **Coqui TTS** (CPU-friendly)
   ```powershell
   pip install TTS
   ```

2. **pyttsx3** (Offline, uses system voices)
   ```powershell
   pip install pyttsx3
   ```

3. **gTTS** (Google Text-to-Speech, requires internet)
   ```powershell
   pip install gTTS
   ```

### Option 3: Disable TTS Feature

TTS is optional. The application works without it:
- Backend gracefully handles missing TTS dependency
- Frontend shows clear error: "Voice narration unavailable. Install orpheus-speech on backend."
- All other game features work normally

## Current Graceful Degradation

✅ **Already Implemented:**
- Backend catches ImportError on missing `orpheus_tts`
- Returns 500 with clear message when TTS endpoint called
- Frontend detects error and shows user-friendly message
- Game continues to function normally without voice narration

## Recommendations

**For Development:**
- Leave TTS disabled unless you have an NVIDIA GPU
- Focus on core gameplay features first
- TTS can be added later with proper GPU setup

**For Production:**
- Consider cloud-based TTS services (AWS Polly, Google TTS, Azure Speech)
- Deploy on GPU-enabled server if using Orpheus TTS
- Or use lighter CPU-based TTS alternatives

## Related Files

- `backend/tts_service.py` - TTS service with graceful import handling
- `backend/routers/chat.py` - TTS endpoint that catches ImportError
- `frontend/src/components/game/TTSAudioPlayer.jsx` - Frontend error handling
- Commits: cc85a20 (backend), f7e3d4f (frontend)

## Testing TTS Endpoint

Even without working TTS, you can verify error handling:

```bash
# Should return 500 with clear error message
curl http://localhost:8000/api/chat/sessions/1/messages/1/tts?voice=tara
```

Expected response:
```json
{
  "detail": "TTS service not available. Install orpheus-speech: pip install orpheus-speech"
}
```

Frontend should show: "Voice narration unavailable. Install orpheus-speech on backend."
