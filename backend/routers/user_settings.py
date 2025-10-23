"""
User Settings API Router

Endpoints for managing user preferences (TTS, UI, RAG, LLM, etc.)
Persists settings in database instead of localStorage.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import UserSettings
from ..schemas import UserSettingsCreate, UserSettingsUpdate, UserSettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/", response_model=UserSettingsResponse)
def get_user_settings(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get user settings (or default settings for anonymous user).
    
    If no user_id provided, returns the first available settings record
    or creates a new one with defaults.
    """
    # For now, support single-user mode (no auth)
    # Find first settings record or user-specific settings
    if user_id:
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
    else:
        # Get first settings record (single-user mode)
        settings = db.query(UserSettings).first()
    
    # Create default settings if none exist
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.post("/", response_model=UserSettingsResponse, status_code=201)
def create_user_settings(
    settings_data: UserSettingsCreate,
    db: Session = Depends(get_db)
):
    """
    Create new user settings.
    
    Note: In single-user mode, only one settings record should exist.
    This endpoint is mainly for future multi-user support.
    """
    # Check if settings already exist for this user
    existing = db.query(UserSettings).filter(
        UserSettings.user_id == settings_data.user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Settings already exist for this user. Use PATCH to update."
        )
    
    # Create new settings
    settings = UserSettings(**settings_data.model_dump())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    
    return settings


@router.patch("/", response_model=UserSettingsResponse)
@router.patch("/{settings_id}", response_model=UserSettingsResponse)
def update_user_settings(
    settings_update: UserSettingsUpdate,
    settings_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Update user settings (partial update).
    
    Can update by:
    - settings_id (path parameter)
    - user_id (query parameter)
    - or update first available settings (single-user mode)
    """
    # Find settings record
    if settings_id:
        settings = db.query(UserSettings).filter(
            UserSettings.id == settings_id
        ).first()
    elif user_id:
        settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
    else:
        # Single-user mode: get first settings
        settings = db.query(UserSettings).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    # Update only provided fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings


@router.delete("/{settings_id}", status_code=204)
def delete_user_settings(
    settings_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete user settings.
    
    Note: Mainly for cleanup/testing. In production, settings
    should be updated rather than deleted.
    """
    settings = db.query(UserSettings).filter(
        UserSettings.id == settings_id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    db.delete(settings)
    db.commit()
    
    return None


@router.get("/tts", response_model=dict)
def get_tts_settings(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get only TTS-related settings.
    
    Convenient endpoint for TTSAudioPlayer to fetch just TTS config.
    """
    settings = get_user_settings(user_id=user_id, db=db)
    
    return {
        "tts_provider": settings.tts_provider,
        "tts_voice": settings.tts_voice,
        "tts_enabled": settings.tts_enabled,
        "tts_auto_play": settings.tts_auto_play,
        "tts_speed": settings.tts_speed,
        "tts_model": settings.tts_model,
    }


@router.patch("/tts", response_model=dict)
def update_tts_settings(
    tts_provider: Optional[str] = None,
    tts_voice: Optional[str] = None,
    tts_enabled: Optional[bool] = None,
    tts_auto_play: Optional[bool] = None,
    tts_speed: Optional[float] = None,
    tts_model: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Update only TTS settings (convenience endpoint).
    
    Allows TTSAudioPlayer to update TTS config without
    affecting other settings.
    """
    # Build partial update
    update_data = UserSettingsUpdate(
        tts_provider=tts_provider,
        tts_voice=tts_voice,
        tts_enabled=tts_enabled,
        tts_auto_play=tts_auto_play,
        tts_speed=tts_speed,
        tts_model=tts_model,
    )
    
    settings = update_user_settings(
        settings_update=update_data,
        user_id=user_id,
        db=db
    )
    
    return {
        "tts_provider": settings.tts_provider,
        "tts_voice": settings.tts_voice,
        "tts_enabled": settings.tts_enabled,
        "tts_auto_play": settings.tts_auto_play,
        "tts_speed": settings.tts_speed,
        "tts_model": settings.tts_model,
    }
