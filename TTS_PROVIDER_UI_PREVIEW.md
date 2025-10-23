# Voice Narration (TTS) Provider Selection UI

## Visual Preview

### Campaign Manager Panel - New TTS Section

```
┌─────────────────────────────────────────────────────────────┐
│ 📜 Test Campaign                                        ⚙️  │
│ A test D&D campaign description...                          │
│                                                              │
│ ┌────────┐ ┌────────────────┐ ┌──────────┐                 │
│ │⭐ Lvl 5 │ │💬 ROLEPLAY     │ │ Sword... │                 │
│ └────────┘ └────────────────┘ └──────────┘                 │
│                                                              │
│ ══════════════════════════════════════════════════════════  │
│                                                              │
│ 📊 Experience Points                    [Award XP]          │
│ 2,500 / 6,500 XP to Level 6                                 │
│ ▓▓▓▓▓▓▓▓░░░░░░░░░░░░ 38%                                    │
│ Total XP: 2,500                                             │
│                                                              │
│ ══════════════════════════════════════════════════════════  │
│                                                              │
│ Party (2)                                                    │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ Test Hero                           50/100 HP        │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ ══════════════════════════════════════════════════════════  │
│                                                              │
│ 🔊 Voice Narration (TTS)                    [Configure]     │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 🎙️ Provider: KittenTTS   Voice: tara   ✅ Enabled      │    │
│ │ Auto-play                                            │    │
│ └──────────────────────────────────────────────────────┘    │
│ Choose between KittenTTS (local, free) or OpenAI...         │
│                                                              │
│ ══════════════════════════════════════════════════════════  │
│                                                              │
│ 💾 Save Progress                                             │
│ Create checkpoints to save campaign progress...             │
│ [Checkpoint Manager Component]                              │
└─────────────────────────────────────────────────────────────┘
```

### TTS Settings Dialog (Opened after clicking "Configure")

```
┌──────────────────────────────────────────────────────┐
│ 🔊 Voice Narration Settings                     ✕   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ☑ Enable Voice Narration                            │
│                                                      │
│ ☑ Auto-play DM Responses                            │
│                                                      │
│ ──────────────────────────────────────────────────── │
│                                                      │
│ TTS Provider                                         │
│                                                      │
│ ◉ KittenTTS (Local)                                 │
│   Free • CPU-optimized • No API key • 8 voices      │
│                                                      │
│ ○ OpenAI Whisper (Cloud)                            │
│   Premium • Requires API key • 6 voices • $15/1M    │
│                                                      │
│ ──────────────────────────────────────────────────── │
│                                                      │
│ Voice Character ▼                                    │
│ ┌────────────────────────────────────────────────┐  │
│ │ Tara (Female, Warm)                        ✓  │  │
│ │ Leah (Female, Friendly)                       │  │
│ │ Jess (Female, Energetic)                      │  │
│ │ Mia (Female, Mysterious)                      │  │
│ │ Leo (Male, Deep)                              │  │
│ │ Dan (Male, Classic)                           │  │
│ │ Zac (Male, Young)                             │  │
│ │ Zoe (Neutral)                                 │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ ℹ️ KittenTTS                                    │  │
│ │                                                │  │
│ │ Ultra-lightweight local TTS (under 25MB).     │  │
│ │ Runs on CPU with no GPU required. Perfect     │  │
│ │ for offline use and privacy-conscious users.  │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│                           [Cancel] [Save Settings]   │
└──────────────────────────────────────────────────────┘
```

### When OpenAI Whisper is Selected

```
┌──────────────────────────────────────────────────────┐
│ 🔊 Voice Narration Settings                     ✕   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ☑ Enable Voice Narration                            │
│                                                      │
│ ☑ Auto-play DM Responses                            │
│                                                      │
│ ──────────────────────────────────────────────────── │
│                                                      │
│ TTS Provider                                         │
│                                                      │
│ ○ KittenTTS (Local)                                 │
│   Free • CPU-optimized • No API key • 8 voices      │
│                                                      │
│ ◉ OpenAI Whisper (Cloud)                            │
│   Premium • Requires API key • 6 voices • $15/1M    │
│                                                      │
│ ──────────────────────────────────────────────────── │
│                                                      │
│ Voice Character ▼                                    │
│ ┌────────────────────────────────────────────────┐  │
│ │ Alloy (Neutral, Balanced)                  ✓  │  │
│ │ Echo (Male, Clear)                            │  │
│ │ Fable (British, Expressive)                   │  │
│ │ Onyx (Deep Male, Authoritative)               │  │
│ │ Nova (Female, Warm)                           │  │
│ │ Shimmer (Female, Bright)                      │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ ℹ️ OpenAI Whisper TTS                          │  │
│ │                                                │  │
│ │ Uses OpenAI's professional text-to-speech     │  │
│ │ API. Requires an OpenAI API key configured    │  │
│ │ in your backend .env file. Offers high-       │  │
│ │ quality neural voices with natural intonation │  │
│ │ and emotion.                                   │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│                           [Cancel] [Save Settings]   │
└──────────────────────────────────────────────────────┘
```

