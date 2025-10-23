# TTS UI Location Map# TTS UI Location Map

**TTS Engine:** Kitten TTS (CPU-optimized, no GPU required!) ## DMChat.jsx - Main Interface

**Model:** KittenML/kitten-tts-nano-0.2

**Voices:** 8 (tara, leah, jess, mia, leo, dan, zac, zoe)```

┌─────────────────────────────────────────────────────────────┐

## DMChat.jsx - Main Interface│ 🏰 Dungeon Master Chat [Settings] │

├─────────────────────────────────────────────────────────────┤

````│ ┌─ Session Controls ─────────────────────────────────────┐ │

┌─────────────────────────────────────────────────────────────┐│  │                                                          │ │

│  🏰 Dungeon Master Chat                          [Settings] ││  │  ☑ RAG Context    [Context (k): 5]  [RAG Enabled]      │ │

├─────────────────────────────────────────────────────────────┤│  │                                                          │ │

│  ┌─ Session Controls ─────────────────────────────────────┐ ││  │  ─────────────────────────────────────────────────────  │ │  ← Divider

│  │                                                          │ ││  │                                                          │ │

│  │  ☑ RAG Context    [Context (k): 5]  [RAG Enabled]      │ ││  │  ☑ Voice    ☑ Auto-play    [Voice: Auto]     ← NEW!    │ │

│  │                                                          │ ││  │     ↑          ↑              ↑                          │ │

│  │  ─────────────────────────────────────────────────────  │ │  ← Divider│  │     │          │              └─ Status chip             │ │

│  │                                                          │ ││  │     │          └─ Auto-play DM responses                 │ │

│  │  ☑ Voice    ☑ Auto-play    [Voice: Auto]     ← NEW!    │ ││  │     └─ Enable voice narration                           │ │

│  │     ↑          ↑              ↑                          │ ││  │                                                          │ │

│  │     │          │              └─ Status chip             │ ││  └──────────────────────────────────────────────────────────┘ │

│  │     │          └─ Auto-play DM responses                 │ │├─────────────────────────────────────────────────────────────┤

│  │     └─ Enable voice narration (Kitten TTS)              │ ││  ┌─ Chat Messages ─────────────────────────────────────────┐ │

│  │                                                          │ ││  │                                                          │ │

│  └──────────────────────────────────────────────────────────┘ ││  │  [Avatar] Dungeon Master                                │ │

├─────────────────────────────────────────────────────────────┤│  │           "You enter a dark tavern..."                  │ │

│  ┌─ Chat Messages ─────────────────────────────────────────┐ ││  │                                                          │ │

│  │                                                          │ ││  │           ┌─ TTSAudioPlayer ─────────────────────┐      │ │

│  │  [Avatar] Dungeon Master                                │ ││  │           │ [Voice: Tara ▼] [▶ Play] 0:00 / 0:05 │      │ │

│  │           "You enter a dark tavern..."                  │ ││  │           │   ↑                                   │      │ │

│  │                                                          │ ││  │           │   └─ Voice selector dropdown          │      │ │

│  │           ┌─ TTSAudioPlayer ─────────────────────┐      │ ││  │           └───────────────────────────────────────┘      │ │

│  │           │ [Voice: Tara ▼] [▶ Play] 0:00 / 0:05 │      │ ││  │                                                          │ │

│  │           │   ↑                                   │      │ ││  │  [Avatar] You                                           │ │

│  │           │   └─ Voice selector dropdown          │      │ ││  │           "I approach the barkeep"                      │ │

│  │           └───────────────────────────────────────┘      │ ││  │                                                          │ │

│  │                                                          │ ││  └──────────────────────────────────────────────────────────┘ │

│  │  [Avatar] You                                           │ │├─────────────────────────────────────────────────────────────┤

│  │           "I approach the barkeep"                      │ ││  [Type your message...                          ] [Send →]  │

│  │                                                          │ │└─────────────────────────────────────────────────────────────┘

│  └──────────────────────────────────────────────────────────┘ │```

├─────────────────────────────────────────────────────────────┤

│  [Type your message...                          ] [Send →]  │## TTSAudioPlayer.jsx - Component Detail

└─────────────────────────────────────────────────────────────┘

````

┌─ TTSAudioPlayer Component ─────────────────────────────────┐

## TTSAudioPlayer.jsx - Component Detail│ │

│ Compact Mode (in chat messages): │

````│ ┌──────────────────────────────────────────────────────┐  │

┌─ TTSAudioPlayer Component ─────────────────────────────────┐│  │ [Voice: Tara ▼]  [▶]  0:00 / 0:05  [🔊]            │  │

│                                                             ││  │    ↑            ↑      ↑              ↑              │  │

│  Compact Mode (in chat messages):                          ││  │    │            │      │              └─ Volume      │  │

