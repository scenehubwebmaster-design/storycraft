# SettingsDrawer TTS Provider Selection Update

## Overview

Updated `SettingsDrawer.jsx` to include TTS provider selection (KittenTTS vs OpenAI Whisper) with database-backed persistence, matching the implementation in `CampaignManager.jsx`.

## Changes Made

### 1. Added Database Integration

**New Imports:**

- `useEffect` - For loading settings on mount
- `Chip` - For provider selection UI

**New State Variables:**

```javascript
const [ttsProvider, setTtsProvider] = useState("kitten");
const [settingsLoaded, setSettingsLoaded] = useState(false);
```

**Load Settings Function:**

```javascript
const loadTtsSettings = async () => {
  const response = await fetch("http://localhost:8000/api/settings/tts");
  const settings = await response.json();
  setTtsProvider(settings.tts_provider || "kitten");
  setTtsEnabled(settings.tts_enabled ?? true);
  setTtsAutoPlay(settings.tts_auto_play ?? false);
  setTtsVoice(settings.tts_voice || "tara");
};
```

**Auto-save on Change:**

```javascript
useEffect(() => {
  if (settingsLoaded) {
    saveTtsSettings();
  }
}, [ttsProvider, ttsVoice, ttsEnabled, ttsAutoPlay]);
```

### 2. Added TTS Provider Selection UI

**Provider Selection Chips:**

```javascript
<Stack direction="row" spacing={1}>
  <Chip
    label="KittenTTS"
    color={ttsProvider === "kitten" ? "primary" : "default"}
    onClick={() => setTtsProvider("kitten")}
    variant={ttsProvider === "kitten" ? "filled" : "outlined"}
  />
  <Chip
    label="OpenAI Whisper"
    color={ttsProvider === "openai" ? "primary" : "default"}
    onClick={() => setTtsProvider("openai")}
    variant={ttsProvider === "openai" ? "filled" : "outlined"}
  />
</Stack>
```

**Provider Description:**

- KittenTTS: "Local, free TTS (8 voices)"
- OpenAI Whisper: "Cloud-based, premium quality (6 voices)"

### 3. Dynamic Voice Options

**Voice Selection Function:**

```javascript
const getVoiceOptions = () => {
  if (ttsProvider === "openai") {
    return [
      { value: "alloy", label: "Alloy (Neutral)" },
      { value: "echo", label: "Echo (Male)" },
      { value: "fable", label: "Fable (British Male)" },
      { value: "onyx", label: "Onyx (Deep Male)" },
      { value: "nova", label: "Nova (Female)" },
      { value: "shimmer", label: "Shimmer (Soft Female)" },
    ];
  }
  // KittenTTS voices (8 options)
  return [...];
};
```

**Updated Voice Select:**

```javascript
<Select value={ttsVoice} label="Voice Character">
  {getVoiceOptions().map((voice) => (
    <MenuItem key={voice.value} value={voice.value}>
      {voice.label}
    </MenuItem>
  ))}
</Select>
```

## UI Layout

### TTS Settings Accordion (Expanded View)

```
┌─────────────────────────────────────────────┐
│ 🔊 Voice Narration (TTS)              ▼    │
├─────────────────────────────────────────────┤
│                                             │
│ ☑ Enable Voice Narration                   │
│                                             │
│ ☑ Auto-play DM Responses                   │
│                                             │
│ TTS Provider                                │
│ ┌──────────┐ ┌──────────────────┐          │
│ │ KittenTTS│ │ OpenAI Whisper   │          │
│ └──────────┘ └──────────────────┘          │
│ Local, free TTS (8 voices)                 │
│                                             │
│ Voice Character                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 🎙️ Tara (Female, Warm)         ▼      │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ☑ Narrate RP Text Only (skip stats)        │
│                                             │
│ Text-to-speech converts DM messages...     │
└─────────────────────────────────────────────┘
```

## Features

✅ **Database-Backed Persistence**

- Settings load from `/api/settings/tts` on mount
- Auto-save to database when any setting changes
- No localStorage dependencies

✅ **Provider Selection**

- Visual chip-based selection
- Clear provider descriptions
- Instant voice list updates

✅ **Dynamic Voice Options**

- KittenTTS: 8 voices (Tara, Leah, Jess, Mia, Leo, Dan, Zac, Zoe)
- OpenAI Whisper: 6 voices (Alloy, Echo, Fable, Onyx, Nova, Shimmer)

✅ **Consistent UX**

- Matches CampaignManager implementation
- Material-UI design system
- Responsive layout

## API Integration

### Endpoints Used

- **GET `/api/settings/tts`** - Load TTS settings
- **PATCH `/api/settings/`** - Save TTS settings

### Settings Payload

```json
{
  "tts_provider": "openai",
  "tts_voice": "nova",
  "tts_enabled": true,
  "tts_auto_play": true
}
```

## Testing

### Manual Test Steps

1. **Start Backend & Frontend:**

   ```bash
   # Terminal 1: Backend
   python -m uvicorn backend.main:app --reload

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Open Settings Drawer:**

   - Click settings icon in app
   - Expand "Voice Narration (TTS)" accordion

3. **Test Provider Selection:**

   - Click "KittenTTS" chip → Voice list shows 8 KittenTTS voices
   - Click "OpenAI Whisper" chip → Voice list shows 6 OpenAI voices
   - Select different voice → Setting saved automatically

4. **Verify Persistence:**

   - Change provider and voice
   - Refresh page
   - Open settings drawer
   - Confirm selections persisted

5. **Test Database:**
   ```bash
   sqlite3 storycraft.db "SELECT tts_provider, tts_voice FROM user_settings;"
   ```

## Benefits

### Before (Hardcoded)

- ❌ Only KittenTTS voices shown
- ❌ No OpenAI Whisper option
- ❌ Inconsistent with CampaignManager
- ❌ Settings not persisted

### After (Database-Backed)

- ✅ Both providers available
- ✅ Dynamic voice options
- ✅ Consistent across components
- ✅ Settings persist in database
- ✅ Auto-save on change

## Related Files

- `frontend/src/components/SettingsDrawer.jsx` - **UPDATED** with provider selection
- `frontend/src/components/CampaignManager.jsx` - Already has provider selection
- `backend/routers/user_settings.py` - Settings API
- `backend/models.py` - UserSettings model
- `DATABASE_USER_SETTINGS.md` - Full documentation

## Next Steps

1. **Update TTSAudioPlayer.jsx** - Read provider from database and route to correct endpoint
2. **Test with actual TTS** - Verify both providers work end-to-end
3. **Add unified TTS endpoint** - `/api/tts/speak` that auto-routes based on settings
4. **Update other components** - Ensure all TTS consumers use database settings

---

**Update Date**: October 23, 2025
**Status**: ✅ Complete - Ready for testing
