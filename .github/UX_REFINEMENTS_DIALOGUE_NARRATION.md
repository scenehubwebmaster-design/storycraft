# UX Refinements & Dialogue Narration Feature

## Summary of Changes

This update implements four major refinements to improve the user experience and add immersive dialogue narration:

1. ✅ **Skip text animations on campaign revisit** - Existing messages display instantly
2. ✅ **Fix auto-scroll to message container only** - No more outer scrollbar jumping
3. ✅ **Full text to KittenTTS with chunking** - No more 500-char truncation
4. ✅ **Dialogue narration feature** - Sequential dialogue playback with voice assignment

---

## 1. Skip Text Animations on Revisit

### Problem

When returning to an ongoing campaign, all previous DM messages would replay the typing animation, forcing users to wait before reading.

### Solution

Added `hasAnimatedRef` to track whether a message has already been animated. Messages with IDs (from database) that haven't been animated yet are considered "existing" and display instantly.

**File**: `frontend/src/components/game/CinematicMessageCard.jsx`

```javascript
const hasAnimatedRef = useRef(false);

// Check if message is "new" or "existing"
const isExistingMessage = message.id && !hasAnimatedRef.current;

if (isExistingMessage) {
  // Skip animation for existing messages
  setDisplayedText(message.content);
  setIsTyping(false);
  hasAnimatedRef.current = true;
  return;
}
```

**Benefits**:

- Instant text display on page reload
- Typing animation only plays for NEW messages
- Better UX for reviewing conversation history

---

## 2. Fix Auto-Scroll to Message Container

### Problem

The typing animation's auto-scroll was affecting the outer page scrollbar, causing the entire viewport to jump unexpectedly.

### Solution

Added `messageCardRef` to the message card and made it scroll itself into view instead of relying on the parent's `bottomRef`.

**File**: `frontend/src/components/game/CinematicMessageCard.jsx`

```javascript
const messageCardRef = useRef(null);

// Scroll the message card itself, not the parent container
if (messageCardRef.current) {
  messageCardRef.current.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
    inline: "nearest",
  });
}
```

**Benefits**:

- Smooth scrolling within message container only
- No disruption to outer page scroll
- Better control over scroll behavior

---

## 3. Full Text to KittenTTS with Chunking

### Problem

KittenTTS was limited to 500 characters, truncating long DM responses and losing important narrative.

### Solution

Implemented intelligent text chunking that splits long text at sentence boundaries and concatenates the audio.

**File**: `backend/tts_service.py`

**New Methods**:

- `_split_into_chunks()` - Splits text at sentence boundaries (~400 chars/chunk)
- `_generate_audio_array()` - Generates audio for single chunk
- `_generate_single_chunk()` - Handles single-chunk generation
- Updated `generate_speech()` - Auto-detects when chunking is needed

```python
def generate_speech(self, text, voice, ...):
    # Check if text needs chunking (safe limit: ~400 chars per chunk)
    chunk_size = 400
    if len(text) <= chunk_size:
        return self._generate_single_chunk(text, kitten_voice)

    # Multiple chunks needed - split and concatenate
    chunks = self._split_into_chunks(text, chunk_size)

    # Generate audio for each chunk
    audio_arrays = []
    for chunk in chunks:
        audio_array = self._generate_audio_array(chunk, kitten_voice)
        audio_arrays.append(audio_array)

    # Concatenate all audio arrays
    combined_audio = np.concatenate(audio_arrays)
    return wav_data
```

**Benefits**:

- ✅ Full DM responses narrated (no truncation)
- ✅ Smart sentence boundary splitting
- ✅ No ONNX "invalid expand shape" errors
- ✅ Seamless audio concatenation

---

## 4. Dialogue Narration Feature

### Overview

Automatically extract quoted dialogue from DM responses, assign appropriate voices based on gender detection, and enable sequential playback for immersive storytelling.

### Components Created

#### A. DialogueNarrationPlayer Component

**File**: `frontend/src/components/game/DialogueNarrationPlayer.jsx`

**Features**:

