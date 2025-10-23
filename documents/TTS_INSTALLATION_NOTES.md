# Kitten TTS Installation Notes# Orpheus TTS Installation Notes

## Current Status: ✅ CPU-Optimized & Lightweight!## Current Status: ⚠️ Not Functional on Windows (CUDA Required)

### Benefits### Issue

Kitten TTS is a state-of-the-art text-to-speech model that runs anywhere:Orpheus TTS requires CUDA-enabled PyTorch but the system has CPU-only PyTorch installed.

- **Ultra-lightweight**: Model size under 25MB**Error:**

- **CPU-optimized**: No GPU or CUDA required!

- **High-quality voices**: Multiple expressive voice options```

- **Fast inference**: Optimized for real-time speech synthesisAssertionError: Torch not compiled with CUDA enabled

- **Works on Windows**: No CUDA dependencies```

**No more CUDA errors!** Kitten TTS works perfectly on CPU-only systems.### Why This Happens

### Installation- Orpheus TTS automatically tries to move models to CUDA device

- Windows installation of PyTorch defaults to CPU-only version

```powershell- The `orpheus_tts` package doesn't support CPU-only operation

# Install Kitten TTS from wheel

pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl### Installation Attempted

# Install soundfile for audio file generation```powershell

pip install soundfilepip install --user orpheus-speech

````



**Verification:****Result:** Package installed successfully, but fails on import due to CUDA requirement.



```python## Options to Enable TTS

import kittentts

print("Kitten TTS imported successfully!")### Option 1: Install CUDA PyTorch (Recommended for GPU users)



from kittentts import KittenTTS**Prerequisites:**

m = KittenTTS("KittenML/kitten-tts-nano-0.2")

print("Kitten TTS model loaded successfully!")- NVIDIA GPU

```- CUDA Toolkit 11.8 or 12.1



### Available Voices**Steps:**



Kitten TTS provides **8 unique voices** (mapped from original Orpheus voice names):```powershell

# Uninstall CPU PyTorch

**Female Voices:**pip uninstall torch torchvision torchaudio

- **tara** (expr-voice-2-f) - Clear, professional narrator

- **leah** (expr-voice-3-f) - Warm, friendly storyteller# Install CUDA 11.8 version

- **jess** (expr-voice-4-f) - Energetic, adventurous tonepip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

- **mia** (expr-voice-5-f) - Mysterious, dramatic flair

# Or CUDA 12.1 version

**Male Voices:**pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

- **leo** (expr-voice-2-m) - Deep, authoritative narrator

- **dan** (expr-voice-3-m) - Calm, classic storyteller# Reinstall orpheus-speech

- **zac** (expr-voice-4-m) - Young, enthusiastic adventurerpip install --user orpheus-speech

- **zoe** (expr-voice-5-m) - Gender-neutral, versatile```



### Quick Test**Verification:**



```python```python

from kittentts import KittenTTSimport torch

import soundfile as sfprint(f"CUDA available: {torch.cuda.is_available()}")

