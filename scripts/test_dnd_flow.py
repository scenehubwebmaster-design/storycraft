#!/usr/bin/env python3
"""
Quick test script to exercise the backend DnD generation endpoint and inspect
structured_data, name suggestions, and physical trait fallbacks.

Usage: python scripts/test_dnd_flow.py

This script assumes the backend is reachable at http://localhost:8000
"""
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

API_BASE = "http://localhost:8000"
GENERATE_PATH = "/api/characters/dnd/generate/"
HEADERS = {"Content-Type": "application/json"}

payload = {
    "provider": "groq",
    "model": "",
    "cultural_origin": "generic",
    "archetype": "adventurer",
    "themes": ["exploration"],
    "personality_traits": ["brave"],
    "physical_traits": ["athletic"],
    "emotional_traits": ["stoic"],
    "dnd_level": 3,
    "dnd_class": "fighter",
    "dnd_species": "human",
    "dnd_background": "soldier",
    "name": "Test Fighter",
    "generate_narrative": True,
    "narrative_provider": "groq",
    "narrative_model": "",
    "use_structured": True,
    "custom_details": "Testing narrative + fallback for physical traits and names"
}


def post_json(path, data):
    url = API_BASE + path
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers=HEADERS, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body)
    except HTTPError as he:
        print(f"HTTP error: {he.code} {he.reason}")
        try:
            body = he.read().decode("utf-8")
            print("Response body:", body)
        except Exception:
            pass
        raise
    except URLError as ue:
        print("Connection error:", ue)
        raise


def get_json(path):
    url = API_BASE + path
    req = Request(url, headers={})
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("GET error:", e)
        raise


if __name__ == "__main__":
    print("Posting generation request to backend...\n")
    try:
        resp = post_json(GENERATE_PATH, payload)
    except Exception as e:
        print("Failed to POST generation request:", e)
        sys.exit(2)

    print("Generation response received. Summary:\n")
    # Print top-level keys
    for k in ("id", "name", "is_dnd", "dnd_class", "dnd_level"):
        if k in resp:
            print(f"{k}: {resp.get(k)!r}")
    # Inspect structured_data
    structured = resp.get("structured_data")
    print("\nstructured_data:")
    if structured is None:
        print("  structured_data is null")
    else:
        print(json.dumps(structured, indent=2, ensure_ascii=False))

    # generation_log.ai_narrative
    genlog = resp.get("generation_log") or {}
    ai_narr = genlog.get("ai_narrative")
    print("\ngeneration_log.ai_narrative:")
    if ai_narr is None:
        print("  ai_narrative is null")
    else:
        print(json.dumps(ai_narr, indent=2, ensure_ascii=False))

    # name suggestions
    names = resp.get("name_suggestions") or (structured.get("name_suggestions") if isinstance(structured, dict) else None)
    print("\nCombined name suggestions (top-level or structured_data):")
    if not names:
        print("  None")
    else:
        print(json.dumps(names, indent=2, ensure_ascii=False))

    # physical traits
    print("\nPhysical traits check:")
    keys = ["skin", "eyes", "hair", "character_appearance"]
    found = {}
    if isinstance(structured, dict):
        for k in keys:
            if k in structured and structured.get(k):
                found[k] = structured.get(k)
    # if not in structured, also check generation_log.ai_narrative
    if not found and isinstance(ai_narr, dict):
        for k in keys:
            if k in ai_narr and ai_narr.get(k):
                found[k] = ai_narr.get(k)

    if not found:
        print("  No physical traits found in structured_data or ai_narrative")
    else:
        print(json.dumps(found, indent=2, ensure_ascii=False))

    # Fetch full character by id to confirm stored data
    char_id = resp.get("id")
    if char_id:
        print(f"\nFetching saved character id={char_id} to confirm persistence...")
        try:
            fetched = get_json(f"/api/characters/{char_id}")
            print("Fetched character structured_data:")
            sd = fetched.get("structured_data")
            if sd is None:
                print("  structured_data is null on GET")
            else:
                print(json.dumps(sd, indent=2, ensure_ascii=False))
        except Exception as e:
            print("Failed to GET character:", e)

    print("\nDone.")
