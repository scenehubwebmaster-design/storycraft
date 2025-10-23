# Kitten TTS ONNX Error Fix

**Date:** October 22, 2025  
**Issue:** 500 Internal Server Error when generating TTS audio  
**Root Cause:** ONNX runtime "Expand node" error with texts over 400 characters  
**Status:** ✅ Fixed

## Problem Description

### Error Symptoms

```
[backend] 2025-10-22 18:42:49 [E:onnxruntime:, sequential_executor.cc:516
onnxruntime::ExecuteKernel] Non-zero status code returned while running
Expand node. Name:'/bert/Expand' Status Message: invalid expand shape

[frontend] :8000/api/chat/sessions/19/messages/19/tts?voice=tara:1
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

### Root Cause

Kitten TTS's ONNX model has a limitation on input text length. When text exceeds approximately 400 characters, the BERT tokenizer's expand operation fails, causing an ONNX runtime error.

Testing revealed:

- ✅ Texts under 400 characters: Work perfectly
- ❌ Texts over 500 characters: Cause ONNX "Expand node" error
- ⚠️ Texts 400-500 characters: Risky zone

## Solution

### 1. Added Text Preprocessing (`_preprocess_text`)

Added a new method to clean and truncate text before TTS generation:

**Location:** `backend/tts_service.py`

**Features:**

- Removes excessive whitespace
- Strips markdown formatting (`**bold**`, `*italic*`, `` `code` ``)
- Truncates at 400 character limit
- Intelligently breaks at sentence boundaries
- Handles empty/whitespace-only input

**Example:**

```python
def _preprocess_text(self, text: str) -> str:
    """
    Preprocess text for TTS generation.

    - Limit: 400 characters (safe for ONNX model)
    - Smart truncation at sentence boundaries
    - Markdown cleanup
    """
```

### 2. Enhanced Error Logging

Added detailed error logging to chat router:

**Location:** `backend/routers/chat.py`

**Improvements:**

- Full stack traces on errors
- Log message content (first 100 chars)
- Better error identification

```python
except Exception as e:
    print(f"[ERROR] TTS generation failed for message {message_id}: {e}")
    print(f"[ERROR] Message content: {message.content[:100]}...")
    traceback.print_exc()
```

## Testing Results

Created comprehensive test suite: `test_tts_problematic.py`

### Test Cases

| Test Case          | Length  | Result                            |
| ------------------ | ------- | --------------------------------- |
| Empty text         | 0       | ✅ Success (fallback)             |
| Whitespace only    | 7       | ✅ Success (fallback)             |
| Markdown bold      | 21      | ✅ Success (cleaned)              |
| Markdown italic    | 16      | ✅ Success (cleaned)              |
| Code blocks        | 31      | ✅ Success (cleaned)              |
| **Very long text** | **516** | ✅ **Success (truncated to 399)** |
| Special characters | 36      | ✅ Success                        |
| Multiple newlines  | 28      | ✅ Success (collapsed)            |
| D&D content        | 74      | ✅ Success                        |
| Real message       | 79      | ✅ Success                        |

**Key Finding:** Before fix, 516-character text caused ONNX error.  
After fix, automatically truncated to 399 characters and worked perfectly.

## Implementation Details

### Text Length Handling

```python
max_length = 400  # Safe limit for Kitten TTS ONNX model

if len(text) > max_length:
    # Truncate intelligently
    truncated = text[:max_length]

    # Find last sentence break (., ?, !)
    last_sentence = max(
        truncated.rfind('.'),
        truncated.rfind('?'),
        truncated.rfind('!')
    )

    if last_sentence > max_length * 0.6:
        # Good break point found
        text = truncated[:last_sentence + 1]
    else:
        # No good break, truncate at word boundary
        last_space = truncated.rfind(' ')
        text = truncated[:last_space] + '...'
```

### Markdown Cleanup

````python
# Remove bold/italic
text = text.replace('**', '').replace('*', '')

# Remove code blocks
text = text.replace('```', '').replace('`', '')

# Collapse whitespace
text = ' '.join(text.split())
````

## Performance Impact

### Before Fix

- ❌ Long messages: ONNX error (500 response)
- ❌ User experience: Audio player shows error
- ❌ No fallback: Complete TTS failure

### After Fix

- ✅ Long messages: Automatically truncated
- ✅ User experience: Audio plays first 400 chars
- ✅ Graceful degradation: Partial narration better than none
- ✅ No errors: All texts process successfully

### Generation Times

| Text Length | Generation Time |
| ----------- | --------------- |
| ~20 chars   | 0.5-0.8s        |
| ~80 chars   | 1.5-2.0s        |
| ~400 chars  | 8-9s            |

**Note:** 400-char limit is a reasonable UX trade-off. Most D&D narrations are under 200 characters, and voice narration of very long texts would be tiresome anyway.

## User Experience

### For Short Messages (< 400 chars)

✅ **No change** - Perfect voice narration

### For Long Messages (> 400 chars)

✅ **Graceful truncation:**

- First 400 characters narrated
- Breaks at sentence boundary when possible
- User can read full text in chat
- Audio provides "introduction" to message

### Example

**Original Message (600 chars):**

```
Looking at the spell details:

