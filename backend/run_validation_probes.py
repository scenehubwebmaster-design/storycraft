import requests
import json
import time
from pathlib import Path

PROBE_DIR = Path(__file__).resolve().parent / 'probe_responses'
PROBE_DIR.mkdir(parents=True, exist_ok=True)

URL = 'http://localhost:8000/api/characters/dnd/generate/'

# Minimal request payload for generation; uses groq provider like previous probes
payload = {
    "dnd_class": "fighter",
    "dnd_species": "human",
    "dnd_background": "soldier",
    "generate_narrative": True,
    "narrative_provider": "groq",
    "use_structured": True,
    "dnd_level": 1
}

for i in range(1, 6):
    try:
        print(f"Running validation probe {i}...")
        resp = requests.post(URL, json=payload, timeout=60)
        data = {
            'status_code': resp.status_code,
            'response': None
        }
        try:
            data['response'] = resp.json()
        except Exception:
            data['response'] = resp.text

        out_path = PROBE_DIR / f'validation_{i}.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {out_path}")
    except Exception as e:
        print(f"Probe {i} failed: {e}")
    time.sleep(2)

print("Validation probes complete.")
