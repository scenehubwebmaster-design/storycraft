from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Story
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic schemas
class StoryBase(BaseModel):
    title: str
    description: str | None = None
    genre: str | None = None

class StoryCreate(StoryBase):
    pass

class StoryResponse(StoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[StoryResponse])
def get_stories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stories"""
    stories = db.query(Story).offset(skip).limit(limit).all()
    return stories

@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: int, db: Session = Depends(get_db)):
    """Get a specific story by ID"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/", response_model=StoryResponse)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    """Create a new story"""
    db_story = Story(**story.dict())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.put("/{story_id}", response_model=StoryResponse)
def update_story(story_id: int, story: StoryCreate, db: Session = Depends(get_db)):
    """Update an existing story"""
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    for key, value in story.dict().items():
        setattr(db_story, key, value)
    
    db.commit()
    db.refresh(db_story)
    return db_story

@router.delete("/{story_id}/")
def delete_story(story_id: int, db: Session = Depends(get_db)):
    """Delete a story"""
    db_story = db.query(Story).filter(Story.id == story_id).first()
    if db_story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(db_story)
    db.commit()
    return {"message": "Story deleted successfully"}
