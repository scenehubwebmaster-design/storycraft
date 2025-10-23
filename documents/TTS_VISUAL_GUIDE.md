# TTS Controls - Visual Guide

## What You Should See

After the changes, each DM message in the chat will now show:

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│ 👤 [Avatar]  ┌─────────────────────────────┐   │
│              │ Dungeon Master              │   │
│              │                             │   │
│              │ [Message text content]      │   │
│              └─────────────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ DM Voice: [Tara (Female, Warm)  ▼]      │  │
│  │                                          │  │
│  │ ☐ RP Text Only (skip mechanics)         │  │
│  │                                          │  │
│  │ [▶️] [⏹️]  ━━━━━━━━●━━━━━  [🔊] ━━━━━●  │  │
│  │           0:05        0:45               │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Components Visible

1. **Voice Selector Dropdown**

   - Label: "DM Voice"
   - Shows current voice (default: "Tara (Female, Warm)")
   - Click to see all 8 voice options
   - Icon: 🎤 on the left

2. **RP Text Only Checkbox** ⭐ NEW

   - Label: "RP Text Only (skip mechanics)"
   - Unchecked by default
   - Below the voice selector

3. **Playback Controls**
   - Play/Pause button (▶️/⏸️)
   - Stop button (⏹️)
   - Progress bar with timestamps
   - Volume control (🔊) with slider

## Before vs After

### BEFORE (Compact Mode)

```
┌───────────────────────────────────┐
│ 👤 [Avatar]  [Message bubble]     │
│              [▶️] Loading...      │
└───────────────────────────────────┘
```

- Only shows play button
- No voice selector
- No RP Text Only toggle

### AFTER (Full Mode with Voice Selector)

```
┌─────────────────────────────────────────────────┐
│ 👤 [Avatar]  [Message bubble]                   │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ DM Voice: [Tara  ▼]                        │ │
│  │ ☐ RP Text Only (skip mechanics)            │ │
│  │ [▶️] [⏹️]  Progress bar  [🔊] Volume       │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

- Full audio player
- Voice selector dropdown ✅
- RP Text Only checkbox ✅
- All playback controls

## How to Test

1. **Restart your frontend dev server** (if running):

   ```bash
   cd e:\storycraft\frontend
   npm run dev
   ```

2. **Navigate to DMChat** in your browser

3. **Enable TTS** (Voice Narration checkbox at top)

4. **Send a message** to the DM (e.g., "Tell me about the Lightning Bolt spell")

5. **Look below the DM's response** - You should see:
   - A voice selector dropdown
   - The new "RP Text Only (skip mechanics)" checkbox
   - Full playback controls

## Testing the Feature

### Test 1: Voice Selection

1. Click the voice dropdown
2. Select a different voice (e.g., "Leo (Male, Deep)")
3. Audio should regenerate with the new voice

### Test 2: RP Text Only Toggle

1. Request a spell description: "Tell me about Lightning Bolt"
2. Play the audio (should be ~30-40 seconds, full text)
3. Check the "RP Text Only (skip mechanics)" box
4. Audio should regenerate (~10-15 seconds, only flavor text)
5. Uncheck the box - audio regenerates with full text again

### Test 3: Both Together

1. Select voice "Mia (Female, Mysterious)"
2. Check "RP Text Only (skip mechanics)"
3. Request a spell description
4. Should hear Mia's voice narrating only the flavor text

## Troubleshooting

### "I still see the compact player"

- Make sure you've saved the file changes
- Restart the frontend dev server
- Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

### "Voice selector is visible but checkbox is missing"

- Check browser console for errors
- Verify TTSAudioPlayer.jsx has the checkbox code
- Ensure you're using the latest version of the file

### "Changes aren't taking effect"

1. Stop frontend dev server (Ctrl+C)
2. Clear browser cache
3. Restart dev server: `npm run dev`
4. Hard refresh browser

## Expected File Changes

After this update, `DMChatPanel.jsx` now renders:

```jsx
<TTSAudioPlayer
  sessionId={sessionId}
  messageId={msg.id}
  autoPlay={ttsAutoPlay}
  showVoiceSelector={true} // ✅ Changed from compact={true}
  compact={false} // ✅ Explicitly set to false
/>
```

The audio player now appears **below** the message bubble with full width, showing all controls including the voice selector and RP Text Only checkbox.
