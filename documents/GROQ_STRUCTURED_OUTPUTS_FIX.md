# Groq Structured Outputs Fix

## Problem

When using Groq for structured character/world generation, the following error occurred:

```
Structured LLM generation failed: Error code: 400 - {'error': {'message': 'This model does not support response format `json_schema`. See supported models at https://console.groq.com/docs/structured-outputs#supported-models', 'type': 'invalid_request_error'}}
```

## Root Cause

The default model for Groq structured outputs was set to `llama-3.3-70b-versatile`, which **does NOT support** structured outputs with `json_schema` response format.

## Groq Structured Output Support

According to [Groq's documentation](https://console.groq.com/docs/structured-outputs#supported-models), only the following models support structured outputs (JSON Schema mode):

### ✅ Supported Models

1. **`openai/gpt-oss-20b`** - GPT-OSS 20B
2. **`openai/gpt-oss-120b`** - GPT-OSS 120B
3. **`moonshotai/kimi-k2-instruct-0905`** - Kimi K2 Instruct
4. **`meta-llama/llama-4-maverick-17b-128e-instruct`** - Llama 4 Maverick
5. **`meta-llama/llama-4-scout-17b-16e-instruct`** - Llama 4 Scout ⭐ (NEW DEFAULT)

### ❌ NOT Supported

- `llama-3.3-70b-versatile` ❌ (was the default)
- `llama-3.1-8b-instant` ❌
- Most other Llama 3.x models ❌

## Solution

Changed the default Groq model for structured outputs from `llama-3.3-70b-versatile` to `meta-llama/llama-4-scout-17b-16e-instruct`.

### Code Change

**File**: `backend/routers/generation.py`

**Before** (Line ~663):

```python
elif provider.lower() == "groq":
    response_text = await LLMProvider.generate_groq(
        prompt,
        model or "llama-3.3-70b-versatile",  # ❌ Not supported
        max_tokens=max_tokens,
        temperature=0.7,
        response_format=schema
    )
    metadata = {"model": model or "llama-3.3-70b-versatile", "provider": "groq", "structured": True}
```

**After**:

```python
elif provider.lower() == "groq":
    # Use Llama 4 Scout which supports structured outputs (json_schema)
    # Supported models: meta-llama/llama-4-scout-17b-16e-instruct, meta-llama/llama-4-maverick-17b-128e-instruct
    # See: https://console.groq.com/docs/structured-outputs#supported-models
    response_text = await LLMProvider.generate_groq(
        prompt,
        model or "meta-llama/llama-4-scout-17b-16e-instruct",  # ✅ Supports structured outputs
        max_tokens=max_tokens,
        temperature=0.7,
        response_format=schema
    )
    metadata = {"model": model or "meta-llama/llama-4-scout-17b-16e-instruct", "provider": "groq", "structured": True}
```

## Key Differences: JSON Object Mode vs Structured Outputs

### JSON Object Mode (All Models)

- ✅ Available on all Groq models
- ⚠️ Returns syntactically valid JSON
- ❌ **Does NOT guarantee schema compliance**
- ❌ May return JSON with wrong structure
- 💡 Use: `response_format: { "type": "json_object" }`

### Structured Outputs / JSON Schema Mode (Limited Models)

- ⭐ Only available on 5 specific models (listed above)
- ✅ Returns schema-compliant JSON **or throws error**
- ✅ Guarantees exact schema match
- ✅ Type-safe responses
- 💡 Use: `response_format: { "type": "json_schema", "json_schema": {...} }`

## Impact

This fix affects:

- ✅ **Structured Character Generation** - `/api/generate/character/structured`
- ✅ **Structured World Generation** - `/api/generate/world/structured`
- ✅ Any future structured generation endpoints using Groq

## Testing

1. **Character Generation with Groq**:
   - Go to Create Character page
   - Enable "Structured Generation" toggle
   - Select **Groq** as provider
   - Select any model (will default to Llama 4 Scout if none specified)
   - Generate character
   - Should succeed without 400 errors

2. **World Generation with Groq**:
   - Go to Create World page
   - Enable "Structured Generation" toggle
   - Select **Groq** as provider
   - Generate world
   - Should succeed without 400 errors

## Model Selection in UI

Users can still manually select models in the UI. If they select an unsupported model for structured generation:

1. **Recommended**: Update the UI to show which models support structured outputs
2. **Alternative**: Add validation to prevent selecting unsupported models when structured mode is enabled
3. **Fallback**: Add error handling to gracefully fallback to JSON Object Mode with validation

## Rate Limits for Llama 4 Scout

According to Groq's rate limits (free tier):

- **Requests**: 30 per minute, 14,400 per day
- **Tokens**: 15,000 per minute, 500,000 per day

This is the same as Llama Guard models and suitable for development/testing.

## Alternative Models

If Llama 4 Scout doesn't meet your needs, you can also use:

1. **`meta-llama/llama-4-maverick-17b-128e-instruct`** - More capable but similar limits
2. **`openai/gpt-oss-120b`** - Larger model, lower rate limits (8K tokens/min)
3. **`moonshotai/kimi-k2-instruct-0905`** - Alternative provider within Groq

## Next Steps

1. ✅ Fixed default model to `meta-llama/llama-4-scout-17b-16e-instruct`
2. 🔄 **Server restart required** - The backend needs to restart to pick up changes
3. 🧪 **Test structured generation** - Try creating characters/worlds with Groq
4. 📝 **Consider UI updates** - Show which models support structured outputs
5. 📚 **Update documentation** - Add this info to user-facing docs

## Server Restart

The backend server has auto-reload enabled, so it should pick up the changes automatically. If not, restart manually:

```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## References

- [Groq Structured Outputs Documentation](https://console.groq.com/docs/structured-outputs#supported-models)
- [Groq Models Documentation](https://console.groq.com/docs/models)
- [Groq Rate Limits](https://console.groq.com/docs/rate-limits)
