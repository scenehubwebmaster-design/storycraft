import json
import difflib
from typing import List, Dict, Tuple

def extract_json_array_from_text(text: str) -> List[Dict]:
    """Try to find and parse the first JSON array in the text.
    Returns parsed list or raises ValueError.
    """
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON array found in text")
    raw = text[start:end+1]
    return json.loads(raw)


def name_similarity(a: str, b: str) -> float:
    """Return a similarity ratio between two names (0-1) using SequenceMatcher."""
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def has_near_duplicates(names: List[str], threshold: float = 0.65) -> Tuple[bool, List[Tuple[int,int,float]]]:
    """Check list of names for any pairs with similarity above threshold.
    Returns (has_duplicates, list of (i,j,ratio) pairs exceeding threshold)
    """
    pairs = []
    n = len(names)
    for i in range(n):
        for j in range(i+1, n):
            sim = name_similarity(names[i], names[j])
            if sim >= threshold:
                pairs.append((i, j, sim))
    return (len(pairs) > 0, pairs)


def sanitize_name_options(options: List[Dict]) -> List[str]:
    """Extract full name strings from structured options for similarity checks."""
    names = []
    for opt in options:
        first = opt.get("first_name", "").strip()
        surname = opt.get("surname", "").strip()
        title = opt.get("title", "").strip()
        parts = [p for p in [first, surname] if p]
        full = " ".join(parts)
        if title:
            full = f"{full}, {title}"
        names.append(full)
    return names


def needs_retry_from_text(content: str, threshold: float = 0.65) -> Tuple[bool, List[Tuple[int,int,float]]]:
    """Parse LLM content and determine if the generated names require a retry due to similarity."""
    try:
        options = extract_json_array_from_text(content)
    except Exception:
        # If parse fails, request retry
        return True, [(0,0,0.0)]
    names = sanitize_name_options(options)
    return has_near_duplicates(names, threshold)
