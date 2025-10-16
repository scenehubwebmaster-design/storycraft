"""
Claude (Anthropic) model management and API client.
This module handles Claude model definitions and provides model-specific
information based on Anthropic's API documentation.

Model information based on Anthropic's documentation as of October 2025:
https://docs.anthropic.com/en/docs/about-claude/models
"""

from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Claude model definitions with capabilities and pricing
# Based on https://docs.anthropic.com/en/docs/about-claude/models/overview
CLAUDE_MODELS = {
    # Claude Sonnet 4.5 - Best for complex agents and coding
    "claude-sonnet-4-5": {
        "id": "claude-sonnet-4-5",
        "name": "Claude Sonnet 4.5",
        "version": "claude-sonnet-4-5-20250929",
        "description": "Our best model for complex agents and coding",
        "context_window": 200_000,  # 200K default, 1M beta available
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,  # per MTok
            "output": 15.00,  # per MTok
            "cache_write_5m": 3.75,  # per MTok (5-min cache)
            "cache_write_1h": 6.00,  # per MTok (1-hour cache)
            "cache_read": 0.30,  # per MTok
        },
        "strengths": ["coding", "reasoning", "agentic", "long-context"],
        "latency": "fast",
    },
    "claude-sonnet-4-5-20250929": {
        "id": "claude-sonnet-4-5-20250929",
        "name": "Claude Sonnet 4.5",
        "version": "20250929",
        "description": "Our best model for complex agents and coding",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write_5m": 3.75,
            "cache_write_1h": 6.00,
            "cache_read": 0.30,
        },
        "strengths": ["coding", "reasoning", "agentic", "long-context"],
        "latency": "fast",
    },
    
    # Claude Sonnet 4 - High-performance model
    "claude-sonnet-4": {
        "id": "claude-sonnet-4",
        "name": "Claude Sonnet 4",
        "version": "claude-sonnet-4-20250514",
        "description": "High-performance model",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write_5m": 3.75,
            "cache_write_1h": 6.00,
            "cache_read": 0.30,
        },
        "strengths": ["balanced-performance", "intelligence"],
        "latency": "fast",
    },
    "claude-sonnet-4-20250514": {
        "id": "claude-sonnet-4-20250514",
        "name": "Claude Sonnet 4",
        "version": "20250514",
        "description": "High-performance model",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write_5m": 3.75,
            "cache_write_1h": 6.00,
            "cache_read": 0.30,
        },
        "strengths": ["balanced-performance", "intelligence"],
        "latency": "fast",
    },
    
    # Claude Sonnet 3.7 - High-performance with extended thinking
    "claude-3-7-sonnet": {
        "id": "claude-3-7-sonnet",
        "name": "Claude Sonnet 3.7",
        "version": "claude-3-7-sonnet-20250219",
        "description": "High-performance model with early extended thinking",
        "context_window": 200_000,
        "max_output": 64_000,  # 128K with beta header
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write_5m": 3.75,
            "cache_write_1h": 6.00,
            "cache_read": 0.30,
        },
        "strengths": ["thinking", "intelligence"],
        "latency": "fast",
    },
    "claude-3-7-sonnet-20250219": {
        "id": "claude-3-7-sonnet-20250219",
        "name": "Claude Sonnet 3.7",
        "version": "20250219",
        "description": "High-performance model with early extended thinking",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write_5m": 3.75,
            "cache_write_1h": 6.00,
            "cache_read": 0.30,
        },
        "strengths": ["thinking", "intelligence"],
        "latency": "fast",
    },
    
    # Claude Haiku 4.5 - Fastest and most intelligent Haiku
    "claude-haiku-4-5": {
        "id": "claude-haiku-4-5",
        "name": "Claude Haiku 4.5",
        "version": "claude-haiku-4-5-20251001",
        "description": "Our fastest and most intelligent Haiku model",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 1.00,
            "output": 5.00,
            "cache_write_5m": 1.25,
            "cache_write_1h": 2.00,
            "cache_read": 0.10,
        },
        "strengths": ["speed", "cost-efficiency", "thinking"],
        "latency": "fastest",
    },
    "claude-haiku-4-5-20251001": {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "version": "20251001",
        "description": "Our fastest and most intelligent Haiku model",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 1.00,
            "output": 5.00,
            "cache_write_5m": 1.25,
            "cache_write_1h": 2.00,
            "cache_read": 0.10,
        },
        "strengths": ["speed", "cost-efficiency", "thinking"],
        "latency": "fastest",
    },
    
    # Claude Haiku 3.5 - Fast and compact
    "claude-3-5-haiku": {
        "id": "claude-3-5-haiku",
        "name": "Claude Haiku 3.5",
        "version": "claude-3-5-haiku-20241022",
        "description": "Our fastest model",
        "context_window": 200_000,
        "max_output": 8_192,
        "supports_vision": True,
        "supports_thinking": False,
        "supports_caching": True,
        "pricing": {
            "input": 0.80,
            "output": 4.00,
            "cache_write_5m": 1.00,
            "cache_write_1h": 1.60,
            "cache_read": 0.08,
        },
        "strengths": ["speed", "cost-efficiency"],
        "latency": "fastest",
    },
    "claude-3-5-haiku-20241022": {
        "id": "claude-3-5-haiku-20241022",
        "name": "Claude Haiku 3.5",
        "version": "20241022",
        "description": "Our fastest model",
        "context_window": 200_000,
        "max_output": 8_192,
        "supports_vision": True,
        "supports_thinking": False,
        "supports_caching": True,
        "pricing": {
            "input": 0.80,
            "output": 4.00,
            "cache_write_5m": 1.00,
            "cache_write_1h": 1.60,
            "cache_read": 0.08,
        },
        "strengths": ["speed", "cost-efficiency"],
        "latency": "fastest",
    },
    
    # Claude Opus 4.1 - Exceptional for specialized tasks
    "claude-opus-4-1": {
        "id": "claude-opus-4-1",
        "name": "Claude Opus 4.1",
        "version": "claude-opus-4-1-20250805",
        "description": "Exceptional model for specialized complex tasks",
        "context_window": 200_000,
        "max_output": 32_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 15.00,
            "output": 75.00,
            "cache_write_5m": 18.75,
            "cache_write_1h": 30.00,
            "cache_read": 1.50,
        },
        "strengths": ["reasoning", "specialized-tasks", "complex-problems"],
        "latency": "moderately-fast",
    },
    "claude-opus-4-1-20250805": {
        "id": "claude-opus-4-1-20250805",
        "name": "Claude Opus 4.1",
        "version": "20250805",
        "description": "Exceptional model for specialized complex tasks",
        "context_window": 200_000,
        "max_output": 32_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 15.00,
            "output": 75.00,
            "cache_write_5m": 18.75,
            "cache_write_1h": 30.00,
            "cache_read": 1.50,
        },
        "strengths": ["reasoning", "specialized-tasks", "complex-problems"],
        "latency": "moderately-fast",
    },
    
    # Claude Opus 4 - Previous flagship
    "claude-opus-4": {
        "id": "claude-opus-4",
        "name": "Claude Opus 4",
        "version": "claude-opus-4-20250514",
        "description": "Our previous flagship model",
        "context_window": 200_000,
        "max_output": 32_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 15.00,
            "output": 75.00,
            "cache_write_5m": 18.75,
            "cache_write_1h": 30.00,
            "cache_read": 1.50,
        },
        "strengths": ["intelligence", "capability"],
        "latency": "moderately-fast",
    },
    "claude-opus-4-20250514": {
        "id": "claude-opus-4-20250514",
        "name": "Claude Opus 4",
        "version": "20250514",
        "description": "Our previous flagship model",
        "context_window": 200_000,
        "max_output": 32_000,
        "supports_vision": True,
        "supports_thinking": True,
        "supports_caching": True,
        "pricing": {
            "input": 15.00,
            "output": 75.00,
            "cache_write_5m": 18.75,
            "cache_write_1h": 30.00,
            "cache_read": 1.50,
        },
        "strengths": ["intelligence", "capability"],
        "latency": "moderately-fast",
    },
}

