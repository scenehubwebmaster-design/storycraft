#!/usr/bin/env python3
"""
Request the portrait endpoint and save the returned base64 image to scripts/last_portrait.png
"""
import requests
import base64
import os

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

out_path = os.path.join(os.path.dirname(__file__), "last_portrait.png")

try:
    resp = requests.post(API, json=payload, headers=headers, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    img_b64 = data.get('image_base64')
    if not img_b64:
        print('No image_base64 in response; full response:')
        print(data)
    else:
        img_bytes = base64.b64decode(img_b64)
        with open(out_path, 'wb') as f:
            f.write(img_bytes)
        print('Saved portrait to', out_path)
except Exception as exc:
    print('Failed to save portrait:', exc)
    try:
        print('Raw response:', resp.text[:4000])
    except Exception:
        pass
