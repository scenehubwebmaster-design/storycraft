# Scene Image SSE Fix - October 27, 2025

## Problem

Scene images were being generated successfully by the backend but never appearing in the UI. The backend logs showed:

- ✅ Scene summarizer completed
- ✅ SD image generated successfully
- ✅ Image fetched from SD server

But the frontend `SceneImageDisplay` component never displayed the image.

## Root Cause

The `SceneImageDisplay.jsx` component's `useEffect` hook was not properly reacting to SSE (Server-Sent Events) metadata updates:

1. ✅ Backend generated image and called `publish_event`
2. ✅ Frontend received SSE event via `EventSource` in `DMChat.jsx`
3. ✅ DMChat updated the `messages` state with new metadata
4. ✅ SceneImageDisplay received updated `messageMetadata` prop
5. ❌ **BUT** the component had set up a polling interval and marked `hasAttemptedGeneration = true`, so the useEffect ignored the metadata update

The old code started a 30-second polling loop looking for the image, instead of trusting the SSE system to deliver it immediately.

## Solution

### 1. Frontend: SceneImageDisplay.jsx

**Simplified the metadata reactivity logic:**

- Removed the polling interval fallback (SSE handles real-time updates)
- Made the useEffect properly react to `messageMetadata` changes
- Added comprehensive logging to track metadata flow
- When `messageMetadata.scene_image.image` arrives via SSE, immediately display it

**Key changes:**

```javascript
// OLD: Started polling interval, ignored SSE updates
React.useEffect(() => {
  if (cached.image) {
    setImage(cached.image);
    return;
  }
  // Poll for 30 seconds... ❌
  const interval = setInterval(/* polling logic */, 2000);
}, [messageMetadata]);

// NEW: Trust SSE to deliver updates, stable dependency array
React.useEffect(() => {
  if (cached.image) {
    console.log("✅ Displaying image from SSE update");
    setImage(cached.image);
    setLoading(false);
    return;
  }
  console.log("⏳ Waiting for image via SSE");
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [messageMetadata]); // Stable dependency - prevents React warning about array size
```

**Note:** The final fix uses only `[messageMetadata]` in the dependency array to prevent React warnings about changing dependency array size. Including `messageId` and `hasAttemptedGeneration` caused the warning because they were sometimes undefined on first render.

### 2. Frontend: DMChat.jsx

**Enhanced SSE event handler with logging:**

```javascript
es.onmessage = (ev) => {
  const obj = JSON.parse(ev.data);
  console.log("[DMChat] SSE event received:", obj);

  if (obj.type === "message_metadata_updated") {
    // Update messages state with new metadata
    // SceneImageDisplay will react to the prop change
  }
};
```

### 3. Backend: chat.py

**Added detailed logging to background image generation:**

```python
# Inside _generate_and_cache_image background task
msg.meta["scene_image"] = si
db2.commit()

print(f"[Background Scene Image] ✅ Cached image, bytes={img_len}")
print(f"[Background Scene Image] 📡 Publishing SSE event...")

publish_event(msg.session_id, {
    "type": "message_metadata_updated",
    "message_id": msg.id,
    "metadata": {"scene_image": si}
})

print("[Background Scene Image] ✅ SSE event published successfully")
```

## Testing Instructions

### 1. Restart Backend

```cmd
cd e:\storycraft\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Clear Browser Cache

- Open DevTools (F12)
- Right-click Refresh → Empty Cache and Hard Reload
- Or: Application tab → Clear Storage → Clear site data

### 3. Test Auto-Generation Flow

1. Open DMChat and create/select a session
2. Send a DM message that describes a scene (e.g., "The party enters a dark tavern")
3. Watch **both** browser console and backend terminal

**Expected Backend Logs:**

```
INFO:backend.routers.chat:[Scene Summarizer] invoking summarize_scene_for_image helper
INFO:backend.routers.chat:[Scene Summarizer] helper returned descriptors/prompt
INFO:backend.stablediffusion_client:Generating SD image with prompt: a dimly lit tavern...
INFO:backend.stablediffusion_client:Fetching generated image from: http://192.168.250.14:7861/...
[Background Scene Image] ✅ Cached image in message 178 metadata, bytes=123456
[Background Scene Image] 📡 Publishing SSE event for session 1, message 178
[Background Scene Image] ✅ SSE event published successfully
```

**Expected Frontend Console:**

```
[DMChat] SSE event received: {type: "message_metadata_updated", message_id: 178, metadata: {...}}
[DMChat] Updating metadata for message 178: {scene_image: {...}}
[DMChat] Merged metadata for message 178: {scene_image: {image: "...", prompt: "..."}}
[Scene Image] useEffect triggered for message 178, has metadata: true, has scene_image: true
[Scene Image] Processing metadata for message 178: {hasImage: true, imageLength: 123456}
[Scene Image] ✅ Displaying image for message 178 (123456 bytes)
```

### 4. Verify Image Appears

- Scene image should appear **automatically** within 5-10 seconds
- No manual "Generate Scene Image" button (removed in previous fix)
- Image should display below the DM message card

### 5. Test Manual Regeneration

- Click the Refresh icon on the scene image card
- Should force generate a new image with same prompt

## Debugging Checklist

If image still doesn't appear:

- [ ] **Check SSE connection:** DevTools → Network tab → filter "events" → should see `session_events` with status 200
- [ ] **Check SSE messages:** Click on `session_events` → Response tab → should see `data: {"type":"message_metadata_updated",...}`
- [ ] **Check console logs:** Both backend and frontend should show the expected log messages above
- [ ] **Check metadata structure:** Console → expand the SSE event → verify `metadata.scene_image.image` exists
- [ ] **Check React prop updates:** React DevTools → find SceneImageDisplay → watch `messageMetadata` prop change
- [ ] **Verify database:** Run `sqlite3 storycraft.db "SELECT id, meta FROM chat_messages WHERE id=178;"` → should see scene_image in JSON

## Files Changed

1. ✅ `frontend/src/components/game/SceneImageDisplay.jsx` - Simplified SSE reactivity
2. ✅ `frontend/src/pages/DMChat.jsx` - Added SSE event logging
3. ✅ `backend/routers/chat.py` - Added background task logging

## Related Issues Fixed

- ✅ Scene images auto-generate during DM responses (verified working)
- ✅ Manual "Generate Scene Image" button removed (completed in previous session)
- ✅ DM roll setting wired to backend (completed in previous session)

## Next Steps

After confirming this fix works:

1. Test with multiple concurrent messages (ensure SSE events target correct message)
2. Test with poor/intermittent network (SSE reconnection)
3. Consider adding retry logic if SSE connection fails
4. Monitor performance with large images (base64 strings can be 100KB+)
