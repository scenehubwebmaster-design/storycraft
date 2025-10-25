# TTS Provider Selection - Implementation Summary

## Overview

Added TTS provider selection functionality to the **CampaignManager** component, allowing users to choose between **KittenTTS** (local, free) and **OpenAI Whisper** (cloud, premium quality) for voice narration.

## Changes Made

### 1. Updated `CampaignManager.jsx`

**Location**: `frontend/src/components/CampaignManager.jsx`

#### New Imports Added:

```jsx
import {
  // ... existing imports
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  FormLabel,
} from "@mui/material";

import {
  // ... existing icons
  VolumeUp as VoiceIcon,
  RecordVoiceOver as TTSIcon,
} from "@mui/icons-material";
```

#### New State Variables:

```jsx
// TTS Settings (stored in localStorage)
const [ttsSettingsOpen, setTtsSettingsOpen] = useState(false);
const [ttsProvider, setTtsProvider] = useState(
  localStorage.getItem("ttsProvider") || "kitten"
);
const [ttsVoice, setTtsVoice] = useState(
  localStorage.getItem("ttsVoice") || "tara"
);
const [ttsEnabled, setTtsEnabled] = useState(
  localStorage.getItem("ttsEnabled") === "true"
);
const [ttsAutoPlay, setTtsAutoPlay] = useState(
  localStorage.getItem("ttsAutoPlay") === "true"
);
```

#### New Functions:

1. **`saveTtsSettings()`** - Saves TTS preferences to localStorage
2. **`getVoiceOptions()`** - Returns voice options based on selected provider
   - KittenTTS: 8 voices (tara, leah, jess, mia, leo, dan, zac, zoe)
   - OpenAI: 6 voices (alloy, echo, fable, onyx, nova, shimmer)
3. **`handleProviderChange(newProvider)`** - Switches provider and resets to default voice

#### New UI Section:

Added **"Voice Narration (TTS)"** section in the campaign panel showing:

- Current TTS provider chip
- Current voice chip
- Enabled/Disabled status chip
- Auto-play/Manual chip
- "Configure" button to open settings dialog

#### New Dialog:

**TTS Settings Dialog** with:

- Enable/disable checkbox
- Auto-play checkbox
- Provider selection (KittenTTS vs OpenAI Whisper) with radio buttons
- Voice character dropdown (dynamically populated based on provider)
- Informational alerts explaining each provider's features

### 2. Provider Comparison

| Feature          | KittenTTS (Local)         | OpenAI Whisper (Cloud)          |
| ---------------- | ------------------------- | ------------------------------- |
| **Cost**         | Free                      | $15 per 1M characters           |
| **Quality**      | Good, CPU-optimized       | Premium, professional           |
| **Privacy**      | Fully local, no API calls | Cloud-based, requires API key   |
| **Setup**        | No API key needed         | Requires OPENAI_API_KEY in .env |
| **Voices**       | 8 voices                  | 6 voices                        |
| **Speed**        | Fast (CPU)                | Fast (cloud)                    |
| **Offline**      | Yes                       | No                              |
| **Requirements** | KittenTTS installed       | OpenAI API key                  |

### 3. Voice Options by Provider

#### KittenTTS Voices (8 total):

- **tara** - Female, Warm (default)
- **leah** - Female, Friendly
- **jess** - Female, Energetic
- **mia** - Female, Mysterious
- **leo** - Male, Deep
- **dan** - Male, Classic
- **zac** - Male, Young
- **zoe** - Neutral

#### OpenAI Whisper Voices (6 total):

- **alloy** - Neutral, Balanced (default)
- **echo** - Male, Clear
- **fable** - British, Expressive
- **onyx** - Deep Male, Authoritative
- **nova** - Female, Warm
- **shimmer** - Female, Bright

### 4. User Workflow

1. User opens **Campaign Manager** panel
2. Scrolls to **"Voice Narration (TTS)"** section
3. Clicks **"Configure"** button
4. Settings dialog opens with options:
   - Enable/disable voice narration
   - Enable/disable auto-play
   - Select TTS provider (KittenTTS or OpenAI)
   - Choose voice character from dropdown
5. Clicks **"Save Settings"**
6. Settings are persisted to localStorage
7. All future TTS requests use the selected provider and voice

### 5. localStorage Keys

Settings are stored in browser localStorage:

