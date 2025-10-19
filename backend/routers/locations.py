from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Location

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("/", response_model=List[dict])
def list_locations(world_id: int | None = None, db: Session = Depends(get_db)):
    """Return locations, optionally filtered by world_id"""
    try:
        query = db.query(Location)
        if world_id:
            query = query.filter(Location.world_id == world_id)
        locs = query.all()
        results = []
        for loc in locs:
            results.append({
                "id": loc.id,
                "name": loc.name,
                "coordinates": loc.coordinates,
                "location_image": loc.location_image,
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
