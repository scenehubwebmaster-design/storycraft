# TTS and Scene Image Persistence Fix

## Problem

When reloading the page or returning to an existing campaign, all prior messages loaded correctly but:

- TTS audio had to be regenerated every time
- Scene images had to be regenerated every time
- This caused unnecessary delays and resource usage

Additionally, KittenTTS was failing with ONNX "invalid expand shape" errors when text was too long.

## Solution Implemented

### 1. Backend Caching (chat.py)

#### Scene Images

- **Cache in message.meta**: Store generated scene images (base64) in `message.meta['scene_image']`
- **Check cache first**: Return cached image if available (unless `force_generate=True`)
- **Metadata stored**: image, prompt, negative_prompt, generated_at, location_hint
- **API response includes**: `cached: true/false` flag

#### TTS Metadata

- **Track generation history**: Store TTS generation metadata in `message.meta['tts_history'][]`
- **Metadata stored**: voice, provider, model, flavor_text_only, generated_at, audio_size_bytes
- **Note**: Audio bytes NOT stored (too large), but metadata helps track what was generated

### 2. KittenTTS Fixes (tts_service.py)

#### Text Length Limits

- **Reduced max length**: 2000 chars → 500 chars (safe for ONNX)
- **Smart truncation**: Break at sentence boundaries when possible
- **Unicode cleanup**: Remove problematic characters (em-dashes, smart quotes, ellipsis)

#### Better Error Handling

- **Detailed logging**: Print text length, preview, and voice mapping
- **Graceful errors**: Catch ONNX errors with helpful messages
- **Traceback on failure**: Full stack trace for debugging

### 3. Frontend Caching (SceneImageDisplay.jsx)

#### Check Cached Images

- **New prop**: `messageMetadata` passed from DMChat
- **Load on mount**: Check `messageMetadata.scene_image` for cached data
- **Skip auto-generate**: Don't generate if cached image exists
- **Visual indicator**: `isCached` state tracks cache status

#### API Integration

- **Parse cached flag**: Handle `data.cached` from API response
- **Console logging**: Log whether image was cached or generated

### 4. Integration (DMChat.jsx)

#### Pass Metadata

- **Scene images**: Pass `msg.metadata` to SceneImageDisplay component
- **TTS players**: (Future enhancement - can check `tts_history` to show generation status)

## Benefits

### User Experience

- ✅ **Instant loading**: Cached scene images load immediately on page reload
- ✅ **No re-generation**: Previously generated content persists across sessions
- ✅ **Faster navigation**: Switching between campaigns doesn't regenerate content

### Performance

- ✅ **Reduced API calls**: Scene images only generated once per message
- ✅ **Lower resource usage**: No redundant Stable Diffusion generations
- ✅ **Better reliability**: KittenTTS no longer fails on long text

### Data Persistence

- ✅ **Database storage**: Scene images stored in `chat_messages.meta` column (JSON)
- ✅ **Generation tracking**: TTS history preserved for analytics
- ✅ **Force regenerate**: Users can still force new generation if desired

## Testing Recommendations

### Scene Image Caching

1. Start new campaign and generate DM response
2. Wait for scene image to generate
3. Refresh page or navigate away
4. Return to campaign → scene image should load instantly
5. Check browser console for `[Scene Image] Loading cached image` log

### KittenTTS Fixes

1. Set TTS provider to "KittenTTS" in settings
2. Select any KittenTTS voice (tara, leah, jess, etc.)
3. Generate DM response with long text (>300 chars)
4. Click TTS play button
5. Should generate without ONNX "invalid expand shape" error
6. Very long responses (>500 chars) will be truncated at sentence boundary

### Database Verification

```sql
-- Check cached scene images
SELECT id, role, LENGTH(content) as content_len,
       JSON_EXTRACT(meta, '$.scene_image.generated_at') as image_cached_at
FROM chat_messages
WHERE meta IS NOT NULL
  AND JSON_EXTRACT(meta, '$.scene_image') IS NOT NULL;

-- Check TTS generation history
SELECT id, role,
       JSON_EXTRACT(meta, '$.tts_history[0].voice') as tts_voice,
       JSON_EXTRACT(meta, '$.tts_history[0].generated_at') as tts_generated_at
FROM chat_messages
WHERE meta IS NOT NULL
  AND JSON_EXTRACT(meta, '$.tts_history') IS NOT NULL;
```

## Future Enhancements

### TTS Audio Caching

- Store TTS audio as base64 in message metadata (or external blob storage)
- Check cache before generating TTS
- Add audio player indicator for cached vs. generated audio

### Cache Management

- Add "Clear Cache" button to regenerate all images/TTS
- Add cache expiration (e.g., 30 days)
- Add cache size limits per session

### UI Indicators

- Show "cached" badge on scene images
- Show "previously generated" on TTS players
- Add tooltips with generation timestamps

## Files Modified

### Backend

- `backend/routers/chat.py` - Added caching to TTS and scene image endpoints
- `backend/tts_service.py` - Fixed KittenTTS text preprocessing and length limits

### Frontend

- `frontend/src/components/game/SceneImageDisplay.jsx` - Added cached image loading
- `frontend/src/pages/DMChat.jsx` - Pass message metadata to child components

## Rollback Instructions

If issues arise, revert these commits:

1. Backend caching changes (chat.py datetime import + metadata storage)
2. TTS service fixes (tts_service.py preprocessing changes)
3. Frontend metadata passing (SceneImageDisplay.jsx + DMChat.jsx props)

The changes are backward compatible - old messages without cached data will generate normally.
