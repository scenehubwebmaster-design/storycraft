# OpenAI TTS and Whisper Integration

StoryCraft now supports **OpenAI's Text-to-Speech (TTS)** and **Whisper speech-to-text** APIs for high-quality voice narration and transcription.

## 🎤 Features

### Text-to-Speech (TTS)

- **6 High-Quality Voices:** alloy, echo, fable, onyx, nova, shimmer
- **Multiple Audio Formats:** MP3, Opus, AAC, FLAC, WAV, PCM
- **Quality Levels:** Standard (faster) or HD (higher quality)
- **Speed Control:** 0.25x to 4.0x playback speed
- **Streaming Support:** Real-time audio streaming

### Speech-to-Text (Whisper)

- **Multi-language Support:** Automatic language detection or specify language
- **High Accuracy:** OpenAI's Whisper model
- **Multiple Formats:** FLAC, M4A, MP3, MP4, MPEG, MPGA, OGA, OGG, WAV, WEBM

## 📋 Prerequisites

1. **OpenAI API Key**

   - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Set environment variable: `OPENAI_API_KEY=your_api_key_here`

2. **Python Package**
   ```bash
   pip install openai
   ```

## 🚀 API Endpoints

### Get Service Status

```http
GET /api/audio/status
```

Response:

```json
{
  "available": true,
  "service": "openai",
  "api_key_configured": true,
  "voices_count": 6,
  "models": ["standard", "hd"],
  "formats": ["mp3", "opus", "aac", "flac", "wav", "pcm"]
}
```

### List Available Voices

```http
GET /api/audio/voices
```

Response:

```json
{
  "voices": [
    {
      "id": "alloy",
      "name": "Alloy",
      "description": "Neutral and balanced, suitable for general narration",
      "gender": "neutral",
      "accent": "american"
    },
    {
      "id": "echo",
      "name": "Echo",
      "description": "Male voice, clear and articulate",
      "gender": "male",
      "accent": "american"
    },
    ...
  ],
  "default_voice": "alloy"
}
```

### Generate Speech (TTS)

```http
POST /api/audio/speak
Content-Type: application/json

{
  "text": "Greetings, adventurers! Welcome to the world of StoryCraft.",
  "voice": "alloy",
  "model": "standard",
  "speed": 1.0,
  "format": "mp3",
  "streaming": false
}
```

Response: Audio file (MP3/WAV/etc.)

### Transcribe Audio (Whisper)

```http
POST /api/audio/transcribe
Content-Type: multipart/form-data

file: (audio file)
language: "en" (optional)
prompt: "optional prompt to guide transcription" (optional)
temperature: 0.0 (optional, 0-1)
```

Response:

```json
{
  "text": "The transcribed text from the audio file.",
  "duration": 1.23
}
```

### Test Voice

```http
POST /api/audio/test-voice
Content-Type: application/x-www-form-urlencoded

voice=alloy
model=standard
speed=1.0
```

Response: Audio file with sample text

## 🎮 Voice Options

| Voice       | Gender  | Accent   | Description                                 |
| ----------- | ------- | -------- | ------------------------------------------- |
| **alloy**   | Neutral | American | Balanced, suitable for general narration    |
| **echo**    | Male    | American | Clear and articulate, good for serious tone |
| **fable**   | Neutral | British  | Expressive storytelling, dramatic flair     |
| **onyx**    | Male    | American | Deep voice, authoritative narrator          |
| **nova**    | Female  | American | Warm and engaging, friendly tone            |
| **shimmer** | Female  | American | Bright and energetic, youthful              |

## 💻 Python Usage Example

```python
from backend.openai_tts_service import get_openai_tts_service

# Initialize service
tts = get_openai_tts_service(
    voice="alloy",
    model="standard",
    audio_format="mp3"
)

# Generate speech
audio_data = tts.generate_speech(
    text="The dragon roars as it emerges from the cave!",
    voice="onyx",
    speed=1.2
)

# Save to file
with open("narration.mp3", "wb") as f:
    f.write(audio_data)

# Transcribe audio
text = tts.transcribe_file(
    file_path="recording.mp3",
    language="en"
)
print(f"Transcribed: {text}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional defaults can be set in code
DEFAULT_TTS_VOICE=alloy
DEFAULT_TTS_MODEL=standard
DEFAULT_AUDIO_FORMAT=mp3
```

### Service Initialization

```python
from backend.openai_tts_service import OpenAITTSService

# Custom initialization
service = OpenAITTSService(
    api_key="your_key",        # Optional, reads from env
    default_voice="nova",      # Female voice
    default_model="hd",        # High quality
    default_format="wav"       # WAV format
)
```

