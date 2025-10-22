# TTS UI Location Map

## DMChat.jsx - Main Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🏰 Dungeon Master Chat                          [Settings] │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Session Controls ─────────────────────────────────────┐ │
│  │                                                          │ │
│  │  ☑ RAG Context    [Context (k): 5]  [RAG Enabled]      │ │
│  │                                                          │ │
│  │  ─────────────────────────────────────────────────────  │ │  ← Divider
│  │                                                          │ │
│  │  ☑ Voice    ☑ Auto-play    [Voice: Auto]     ← NEW!    │ │
│  │     ↑          ↑              ↑                          │ │
│  │     │          │              └─ Status chip             │ │
│  │     │          └─ Auto-play DM responses                 │ │
│  │     └─ Enable voice narration                           │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Chat Messages ─────────────────────────────────────────┐ │
│  │                                                          │ │
│  │  [Avatar] Dungeon Master                                │ │
│  │           "You enter a dark tavern..."                  │ │
│  │                                                          │ │
│  │           ┌─ TTSAudioPlayer ─────────────────────┐      │ │
│  │           │ [Voice: Tara ▼] [▶ Play] 0:00 / 0:05 │      │ │
│  │           │   ↑                                   │      │ │
│  │           │   └─ Voice selector dropdown          │      │ │
│  │           └───────────────────────────────────────┘      │ │
│  │                                                          │ │
│  │  [Avatar] You                                           │ │
│  │           "I approach the barkeep"                      │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [Type your message...                          ] [Send →]  │
└─────────────────────────────────────────────────────────────┘
```

## TTSAudioPlayer.jsx - Component Detail

```
┌─ TTSAudioPlayer Component ─────────────────────────────────┐
│                                                             │
│  Compact Mode (in chat messages):                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ [Voice: Tara ▼]  [▶]  0:00 / 0:05  [🔊]            │  │
│  │    ↑            ↑      ↑              ↑              │  │
│  │    │            │      │              └─ Volume      │  │
│  │    │            │      └─ Progress bar               │  │
│  │    │            └─ Play/Pause button                 │  │
│  │    └─ Voice selector (8 options)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Full Mode (in GameSession page):                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 🎙️ Dungeon Master Narration                          │  │
│  │                                                       │  │
│  │ Voice: [Tara (Female)      ▼]                        │  │
│  │                                                       │  │
│  │ [▶ Play]  ━━━━━━━━○━━━━━━━  0:03 / 0:05            │  │
│  │                                                       │  │
│  │ Volume: [━━━━━━●━━━] 70%                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Voice Selector Dropdown

```
┌─ Select Voice ──────┐
│ ✓ Tara (Female)     │ ← Currently selected
│   Leah (Female)     │
│   Jess (Female)     │
│   Mia (Female)      │
│   Leo (Male)        │
│   Dan (Male)        │
│   Zac (Male)        │
│   Zoe (Neutral)     │
└─────────────────────┘
```

## Settings Drawer (Alternative Access)

```
┌─ Settings Drawer ───────────────────┐
│                                     │
│  ⚙️ Session Settings                │
│                                     │
│  Provider: [Groq            ▼]     │
│  Model: [mixtral-8x7b       ▼]     │
│                                     │
│  ────────────────────────────────  │
│                                     │
│  🔊 Voice Narration (TTS)          │
│                                     │
│  ☑ Enable Voice Narration          │
│  ☑ Auto-play Responses             │
│                                     │
│  ────────────────────────────────  │
│                                     │
│  📖 RAG Settings                    │
│  ☑ Include Context                 │
│  Top K: [5]                        │
│                                     │
└─────────────────────────────────────┘
```

## User Flow: Enabling TTS

### Quick Path (NEW):

1. Open DMChat page
2. Select or create a session
3. See session controls at top
4. ✅ Check "Voice" checkbox
5. ✅ Check "Auto-play" (optional)
6. Send message
7. DM response auto-plays with audio

### Manual Voice Selection:

1. After DM responds
2. Audio player appears below message
3. Click voice dropdown "Tara ▼"
4. Select preferred voice
5. Click ▶ Play to hear
6. Next response uses new voice

### Settings Path (Original):

1. Click ⚙️ Settings icon (top right)
2. Scroll to "Voice Narration (TTS)"
3. Toggle switches
4. Close drawer
5. TTS enabled for session

## Integration Points

### DMChat.jsx

```jsx
// Lines 76-77: State management
const [ttsEnabled, setTtsEnabled] = useState(true);
const [ttsAutoPlay, setTtsAutoPlay] = useState(false);

// Lines 710-756: NEW visible controls
<FormControlLabel
  control={<Checkbox checked={ttsEnabled} />}
  label={<Stack><VolumeUpIcon /><Typography>Voice</Typography></Stack>}
/>
<FormControlLabel
  control={<Checkbox checked={ttsAutoPlay} />}
  label={<Stack><PlayArrowIcon /><Typography>Auto-play</Typography></Stack>}
/>
<Chip label={ttsAutoPlay ? "Voice: Auto" : "Voice: Manual"} />

// Lines 870-889: Audio player in messages
{msg.role === "assistant" && ttsEnabled && (
  <TTSAudioPlayer
    sessionId={selectedSession.id}
    messageId={msg.id}
    autoPlay={ttsAutoPlay}
  />
)}
```

### DMChatPanel.jsx

```jsx
// Lines 29-35: Props
function DMChatPanel({
  messages = [],
  sessionId = null,
  ttsEnabled = true, // ← Passed from parent
  ttsAutoPlay = false, // ← Passed from parent
}) {
  // Lines 163-175: Audio player rendering
  isDM && ttsEnabled && msg.id && sessionId && (
    <TTSAudioPlayer
      sessionId={sessionId}
      messageId={msg.id}
      autoPlay={ttsAutoPlay}
      compact={true} // ← Compact UI for chat
    />
  );
}
```

### TTSAudioPlayer.jsx

```jsx
// Lines 15-18: State with voice selection
const [selectedVoice, setSelectedVoice] = useState("tara");
const [isPlaying, setIsPlaying] = useState(false);
const [volume, setVolume] = useState(0.7);

// Lines 45-58: Voice selector
<Select
  value={selectedVoice}
  onChange={(e) => setSelectedVoice(e.target.value)}
>
  <MenuItem value="tara">Tara (Female)</MenuItem>
  <MenuItem value="leah">Leah (Female)</MenuItem>
  {/* ... 6 more voices */}
</Select>;

// Lines 80-85: Fetch audio with voice parameter
const audioUrl = `/api/game-chat/tts/${sessionId}/${messageId}?voice=${selectedVoice}`;
```

## Key Features

✅ **Visible Controls** - No need to open settings
✅ **Voice Selection** - 8 unique voices per message
✅ **Auto-play Option** - Immersive or manual control
✅ **Status Indicator** - Always know TTS state
✅ **Persistent State** - Settings saved per session
✅ **Compact UI** - Doesn't clutter chat interface

## Commit History

- **8c40e89** - Phase 3: Narrative engine MCP integration
- **cf6af08** - Phase 4: DM chat handler D&D commands
- **b98eb6b** - Add visible TTS controls to main interface ← YOU ARE HERE

---

**All TTS functionality is now easily accessible!** 🎙️✨
