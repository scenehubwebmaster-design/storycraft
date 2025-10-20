"""
Simple model capability registry for structured outputs.

This module exposes a small whitelist mapping providers -> models that are
known to accept structured output parameters (like OpenAI's response_format).
It also provides a helper to check if a given provider+model supports native
structured outputs. Keep this list configurable; it's intentionally small and
updated minimally to avoid overreliance on runtime discovery.
"""
from typing import Dict, List

# Known provider -> set/list of model name prefixes that support structured outputs.
# Use prefixes to match families like 'gpt-4' or 'gpt-4o' or exact names where useful.
_STRUCTURED_MODEL_MAP: Dict[str, List[str]] = {
    "openai": [
        # Canonical GPT-4 families that support structured outputs
        "gpt-4",
        "gpt-4-turbo",
        # gpt-4o family (realtime / mini variants)
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4o-realtime",
        # 3.5 family variants with extended token windows
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ],
    "google": [
        # Gemini family prefixes - keep general to match minor versioning
        "gemini",
        "gemini-1.5",
        "gemini-2",
        "gemini-2.5",
    ],
    "groq": [
        # Groq Llama 4 variants known to support json_schema structured outputs
        "llama-4-scout",
        "llama-4-maverick",
        "llama-4-",
    ],
    # Anthropic does not have a native structured param in our current flow
}


def supports_model_structured(provider: str, model: str | None) -> bool:
    """Return True if the provider+model is known to accept native structured params.

    If `model` is None, return True only if the provider is known to accept structured
    params for some default model family.
    """
    if not provider:
        return False
    p = provider.lower()
    if p not in _STRUCTURED_MODEL_MAP:
        return False

    if not model:
        # If no model specified, assume structured supported for provider if map has entries
        return len(_STRUCTURED_MODEL_MAP.get(p, [])) > 0

    m = model.lower()
    prefixes = _STRUCTURED_MODEL_MAP.get(p, [])
    for pref in prefixes:
        if m.startswith(pref):
            return True
    return False


# Recommended per-model maximum output token budgets (approximate).
# These are used to decide whether a schema's expected output might exceed
# a model's comfortable output window and to pick a safe increased retry.
# Keys are provider lowercase -> model prefix -> recommended max output tokens.
_MODEL_OUTPUT_LIMITS: Dict[str, Dict[str, int]] = {
    "openai": {
        "gpt-4": 6000,
        "gpt-4-turbo": 8000,
        "gpt-3.5-turbo-16k": 14000,
        "gpt-3.5-turbo": 4000,
    },
    "google": {
        "gemini-2.5": 8000,
        "gemini-2": 6000,
    },
    "groq": {
        # Groq/llama families have smaller/default windows depending on model
        "llama-4-scout": 4000,
        "llama-4-maverick": 6000,
        "llama-3.3-70b-versatile": 3000,
        # Additional Groq-hosted model families we may call
        "moonshotai/kimi-k2": 6000,
        "openai/gpt-oss-20b": 4000,
        "openai/gpt-oss-120b": 8000,
    }
}


def get_model_output_limit(provider: str, model: str | None, default: int = 3000) -> int:
    """Return a recommended max output tokens for a provider+model.

    Falls back to `default` when no specific entry exists.
    """
    if not provider:
        return default
    p = provider.lower()
    if not model:
        # Return a conservative default for known providers
        return default
    m = model.lower()
    provider_limits = _MODEL_OUTPUT_LIMITS.get(p, {})
    # Prefer prefix matches (longest prefix wins)
    best = None
    best_len = 0
    for pref, limit in provider_limits.items():
        if m.startswith(pref) and len(pref) > best_len:
            best = limit
            best_len = len(pref)
    if best is not None:
        return best
    return default
