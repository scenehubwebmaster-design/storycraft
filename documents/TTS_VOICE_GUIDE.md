# Kitten TTS Voice Selection Guide# OrpheusTTS Voice Selection Guide

## Available Voices## Available Voices

Kitten TTS provides **8 unique voices** for D&D narration:OrpheusTTS provides **8 unique voices** for D&D narration:

### Female Voices### Female Voices

- **tara** - Clear, professional narrator- **tara** - Clear, professional narrator

- **leah** - Warm, friendly storyteller- **leah** - Warm, friendly storyteller

- **jess** - Energetic, adventurous tone- **jess** - Energetic, adventurous tone

- **mia** - Mysterious, dramatic flair- **mia** - Mysterious, dramatic flair

### Male Voices### Male Voices

- **leo** - Deep, authoritative narrator- **leo** - Deep, authoritative narrator

- **dan** - Calm, classic storyteller- **dan** - Calm, classic storyteller

- **zac** - Young, enthusiastic adventurer- **zac** - Young, enthusiastic adventurer

- **zoe** - Gender-neutral, versatile- **zoe** - Gender-neutral, versatile (technically male-coded)

## Voice Selection UI## Voice Selection UI

### Location: TTSAudioPlayer Component### Location: TTSAudioPlayer Component

The voice selector is **already implemented** in:The voice selector is **already implemented** in:

```

frontend/src/components/game/TTSAudioPlayer.jsxfrontend/src/components/game/TTSAudioPlayer.jsx

```

### Features:### Features:

- **Dropdown menu** with all 8 voices- **Dropdown menu** with all 8 voices

- **Live preview** - Voice changes apply to new audio requests- **Live preview** - Voice changes apply to new audio requests

- **Persistent selection** - Remembers your choice per session- **Persistent selection** - Remembers your choice per session

- **Compact mode** - Optional slim UI for chat messages- **Compact mode** - Optional slim UI for chat messages

### Usage:### Usage:

1. When TTS is enabled, each DM message shows an audio player1. When TTS is enabled, each DM message shows an audio player

2. Click the **voice dropdown** (shows current voice name)2. Click the **voice dropdown** (shows current voice name)

3. Select your preferred voice from the list3. Select your preferred voice from the list

4. New audio will use the selected voice4. New audio will use the selected voice

## TTS Controls (Phase 4 Enhancement)## TTS Controls (NEW - Phase 4 Enhancement)

### Main Interface Controls (DMChat.jsx)### Main Interface Controls (DMChat.jsx)

Now prominently displayed in the session controls area:Now prominently displayed in the session controls area:

- ✅ **Voice Narration** checkbox - Enable/disable TTS- ✅ **Voice Narration** checkbox - Enable/disable TTS

- ✅ **Auto-play** checkbox - Automatically play DM responses- ✅ **Auto-play** checkbox - Automatically play DM responses

- ✅ **Status chip** - Shows "Voice: Auto" or "Voice: Manual"- ✅ **Status chip** - Shows "Voice: Auto" or "Voice: Manual"

**Location:** Top of the chat area, next to RAG controls**Location:** Top of the chat area, next to RAG controls

### Settings Drawer (Advanced)### Settings Drawer (Advanced)

Additional TTS options available in settings:Additional TTS options available in settings:

- Same enable/auto-play toggles- Same enable/auto-play toggles

- Additional configuration options- Additional configuration options

## Voice Mapping (Technical Details)## Emotion Tags (Advanced)

Kitten TTS uses internal voice IDs that are mapped from friendly names:OrpheusTTS supports emotion tags in text:

| Friendly Name | Kitten Voice ID | Gender | Character |- `<laugh>` - Laughter

|---------------|-----------------|--------|-----------|- `<chuckle>` - Light laugh

| tara | expr-voice-2-f | Female | Clear, professional |- `<sigh>` - Exhale/disappointment

| leah | expr-voice-3-f | Female | Warm, friendly |- `<gasp>` - Surprise/shock

| jess | expr-voice-4-f | Female | Energetic |- `<cough>` - Coughing sound

| mia | expr-voice-5-f | Female | Mysterious |- `<yawn>` - Tired/bored

| leo | expr-voice-2-m | Male | Authoritative |- `<sniff>` - Crying/sadness

| dan | expr-voice-3-m | Male | Classic |

| zac | expr-voice-4-m | Male | Enthusiastic |### Example:

| zoe | expr-voice-5-m | Male | Versatile |

````

