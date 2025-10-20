#!/usr/bin/env python3
"""
End-to-end portrait generation test.
Posts to /character/generate-portrait/ with provider 'stablediffusion' and prints response.
"""
import requests
import json

API = "http://localhost:8000/api/generate/character/generate-portrait/"

payload = {
    "character_name": "Sakura Rylan",
    "appearance_text": "Orc, piercing yellow with vertical pupils eyes, greenish grey rugged orcish skin, battle-hardened, short spiky brown hair, scars on cheek",
    "provider": "stablediffusion",
    "model": "",
    "aspect_ratio": "3:4",
    "custom_prompt": None,
    "style_preset": "photorealistic",
    "quality": "standard"
}

headers = {"Content-Type": "application/json"}

try:
    resp = requests.post(API, json=payload, headers=headers, timeout=300)
    print("Status:", resp.status_code)
    try:
        data = resp.json()
        print(json.dumps(data, indent=2)[:4000])
    except Exception:
        print("Response not JSON, text:")
        print(resp.text[:4000])
except Exception as exc:
    print("Request failed:", exc)