**Fireball** (3rd-level evocation)
Casting Time: 1 action
Range: 150 feet
Components: V, S, M (a tiny ball of bat guano and sulfur)
Duration: Instantaneous

A bright streak flashes from your pointing finger to a point you choose within
range and then blossoms with a low roar into an explosion of flame. Each creature
in a 20-foot-radius sphere centered on that point must make a Dexterity saving
throw. A target takes 8d6 fire damage on a failed save, or half as much damage
on a successful one. The fire spreads around corners...
```

**Narrated (truncated at sentence):**

```
Looking at the spell details: Fireball (3rd-level evocation) Casting Time:
1 action Range: 150 feet Components: V, S, M (a tiny ball of bat guano and
sulfur) Duration: Instantaneous A bright streak flashes from your pointing
finger to a point you choose within range and then blossoms with a low roar
into an explosion of flame.
```

## Monitoring & Debugging

### Check if truncation occurred:

```python
# Backend logs show:
# "Generating speech (voice=tara, length=399 chars)"
# If original was longer, truncation happened
```

### Verify TTS endpoint:

```bash
curl http://localhost:8000/api/chat/sessions/1/messages/1/tts?voice=tara --output test.wav
```

### Test locally:

```python
from backend.tts_service import TTSService

tts = TTSService()
long_text = "Very long message..." * 100
audio = tts.generate_speech(long_text, 'tara')
print(f"Success: {len(audio)} bytes")
```

## Known Limitations

### Character Limit

- **Maximum:** 400 characters per TTS request
- **Reason:** Kitten TTS ONNX model constraint
- **Alternative:** Split very long messages into multiple TTS requests (future enhancement)

### Truncation Logic

- Prefers sentence breaks (., ?, !)
- Falls back to word boundaries
- May cut mid-sentence if no good break point
- Users see full text in chat (only audio is truncated)

## Future Enhancements

### Option 1: Chunk Long Texts

Split long messages into multiple 400-char chunks and generate separate audio files:

```python
def generate_chunked_speech(text, voice):
    chunks = split_at_sentences(text, max_length=400)
    audio_parts = [tts.generate_speech(chunk, voice) for chunk in chunks]
    return combine_audio(audio_parts)
```

### Option 2: Use Different TTS Model

If longer texts are critical, consider:

- Coqui TTS (no length limit)
- Cloud TTS services (AWS Polly, Google TTS)
- Streaming TTS models

### Option 3: Progressive Audio

Generate audio for first chunk immediately, then stream additional chunks:

```python
# Play first 400 chars instantly
# Generate rest in background
# Seamless audio continuation
```

## Files Modified

1. **`backend/tts_service.py`**

   - Added `_preprocess_text()` method
   - Integrated preprocessing into `generate_speech()`
   - 400-character limit with smart truncation

2. **`backend/routers/chat.py`**

   - Enhanced error logging
   - Stack traces for debugging
   - Log message content on error

3. **`test_tts_problematic.py`** (new)

   - Comprehensive test suite
   - Tests edge cases and problematic inputs
   - Validates fix

4. **`KITTEN_TTS_ONNX_FIX.md`** (this file)
   - Documents the issue and solution
   - Testing results
   - Future enhancements

## Deployment Checklist

- [x] Identify root cause (text length > 400 chars)
- [x] Implement text preprocessing
- [x] Add 400-character limit
- [x] Smart truncation at sentence boundaries
- [x] Markdown cleanup
- [x] Enhanced error logging
- [x] Comprehensive testing
- [x] Document fix and limitations

## References

- **Original Issue:** ONNX "Expand node" error
- **Kitten TTS:** https://github.com/KittenML/KittenTTS
- **Test Suite:** `test_tts_problematic.py`
- **Migration Guide:** `KITTEN_TTS_MIGRATION.md`

---

**Status:** ✅ Production Ready  
**Fix Date:** October 22, 2025  
**Tested By:** Automated test suite + manual verification
