"""
OpenAI model management and API client.
This module handles OpenAI model definitions and provides model-specific
information based on OpenAI's API documentation.

Model information based on OpenAI's documentation as of October 2025:
https://platform.openai.com/docs/models
"""

from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# OpenAI model definitions with capabilities and pricing
# Based on https://platform.openai.com/docs/models
OPENAI_MODELS = {
    # GPT-4o - Flagship model for complex tasks
    "gpt-4o": {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "description": "Our flagship model for complex tasks, multimodal",
        "context_window": 128_000,
        "max_output": 16_384,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 2.50,  # per MTok
            "output": 10.00,  # per MTok
        },
        "strengths": ["reasoning", "coding", "vision", "multimodal"],
        "latency": "fast",
    },
    "gpt-4o-2024-11-20": {
        "id": "gpt-4o-2024-11-20",
        "name": "GPT-4o (Nov 2024)",
        "description": "Latest GPT-4o snapshot",
        "context_window": 128_000,
        "max_output": 16_384,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 2.50,
            "output": 10.00,
        },
        "strengths": ["reasoning", "coding", "vision", "multimodal"],
        "latency": "fast",
    },
    
    # GPT-4o-mini - Affordable and fast
    "gpt-4o-mini": {
        "id": "gpt-4o-mini",
        "name": "GPT-4o mini",
        "description": "Affordable and intelligent small model for fast tasks",
        "context_window": 128_000,
        "max_output": 16_384,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 0.15,  # per MTok
            "output": 0.60,  # per MTok
        },
        "strengths": ["speed", "affordability", "vision"],
        "latency": "very-fast",
    },
    "gpt-4o-mini-2024-07-18": {
        "id": "gpt-4o-mini-2024-07-18",
        "name": "GPT-4o mini (Jul 2024)",
        "description": "GPT-4o mini snapshot",
        "context_window": 128_000,
        "max_output": 16_384,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 0.15,
            "output": 0.60,
        },
        "strengths": ["speed", "affordability", "vision"],
        "latency": "very-fast",
    },
    
    # GPT-4 Turbo - Previous generation
    "gpt-4-turbo": {
        "id": "gpt-4-turbo",
        "name": "GPT-4 Turbo",
        "description": "Previous generation high-intelligence model",
        "context_window": 128_000,
        "max_output": 4_096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 10.00,
            "output": 30.00,
        },
        "strengths": ["reasoning", "coding"],
        "latency": "moderate",
    },
    
    # GPT-3.5 Turbo - Fast and affordable
    "gpt-3.5-turbo": {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "description": "Fast, inexpensive model for simple tasks",
        "context_window": 16_385,
        "max_output": 4_096,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 0.50,
            "output": 1.50,
        },
        "strengths": ["speed", "affordability", "simple-tasks"],
        "latency": "very-fast",
    },
    "gpt-3.5-turbo-0125": {
        "id": "gpt-3.5-turbo-0125",
        "name": "GPT-3.5 Turbo (Jan 2024)",
        "description": "Latest GPT-3.5 Turbo snapshot",
        "context_window": 16_385,
        "max_output": 4_096,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_json_mode": True,
        "pricing": {
            "input": 0.50,
            "output": 1.50,
        },
        "strengths": ["speed", "affordability", "simple-tasks"],
        "latency": "very-fast",
    },
    
    # O1 Series - Advanced reasoning
    "o1-preview": {
        "id": "o1-preview",
        "name": "O1 Preview",
        "description": "Advanced reasoning model for complex problems",
        "context_window": 128_000,
        "max_output": 32_768,
        "supports_vision": False,
        "supports_function_calling": False,
        "supports_json_mode": False,
        "pricing": {
            "input": 15.00,
            "output": 60.00,
        },
        "strengths": ["reasoning", "mathematics", "science"],
        "latency": "slow",
    },
    "o1-mini": {
        "id": "o1-mini",
        "name": "O1 Mini",
        "description": "Fast reasoning model for STEM tasks",
        "context_window": 128_000,
        "max_output": 65_536,
        "supports_vision": False,
        "supports_function_calling": False,
        "supports_json_mode": False,
        "pricing": {
            "input": 3.00,
            "output": 12.00,
        },
        "strengths": ["reasoning", "STEM", "speed"],
        "latency": "moderate",
    },
}