## 🎯 Use Cases

### 1. AI DM Narration

Use TTS to narrate DM responses with different voices for different NPCs:

```python
# Authoritative narrator for DM
dm_audio = tts.generate_speech(
    text=dm_response,
    voice="onyx",
    model="hd"
)

# Different voice for NPC dialogue
npc_audio = tts.generate_speech(
    text=npc_dialogue,
    voice="fable",
    speed=1.1
)
```

### 2. Voice Commands

Players can speak their actions using Whisper:

```python
# Transcribe player's voice input
action = tts.transcribe_file(
    file_path="player_command.mp3",
    prompt="D&D game commands and actions"
)
print(f"Player said: {action}")
```

### 3. Story Audiobooks

Convert campaign logs to audiobooks:

```python
# Generate chapter narration
for chapter in campaign_log:
    audio = tts.generate_speech(
        text=chapter.text,
        voice="alloy",
        model="hd"
    )
    save_chapter_audio(chapter.id, audio)
```

## 📊 Performance & Pricing

### TTS Performance

- **Standard Model:** ~1-2 seconds latency for short text
- **HD Model:** ~2-4 seconds latency for higher quality
- **Streaming:** Real-time chunks, lower perceived latency

### OpenAI Pricing (as of 2024)

- **TTS:** $0.015 per 1,000 characters (standard), $0.030 per 1,000 characters (HD)
- **Whisper:** $0.006 per minute of audio

Example costs:

- 100-word DM response (~500 chars): $0.0075 (standard) or $0.015 (HD)
- 5-minute voice recording: $0.03

## 🔐 Security Notes

- **API Key Storage:** Never commit API keys to version control
- **Environment Variables:** Use `.env` file (excluded from git)
- **Rate Limits:** OpenAI has rate limits per API key
- **Token Limits:** TTS max 4096 characters per request

## 🆚 Comparison with Kitten TTS

| Feature          | OpenAI TTS            | Kitten TTS      |
| ---------------- | --------------------- | --------------- |
| **Quality**      | Professional, natural | Good, synthetic |
| **Voices**       | 6 options             | 8 options       |
| **Speed**        | 0.25x - 4.0x          | Fixed           |
| **Formats**      | 6 formats             | WAV only        |
| **Streaming**    | Yes                   | No              |
| **Cost**         | $0.015/1k chars       | Free            |
| **Requirements** | API key, internet     | Local, no deps  |
| **Latency**      | 1-4 seconds           | <1 second       |

## 🧪 Testing

Run the integration test:

```bash
python backend/test_openai_tts.py
```

This will test:

1. Service initialization
2. Basic TTS generation
3. Multiple voices
4. Speed control
5. Whisper transcription
6. API endpoints

## 📝 Migration from Kitten TTS

If you're currently using Kitten TTS, you can switch to OpenAI TTS:

```python
# Old (Kitten TTS)
from backend.tts_service import get_tts_service
tts = get_tts_service()
audio = tts.generate_speech(text, voice="tara")

# New (OpenAI TTS)
from backend.openai_tts_service import get_openai_tts_service
tts = get_openai_tts_service()
audio = tts.generate_speech(text, voice="alloy")
```

Voice mapping suggestions:

- `tara` (female narrator) → `alloy` or `nova`
- `leo` (male narrator) → `onyx` or `echo`
- `jess` (energetic) → `shimmer`
- `mia` (mysterious) → `fable`

## 🔗 Additional Resources

- [OpenAI TTS API Documentation](https://platform.openai.com/docs/guides/text-to-speech)
- [Whisper API Documentation](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI Pricing](https://openai.com/pricing)
- [API Reference](https://platform.openai.com/docs/api-reference/audio)

## ❓ Troubleshooting

### "OpenAI API key not found"

- Set `OPENAI_API_KEY` environment variable
- Or pass `api_key` parameter when initializing service

### "Request failed with status 401"

- Check API key is valid
- Verify key has credits/billing enabled

### "Audio quality is poor"

- Try `model="hd"` for higher quality
- Adjust `speed` parameter (1.0 is optimal)

### "Transcription inaccurate"

- Provide `language` parameter
- Add context via `prompt` parameter
- Ensure audio quality is good

## 🎉 Summary

StoryCraft now has professional-grade TTS and STT capabilities powered by OpenAI! You can:

✅ Generate high-quality narration with 6 voices  
✅ Support multiple audio formats  
✅ Control speech speed and quality  
✅ Transcribe player voice commands  
✅ Stream audio for lower latency  
✅ Integrate seamlessly with existing AI DM features

Enjoy bringing your adventures to life with voice! 🎲🎤
