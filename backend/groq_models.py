"""
Groq model management and rate limit definitions.
This module handles dynamic model fetching from Groq's API and provides
model-specific rate limits based on the free tier quotas.

Rate limit definitions are based on Groq's free tier as of 2025:
https://console.groq.com/docs/rate-limits
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Model-specific rate limits from Groq free tier
# https://console.groq.com/docs/rate-limits
MODEL_RATE_LIMITS = {
    # Production Models
    "llama-3.1-8b-instant": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 6_000,
        "tokens_per_day": 500_000,
    },
    "llama-3.3-70b-versatile": {
        "requests_per_minute": 30,
        "requests_per_day": 1_000,
        "tokens_per_minute": 12_000,
        "tokens_per_day": 100_000,
    },
    "llama-guard-3-8b": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 15_000,
        "tokens_per_day": 500_000,
    },
    "meta-llama/llama-guard-4-12b": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 15_000,
        "tokens_per_day": 500_000,
    },
    "openai/gpt-oss-120b": {
        "requests_per_minute": 30,
        "requests_per_day": 1_000,
        "tokens_per_minute": 8_000,
        "tokens_per_day": 200_000,
    },
    "openai/gpt-oss-20b": {
        "requests_per_minute": 30,
        "requests_per_day": 1_000,
        "tokens_per_minute": 8_000,
        "tokens_per_day": 200_000,
    },
    
    # Preview Models
    "meta-llama/llama-4-maverick-17b-128e-instruct": {
        "requests_per_minute": 30,
        "requests_per_day": 1_000,
        "tokens_per_minute": 6_000,
        "tokens_per_day": 500_000,
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "requests_per_minute": 30,
        "requests_per_day": 1_000,
        "tokens_per_minute": 30_000,
        "tokens_per_day": 500_000,
    },
    "meta-llama/llama-prompt-guard-2-22m": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 15_000,
        "tokens_per_day": 500_000,
    },
    "meta-llama/llama-prompt-guard-2-86m": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 15_000,
        "tokens_per_day": 500_000,
    },
    "moonshotai/kimi-k2-instruct": {
        "requests_per_minute": 60,
        "requests_per_day": 1_000,
        "tokens_per_minute": 10_000,
        "tokens_per_day": 300_000,
    },
    "moonshotai/kimi-k2-instruct-0905": {
        "requests_per_minute": 60,
        "requests_per_day": 1_000,
        "tokens_per_minute": 10_000,
        "tokens_per_day": 300_000,
    },
    "qwen/qwen3-32b": {
        "requests_per_minute": 60,
        "requests_per_day": 1_000,
        "tokens_per_minute": 6_000,
        "tokens_per_day": 500_000,
    },
    
    # Systems (Compound models)
    "groq/compound": {
        "requests_per_minute": 30,
        "requests_per_day": 250,
        "tokens_per_minute": 70_000,
        "tokens_per_day": None,  # Not specified
    },
    "groq/compound-mini": {
        "requests_per_minute": 30,
        "requests_per_day": 250,
        "tokens_per_minute": 70_000,
        "tokens_per_day": None,  # Not specified
    },
    
    # Legacy support for common model names
    "mixtral-8x7b-32768": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 5_000,
        "tokens_per_day": 500_000,
    },
    "llama2-70b-4096": {
        "requests_per_minute": 30,
        "requests_per_day": 14_400,
        "tokens_per_minute": 6_000,
        "tokens_per_day": 500_000,
    },
}


async def fetch_available_models() -> List[Dict]:
    """
    Fetch available Groq models from the API.
    Returns a list of model dictionaries with id, name, and rate_limits.
    
    Note: Requires GROQ_API_KEY environment variable to be set.
    Falls back to hardcoded list if API call fails.
    """
    try:
        import os
        import httpx
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set, using fallback model list")
            return get_fallback_models()
        
        # Fetch models from Groq API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=5.0,
            )
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get("data", []):
                model_id = model_data.get("id")
                if model_id:
                    # Get rate limits for this model if available
                    rate_limits = get_model_limits(model_id)
                    
                    models.append({
                        "id": model_id,
                        "name": model_data.get("name", model_id),
                        "rate_limits": rate_limits,
                        "owned_by": model_data.get("owned_by", "groq"),
                    })
            
            logger.info(f"Fetched {len(models)} models from Groq API")
            return models
            
    except Exception as e:
        logger.error(f"Failed to fetch Groq models from API: {e}")
        return get_fallback_models()


def get_fallback_models() -> List[Dict]:
    """
    Return a hardcoded list of Groq models as fallback.
    This is used when the API is unavailable or GROQ_API_KEY is not set.
    """
    return [
        {
            "id": "llama-3.3-70b-versatile",
            "name": "Meta Llama 3.3 70B",
            "rate_limits": get_model_limits("llama-3.3-70b-versatile"),
            "owned_by": "meta",
        },
        {
            "id": "llama-3.1-8b-instant",
            "name": "Meta Llama 3.1 8B (Instant)",
            "rate_limits": get_model_limits("llama-3.1-8b-instant"),
            "owned_by": "meta",
        },
        {
            "id": "meta-llama/llama-4-scout-17b-16e-instruct",
            "name": "Meta Llama 4 Scout 17B 16E",
            "rate_limits": get_model_limits("meta-llama/llama-4-scout-17b-16e-instruct"),
            "owned_by": "meta",
        },
        {
            "id": "groq/compound",
            "name": "Groq Compound (with tools)",
            "rate_limits": get_model_limits("groq/compound"),
            "owned_by": "groq",
        },
        {
            "id": "openai/gpt-oss-120b",
            "name": "OpenAI GPT-OSS 120B",
            "rate_limits": get_model_limits("openai/gpt-oss-120b"),
            "owned_by": "openai",
        },
    ]


def get_model_limits(model_id: str) -> Optional[Dict[str, int]]:
    """
    Get the rate limits for a specific Groq model.
    
    Args:
        model_id: The Groq model identifier
        
    Returns:
        Dictionary with rate limit keys, or None if model not found
    """
    return MODEL_RATE_LIMITS.get(model_id)