The backend automatically handles this mapping, so frontend code continues to use friendly names like "tara" and "leo".The ancient dragon laughs <laugh> as it unfolds its massive wings.

"You dare challenge me?" it roars <gasp>.

## Implementation Details```



### Backend (Python)## Implementation Details



```python### Backend (Python)

# backend/chat.py - TTS endpoint

POST /api/chat/sessions/{session_id}/messages/{message_id}/tts?voice=tara```python

# backend/chat.py - TTS endpoint

# backend/tts_service.py - Kitten TTS integrationPOST /api/game-chat/tts/{session_id}/{message_id}?voice=tara

def generate_audio(text: str, voice: str = "tara") -> bytes

```# backend/tts_service.py - OrpheusTTS integration

def generate_audio(text: str, voice: str = "tara") -> bytes

### Frontend (React)```



```jsx### Frontend (React)

// TTSAudioPlayer.jsx - Voice selector component

<Select value={selectedVoice} onChange={handleVoiceChange}>```jsx

  <MenuItem value="tara">Tara</MenuItem>// TTSAudioPlayer.jsx - Voice selector component

  <MenuItem value="leah">Leah</MenuItem><Select value={selectedVoice} onChange={handleVoiceChange}>

  {/* ... 6 more voices */}  <MenuItem value="tara">Tara</MenuItem>

</Select>  <MenuItem value="leah">Leah</MenuItem>

```  {/* ... 6 more voices */}

</Select>

### API Integration```



```javascript### API Integration

// Fetch audio with selected voice

const audioUrl = `/api/chat/sessions/${sessionId}/messages/${messageId}/tts?voice=${voice}`;```javascript

```// Fetch audio with selected voice

const audioUrl = `/api/game-chat/tts/${sessionId}/${messageId}?voice=${voice}`;

## Best Practices```



1. **Choose voice based on campaign tone:**## Best Practices



   - Epic fantasy → Leo (deep, authoritative)1. **Choose voice based on campaign tone:**

   - Lighthearted adventure → Jess (energetic)

   - Mystery/horror → Mia (dramatic)   - Epic fantasy → Leo (deep, authoritative)

   - Classic D&D → Dan (calm storyteller)   - Lighthearted adventure → Jess (energetic)

   - Mystery/horror → Mia (dramatic)

2. **Use auto-play for immersive experience**   - Classic D&D → Dan (calm storyteller)



   - Disable if you prefer to read first, listen later2. **Use auto-play for immersive experience**

   - Manual mode gives you control over when audio plays

   - Disable if you prefer to read first, listen later

3. **Experiment with different voices**   - Manual mode gives you control over when audio plays

   - Each voice has unique character

   - Try different voices for different NPCs (future feature)3. **Experiment with different voices**

   - Each voice has unique character

## Migration from Orpheus TTS   - Try different voices for different NPCs (future feature)



### What Changed## Future Enhancements



- Same 8 friendly voice names (tara, leah, jess, mia, leo, dan, zac, zoe)### Planned Features:

- Backend now maps to Kitten TTS voice IDs

- No frontend changes required- **Per-NPC voice selection** - Different voices for different characters

- Emotion tags no longer supported (see below)- **Voice pitch/speed controls** - Customize each voice further

- **Background music integration** - Ambient sounds with narration

### Emotion Tags Removed- **Multi-voice dialogue** - Separate voices for each speaker in a scene



⚠️ **Emotion tags not supported in Kitten TTS**### OrpheusTTS Capabilities (from GitHub):



Previously supported tags in Orpheus TTS:- **Low latency** - Fast audio generation (250ms for 17 tokens)

- `<laugh>` - Laughter- **High quality** - Natural-sounding speech

- `<chuckle>` - Light laugh- **Emotion support** - Tags for expressive narration

- `<sigh>` - Exhale/disappointment- **No API keys** - Self-hosted, no external dependencies

- `<gasp>` - Surprise/shock

- `<cough>` - Coughing sound## Troubleshooting

- `<yawn>` - Tired/bored

- `<sniff>` - Crying/sadness### Voice not changing?



These tags are now **ignored** by Kitten TTS. Text is generated as-is without emotion markup.- Ensure TTS is enabled (checkbox at top of chat)

- New audio requests use the newly selected voice

If you had custom prompts or scripts using emotion tags, they will still work but the tags will be treated as regular text (and likely mispronounced).- Existing audio keeps its original voice (re-generate to update)



**Workaround:** Rely on natural language and punctuation for expression:### Audio not playing?

