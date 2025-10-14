"""
Google Gemini Model Manager
Fetches available models and their rate limits from the Gemini API.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


# Model rate limits based on user's quota table
# Format: RPM (Requests Per Minute), TPM (Tokens Per Minute), RPD (Requests Per Day)
MODEL_RATE_LIMITS = {
    "gemini-2.5-flash": {
        "requests_per_minute": 10,  # From user's table: 3/10
        "tokens_per_minute": 250_000,  # From user's table: 7.65K/250K
        "requests_per_day": 250,  # From user's table: 3/250
        "display_name": "Gemini 2.5 Flash",
        "description": "Fast and intelligent model with thinking capabilities"
    },
    "gemini-2.0-flash": {
        "requests_per_minute": 15,  # From user's table: 1/15
        "tokens_per_minute": 1_000_000,  # From user's table: 190/1M
        "requests_per_day": 200,  # From user's table: 1/200
        "display_name": "Gemini 2.0 Flash",
        "description": "Second generation workhorse model with 1M token context"
    },
}


async def fetch_available_models() -> List[Dict[str, Any]]:
    """
    Fetch available Gemini models from the API.
    Falls back to hardcoded list if API call fails.
    """
    if not GOOGLE_AVAILABLE:
        logger.warning("Google AI client not available, using fallback model list")
        return get_fallback_models()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("Google API key not configured, using fallback model list")
        return get_fallback_models()
    
    try:
        genai.configure(api_key=api_key)
        
        # List all available models
        models = []
        for model in genai.list_models():
            model_id = model.name.replace("models/", "")
            
            # Only include text generation models we support
            if model_id in MODEL_RATE_LIMITS:
                models.append({
                    "id": model_id,
                    "display_name": MODEL_RATE_LIMITS[model_id]["display_name"],
                    "description": MODEL_RATE_LIMITS[model_id]["description"],
                    "rate_limits": {
                        "requests_per_minute": MODEL_RATE_LIMITS[model_id]["requests_per_minute"],
                        "tokens_per_minute": MODEL_RATE_LIMITS[model_id]["tokens_per_minute"],
                        "requests_per_day": MODEL_RATE_LIMITS[model_id]["requests_per_day"],
                    },
                    "supported_generation_methods": model.supported_generation_methods,
                })
        
        if not models:
            logger.warning("No supported models found from API, using fallback")
            return get_fallback_models()
        
        logger.info(f"Fetched {len(models)} available Gemini models from API")
        return models
    
    except Exception as e:
        logger.error(f"Failed to fetch models from Gemini API: {e}")
        return get_fallback_models()


def get_fallback_models() -> List[Dict[str, Any]]:
    """
    Return hardcoded list of supported models when API fetch fails.
    """
    return [
        {
            "id": "gemini-2.5-flash",
            "display_name": "Gemini 2.5 Flash",
            "description": "Fast and intelligent model with thinking capabilities",
            "rate_limits": {
                "requests_per_minute": 10,
                "tokens_per_minute": 250_000,
                "requests_per_day": 250,
            },
            "supported_generation_methods": ["generateContent", "countTokens"],
        },
        {
            "id": "gemini-2.0-flash",
            "display_name": "Gemini 2.0 Flash",
            "description": "Second generation workhorse model with 1M token context",
            "rate_limits": {
                "requests_per_minute": 15,
                "tokens_per_minute": 1_000_000,
                "requests_per_day": 200,
            },
            "supported_generation_methods": ["generateContent", "countTokens"],
        },
    ]


def get_model_limits(model_id: str) -> Optional[Dict[str, int]]:
    """Get rate limits for a specific model."""
    if model_id in MODEL_RATE_LIMITS:
        return {
            "requests_per_minute": MODEL_RATE_LIMITS[model_id]["requests_per_minute"],
            "tokens_per_minute": MODEL_RATE_LIMITS[model_id]["tokens_per_minute"],
            "requests_per_day": MODEL_RATE_LIMITS[model_id]["requests_per_day"],
        }
    return None
