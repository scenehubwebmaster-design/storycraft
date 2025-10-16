from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import Character
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic schemas
class CharacterBase(BaseModel):
    name: str
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None
    motivations: str | None = None
    relationships: Dict[str, Any] | list | None = None

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    """Schema for updating a character"""
    name: str | None = None
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None
    motivations: str | None = None
    relationships: Dict[str, Any] | list | None = None
    portrait_image: str | None = None
    image_prompt: str | None = None
    structured_data: Dict[str, Any] | str | None = None

class CharacterResponse(CharacterBase):
    id: int
    portrait_image: str | None = None
    image_prompt: str | None = None
    generation_log: Dict[str, Any] | list | str | None = None
    structured_data: Dict[str, Any] | str | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CharacterResponse])
def get_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all characters"""
    characters = db.query(Character).offset(skip).limit(limit).all()
    return characters

@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a specific character by ID"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.post("/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.put("/{character_id}", response_model=CharacterResponse)
def update_character(character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)):
    """Update an existing character"""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Only update fields that are provided (not None)
    update_data = character.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

@router.delete("/{character_id}")
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character"""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(db_character)
    db.commit()
    return {"message": "Character deleted successfully"}
