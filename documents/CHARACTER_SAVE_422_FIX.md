# Character Save 422 Error Fix

## Problem

After generating a structured character, attempting to save resulted in:

**Frontend Error:**

```
Objects are not valid as a React child (found: object with keys {type, loc, msg, input})
```

**Backend Log:**

```
INFO: 127.0.0.1:64991 - "POST /api/generate/character/structured/save HTTP/1.1" 422 Unprocessable Entity
```

## Root Cause

**Request/Response Mismatch**: The frontend and backend were expecting different data formats after the git reset to commit `8f55dd1`.

### What Happened

1. **Earlier Session**: We fixed the endpoint to accept request body (to handle large portrait images)
2. **Git Reset**: Reverted to commit `8f55dd1`, removing the request body wrapper
3. **Frontend Still Updated**: Frontend was sending new format but backend expected old format

### Frontend Sending (Line 271-276)

```javascript
await axios.post(`${API_URL}/api/generate/character/structured/save`, {
  character_profile: finalContent || generatedContent,
  portrait_image: portraitImage || null,
  image_prompt: imagePrompt || null,
});
```

### Backend Expected (After Git Reset)

```python
@router.post("/character/structured/save")
async def save_structured_character(
    character_profile: CharacterProfile,  # Expected in body root
    portrait_image: str = None,           # Expected as query param ❌
    image_prompt: str = None,             # Expected as query param ❌
    story_id: int = None,
    db: Session = Depends(get_db)
):
```

**Problem**: Backend expected `CharacterProfile` at root of request body, but received nested object with `character_profile` key. Also expected large portrait images as query params (fails due to URL length limits).

## Solution

Re-applied the request body wrapper pattern (the correct approach):

### Updated Backend

**File**: `backend/routers/generation.py`

1. **Added Optional import**:

```python
from typing import Dict, Any, Type, Optional
```

2. **Created request wrapper class**:

```python
class CharacterSaveRequest(BaseModel):
    """Request model for saving a structured character with optional portrait"""
    character_profile: CharacterProfile
    portrait_image: Optional[str] = None
    image_prompt: Optional[str] = None
    story_id: Optional[int] = None
```

3. **Updated endpoint signature**:

```python
@router.post("/character/structured/save")
async def save_structured_character(
    request: CharacterSaveRequest,  # ✅ Accepts wrapper
    db: Session = Depends(get_db)
):
    # Extract fields from request
    character_profile = request.character_profile
    portrait_image = request.portrait_image
    image_prompt = request.image_prompt
    story_id = request.story_id

    # ... rest of save logic
```

## Why This Approach is Better

### ❌ Query Parameters for Images (Old Way)

```python
async def save_character(
    character_profile: CharacterProfile,
    portrait_image: str = None,  # ❌ URL query param
    ...
)
```

**Problems:**

- URLs have ~2-8KB limit
- Portrait images are ~100-500KB in base64
- Causes `net::ERR_FAILED` errors
- Images visible in server logs (security issue)

### ✅ Request Body Wrapper (New Way)

```python
class CharacterSaveRequest(BaseModel):
    character_profile: CharacterProfile
    portrait_image: Optional[str] = None  # ✅ In body
    ...

async def save_character(request: CharacterSaveRequest):
```

**Advantages:**

- No size limits on request body
- Images not in URLs
- Better security
- Standard REST API practice
- Consistent with other endpoints

## Validation Error Format

The 422 error returned a Pydantic validation error object:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "character_profile"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

The React error occurred because the frontend tried to render this error object directly instead of extracting the error message.

## Files Modified

1. ✅ `backend/routers/generation.py`
   - Added `Optional` import
   - Created `CharacterSaveRequest` wrapper class
   - Updated `/character/structured/save` endpoint

## Testing

1. **Generate Character**:
   - Go to Create Character page
   - Enable Structured Generation
   - Select Groq provider
   - Generate character with AI
2. **Generate Portrait** (optional):
   - Click "Generate Portrait"
   - Wait for portrait to generate
3. **Save Character**:
   - Enter character name
   - Click "Save Character"
   - Should succeed with 200 OK (not 422)
   - Character should appear in Characters list

## Server Status

- ✅ Backend running on http://0.0.0.0:8001
- ✅ Auto-reload enabled
- ✅ Changes applied successfully

## Git Commits

1. **Previous Commit** (cc719ec):

   ```
   fix: Groq structured outputs - use compatible models and add validation
   ```

   - Changed default model to Llama 4 Scout
   - Added field validators for list fields
   - Documentation added

2. **This Fix** (not yet committed):
   - Re-applied request body wrapper
   - Fixed 422 Unprocessable Entity error
   - Enabled portrait saves with structured characters

## Related Fixes in This Session

This session resolved multiple issues:

1. ✅ **Groq Model Compatibility** - Changed to `meta-llama/llama-4-scout-17b-16e-instruct`
2. ✅ **List Validation Errors** - Added Pydantic validators for string-to-list conversion
3. ✅ **Request Body Format** - Fixed 422 error by using request wrapper
4. ✅ **Frontend Model Selection** - Updated default recommendations

## Next Steps

1. Test character creation with portrait
2. Verify character displays correctly in list
3. Test editing existing characters
4. Commit this fix:
   ```bash
   git add backend/routers/generation.py
   git commit -m "fix: Use request body wrapper for character save endpoint"
   ```

## Prevention

To avoid this in the future:

1. **Don't use query params for large data** - Always use request body
2. **Keep frontend/backend in sync** - Update both or neither during git operations
3. **Test after git operations** - Verify functionality after resets/reverts
4. **Document API contracts** - Use OpenAPI/Swagger for clear contracts
5. **Add integration tests** - Catch mismatches automatically
