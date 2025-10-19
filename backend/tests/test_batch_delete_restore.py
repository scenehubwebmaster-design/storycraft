import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, engine, Base
from backend.models import Character

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def create_character(session, name="TestChar"):
    c = Character(name=name, description="desc")
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


def test_bulk_delete_and_restore(client):
    # ensure DB tables exist
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # create three characters
        c1 = create_character(session, "Bulk1")
        c2 = create_character(session, "Bulk2")
        c3 = create_character(session, "Bulk3")

        ids = [c1.id, c2.id, c3.id]

        # Call bulk-delete endpoint
        resp = client.post("/api/characters/bulk-delete/", json={"ids": ids})
        assert resp.status_code == 200
        data = resp.json()
        assert "deleted" in data
        assert set(data["deleted"]) == set(ids)

        # Ensure get_characters doesn't return deleted ones
        resp2 = client.get("/api/characters/")
        assert resp2.status_code == 200
        remaining = resp2.json()
        remaining_ids = [c["id"] for c in remaining]
        assert not any(i in remaining_ids for i in ids)

        # Restore two of them
        resp3 = client.post("/api/characters/restore/", json={"ids": [c1.id, c2.id]})
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert "restored" in data3
        assert set(data3["restored"]) == {c1.id, c2.id}

        # Now get_characters should include restored ones
        resp4 = client.get("/api/characters/")
        assert resp4.status_code == 200
        ids_now = [c["id"] for c in resp4.json()]
        assert c1.id in ids_now and c2.id in ids_now
    finally:
        session.close()
