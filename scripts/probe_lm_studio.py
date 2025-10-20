#!/usr/bin/env python3
import requests
import json

URL = "http://100.120.44.114:1234/v1/chat/completions"
payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello from automated probe. Reply with JSON: {\"status\": \"ok\"}"}],
    "max_tokens": 50
}

try:
    r = requests.post(URL, json=payload, timeout=30)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:8000])
    except Exception:
        print('Response text:', r.text[:8000])
except Exception as e:
    print('Request failed:', e)
