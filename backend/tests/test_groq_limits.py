from backend.model_cache import set_models, clear
from backend.rate_limiter import RateLimiter


def test_groq_model_limits_from_cache(monkeypatch):
    # Ensure clean cache
    clear()

    # Insert a fake Groq model with specific rate limits
    fake_model = {
        "id": "meta-llama/llama-4-scout-17b-16e-instruct",
        "name": "Meta Llama Scout",
        "rate_limits": {"tokens_per_minute": 30000, "requests_per_minute": 30},
    }
    set_models("groq", [fake_model])

    rl = RateLimiter()

    # Simulate check for the specific model; ensure no None and token limit honored
    res = rl.check_rate_limit("groq", estimated_tokens=1000, model=fake_model["id"])
    # If check returns None, it's allowed; ensure projected tokens <= tokens_per_minute
    assert res is None or res.get("limit_type") != "tokens_per_minute"

    # Clean up
    clear()