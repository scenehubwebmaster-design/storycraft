"""
Simple in-memory cache for provider models and metadata.
Used to store results from backend.groq_models.fetch_available_models() at startup.
"""
from typing import Dict, List, Optional
import threading

_lock = threading.Lock()
_cache: Dict[str, List[Dict]] = {}


def set_models(provider: str, models: List[Dict]):
    with _lock:
        _cache[provider.lower()] = models


def get_models(provider: str) -> Optional[List[Dict]]:
    return _cache.get(provider.lower())


def clear():
    with _lock:
        _cache.clear()
