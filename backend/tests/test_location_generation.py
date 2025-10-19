def test_generate_location_endpoint(client):
    """Post a minimal LocationGenerationRequest to /api/generate/location and expect a GenerationResponse-like dict."""
    payload = {
        "world_context": "A rugged coastal trade city with foggy docks",
        "location_type": "harbor",
        "importance": "minor",
        "themes": ["Fantasy", "Maritime"],
        "custom_details": "A lighthouse that hides an old secret",
        "provider": "groq",
        "model": None
    }

    resp = client.post("/api/generate/location", json=payload)
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code} - {resp.text}"
    data = resp.json()
    assert "content" in data
    assert "prompt_used" in data
    assert isinstance(data["content"], str) and len(data["content"]) > 0
    assert isinstance(data["prompt_used"], str) and len(data["prompt_used"]) > 0