# Default model recommendations by use case
DEFAULT_MODELS = {
    "general": "gpt-4o-mini",
    "creative": "gpt-4o",
    "coding": "gpt-4o",
    "chat": "gpt-4o-mini",
    "reasoning": "o1-preview",
    "affordable": "gpt-3.5-turbo",
    "vision": "gpt-4o-mini",
}


def get_available_models() -> List[Dict]:
    """
    Get list of available OpenAI models.
    
    Returns:
        List of models with standardized format
    """
    models = []
    
    for model_id, model_info in OPENAI_MODELS.items():
        # Skip dated versions if the base version exists
        if model_id.endswith(('-2024-11-20', '-2024-07-18', '-0125')) and \
           model_id.split('-')[0] + ('-' + model_id.split('-')[1] if len(model_id.split('-')) > 2 else '') in OPENAI_MODELS:
            continue
            
        models.append({
            "id": model_info["id"],
            "name": model_info["name"],
            "description": model_info["description"],
            "context_window": model_info["context_window"],
            "max_output": model_info["max_output"],
            "supports_vision": model_info["supports_vision"],
            "supports_function_calling": model_info["supports_function_calling"],
            "supports_json_mode": model_info["supports_json_mode"],
            "pricing_per_mtok": {
                "input": model_info["pricing"]["input"],
                "output": model_info["pricing"]["output"],
            },
            "strengths": model_info["strengths"],
            "latency": model_info["latency"],
            "provider": "openai"
        })
    
    return models


def get_model_info(model_id: str) -> Optional[Dict]:
    """Get information about a specific OpenAI model"""
    return OPENAI_MODELS.get(model_id)


def get_recommended_model(use_case: str = "general") -> str:
    """Get recommended model for a specific use case"""
    return DEFAULT_MODELS.get(use_case, "gpt-4o-mini")


def supports_feature(model_id: str, feature: str) -> bool:
    """
    Check if a model supports a specific feature.
    
    Args:
        model_id: The model identifier
        feature: Feature to check ('vision', 'function_calling', 'json_mode')
    
    Returns:
        True if the model supports the feature, False otherwise
    """
    model = OPENAI_MODELS.get(model_id)
    if not model:
        return False
    
    feature_map = {
        "vision": "supports_vision",
        "function_calling": "supports_function_calling",
        "json_mode": "supports_json_mode",
    }
    
    feature_key = feature_map.get(feature, f"supports_{feature}")
    return model.get(feature_key, False)


def fetch_available_models() -> List[Dict]:
    """
    Fetch available OpenAI models.
    This function mirrors the API used by other providers (Groq, Gemini, Claude).
    
    Returns:
        List of available models with their metadata
    """
    try:
        return get_available_models()
    except Exception as e:
        logger.error(f"Error fetching OpenAI models: {str(e)}")
        return []


# For testing
if __name__ == "__main__":
    print("=== Available OpenAI Models ===")
    models = get_available_models()
    for model in models:
        print(f"\n{model['name']} ({model['id']})")
        print(f"  Description: {model['description']}")
        print(f"  Context: {model['context_window']:,} tokens")
        print(f"  Max Output: {model['max_output']:,} tokens")
        print(f"  Vision: {model['supports_vision']}")
        print(f"  Function Calling: {model['supports_function_calling']}")
        print(f"  JSON Mode: {model['supports_json_mode']}")
        print(f"  Pricing: ${model['pricing_per_mtok']['input']}/MTok input, ${model['pricing_per_mtok']['output']}/MTok output")
        print(f"  Strengths: {', '.join(model['strengths'])}")
        print(f"  Latency: {model['latency']}")
    
    print("\n=== Default Models by Use Case ===")
    for use_case, model_id in DEFAULT_MODELS.items():
        model_info = get_model_info(model_id)
        if model_info:
            print(f"  {use_case}: {model_info['name']} ({model_id})")
    
    print("\n=== Feature Check Examples ===")
    print(f"  gpt-4o supports vision: {supports_feature('gpt-4o', 'vision')}")
    print(f"  gpt-3.5-turbo supports vision: {supports_feature('gpt-3.5-turbo', 'vision')}")
    print(f"  o1-preview supports function_calling: {supports_feature('o1-preview', 'function_calling')}")
