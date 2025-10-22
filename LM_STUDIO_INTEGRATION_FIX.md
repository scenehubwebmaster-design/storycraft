# LM Studio Integration Fix

**Commit**: 8913cf2  
**Date**: 2025-01-22  
**Issue**: DMChat 500 error when using LM Studio provider

---

## Problems Solved

### 1. Backend: Unsupported Provider Error
**Symptom**:
```
Error: Generate failed: 500 {"detail":"LLM call failed: 500: LLM generation failed: Unsupported provider: http://100.120.44.114:1234/v1"}
```

**Root Cause**:
- `call_llm()` function in `backend/routers/generation.py` only recognized named providers (openai, anthropic, google, groq)
- When a URL like `http://100.120.44.114:1234/v1` was passed as the provider, it failed validation

**Solution**:
- Modified `call_llm()` to detect URL-based providers by checking for `'http'` or `'localhost'` in the provider string
- URL-based providers are treated as OpenAI-compatible servers (LM Studio uses OpenAI's API format)
- Uses `AsyncOpenAI` client with custom `base_url` parameter
- Skips rate limiting for local servers (no need to throttle localhost)
- Returns metadata with `'lm-studio'` as the provider name for telemetry

**Code Changes** (`backend/routers/generation.py`, lines ~380-420):
```python
async def call_llm(prompt: str, provider: str, model: str = None) -> tuple[str, Dict[str, Any]]:
    """
    Call the specified LLM provider and return the response.
    
    Supports:
    - Named providers: openai, anthropic, google, groq
    - LM Studio: URLs containing 'http' or 'localhost' (OpenAI-compatible API)
    """
    try:
        # Skip rate limiting for local LM Studio
        if not ('http' in provider.lower() or 'localhost' in provider.lower()):
            rate_limit_error = rate_limiter.check_rate_limit(provider, estimated_tokens)
            # ... existing rate limit logic
        
        prov = provider.lower()
        
        # Check if provider is a URL (LM Studio or other OpenAI-compatible server)
        if 'http' in prov or 'localhost' in prov:
            from openai import AsyncOpenAI
            
            # Extract base URL (ensure /v1 suffix)
            base_url = provider
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'
            
            client = AsyncOpenAI(
                base_url=base_url,
                api_key="lm-studio"  # LM Studio doesn't validate keys
            )
            
            response = await client.chat.completions.create(
                model=model or "local-model",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            metadata = {
                "model": model or "local-model",
                "provider": "lm-studio",
                "base_url": base_url
            }
        
        # ... existing named provider logic (openai, anthropic, etc.)
```

---

### 2. Frontend: Undefined `placeholderId` Error
**Symptom**:
```javascript
DMChat.jsx:255  Uncaught ReferenceError: placeholderId is not defined
    at DMChat.jsx:255:53
    at Array.filter (<anonymous>)
```

**Root Cause**:
- Variable `placeholderId` was defined as `tempPlaceholderId` in the success path
- Error handling code referenced the wrong variable name (`placeholderId` instead of `tempPlaceholderId`)
- When the backend failed, the error handler tried to clean up the placeholder message but crashed due to undefined variable

**Solution**:
- Changed all references from `placeholderId` to `tempPlaceholderId` in the error handling block
- Ensures placeholder messages are properly removed from the UI when errors occur

**Code Changes** (`frontend/src/pages/DMChat.jsx`, lines ~242-256):
```javascript
// Before (incorrect):
if (assistantMsg) {
  setMessages((m) =>
    m.map((it) => (it.id === placeholderId ? assistantMsg : it))  // ❌ wrong variable
  );
} else {
  setMessages((m) => m.filter((it) => it.id !== placeholderId));  // ❌ wrong variable
}
} catch (e) {
  console.error(e);
  setError(String(e));
  setMessages((m) => m.filter((it) => it.id !== placeholderId));  // ❌ wrong variable
}

// After (correct):
if (assistantMsg) {
  setMessages((m) =>
    m.map((it) => (it.id === tempPlaceholderId ? assistantMsg : it))  // ✅ correct
  );
} else {
  setMessages((m) => m.filter((it) => it.id !== tempPlaceholderId));  // ✅ correct
}
} catch (e) {
  console.error(e);
  setError(String(e));
  setMessages((m) => m.filter((it) => it.id !== tempPlaceholderId));  // ✅ correct
}
```

---

## LM Studio Configuration

### How to Use LM Studio as Provider

**Session Settings** (DMChat.jsx):
1. Set **Provider** to: `http://100.120.44.114:1234/v1` (or your LM Studio URL)
2. Set **Model** to: `local-model` (or the model identifier shown in LM Studio)
3. The system will automatically detect the URL and use OpenAI-compatible API calls

**Supported URL Formats**:
- Full URL with `/v1` suffix: `http://100.120.44.114:1234/v1`
- URL without suffix (auto-appended): `http://100.120.44.114:1234`
- Localhost URLs: `http://localhost:1234/v1`
- HTTPS URLs: `https://your-lm-studio-server.com/v1`

**LM Studio Setup**:
1. Start LM Studio server on port 1234 (default)
2. Load a model (e.g., Qwen2.5 7B Instruct)
3. Verify server is running: `http://100.120.44.114:1234/v1/models`
4. Configure DMChat session with the full URL

---

## Alternative: LM Studio Python SDK

While the current fix uses OpenAI-compatible API calls, you could also migrate to the official LM Studio Python SDK for better integration:

### Installation
```bash
pip install lmstudio
```

### Usage Example
```python
import lmstudio as lms

# Configure server (if not localhost:1234)
lms.configure_default_client("100.120.44.114:1234")

# Simple API
model = lms.llm()
response = model.respond("What is the meaning of life?")

# Streaming API
for fragment in model.respond_stream("Generate a character"):
    print(fragment.content, end="", flush=True)

# Chat context
chat = lms.Chat("You are a D&D Dungeon Master")
chat.add_user_message("I cast Fireball at the goblin")
result = model.respond(chat)
```

### Benefits of SDK Migration
- **Simpler API**: No need to manage OpenAI client manually
- **Better error handling**: SDK handles retries and connection management
- **Model management**: `lms.list_loaded_models()`, `lms.list_downloaded_models()`
- **Progress callbacks**: Track prompt processing progress
- **Structured outputs**: Native support for JSON schema responses

### Migration Path (Optional)
If you want to use the SDK instead of OpenAI-compatible calls:

1. Add to `requirements.txt`:
   ```
   lmstudio>=1.5.0
   ```

2. Create new LM Studio provider in `backend/routers/llm.py`:
   ```python
   @staticmethod
   async def generate_lmstudio(prompt: str, model: str = None, base_url: str = "localhost:1234") -> str:
       import lmstudio as lms
       
       # Configure if non-default server
       if base_url != "localhost:1234":
           lms.configure_default_client(base_url)
       
       llm = lms.llm(model or "local-model")
       response = llm.respond(prompt)
       return response
   ```

3. Update `call_llm()` to detect LM Studio and call new provider

**Decision**: Current OpenAI-compatible approach is simpler and requires no new dependencies. SDK migration is optional and should be done only if advanced features (streaming, model management, progress callbacks) are needed.

---

## Testing

### Manual Test (DMChat)
1. Start backend: `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Create new DMChat session
4. Set provider to: `http://100.120.44.114:1234/v1`
5. Set model to: `local-model` (or your LM Studio model)
6. Send message: "Tell me about a dragon"
7. Verify response is generated without errors

### Expected Behavior
- ✅ Backend logs: `Generated response using lm-studio - local-model`
- ✅ Frontend: Message appears with DM response
- ✅ No console errors about `placeholderId`
- ✅ Placeholder message is properly replaced or removed

### Error Recovery Test
1. Stop LM Studio server
2. Send message in DMChat
3. Verify placeholder message is removed (not left hanging)
4. Verify error message is shown to user
5. Restart LM Studio, send message again
6. Verify recovery works

---

## Files Modified

1. **`backend/routers/generation.py`** (52 insertions, 16 deletions)
   - Modified `call_llm()` function to support URL-based providers
   - Added LM Studio detection and OpenAI client initialization
   - Skipped rate limiting for local servers

2. **`frontend/src/pages/DMChat.jsx`** (small fix)
   - Fixed `placeholderId` → `tempPlaceholderId` reference errors
   - Ensures proper error handling and placeholder cleanup

---

## Related Documentation

- **LM Studio Python SDK**: https://lmstudio.ai/docs/python
- **OpenAI Python Library**: https://github.com/openai/openai-python
- **LM Studio Server**: https://lmstudio.ai/docs/app/server

---

## Future Enhancements

1. **Auto-detect LM Studio models**: Call `/v1/models` endpoint to populate model dropdown
2. **Connection health check**: Verify LM Studio server is reachable before sending prompts
3. **Streaming responses**: Use `client.chat.completions.create(stream=True)` for real-time text generation
4. **Model switching**: Allow users to switch between loaded models without restarting LM Studio
5. **SDK migration**: Optionally migrate to `lmstudio` Python SDK for advanced features

---

## Notes

- **Rate Limiting**: Local LM Studio servers are exempt from rate limiting (no throttling needed)
- **API Key**: LM Studio doesn't validate API keys, so we use placeholder `"lm-studio"`
- **OpenAI Compatibility**: LM Studio implements OpenAI's chat completion API format
- **Network Access**: Ensure LM Studio server allows network connections (not just localhost)
- **CORS**: If frontend calls LM Studio directly (not through backend), CORS headers may be needed