# Default model recommendations by use case
DEFAULT_MODELS = {
    "coding": "claude-sonnet-4-5",
    "reasoning": "claude-opus-4-1",
    "fast": "claude-haiku-4-5",
    "cost-effective": "claude-haiku-3-5",
    "balanced": "claude-sonnet-4",
    "thinking": "claude-3-7-sonnet",
}


def get_available_models() -> List[Dict]:
    """
    Get list of available Claude models with their capabilities.
    
    Returns:
        List of model dictionaries with id, name, description, and capabilities
    """
    models = []
    seen_ids = set()
    
    for model_id, model_info in CLAUDE_MODELS.items():
        # Only include base model names (not versioned duplicates)
        if model_id in seen_ids:
            continue
        
        # Add to seen set to avoid duplicates
        base_id = model_info["id"]
        if "-202" not in base_id:  # Skip if it's a dated version
            seen_ids.add(base_id)
            
            models.append({
                "id": base_id,
                "name": model_info["name"],
                "description": model_info["description"],
                "context_window": model_info["context_window"],
                "max_output": model_info["max_output"],
                "supports_vision": model_info["supports_vision"],
                "supports_thinking": model_info["supports_thinking"],
                "supports_caching": model_info["supports_caching"],
                "pricing_per_mtok": {
                    "input": model_info["pricing"]["input"],
                    "output": model_info["pricing"]["output"],
                },
                "strengths": model_info["strengths"],
                "latency": model_info["latency"],
            })
    
    return models