- Dialogue extraction from quoted text
- Speaker and gender detection
- Voice assignment (male/female)
- Sequential playback
- Pre-loading without auto-play
- Skip/pause/stop controls

**Functions**:

- `extractDialogue(content)` - Extracts quoted dialogue with regex
- `detectGender(speaker, text)` - Determines gender from context
- `preloadAllDialogues()` - Pre-fetches TTS for all dialogue
- `playDialogue(index)` - Plays specific dialogue from cache
- Sequential playback with automatic progression

**Voice Mapping**:

- **Female**: leah (default), tara, jess, mia
- **Male**: leo (default), dan, zac, zoe

**Gender Detection Heuristics**:

- Checks speaker attribution: "said John" → male, "said Mary" → female
- Checks pronouns: he/him/his → male, she/her → female
- Checks titles: king/lord/sir → male, queen/lady → female
- Defaults to female (DM narrator voice)

#### B. Backend Dialogue TTS Endpoint

**File**: `backend/routers/chat.py`

**New Endpoint**: `POST /api/tts/dialogue`

```python
class DialogueTTSRequest(BaseModel):
    text: str
    voice: str = "leah"

@router.post("/tts/dialogue")
async def generate_dialogue_tts(request: DialogueTTSRequest, ...):
    """Generate TTS for a single dialogue snippet."""
    tts = get_tts_service()
    audio_data = tts.generate_speech(
        text=request.text,
        voice=request.voice,
        add_dm_personality=False,  # Dialogue is already in character
        flavor_text_only=False
    )
    return StreamingResponse(iter([audio_data]), media_type="audio/wav")
```

**Benefits**:

- Simplified endpoint for dialogue-only TTS
- No message association needed
- Uses KittenTTS chunking for any length dialogue
- Consistent voice quality

#### C. Integration with DMChat

**File**: `frontend/src/pages/DMChat.jsx`

Added DialogueNarrationPlayer after TTSAudioPlayer:

```javascript
{
  /* Dialogue Narration Player */
}
{
  msg.role === "assistant" && ttsEnabled && msg.id && !msg._optimistic && (
    <DialogueNarrationPlayer
      sessionId={selectedSession.id}
      messageId={msg.id}
      messageContent={msg.content}
      enabled={true}
    />
  );
}
```

### User Workflow

1. **DM Response Generated** → Text animation plays (for new messages only)
2. **Animation Completes** → Dialogue player appears (if dialogue found)
3. **User Clicks "Load Dialogue"** → Pre-loads all dialogue TTS clips
4. **User Clicks "Play Dialogue"** → Sequential playback begins
5. **Each dialogue plays** → Automatically advances to next
6. **User can control** → Pause, stop, or skip to next dialogue

### UI Elements

**Dialogue Player Display**:

- Header: "Scene Dialogue (X clips)"
- Load button: "Load Dialogue" (pre-loading)
- Current dialogue info:
  - Index: "1/5"
  - Speaker: "The Innkeeper"
  - Gender badge: "female" (pink) or "male" (blue)
  - Preview: First 80 chars of dialogue text
- Playback controls:
  - Play/Pause button
  - Stop button
  - Skip to next button

**Visual States**:

- Not loaded: Shows "Load Dialogue" button
- Pre-loading: Linear progress bar
- Loaded: Shows current dialogue + controls
- Playing: Active play icon, can pause
- Finished: Returns to first dialogue

---

## Testing Checklist

### Text Animation Skip

- [ ] Generate new DM response → typing animation plays
- [ ] Refresh page → existing messages display instantly (no animation)
- [ ] Navigate away and return → messages still display instantly

### Auto-Scroll Fix

- [ ] Generate long DM response with typing animation
- [ ] Verify message container scrolls (not outer page)
- [ ] Check that outer scrollbar doesn't jump
- [ ] Manual scroll during typing works correctly

### Full Text TTS

- [ ] Set TTS provider to KittenTTS
- [ ] Generate long DM response (>500 chars)
- [ ] Click TTS play button
- [ ] Verify full text is narrated (not truncated)
- [ ] Check console for chunking logs: "Split into X chunks"
- [ ] Listen for seamless audio transitions between chunks

