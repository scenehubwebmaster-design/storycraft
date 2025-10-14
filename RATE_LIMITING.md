# Rate Limiting Implementation

## Overview

StoryCraft implements comprehensive rate limiting to respect LLM provider quotas and prevent API abuse. The system tracks requests and tokens per provider using sliding window algorithms.

## Provider Limits

### Google Gemini (Free Tier)
- **15 requests/minute**
- **1,000,000 tokens/minute**
- **1,500 requests/day**

### OpenAI (Configurable by tier)
- **60 requests/minute** (default)
- **90,000 tokens/minute** (default)
- **10,000 requests/day** (default)

### Anthropic Claude (Configurable by tier)
- **50 requests/minute** (default)
- **100,000 tokens/minute** (default)
- **10,000 requests/day** (default)

## Architecture

### Rate Limiter Module (`backend/rate_limiter.py`)

The `RateLimiter` class uses collections.deque for efficient sliding window tracking:

```python
from rate_limiter import rate_limiter

# Check if request can proceed
error = rate_limiter.check_rate_limit("google", estimated_tokens=2000)
if error:
    # Handle rate limit exceeded
    pass

# Record successful request
rate_limiter.record_request("google", actual_tokens=1847)
```

### Key Features

1. **Sliding Window Tracking**
   - Uses `deque` for efficient O(1) append/pop operations
   - Automatically cleans up old entries outside the window
   - Tracks separate windows for minute and day limits

2. **Token Estimation**
   - Rough estimate: **1 token ≈ 4 characters ≈ 0.75 words**
   - Estimates before API call to prevent quota exhaustion
   - Records actual usage after successful generation

3. **HTTP 429 Responses**
   - Returns structured error with wait time when limits exceeded
   - Includes current usage, limit, and retry-after information

4. **Usage Monitoring**
   - GET `/api/llm/rate-limits` - All providers
   - GET `/api/llm/rate-limits/{provider}` - Specific provider
   - Returns current/limit/available for all quotas

## Integration Points

### 1. LLM Router (`backend/routers/llm.py`)

```python
@router.post("/generate")
async def generate_content(request: LLMRequest):
    # Check rate limits BEFORE making API call
    estimated_tokens = len(request.prompt) // 4 + request.max_tokens
    rate_limit_error = rate_limiter.check_rate_limit(request.provider, estimated_tokens)
    
    if rate_limit_error:
        raise HTTPException(status_code=429, detail=rate_limit_error)
    
    # Make API call...
    content = await LLMProvider.generate_google(prompt, model)
    
    # Record successful request AFTER generation
    actual_tokens = len(content) // 4
    rate_limiter.record_request(request.provider, actual_tokens)
```

### 2. Generation Router (`backend/routers/generation.py`)

The `call_llm()` function includes rate limiting for all AI generation endpoints:
- Character generation
- Story generation
- World generation
- Scene generation
- Location generation

## Error Response Format

When rate limit is exceeded, the API returns HTTP 429 with:

```json
{
  "error": "rate_limit_exceeded",
  "limit_type": "requests_per_minute",
  "current": 15,
  "limit": 15,
  "wait_seconds": 42,
  "message": "Rate limit exceeded: 15/15 requests/min. Wait 42s."
}
```

## Usage Statistics Response

GET `/api/llm/rate-limits/google` returns:

```json
{
  "provider": "google",
  "requests_per_minute": {
    "current": 8,
    "limit": 15,
    "available": 7
  },
  "tokens_per_minute": {
    "current": 16234,
    "limit": 1000000,
    "available": 983766
  },
  "requests_per_day": {
    "current": 342,
    "limit": 1500,
    "available": 1158
  }
}
```

## Best Practices

### For Heavy Usage Sessions

1. **Batch Operations**
   - Combine multiple prompts into single requests when possible
   - Use larger context windows instead of many small calls

2. **Client-Side Throttling**
   - Debounce generate buttons (e.g., 2-second cooldown)
   - Show rate limit status in UI
   - Disable buttons when limits are close to exceeded

3. **Caching Strategy**
   - Store generated content in database
   - Reuse previous generations when appropriate
   - Cache prompt templates and common responses

4. **Progressive Generation**
   - Stream large outputs instead of waiting for complete response
   - Show partial results to improve perceived performance

5. **Fallback Providers**
   - Allow users to switch providers when one is exhausted
   - Configure multiple API keys for load distribution

### Token Usage Optimization

**Example Token Counts:**
- Short prompt (100 words): ~133 tokens
- Medium prompt (500 words): ~667 tokens
- Character generation (full): ~1,500-2,500 tokens
- Story outline: ~500-1,000 tokens
- Full chapter: ~2,000-4,000 tokens

**Gemini Free Tier Capacity:**
- 1M tokens/min ≈ 500 full character generations/min
- 1,500 req/day ≈ 62 sessions × 24 generations each
- 15 req/min = tight constraint for interactive multi-step flows

## Monitoring and Alerts

### Log Messages

The rate limiter logs important events:

```python
logger.info(f"Recorded {provider} request: {tokens_used} tokens used")
logger.warning(f"Rate limit exceeded for {provider}: {rate_limit_error}")
```

### Recommended Monitoring

1. **Track daily usage** - Alert when approaching 80% of daily limit
2. **Monitor burst patterns** - Identify users making excessive requests
3. **Token consumption trends** - Optimize prompts if usage is high
4. **Error rate tracking** - Watch for frequent 429 responses

## Future Enhancements

### Planned Features

1. **User-Level Quotas**
   - Per-user rate limits to prevent single user exhaustion
   - Fair usage policies across multiple users

2. **Queue System**
   - Serialize requests server-side
   - Show queue position and estimated wait time
   - Automatic retry with exponential backoff

3. **Cache Layer**
   - Redis-based caching for repeated prompts
   - Shared cache across users for common generations
   - TTL-based invalidation

4. **Premium Tiers**
   - Allow users to provide their own API keys
   - Higher limits for paid accounts
   - Priority queue for premium users

5. **Analytics Dashboard**
   - Real-time usage visualization
   - Cost tracking per provider
   - User activity heatmaps

## Configuration

To adjust rate limits, edit `backend/rate_limiter.py`:

```python
self.limits = {
    "google": {
        "requests_per_minute": 15,  # Adjust based on your tier
        "tokens_per_minute": 1_000_000,
        "requests_per_day": 1500,
    },
    # ...
}
```

## Testing

To test rate limiting:

```bash
# Make 16 rapid requests to exceed Gemini's 15/min limit
for i in {1..16}; do
  curl -X POST http://localhost:8000/api/llm/generate \
    -H "Content-Type: application/json" \
    -d "{\"provider\":\"google\",\"prompt\":\"Test $i\",\"max_tokens\":100}"
done

# Check rate limit status
curl http://localhost:8000/api/llm/rate-limits/google
```

## Conclusion

The rate limiting implementation ensures StoryCraft respects provider quotas while maintaining a smooth user experience. For single-user sessions, the token quota is generous, but the requests/minute and requests/day limits require careful management for interactive, multi-step workflows.