print(f"CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

m = KittenTTS("KittenML/kitten-tts-nano-0.2")

audio = m.generate("This high quality TTS model works without a GPU", voice='expr-voice-2-f')import orpheus_tts

sf.write('output.wav', audio, 24000)print("Orpheus TTS imported successfully!")

print("Audio generated successfully!")```

```

### Option 2: Use Alternative TTS Service

## Migration from Orpheus TTS

Consider these alternatives that work on CPU:

### What Changed

1. **Coqui TTS** (CPU-friendly)

- **Removed**: `orpheus-speech` package (CUDA-dependent)

- **Added**: `kittentts` wheel + `soundfile`   ```powershell

- **Voice mapping**: Same 8 voice names, mapped to Kitten TTS voices   pip install TTS

- **API**: Compatible interface, seamless migration   ```



### Breaking Changes2. **pyttsx3** (Offline, uses system voices)



⚠️ **Emotion tags not supported**: Kitten TTS doesn't support emotion tags like `<laugh>`, `<sigh>`, etc.   ```powershell

- The `add_dm_personality` parameter is ignored   pip install pyttsx3

- Text is generated as-is without emotion markup   ```



### Benefits of Migration3. **gTTS** (Google Text-to-Speech, requires internet)

   ```powershell

✅ **No CUDA requirement** - Works on any CPU   pip install gTTS

✅ **Smaller model** - Under 25MB vs larger Orpheus models   ```

✅ **Same voice quality** - High-quality natural speech

✅ **Same API** - Drop-in replacement, no frontend changes needed### Option 3: Disable TTS Feature

✅ **Faster installation** - No complex CUDA setup required

TTS is optional. The application works without it:

## Current Graceful Degradation

- Backend gracefully handles missing TTS dependency

✅ **Already Implemented:**- Frontend shows clear error: "Voice narration unavailable. Install orpheus-speech on backend."

- All other game features work normally

- Backend catches ImportError on missing `kittentts`

- Returns 500 with clear message when TTS endpoint called## Current Graceful Degradation

- Frontend detects error and shows user-friendly message

- Game continues to function normally without voice narration✅ **Already Implemented:**



## Troubleshooting- Backend catches ImportError on missing `orpheus_tts`

- Returns 500 with clear message when TTS endpoint called

### Import Error: "No module named 'kittentts'"- Frontend detects error and shows user-friendly message

- Game continues to function normally without voice narration

**Solution:**

## Recommendations

```powershell

pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl**For Development:**

pip install soundfile

```- Leave TTS disabled unless you have an NVIDIA GPU

- Focus on core gameplay features first

### Audio Generation Fails- TTS can be added later with proper GPU setup



**Check:****For Production:**

1. Model downloaded correctly (first run downloads from HuggingFace)

2. Sufficient disk space (~25MB for model)- Consider cloud-based TTS services (AWS Polly, Google TTS, Azure Speech)

3. Python version 3.8+ (required for Kitten TTS)- Deploy on GPU-enabled server if using Orpheus TTS

- Or use lighter CPU-based TTS alternatives

### Voice Not Recognized

## Related Files

**Valid voices:** tara, leah, jess, mia, leo, dan, zac, zoe

- Backend automatically maps to Kitten TTS voice IDs- `backend/tts_service.py` - TTS service with graceful import handling

- Default fallback: "tara" (expr-voice-2-f)- `backend/routers/chat.py` - TTS endpoint that catches ImportError

- `frontend/src/components/game/TTSAudioPlayer.jsx` - Frontend error handling

## Recommendations- Commits: cc85a20 (backend), f7e3d4f (frontend)



**For Development:**## Testing TTS Endpoint



- ✅ TTS now works on any system (CPU or GPU)Even without working TTS, you can verify error handling:

- ✅ Lightweight model loads quickly

- ✅ No GPU setup required```bash

- ✅ Focus on core gameplay features with working TTS# Should return 500 with clear error message

curl http://localhost:8000/api/chat/sessions/1/messages/1/tts?voice=tara

**For Production:**```



- Consider caching generated audio for repeated phrasesExpected response:

- Monitor model download on first run (downloads from HuggingFace)

- Optionally pre-load model on backend startup for faster first request```json

{

## Related Files  "detail": "TTS service not available. Install orpheus-speech: pip install orpheus-speech"

}

- `backend/tts_service.py` - TTS service with Kitten TTS integration```

- `backend/routers/chat.py` - TTS endpoint

- `frontend/src/components/game/TTSAudioPlayer.jsx` - Frontend audio playerFrontend should show: "Voice narration unavailable. Install orpheus-speech on backend."

- `backend/requirements.txt` - Python dependencies

## Testing TTS Endpoint

Test the TTS endpoint after installation:

```bash
# Should return WAV audio file
curl http://localhost:8000/api/chat/sessions/1/messages/1/tts?voice=tara --output test.wav
```

Frontend automatically handles:
- Voice selection dropdown
- Audio playback
- Error messages if TTS unavailable

## References

- Kitten TTS GitHub: https://github.com/KittenML/KittenTTS
- Model: KittenML/kitten-tts-nano-0.2
- License: Apache 2.0
- Model size: <25MB
- Sample rate: 24000 Hz
- Format: WAV (16-bit PCM)

---

**Migration Complete** ✅

- No CUDA required
- CPU-optimized
- Same 8 voices
- Drop-in replacement
- Lightweight and fast
````