│  ┌──────────────────────────────────────────────────────┐  ││  │    │            │      └─ Progress bar               │  │

│  │ [Voice: Tara ▼]  [▶]  0:00 / 0:05  [🔊]            │  ││  │    │            └─ Play/Pause button                 │  │

│  │    ↑            ↑      ↑              ↑              │  ││  │    └─ Voice selector (8 options)                     │  │

│  │    │            │      │              └─ Volume      │  ││  └──────────────────────────────────────────────────────┘  │

│  │    │            │      └─ Progress bar               │  ││                                                             │

│  │    │            └─ Play/Pause button                 │  ││  Full Mode (in GameSession page):                          │

│  │    └─ Voice selector (8 Kitten TTS voices)          │  ││  ┌──────────────────────────────────────────────────────┐  │

│  └──────────────────────────────────────────────────────┘  ││  │ 🎙️ Dungeon Master Narration                          │  │

│                                                             ││  │                                                       │  │

│  Full Mode (in GameSession page):                          ││  │ Voice: [Tara (Female)      ▼]                        │  │

│  ┌──────────────────────────────────────────────────────┐  ││  │                                                       │  │

│  │ 🎙️ Dungeon Master Narration                          │  ││  │ [▶ Play]  ━━━━━━━━○━━━━━━━  0:03 / 0:05            │  │

│  │                                                       │  ││  │                                                       │  │

│  │ Voice: [Tara (Female)      ▼]                        │  ││  │ Volume: [━━━━━━●━━━] 70%                            │  │

│  │                                                       │  ││  └──────────────────────────────────────────────────────┘  │

│  │ [▶ Play]  ━━━━━━━━○━━━━━━━  0:03 / 0:05            │  ││                                                             │

│  │                                                       │  │└─────────────────────────────────────────────────────────────┘

│  │ Volume: [━━━━━━●━━━] 70%                            │  │```

│  └──────────────────────────────────────────────────────┘  │

│                                                             │## Voice Selector Dropdown

└─────────────────────────────────────────────────────────────┘

````

┌─ Select Voice ──────┐

## Voice Selector Dropdown│ ✓ Tara (Female) │ ← Currently selected

│ Leah (Female) │

````│ Jess (Female)     │

┌─ Select Voice ──────┐│   Mia (Female)      │

│ ✓ Tara (Female)     │ ← Currently selected (expr-voice-2-f)│   Leo (Male)        │

│   Leah (Female)     │   (expr-voice-3-f)│   Dan (Male)        │

│   Jess (Female)     │   (expr-voice-4-f)│   Zac (Male)        │

│   Mia (Female)      │   (expr-voice-5-f)│   Zoe (Neutral)     │

│   Leo (Male)        │   (expr-voice-2-m)└─────────────────────┘

│   Dan (Male)        │   (expr-voice-3-m)```

│   Zac (Male)        │   (expr-voice-4-m)

│   Zoe (Neutral)     │   (expr-voice-5-m)## Settings Drawer (Alternative Access)

└─────────────────────┘

     ↑```

     └─ Backend maps to Kitten TTS voice IDs┌─ Settings Drawer ───────────────────┐

```│                                     │

│  ⚙️ Session Settings                │

## Settings Drawer (Alternative Access)│                                     │

│  Provider: [Groq            ▼]     │

```│  Model: [mixtral-8x7b       ▼]     │

┌─ Settings Drawer ───────────────────┐│                                     │

│                                     ││  ────────────────────────────────  │

│  ⚙️ Session Settings                ││                                     │

│                                     ││  🔊 Voice Narration (TTS)          │

│  Provider: [Groq            ▼]     ││                                     │

│  Model: [mixtral-8x7b       ▼]     ││  ☑ Enable Voice Narration          │

│                                     ││  ☑ Auto-play Responses             │

│  ────────────────────────────────  ││                                     │

│                                     ││  ────────────────────────────────  │

│  🔊 Voice Narration (Kitten TTS)   ││                                     │

│                                     ││  📖 RAG Settings                    │

│  ☑ Enable Voice Narration          ││  ☑ Include Context                 │

│  ☑ Auto-play Responses             ││  Top K: [5]                        │

│                                     ││                                     │

│  ────────────────────────────────  │└─────────────────────────────────────┘

│                                     │```

│  📖 RAG Settings                    │

│  ☑ Include Context                 │## User Flow: Enabling TTS

│  Top K: [5]                        │

│                                     │### Quick Path (NEW):

└─────────────────────────────────────┘