- Instead of `"Hello <laugh> there!"` use `"Haha! Hello there!"`

- Instead of `"Oh no <gasp>!"` use `"Oh no!" (with exclamation emphasis)`- Check browser audio permissions

- Verify TTS backend is running (orpheus-speech installed)

## Future Enhancements- Check browser console for error messages



### Planned Features:### Voice selector not visible?



- **Per-NPC voice selection** - Different voices for different characters- Look for the audio player component on DM messages

- **Voice pitch/speed controls** - Customize each voice further- If compact mode is on, controls may be smaller

- **Background music integration** - Ambient sounds with narration- Voice selector appears as a dropdown showing current voice name

- **Multi-voice dialogue** - Separate voices for each speaker in a scene

## Technical Notes

### Kitten TTS Capabilities:

### Voice IDs (Backend)

- **Ultra-lightweight** - Model under 25MB

- **CPU-optimized** - No GPU required```python

- **High quality** - Natural-sounding speechAVAILABLE_VOICES = [

- **Fast generation** - Optimized inference    "tara", "leah", "jess", "mia",  # Female

- **No API keys** - Self-hosted, no external dependencies    "leo", "dan", "zac", "zoe"      # Male

]

## Troubleshooting```



### Voice not changing?### Default Voice



- Ensure TTS is enabled (checkbox at top of chat)- Default: **"tara"** (clear, professional narrator)

- New audio requests use the newly selected voice- Can be changed in TTSAudioPlayer component state

- Existing audio keeps its original voice (re-generate to update)- Persists per browser session



### Audio not playing?### Audio Format



- Check browser audio permissions- Format: **WAV** (uncompressed)

- Verify TTS backend is running (kittentts installed)- Sample rate: **22050 Hz**

- Check browser console for error messages- Channels: **Mono**

- Ensure model downloaded (first run downloads from HuggingFace)- Bit depth: **16-bit**



### Voice selector not visible?## References



- Look for the audio player component on DM messages- OrpheusTTS GitHub: https://github.com/canopyai/Orpheus-TTS

- If compact mode is on, controls may be smaller- Backend implementation: `backend/tts_service.py`

- Voice selector appears as a dropdown showing current voice name- Frontend component: `frontend/src/components/game/TTSAudioPlayer.jsx`

- API endpoint: `backend/chat.py` (POST `/api/game-chat/tts/{session_id}/{message_id}`)

### Voice sounds wrong or robotic?

---

- Kitten TTS is optimized for CPU, quality may vary slightly from Orpheus

- Try different voices to find the best match**Phase 4 Complete** ✅

- Ensure model downloaded correctly (check backend logs)

- D&D content commands: `/spell`, `/monster`, `/item`

## Technical Notes- Intelligent spell/monster detection

- **Visible TTS controls in main interface** (NEW)

### Voice IDs (Backend)- Voice selection fully implemented

- Auto-play toggle for immersive gameplay

```python
AVAILABLE_VOICES = [
    "tara", "leah", "jess", "mia",  # Female
    "leo", "dan", "zac", "zoe"      # Male
]

VOICE_MAP = {
    "tara": "expr-voice-2-f",
    "leah": "expr-voice-3-f",
    "jess": "expr-voice-4-f",
    "mia": "expr-voice-5-f",
    "leo": "expr-voice-2-m",
    "dan": "expr-voice-3-m",
    "zac": "expr-voice-4-m",
    "zoe": "expr-voice-5-m",
}
````

### Default Voice

- Default: **"tara"** (clear, professional narrator)
- Can be changed in TTSAudioPlayer component state
- Persists per browser session

### Audio Format

- Format: **WAV** (uncompressed)
- Sample rate: **24000 Hz**
- Channels: **Mono**
- Bit depth: **16-bit**

## References

- Kitten TTS GitHub: https://github.com/KittenML/KittenTTS
- Backend implementation: `backend/tts_service.py`
- Frontend component: `frontend/src/components/game/TTSAudioPlayer.jsx`
- API endpoint: `backend/routers/chat.py` (POST `/api/chat/sessions/{session_id}/messages/{message_id}/tts`)

---

**Phase 4 Complete** ✅

- D&D content commands: `/spell`, `/monster`, `/item`
- Intelligent spell/monster detection
- **Visible TTS controls in main interface**
- Voice selection fully implemented
- Auto-play toggle for immersive gameplay
- **Migrated to Kitten TTS** (CPU-optimized, no CUDA required)
