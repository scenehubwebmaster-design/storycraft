from fastapi.testclient import TestClient
import json
import os
import sys

# Ensure repository root is on sys.path so `backend` package can be imported
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the app (main creates tables but that's okay for an in-process smoke run)
from backend.main import app

client = TestClient(app)

payload = {
    "world_themes": ["adventure", "mystery"],
    "character_count": 3,
    "custom_details": "Smoke test: short output",
}

print("Calling /api/generate/story/full-generate/ ...")
resp = client.post("/api/generate/story/full-generate/", json=payload)
print("Status code:", resp.status_code)
try:
    data = resp.json()
    print(json.dumps(data, indent=2)[:2000])
except Exception as e:
    print("Failed to parse JSON response:", e)
    print(resp.text)