```1. Open DMChat page

2. Select or create a session

## User Flow: Enabling TTS3. See session controls at top

4. ✅ Check "Voice" checkbox

### Quick Path (NEW):5. ✅ Check "Auto-play" (optional)

6. Send message

1. Open DMChat page7. DM response auto-plays with audio

2. Select or create a session

3. See session controls at top### Manual Voice Selection:

4. ✅ Check "Voice" checkbox

5. ✅ Check "Auto-play" (optional)1. After DM responds

6. Send message2. Audio player appears below message

7. DM response auto-plays with audio (Kitten TTS)3. Click voice dropdown "Tara ▼"

4. Select preferred voice

### Manual Voice Selection:5. Click ▶ Play to hear

6. Next response uses new voice

1. After DM responds

2. Audio player appears below message### Settings Path (Original):

3. Click voice dropdown "Tara ▼"

4. Select preferred voice (8 options)1. Click ⚙️ Settings icon (top right)

5. Click ▶ Play to hear2. Scroll to "Voice Narration (TTS)"

6. Next response uses new voice3. Toggle switches

4. Close drawer

### Settings Path (Original):5. TTS enabled for session



1. Click ⚙️ Settings icon (top right)## Integration Points

2. Scroll to "Voice Narration (TTS)"

3. Toggle switches### DMChat.jsx

4. Close drawer

5. TTS enabled for session```jsx

// Lines 76-77: State management

## Integration Pointsconst [ttsEnabled, setTtsEnabled] = useState(true);

const [ttsAutoPlay, setTtsAutoPlay] = useState(false);

### DMChat.jsx

// Lines 710-756: NEW visible controls

