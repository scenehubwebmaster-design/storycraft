# Additional generation and negative tests


def test_location_save_validation(client):
    # Missing required fields for create (name, content, world_id)
    payload = {
        "location_image": "fake",
        "image_prompt": "prompt"
    }
    resp = client.post("/api/generate/location/save", json=payload)
    assert resp.status_code == 422


def test_generate_character_and_world_endpoints(client):
    # Character generate minimal
    char_payload = {
        "themes": ["Fantasy"],
        "personality_traits": ["Brave"],
        "physical_traits": ["Tall"],
        "provider": "groq"
    }
    r = client.post("/api/generate/character", json=char_payload)
    assert r.status_code == 200
    data = r.json()
    assert "content" in data and data["content"]
    assert "prompt_used" in data and data["prompt_used"]

    # World generate minimal
    world_payload = {
        "themes": ["Medieval"],
        "setting": ["Rural"],
        "provider": "groq"
    }
    rw = client.post("/api/generate/world", json=world_payload)
    assert rw.status_code == 200
    wd = rw.json()
    assert "content" in wd and wd["content"]
    assert "prompt_used" in wd and wd["prompt_used"]


def test_world_save_validation(client):
    # Missing required fields for world save: name and content
    resp = client.post("/api/generate/world/save", json={})
    assert resp.status_code == 422