def get_model_info(model_id: str) -> Optional[Dict]:
    """
    Get detailed information about a specific Claude model.
    
    Args:
        model_id: The model identifier (e.g., "claude-sonnet-4-5" or "claude-sonnet-4-5-20250929")
    
    Returns:
        Model information dictionary, or None if model not found
    """
    return CLAUDE_MODELS.get(model_id)


def get_default_model(use_case: str = "balanced") -> str:
    """
    Get the recommended default model for a specific use case.
    
    Args:
        use_case: The use case (coding, reasoning, fast, cost-effective, balanced, thinking)
    
    Returns:
        Model ID string
    """
    return DEFAULT_MODELS.get(use_case, "claude-sonnet-4-5")


def get_model_pricing(model_id: str) -> Optional[Dict]:
    """
    Get pricing information for a specific model.
    
    Args:
        model_id: The model identifier
    
    Returns:
        Pricing dictionary with input/output/cache costs, or None if model not found
    """
    model_info = get_model_info(model_id)
    if model_info:
        return model_info["pricing"]
    return None


def supports_feature(model_id: str, feature: str) -> bool:
    """
    Check if a model supports a specific feature.
    
    Args:
        model_id: The model identifier
        feature: Feature to check (vision, thinking, caching)
    
    Returns:
        True if feature is supported, False otherwise
    """
    model_info = get_model_info(model_id)
    if not model_info:
        return False
    
    feature_key = f"supports_{feature}"
    return model_info.get(feature_key, False)


def fetch_available_models() -> List[Dict]:
    """
    Fetch available Claude models.
    This function mirrors the API used by other providers (Groq, Gemini).
    
    Returns:
        List of available models with their metadata
    """
    try:
        return get_available_models()
    except Exception as e:
        logger.error(f"Error fetching Claude models: {str(e)}")
        return []


# For testing
if __name__ == "__main__":
    print("=== Available Claude Models ===")
    models = get_available_models()
    for model in models:
        print(f"\n{model['name']} ({model['id']})")
        print(f"  Description: {model['description']}")
        print(f"  Context: {model['context_window']:,} tokens")
        print(f"  Max Output: {model['max_output']:,} tokens")
        print(f"  Vision: {model['supports_vision']}")
        print(f"  Thinking: {model['supports_thinking']}")
        print(f"  Caching: {model['supports_caching']}")
        print(f"  Pricing: ${model['pricing_per_mtok']['input']}/MTok input, ${model['pricing_per_mtok']['output']}/MTok output")
        print(f"  Strengths: {', '.join(model['strengths'])}")
        print(f"  Latency: {model['latency']}")
    
    print("\n=== Default Models by Use Case ===")
    for use_case, model_id in DEFAULT_MODELS.items():
        model_info = get_model_info(model_id)
        if model_info:
            print(f"  {use_case}: {model_info['name']} ({model_id})")
    
    print("\n=== Feature Check Examples ===")
    print(f"  claude-sonnet-4-5 supports vision: {supports_feature('claude-sonnet-4-5', 'vision')}")
    print(f"  claude-haiku-3-5 supports thinking: {supports_feature('claude-3-5-haiku', 'thinking')}")
    print(f"  claude-opus-4-1 supports caching: {supports_feature('claude-opus-4-1', 'caching')}")