```jsx<FormControlLabel

// Lines 76-77: State management  control={<Checkbox checked={ttsEnabled} />}

const [ttsEnabled, setTtsEnabled] = useState(true);  label={<Stack><VolumeUpIcon /><Typography>Voice</Typography></Stack>}

const [ttsAutoPlay, setTtsAutoPlay] = useState(false);/>

<FormControlLabel

// Lines 710-756: NEW visible controls  control={<Checkbox checked={ttsAutoPlay} />}

<FormControlLabel  label={<Stack><PlayArrowIcon /><Typography>Auto-play</Typography></Stack>}

  control={<Checkbox checked={ttsEnabled} />}/>

  label={<Stack><VolumeUpIcon /><Typography>Voice</Typography></Stack>}<Chip label={ttsAutoPlay ? "Voice: Auto" : "Voice: Manual"} />

/>

<FormControlLabel// Lines 870-889: Audio player in messages

  control={<Checkbox checked={ttsAutoPlay} />}{msg.role === "assistant" && ttsEnabled && (

  label={<Stack><PlayArrowIcon /><Typography>Auto-play</Typography></Stack>}  <TTSAudioPlayer

/>    sessionId={selectedSession.id}

<Chip label={ttsAutoPlay ? "Voice: Auto" : "Voice: Manual"} />    messageId={msg.id}

    autoPlay={ttsAutoPlay}

// Lines 870-889: Audio player in messages  />

{msg.role === "assistant" && ttsEnabled && ()}

  <TTSAudioPlayer```

    sessionId={selectedSession.id}

    messageId={msg.id}### DMChatPanel.jsx

    autoPlay={ttsAutoPlay}

  />```jsx

)}// Lines 29-35: Props

```function DMChatPanel({

  messages = [],

### DMChatPanel.jsx  sessionId = null,

  ttsEnabled = true, // ← Passed from parent

```jsx  ttsAutoPlay = false, // ← Passed from parent

// Lines 29-35: Props}) {

function DMChatPanel({  // Lines 163-175: Audio player rendering

  messages = [],  isDM && ttsEnabled && msg.id && sessionId && (

  sessionId = null,    <TTSAudioPlayer

  ttsEnabled = true, // ← Passed from parent      sessionId={sessionId}

  ttsAutoPlay = false, // ← Passed from parent      messageId={msg.id}

}) {      autoPlay={ttsAutoPlay}

  // Lines 163-175: Audio player rendering      compact={true} // ← Compact UI for chat

  isDM && ttsEnabled && msg.id && sessionId && (    />

    <TTSAudioPlayer  );

      sessionId={sessionId}}

      messageId={msg.id}```

      autoPlay={ttsAutoPlay}

      compact={true} // ← Compact UI for chat### TTSAudioPlayer.jsx

    />

  );```jsx

}// Lines 15-18: State with voice selection

```const [selectedVoice, setSelectedVoice] = useState("tara");

const [isPlaying, setIsPlaying] = useState(false);

### TTSAudioPlayer.jsxconst [volume, setVolume] = useState(0.7);



```jsx// Lines 45-58: Voice selector

// Lines 15-18: State with voice selection<Select

const [selectedVoice, setSelectedVoice] = useState("tara");  value={selectedVoice}

const [isPlaying, setIsPlaying] = useState(false);  onChange={(e) => setSelectedVoice(e.target.value)}

const [volume, setVolume] = useState(0.7);>

  <MenuItem value="tara">Tara (Female)</MenuItem>

// Lines 45-58: Voice selector  <MenuItem value="leah">Leah (Female)</MenuItem>

<Select  {/* ... 6 more voices */}

  value={selectedVoice}</Select>;

  onChange={(e) => setSelectedVoice(e.target.value)}

>// Lines 80-85: Fetch audio with voice parameter

  <MenuItem value="tara">Tara (Female)</MenuItem>const audioUrl = `/api/game-chat/tts/${sessionId}/${messageId}?voice=${selectedVoice}`;

  <MenuItem value="leah">Leah (Female)</MenuItem>```

  <MenuItem value="jess">Jess (Female)</MenuItem>

  <MenuItem value="mia">Mia (Female)</MenuItem>## Key Features

  <MenuItem value="leo">Leo (Male)</MenuItem>

  <MenuItem value="dan">Dan (Male)</MenuItem>✅ **Visible Controls** - No need to open settings

  <MenuItem value="zac">Zac (Male)</MenuItem>✅ **Voice Selection** - 8 unique voices per message

  <MenuItem value="zoe">Zoe (Neutral)</MenuItem>✅ **Auto-play Option** - Immersive or manual control

</Select>;✅ **Status Indicator** - Always know TTS state

✅ **Persistent State** - Settings saved per session

// Lines 80-85: Fetch audio with voice parameter✅ **Compact UI** - Doesn't clutter chat interface

// Backend maps "tara" → "expr-voice-2-f", etc.

const audioUrl = `/api/chat/sessions/${sessionId}/messages/${messageId}/tts?voice=${selectedVoice}`;## Commit History

````

- **8c40e89** - Phase 3: Narrative engine MCP integration

### Backend: tts_service.py- **cf6af08** - Phase 4: DM chat handler D&D commands

- **b98eb6b** - Add visible TTS controls to main interface ← YOU ARE HERE

```python

# Voice mapping (transparent to frontend)---

VOICE_MAP = {

    "tara": "expr-voice-2-f",  # Clear, professional**All TTS functionality is now easily accessible!** 🎙️✨

    "leah": "expr-voice-3-f",  # Warm, friendly
    "jess": "expr-voice-4-f",  # Energetic
    "mia": "expr-voice-5-f",   # Mysterious
    "leo": "expr-voice-2-m",   # Authoritative
    "dan": "expr-voice-3-m",   # Classic
    "zac": "expr-voice-4-m",   # Enthusiastic
    "zoe": "expr-voice-5-m",   # Versatile
}

# Initialize Kitten TTS model
model = KittenTTS("KittenML/kitten-tts-nano-0.2")

# Generate audio (CPU-optimized, ~1.2s per sentence)
audio = model.generate(text, voice=VOICE_MAP[voice])
```

## Key Features

✅ **CPU-Optimized** - No GPU/CUDA required (Kitten TTS)
✅ **Lightweight** - Model under 25MB, fast loading
✅ **Visible Controls** - No need to open settings
✅ **Voice Selection** - 8 unique voices per message
✅ **Auto-play Option** - Immersive or manual control
✅ **Status Indicator** - Always know TTS state
✅ **Persistent State** - Settings saved per session
✅ **Compact UI** - Doesn't clutter chat interface

## Technical Specifications

### Kitten TTS Engine

- **Model:** KittenML/kitten-tts-nano-0.2
- **Size:** ~24MB (ONNX format)
- **Hardware:** CPU-only (no GPU required!)
- **Performance:** ~1.2s generation per sentence
- **Quality:** High-quality natural speech
- **License:** Apache 2.0

### Audio Format

- **Format:** WAV (uncompressed)
- **Sample Rate:** 24000 Hz
- **Channels:** Mono
- **Bit Depth:** 16-bit PCM

### Installation

```powershell
pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl
pip install soundfile
```

## Migration from Orpheus TTS

### What Changed

- ✅ No CUDA dependency (CPU-optimized)
- ✅ Smaller model (25MB vs larger)
- ✅ Same 8 voice names (no frontend changes)
- ⚠️ Emotion tags not supported (e.g., `<laugh>`, `<sigh>`)

### Frontend Impact

**None!** The migration is transparent:

- Same voice names (tara, leah, etc.)
- Same API endpoint
- Same UI components
- Drop-in replacement

## Commit History

- **8c40e89** - Phase 3: Narrative engine MCP integration
- **cf6af08** - Phase 4: DM chat handler D&D commands
- **b98eb6b** - Add visible TTS controls to main interface
- **[TODAY]** - Migrate to Kitten TTS (CPU-optimized) ← YOU ARE HERE

---

**All TTS functionality now works on CPU!** 🎙️✨

No more CUDA errors. No more GPU requirements.  
Just lightweight, high-quality voice narration for your D&D adventures!
