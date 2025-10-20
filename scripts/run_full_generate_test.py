"""Simple runner to exercise the full-generate structured flow locally.

Sends a test payload and prints the response (and saves to scripts/last_full_generate_response.json).
"""
import requests
import json
import sys
from pathlib import Path

URL = "http://localhost:8000/api/generate/story/full-generate/"
PAYLOAD = {
    "character_count": 1,
    "world_themes": ["fantasy"],
    "character_provider": "groq",
    "story_provider": "groq"
}

OUT_PATH = Path(__file__).parent / "last_full_generate_response.json"


def main():
    print(f"Posting to {URL} with payload:\n{json.dumps(PAYLOAD, indent=2)}")
    try:
        resp = requests.post(URL, json=PAYLOAD, timeout=240)
    except Exception as e:
        print("Request failed:", e)
        sys.exit(2)

    print("Status code:", resp.status_code)
    try:
        data = resp.json()
        print(json.dumps(data, indent=2)[:2000])
        with open(OUT_PATH, 'w', encoding='utf-8') as f:
            json.dump({'status': resp.status_code, 'body': data}, f, indent=2)
        print(f"Saved response to {OUT_PATH}")
    except Exception:
        text = resp.text
        print(text[:2000])
        with open(OUT_PATH, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Saved raw response to {OUT_PATH}")


if __name__ == '__main__':
    main()