### Dialogue Narration

- [ ] Generate DM response with quoted dialogue
  - Example: "Welcome, traveler!" said the innkeeper.
- [ ] Verify dialogue player appears with "Load Dialogue" button
- [ ] Click "Load Dialogue" → shows loading progress
- [ ] After loading, verify:
  - Shows "Scene Dialogue (X clips)"
  - Displays first dialogue preview
  - Shows speaker name and gender badge
  - Playback controls enabled
- [ ] Click "Play Dialogue" → first dialogue plays
- [ ] Verify auto-advance to next dialogue
- [ ] Test pause/stop/skip controls
- [ ] Verify male vs female voices for different speakers

### Gender Detection

Test with various dialogue patterns:

- [ ] "Hello!" said the king. → male voice
- [ ] "Welcome!" she replied. → female voice
- [ ] "Attack!" shouted the warrior. → (check logs for gender detection)
- [ ] "Greetings." (no attribution) → female (default)

---

## Console Logs to Monitor

### Dialogue Extraction

```
[Dialogue] Extracted 3 dialogue snippets
[Dialogue] Preloading 1/3: "Welcome, traveler!..."
[Dialogue] Preloaded 3 dialogue clips
```

### TTS Chunking

```
[TTS] Text length 1234 exceeds safe limit, chunking into segments
[TTS] Split into 4 chunks
[TTS] Generating chunk 1/4 (length=380 chars)
[TTS] Generated complete audio from 4 chunks, total size: 245678 bytes
```

### Message Animation

```
[Scene Image] Loading cached image for message 42
```

---

## Files Modified

### Frontend

- ✅ `frontend/src/components/game/CinematicMessageCard.jsx` - Animation skip logic + scroll fix
- ✅ `frontend/src/components/game/DialogueNarrationPlayer.jsx` - **NEW** Dialogue player component
- ✅ `frontend/src/pages/DMChat.jsx` - Import and render dialogue player

### Backend

- ✅ `backend/tts_service.py` - Text chunking + full-length support
- ✅ `backend/routers/chat.py` - Dialogue TTS endpoint

---

## Known Limitations

### Dialogue Extraction

- Only detects dialogue in double quotes: `"text"`
- Requires explicit speaker attribution for best gender detection
- Nested quotes may be missed
- Non-English dialogue may have detection issues

### Gender Detection

- Heuristic-based (not perfect)
- Defaults to female if ambiguous
- May mis-gender speakers without clear context
- Cannot detect non-binary speakers (defaults to female)

### Voice Assignment

- Fixed voice per gender (leo for male, leah for female)
- No character-specific voice customization (yet)
- Same speaker may get different voice across messages

---

## Future Enhancements

### Short Term

- [ ] Add voice customization per character/speaker
- [ ] Persist speaker→voice mappings across messages
- [ ] Add volume control for dialogue player
- [ ] Show waveform visualization during playback
- [ ] Add "Replay Dialogue" after completion

### Medium Term

- [ ] Detect character names from campaign context
- [ ] Use campaign party members for voice assignment
- [ ] Add emotion detection for dialogue (happy/sad/angry)
- [ ] Support multiple TTS providers for dialogue
- [ ] Cache dialogue TTS in message metadata

### Long Term

- [ ] ML-based gender detection (more accurate)
- [ ] Voice cloning for specific NPCs
- [ ] Dialogue subtitle display during playback
- [ ] Export dialogue as standalone audio files
- [ ] Multi-language dialogue support

---

## Rollback Instructions

If issues arise:

1. **Text animation skip**: Revert `hasAnimatedRef` logic in CinematicMessageCard.jsx
2. **Auto-scroll fix**: Remove `messageCardRef` and revert to `onTypingProgress` callback
3. **TTS chunking**: Revert `generate_speech()` to single-chunk mode with 500-char limit
4. **Dialogue narration**: Remove DialogueNarrationPlayer import from DMChat.jsx

All changes are isolated and can be reverted independently.