## Feature Highlights

### ✨ Key Features

1. **Seamless Provider Switching**

   - Toggle between KittenTTS (local) and OpenAI Whisper (cloud)
   - Voice options automatically update based on provider
   - Settings persist across browser sessions

2. **Smart Defaults**

   - KittenTTS: Default voice is "tara" (Female, Warm)
   - OpenAI Whisper: Default voice is "alloy" (Neutral, Balanced)
   - When switching providers, automatically sets appropriate default voice

3. **Visual Feedback**

   - Status chips show current configuration at a glance
   - Color-coded chips (primary for enabled, outlined for details)
   - Clear information alerts explaining each provider

4. **localStorage Persistence**

   - All settings saved to browser localStorage
   - Survives page refreshes
   - Campaign-specific settings (can be extended)

5. **Responsive Design**
   - Chips wrap on smaller screens
   - Dialog is responsive (maxWidth: "sm")
   - Touch-friendly controls

### 🎯 User Benefits

| Benefit                  | Description                                                             |
| ------------------------ | ----------------------------------------------------------------------- |
| **Flexibility**          | Choose the TTS provider that fits your needs                            |
| **Cost Control**         | Use free KittenTTS for casual play, premium OpenAI for special sessions |
| **Quality Options**      | 8 diverse voices (Kitten) or 6 professional voices (OpenAI)             |
| **Privacy**              | Keep narration local with KittenTTS                                     |
| **Professional Quality** | Upgrade to OpenAI for high-quality voices                               |
| **Easy Switching**       | Change providers anytime without code changes                           |

### 📊 Comparison Table

| Feature          | KittenTTS      | OpenAI Whisper      |
| ---------------- | -------------- | ------------------- |
| **Cost**         | 🟢 Free        | 🟡 $15 per 1M chars |
| **Quality**      | 🟡 Good        | 🟢 Premium          |
| **Speed**        | 🟢 Fast (CPU)  | 🟢 Fast (Cloud)     |
| **Privacy**      | 🟢 Fully Local | 🔴 Cloud-based      |
| **Offline**      | 🟢 Yes         | 🔴 No               |
| **Setup**        | 🟢 No API Key  | 🟡 Requires API Key |
| **Voices**       | 🟢 8 voices    | 🟡 6 voices         |
| **Requirements** | Python package | API key + internet  |

### 🔄 State Management

```javascript
// Settings stored in localStorage
{
  "ttsProvider": "kitten",    // or "openai"
  "ttsVoice": "tara",         // or "alloy"
  "ttsEnabled": "true",       // or "false"
  "ttsAutoPlay": "true"       // or "false"
}
```

### 🎨 UI Components Used

- **Material-UI Chips**: Provider, voice, status display
- **Radio Buttons**: Provider selection
- **Checkboxes**: Enable/disable options
- **Select Dropdown**: Voice selection
- **Alert**: Informational messages
- **Dialog**: Modal settings editor

### 🚀 Next Integration Steps

1. **TTSAudioPlayer Integration**:

   - Read `localStorage.getItem("ttsProvider")`
   - Route to correct backend endpoint based on provider
   - Use saved voice preference

2. **Backend Routing**:

   - Detect provider from request
   - Route to KittenTTS or OpenAI service
   - Return audio in appropriate format

3. **Error Handling**:
   - Show user-friendly message if OpenAI API key missing
   - Fall back to KittenTTS if OpenAI fails
   - Display quota warnings for OpenAI usage

## Example Usage

### Scenario 1: Casual Home Game (KittenTTS)

```
Settings:
- Provider: KittenTTS
- Voice: Dan (Male, Classic)
- Enabled: Yes
- Auto-play: Yes

Result: Free, local narration with no API costs
```

### Scenario 2: Professional Stream (OpenAI)

```
Settings:
- Provider: OpenAI Whisper
- Voice: Onyx (Deep Male, Authoritative)
- Enabled: Yes
- Auto-play: Yes

Result: Premium quality narration for professional content
```

### Scenario 3: Privacy-Focused (KittenTTS)

```
Settings:
- Provider: KittenTTS
- Voice: Mia (Female, Mysterious)
- Enabled: Yes
- Auto-play: No

Result: No data sent to cloud, fully offline capable
```

---

**Implementation Date**: October 23, 2025  
**Component**: `CampaignManager.jsx`  
**Status**: ✅ Complete - Ready for Integration
