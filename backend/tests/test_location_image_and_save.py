from backend.database import SessionLocal
from backend.models import World, Location
from datetime import datetime


def create_world(db):
    w = World(name="Test World", description="Test world for locations", created_at=datetime.now(), updated_at=datetime.now())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def test_generate_location_image_and_save(client):
    # Test location image generation
    img_payload = {
        "location_name": "Old Lighthouse",
        "location_type": "building",
        "description": "An abandoned lighthouse on a rugged cliff",
        "time_of_day": "dusk",
        "weather": "fog",
        "provider": "stablediffusion",
        "model": None,
        "style_preset": "realistic"
    }

    resp = client.post("/api/generate/location/generate-image", json=img_payload)
    assert resp.status_code == 200, f"Image generation failed: {resp.status_code} - {resp.text}"
    data = resp.json()
    assert "image_base64" in data and data["image_base64"]
    assert "prompt" in data and data["prompt"]

    # Now test save (create) - need a world in DB
    db = SessionLocal()
    try:
        world = create_world(db)
    finally:
        db.close()

    save_payload = {
        "name": "Old Lighthouse",
        "content": "A haunting lighthouse with a secret cellar.",
        "world_id": world.id,
        "location_image": data["image_base64"],
        "image_prompt": data.get("prompt")
    }

    resp2 = client.post("/api/generate/location/save", json=save_payload)
    assert resp2.status_code == 200, f"Location save (create) failed: {resp2.status_code} - {resp2.text}"
    res2 = resp2.json()
    assert "id" in res2
    loc_id = res2["id"]

    # Test update flow
    update_payload = {
        "location_id": loc_id,
        "name": "Old Lighthouse Renovated",
        "content": "Renovated and now a cozy inn.",
        "location_image": data["image_base64"],
        "image_prompt": data.get("prompt"),
    }

    resp3 = client.post("/api/generate/location/save", json=update_payload)
    assert resp3.status_code == 200, f"Location save (update) failed: {resp3.status_code} - {resp3.text}"
    res3 = resp3.json()
    assert res3.get("id") == loc_id

    # Verify persisted changes
    db2 = SessionLocal()
    try:
        updated = db2.query(Location).filter(Location.id == loc_id).first()
        assert updated is not None
        assert updated.name == "Old Lighthouse Renovated"
        assert "cozy inn" in (updated.description or "")
    finally:
        db2.close()
