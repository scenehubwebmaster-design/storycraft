from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import World
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic schemas
class WorldBase(BaseModel):
    name: str
    description: str | None = None
    history: str | None = None
    geography: str | None = None
    culture: str | None = None
    magic_system: str | None = None
    technology_level: str | None = None
    # Optional image/map fields and metadata
    world_image: str | None = None
    world_map: str | None = None
    image_prompt: str | None = None
    climate: str | None = None
    population_level: str | None = None
    danger_level: str | None = None

class WorldCreate(WorldBase):
    pass

class LocationBrief(BaseModel):
    id: int
    name: str
    coordinates: str | None = None
    location_image: str | None = None


class WorldResponse(WorldBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # Include generated images and prompts when available
    world_image: str | None = None
    world_map: str | None = None
    image_prompt: str | None = None
    # Basic list of locations for map overlay / quick access
    locations: list[LocationBrief] | None = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[WorldResponse])
def get_worlds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all worlds"""
    worlds = db.query(World).offset(skip).limit(limit).all()
    return worlds

@router.get("/{world_id}", response_model=WorldResponse)
def get_world(world_id: int, db: Session = Depends(get_db)):
    """Get a specific world by ID"""
    world = db.query(World).filter(World.id == world_id).first()
    if world is None:
        raise HTTPException(status_code=404, detail="World not found")
    # Serialize world with basic location briefs for frontend map overlay
    locations = []
    try:
        for loc in getattr(world, "locations", []) or []:
            locations.append({
                "id": loc.id,
                "name": loc.name,
                "coordinates": getattr(loc, "coordinates", None),
                "location_image": getattr(loc, "location_image", None),
            })
    except Exception:
        locations = None

    result = {
        "id": world.id,
        "name": world.name,
        "description": world.description,
        "history": world.history,
        "geography": world.geography,
        "culture": world.culture,
        "magic_system": world.magic_system,
        "technology_level": world.technology_level,
        "world_image": getattr(world, "world_image", None),
        "world_map": getattr(world, "world_map", None),
        "image_prompt": getattr(world, "image_prompt", None),
        "climate": getattr(world, "climate", None),
        "population_level": getattr(world, "population_level", None),
        "danger_level": getattr(world, "danger_level", None),
        "created_at": world.created_at,
        "updated_at": world.updated_at,
        "locations": locations,
    }
    return result

@router.post("/", response_model=WorldResponse)
def create_world(world: WorldCreate, db: Session = Depends(get_db)):
    """Create a new world"""
    db_world = World(**world.dict())
    db.add(db_world)
    db.commit()
    db.refresh(db_world)
    return db_world

@router.put("/{world_id}", response_model=WorldResponse)
def update_world(world_id: int, world: WorldCreate, db: Session = Depends(get_db)):
    """Update an existing world"""
    db_world = db.query(World).filter(World.id == world_id).first()
    if db_world is None:
        raise HTTPException(status_code=404, detail="World not found")
    
    for key, value in world.dict().items():
        setattr(db_world, key, value)
    
    db.commit()
    db.refresh(db_world)
    return db_world

@router.delete("/{world_id}/")
def delete_world(world_id: int, db: Session = Depends(get_db)):
    """Delete a world"""
    db_world = db.query(World).filter(World.id == world_id).first()
    if db_world is None:
        raise HTTPException(status_code=404, detail="World not found")
    
    db.delete(db_world)
    db.commit()
    return {"message": "World deleted successfully"}
