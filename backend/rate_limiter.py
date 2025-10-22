"""
Rate limiter for LLM API calls to respect provider limits.
Supports per-provider rate limiting with token-based and request-based quotas.
Supports per-model rate limiting for providers that have model-specific quotas.
"""
import logging
from typing import Dict, Optional
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import model-specific rate limits
try:
    from gemini_models import get_model_limits as get_gemini_model_limits
except ImportError:
    logger.warning("Failed to import gemini_models, model-specific limits unavailable")
    get_gemini_model_limits = None

try:
    from groq_models import get_model_limits as get_groq_model_limits
except ImportError:
    try:
        # Try backend package import as a fallback (module lives in backend/groq_models.py)
        from backend.groq_models import get_model_limits as get_groq_model_limits  # type: ignore
    except Exception:
        logger.warning("Failed to import groq_models (tried top-level and backend.groq_models), model-specific limits unavailable")
        get_groq_model_limits = None


class RateLimiter:
    """
    Rate limiter that tracks requests and tokens per provider.
    Supports sliding window rate limiting for both requests/min and requests/day.
    """
    
    def __init__(self):
        # Provider configurations (requests/min, tokens/min, requests/day)
        self.limits = {
            "google": {
                "requests_per_minute": 15,
                "tokens_per_minute": 1_000_000,
                "requests_per_day": 1500,
            },
            "openai": {
                "requests_per_minute": 60,  # Adjust based on your tier
                "tokens_per_minute": 90_000,
                "requests_per_day": 10_000,
            },
            "anthropic": {
                "requests_per_minute": 50,  # Adjust based on your tier
                "tokens_per_minute": 100_000,
                "requests_per_day": 10_000,
            },
            "groq": {
                "requests_per_minute": 30,  # Free tier default
                # Raise default token ceiling for Groq to allow larger structured requests
                "tokens_per_minute": 10_000,
                "requests_per_day": 14_400,  # Free tier default
            }
        }
        
        # Track requests with timestamps for sliding window
        self.request_history: Dict[str, deque] = {
            provider: deque() for provider in self.limits.keys()
        }
        
        # Track tokens with timestamps
        self.token_history: Dict[str, deque] = {
            provider: deque() for provider in self.limits.keys()
        }
        
        # Track daily requests
        self.daily_requests: Dict[str, deque] = {
            provider: deque() for provider in self.limits.keys()
        }
    
    def _cleanup_old_entries(self, provider: str):
        """Remove entries older than the tracking window."""
        now = datetime.now()
        
        # Clean up minute window (keep last 60 seconds)
        minute_ago = now - timedelta(seconds=60)
        while self.request_history[provider] and self.request_history[provider][0] < minute_ago:
            self.request_history[provider].popleft()
        
        while self.token_history[provider] and self.token_history[provider][0][0] < minute_ago:
            self.token_history[provider].popleft()
        
        # Clean up day window (keep last 24 hours)
        day_ago = now - timedelta(days=1)
        while self.daily_requests[provider] and self.daily_requests[provider][0] < day_ago:
            self.daily_requests[provider].popleft()
    
    def check_rate_limit(self, provider: str, estimated_tokens: int = 2000, model: str = None) -> Optional[dict]:
        """
        Check if request can proceed without exceeding rate limits.
        
        Args:
            provider: LLM provider name (google, openai, anthropic)
            estimated_tokens: Estimated token count for this request
            model: Optional model name for model-specific rate limits (e.g., "gemini-2.5-flash")
            
        Returns:
            None if request can proceed, or dict with error info if limit exceeded
        """
        provider = provider.lower()
        
        if provider not in self.limits:
            logger.warning(f"Unknown provider {provider}, allowing request")
            return None
        
        self._cleanup_old_entries(provider)
        
        limits = self.limits[provider].copy()
        
        # Override with model-specific limits if available
        if provider == "google" and model and get_gemini_model_limits:
            model_limits = get_gemini_model_limits(model)
            if model_limits:
                limits.update(model_limits)
                logger.debug(f"Using model-specific limits for {model}: {model_limits}")
        
        if provider == "groq" and model and get_groq_model_limits:
            model_limits = get_groq_model_limits(model)
            if model_limits:
                limits.update(model_limits)
                logger.debug(f"Using model-specific limits for {model}: {model_limits}")

        # If we didn't have groq model limits available at import time, try a lazy import
        if provider == "groq" and model and not get_groq_model_limits:
            try:
                import importlib
                mod = importlib.import_module("backend.groq_models")
                gm = getattr(mod, "get_model_limits", None)
                if gm:
                    # Register into module-level name so subsequent calls use it
                    globals()["get_groq_model_limits"] = gm
                    model_limits = gm(model)
                    if model_limits:
                        limits.update(model_limits)
                        logger.debug(f"Using lazily-loaded model-specific limits for {model}: {model_limits}")
            except Exception:
                # We purposely silence errors here; logging already occurred at import time
                pass
        
        # Check requests per minute
        requests_last_minute = len(self.request_history[provider])
        if requests_last_minute >= limits["requests_per_minute"]:
            wait_time = 60 - (datetime.now() - self.request_history[provider][0]).total_seconds()
            return {
                "error": "rate_limit_exceeded",
                "limit_type": "requests_per_minute",
                "current": requests_last_minute,
                "limit": limits["requests_per_minute"],
                "wait_seconds": int(wait_time) + 1,
                "message": f"Rate limit exceeded: {requests_last_minute}/{limits['requests_per_minute']} requests/min. Wait {int(wait_time) + 1}s."
            }
        
        # Check tokens per minute
        tokens_last_minute = sum(tokens for _, tokens in self.token_history[provider])
        projected_tokens = tokens_last_minute + estimated_tokens
        if projected_tokens > limits["tokens_per_minute"]:
            return {
                "error": "rate_limit_exceeded",
                "limit_type": "tokens_per_minute",
                "current": tokens_last_minute,
                "projected": projected_tokens,
                "limit": limits["tokens_per_minute"],
                "message": f"Token rate limit exceeded: current={tokens_last_minute}, estimated_request={estimated_tokens}, projected={projected_tokens}/{limits['tokens_per_minute']} tokens/min."
            }
        
        # Check requests per day
        requests_last_day = len(self.daily_requests[provider])
        if requests_last_day >= limits["requests_per_day"]:
            return {
                "error": "rate_limit_exceeded",
                "limit_type": "requests_per_day",
                "current": requests_last_day,
                "limit": limits["requests_per_day"],
                "message": f"Daily rate limit exceeded: {requests_last_day}/{limits['requests_per_day']} requests/day."
            }
        
        return None
    
    def record_request(self, provider: str, tokens_used: int):
        """
        Record a successful request with token usage.
        
        Args:
            provider: LLM provider name
            tokens_used: Actual tokens used in the request
        """
        provider = provider.lower()
        
        if provider not in self.limits:
            return
        
        now = datetime.now()
        
        # Record request
        self.request_history[provider].append(now)
        self.daily_requests[provider].append(now)
        
        # Record tokens
        self.token_history[provider].append((now, tokens_used))
        
        logger.info(f"Recorded {provider} request: {tokens_used} tokens used")
    
    def get_usage_stats(self, provider: str) -> dict:
        """Get current usage statistics for a provider."""
        provider = provider.lower()
        
        if provider not in self.limits:
            return {"error": "Unknown provider"}
        
        self._cleanup_old_entries(provider)
        
        limits = self.limits[provider]
        requests_last_minute = len(self.request_history[provider])
        tokens_last_minute = sum(tokens for _, tokens in self.token_history[provider])
        requests_last_day = len(self.daily_requests[provider])
        
        return {
            "provider": provider,
            "requests_per_minute": {
                "current": requests_last_minute,
                "limit": limits["requests_per_minute"],
                "available": limits["requests_per_minute"] - requests_last_minute,
            },
            "tokens_per_minute": {
                "current": tokens_last_minute,
                "limit": limits["tokens_per_minute"],
                "available": limits["tokens_per_minute"] - tokens_last_minute,
            },
            "requests_per_day": {
                "current": requests_last_day,
                "limit": limits["requests_per_day"],
                "available": limits["requests_per_day"] - requests_last_day,
            }
        }


# Global rate limiter instance
rate_limiter = RateLimiter()
