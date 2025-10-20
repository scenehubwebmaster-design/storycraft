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


def extract_json_from_text(text: str):
    """Robustly extract the first JSON object or array from a text blob.

    Attempts multiple strategies:
    1. Find the first balanced JSON object `{...}` by scanning braces.
    2. If that fails, fall back to looking for the first JSON array via
       extract_json_array_from_text.
    3. As a last resort, try to locate a substring that looks like JSON via
       simple regex-esque heuristics and json.loads.

    Returns the parsed Python object (dict or list) or raises ValueError.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    s = text
    # If the first '[' appears before the first '{', prefer extracting an array first
    first_bracket = s.find('[')
    first_brace = s.find('{')
    if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
        try:
            return extract_json_array_from_text(s)
        except Exception:
            # fall through to object scanning if array extraction fails
            pass

    # Strategy 1: find first balanced JSON object by scanning for '{' and matching '}'
    start_idx = s.find('{')
    if start_idx != -1:
        depth = 0
        for i in range(start_idx, len(s)):
            ch = s[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    candidate = s[start_idx:i+1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        # try next possible object by continuing search
                        # find next '{' after start_idx
                        start_idx = s.find('{', start_idx + 1)
                        if start_idx == -1:
                            break
                        # reset loop to new start
                        continue

    # Strategy 2: try extracting a JSON array
    try:
        return extract_json_array_from_text(s)
    except Exception:
        pass

    # Strategy 3: fallback heuristics - look for the first brace/bracey substring
    # Try to find any substring between the first '{' and last '}'
    first = s.find('{')
    last = s.rfind('}')
    if first != -1 and last != -1 and last > first:
        candidate = s[first:last+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Give up
    raise ValueError('No JSON object or array could be extracted from text')


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
