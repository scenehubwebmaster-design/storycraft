#!/usr/bin/env python3
"""
Create a test character via the standard create-character endpoint with
`structured_data` containing `name_suggestions` and physical traits, then
fetch it back and print what the frontend should render (combined name suggestions
and physical traits).
"""
import json
from urllib.request import Request, urlopen

API_BASE = "http://localhost:8000"
CREATE_PATH = "/api/characters/"

payload = {
    "name": "Manual Test",
    "description": "Manual test description",
    "structured_data": {
        "name_suggestions": ["Aldric", {"first_name": "Borin", "origin": "Dwarven"}],
        "skin": "Pale with a faint scar",
        "eyes": "Green slitted",
        "hair": "Long black braid",
    }
}

HEADERS = {"Content-Type": "application/json"}


def post_json(path, data):
    url = API_BASE + path
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers=HEADERS, method="POST")
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(path):
    url = API_BASE + path
    req = Request(url)
    with urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    created = post_json(CREATE_PATH, payload)
    print("Created character id:", created.get("id"))
    char = get_json(f"/api/characters/{created.get('id')}")
    sd = char.get("structured_data") or {}
    top_names = char.get("name_suggestions") or []
    sd_names = sd.get("name_suggestions") if isinstance(sd, dict) else []
    combined = []
    def push(arr):
        if not arr:
            return
        for e in arr:
            if isinstance(e, str):
                combined.append({"first_name": e, "_ai": True})
            elif isinstance(e, dict):
                combined.append({**e, "_ai": True})
    push(top_names)
    push(sd_names)
    print("Combined names for UI:")
    print(json.dumps(combined, indent=2, ensure_ascii=False))
    print("Physical traits from structured_data:")
    for k in ("skin","eyes","hair","character_appearance"):
        if k in sd:
            print(f"{k}: {sd[k]}")
