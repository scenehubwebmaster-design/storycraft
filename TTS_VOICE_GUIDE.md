# OrpheusTTS Voice Selection Guide

## Available Voices

OrpheusTTS provides **8 unique voices** for D&D narration:

### Female Voices

- **tara** - Clear, professional narrator
- **leah** - Warm, friendly storyteller
- **jess** - Energetic, adventurous tone
- **mia** - Mysterious, dramatic flair

### Male Voices

- **leo** - Deep, authoritative narrator
- **dan** - Calm, classic storyteller
- **zac** - Young, enthusiastic adventurer
- **zoe** - Gender-neutral, versatile (technically male-coded)

## Voice Selection UI

### Location: TTSAudioPlayer Component

The voice selector is **already implemented** in:

```
frontend/src/components/game/TTSAudioPlayer.jsx
```

### Features:

- **Dropdown menu** with all 8 voices
- **Live preview** - Voice changes apply to new audio requests
- **Persistent selection** - Remembers your choice per session
- **Compact mode** - Optional slim UI for chat messages

### Usage:

1. When TTS is enabled, each DM message shows an audio player
2. Click the **voice dropdown** (shows current voice name)
3. Select your preferred voice from the list
4. New audio will use the selected voice

## TTS Controls (NEW - Phase 4 Enhancement)

### Main Interface Controls (DMChat.jsx)

Now prominently displayed in the session controls area:

- ✅ **Voice Narration** checkbox - Enable/disable TTS
- ✅ **Auto-play** checkbox - Automatically play DM responses
- ✅ **Status chip** - Shows "Voice: Auto" or "Voice: Manual"

**Location:** Top of the chat area, next to RAG controls

### Settings Drawer (Advanced)

Additional TTS options available in settings:

- Same enable/auto-play toggles
- Additional configuration options

## Emotion Tags (Advanced)

OrpheusTTS supports emotion tags in text:

- `<laugh>` - Laughter
- `<chuckle>` - Light laugh
- `<sigh>` - Exhale/disappointment
- `<gasp>` - Surprise/shock
- `<cough>` - Coughing sound
- `<yawn>` - Tired/bored
- `<sniff>` - Crying/sadness

### Example:

```
The ancient dragon laughs <laugh> as it unfolds its massive wings.
"You dare challenge me?" it roars <gasp>.
```

## Implementation Details

### Backend (Python)

```python
# backend/chat.py - TTS endpoint
POST /api/game-chat/tts/{session_id}/{message_id}?voice=tara

# backend/tts_service.py - OrpheusTTS integration
def generate_audio(text: str, voice: str = "tara") -> bytes
```

### Frontend (React)

```jsx
// TTSAudioPlayer.jsx - Voice selector component
<Select value={selectedVoice} onChange={handleVoiceChange}>
  <MenuItem value="tara">Tara</MenuItem>
  <MenuItem value="leah">Leah</MenuItem>
  {/* ... 6 more voices */}
</Select>
```

### API Integration

```javascript
// Fetch audio with selected voice
const audioUrl = `/api/game-chat/tts/${sessionId}/${messageId}?voice=${voice}`;
```

## Best Practices

1. **Choose voice based on campaign tone:**

   - Epic fantasy → Leo (deep, authoritative)
   - Lighthearted adventure → Jess (energetic)
   - Mystery/horror → Mia (dramatic)
   - Classic D&D → Dan (calm storyteller)

2. **Use auto-play for immersive experience**

   - Disable if you prefer to read first, listen later
   - Manual mode gives you control over when audio plays

3. **Experiment with different voices**
   - Each voice has unique character
   - Try different voices for different NPCs (future feature)

## Future Enhancements

### Planned Features:

- **Per-NPC voice selection** - Different voices for different characters
- **Voice pitch/speed controls** - Customize each voice further
- **Background music integration** - Ambient sounds with narration
- **Multi-voice dialogue** - Separate voices for each speaker in a scene

### OrpheusTTS Capabilities (from GitHub):

- **Low latency** - Fast audio generation (250ms for 17 tokens)
- **High quality** - Natural-sounding speech
- **Emotion support** - Tags for expressive narration
- **No API keys** - Self-hosted, no external dependencies

## Troubleshooting

### Voice not changing?

- Ensure TTS is enabled (checkbox at top of chat)
- New audio requests use the newly selected voice
- Existing audio keeps its original voice (re-generate to update)

### Audio not playing?

- Check browser audio permissions
- Verify TTS backend is running (orpheus-speech installed)
- Check browser console for error messages

### Voice selector not visible?

- Look for the audio player component on DM messages
- If compact mode is on, controls may be smaller
- Voice selector appears as a dropdown showing current voice name

## Technical Notes

### Voice IDs (Backend)

```python
AVAILABLE_VOICES = [
    "tara", "leah", "jess", "mia",  # Female
    "leo", "dan", "zac", "zoe"      # Male
]
```

### Default Voice

- Default: **"tara"** (clear, professional narrator)
- Can be changed in TTSAudioPlayer component state
- Persists per browser session

### Audio Format

- Format: **WAV** (uncompressed)
- Sample rate: **22050 Hz**
- Channels: **Mono**
- Bit depth: **16-bit**

## References

- OrpheusTTS GitHub: https://github.com/canopyai/Orpheus-TTS
- Backend implementation: `backend/tts_service.py`
- Frontend component: `frontend/src/components/game/TTSAudioPlayer.jsx`
- API endpoint: `backend/chat.py` (POST `/api/game-chat/tts/{session_id}/{message_id}`)

---

**Phase 4 Complete** ✅

- D&D content commands: `/spell`, `/monster`, `/item`
- Intelligent spell/monster detection
- **Visible TTS controls in main interface** (NEW)
- Voice selection fully implemented
- Auto-play toggle for immersive gameplay