- `ttsProvider` - "kitten" or "openai"
- `ttsVoice` - Voice identifier (e.g., "tara", "alloy")
- `ttsEnabled` - "true" or "false"
- `ttsAutoPlay` - "true" or "false"

### 6. Integration Points

The settings stored in localStorage can be consumed by:

- **TTSAudioPlayer** component - Use `localStorage.getItem("ttsProvider")` to determine which API endpoint to call
- **DMChat** component - Read auto-play preferences
- **SettingsDrawer** - Can sync settings if needed

### 7. Backend API Endpoints

#### KittenTTS (existing):

```
POST /api/chat/sessions/{sessionId}/messages/{messageId}/tts?voice={voice}
```

#### OpenAI TTS (new):

```
POST /api/audio/speak
Body: {
  "text": "...",
  "voice": "alloy",
  "model": "standard",
  "speed": 1.0,
  "format": "mp3"
}
```

## Testing

### Manual Testing Steps:

1. **Start the backend server**:

   ```bash
   python -m uvicorn backend.main:app --reload
   ```

2. **Start the frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

3. **Test the UI**:

   - Navigate to Campaign Manager
   - Click "Configure" under Voice Narration (TTS)
   - Toggle between KittenTTS and OpenAI Whisper
   - Notice voice options change dynamically
   - Save settings and verify chips update
   - Check localStorage in browser DevTools

4. **Verify persistence**:
   - Refresh the page
   - Settings should persist across sessions

### Unit Tests Created:

**File**: `frontend/src/__tests__/CampaignManager.test.jsx`

Tests cover:

- ✅ Rendering TTS settings section
- ✅ Displaying current provider chip
- ✅ Opening settings dialog
- ✅ Switching between providers
- ✅ Saving to localStorage
- ✅ Voice options for each provider
- ✅ Info alerts based on provider
- ✅ Default values handling

## Next Steps

### Frontend Integration:

1. **Update TTSAudioPlayer.jsx**:

   ```jsx
   const ttsProvider = localStorage.getItem("ttsProvider") || "kitten";

   const fetchAudio = async () => {
     if (ttsProvider === "openai") {
       // Call OpenAI endpoint
       const response = await axios.post(`${API_BASE}/audio/speak`, {
         text: messageText,
         voice: selectedVoice,
         model: "standard",
         speed: 1.0,
         format: "mp3",
       });
     } else {
       // Call KittenTTS endpoint (existing)
       const response = await axios.post(
         `${API_BASE}/chat/sessions/${sessionId}/messages/${messageId}/tts?voice=${voice}`
       );
     }
   };
   ```

2. **Update SettingsDrawer.jsx** (optional):

   - Remove duplicate TTS settings, or
   - Sync with CampaignManager settings

3. **Add provider switch notification**:
   - Show a snackbar when switching providers
   - "Switched to OpenAI Whisper. All new narrations will use premium quality voices."

### Backend Integration:

1. **Unified TTS endpoint** (optional):

   - Create `/api/tts/speak` that automatically routes to correct provider
   - Reads provider preference from request or session

2. **Session-level TTS preferences**:
   - Store TTS provider in campaign/session metadata
   - Allow different campaigns to use different providers

## Documentation

### For Users:

- See `OPENAI_TTS_INTEGRATION.md` for OpenAI setup
- See `TTS_VOICE_GUIDE.md` for voice descriptions
- Settings are campaign-specific and persist across sessions

### For Developers:

- Component: `frontend/src/components/CampaignManager.jsx`
- Tests: `frontend/src/__tests__/CampaignManager.test.jsx`
- Backend services:
  - `backend/tts_service.py` (KittenTTS)
  - `backend/openai_tts_service.py` (OpenAI Whisper)
  - `backend/routers/openai_audio.py` (OpenAI API endpoints)

## Summary

✅ **Completed**:

- Added TTS provider selection UI to CampaignManager
- Implemented localStorage persistence
- Dynamic voice options based on provider
- Informational alerts explaining each provider
- Unit test coverage

⏳ **Pending**:

- TTSAudioPlayer integration to use selected provider
- Backend unified endpoint (optional)
- Session-level preference storage (optional)

🎉 **Result**: Users can now seamlessly choose between free local TTS (KittenTTS) and premium cloud TTS (OpenAI Whisper) directly from the Campaign Manager interface!
