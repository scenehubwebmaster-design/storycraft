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

class WorldCreate(WorldBase):
    pass

class WorldResponse(WorldBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
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
    return world

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

@router.delete("/{world_id}")
def delete_world(world_id: int, db: Session = Depends(get_db)):
    """Delete a world"""
    db_world = db.query(World).filter(World.id == world_id).first()
    if db_world is None:
        raise HTTPException(status_code=404, detail="World not found")
    
    db.delete(db_world)
    db.commit()
    return {"message": "World deleted successfully"}
