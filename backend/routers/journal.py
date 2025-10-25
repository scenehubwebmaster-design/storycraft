"""
Journal API Router - Campaign event logging and NPC tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models import JournalEntry, NPC, Quest, Campaign

router = APIRouter()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class JournalEntryCreate(BaseModel):
    campaign_id: int
    chat_session_id: Optional[int] = None
    chat_message_id: Optional[int] = None
    entry_type: str  # "npc_met", "decision", "quest_update", "location_visited", "combat", "loot", "rest"
    title: str
    description: Optional[str] = None
    npc_id: Optional[int] = None
    quest_id: Optional[int] = None
    location_name: Optional[str] = None
    importance: int = 3
    tags: Optional[List[str]] = None
    involved_characters: Optional[List[int]] = None
    game_session_number: Optional[int] = None


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    importance: Optional[int] = None
    tags: Optional[List[str]] = None


class NPCUpdate(BaseModel):
    description: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    personality: Optional[str] = None
    relationship_to_party: Optional[int] = None
    is_alive: Optional[bool] = None
    importance: Optional[int] = None
    tags: Optional[List[str]] = None
    quests_related: Optional[List[int]] = None


# ============================================================================
# Journal Entry Endpoints
# ============================================================================

@router.get("/campaigns/{campaign_id}/journal/entries")
async def get_journal_entries(
    campaign_id: int,
    entry_type: Optional[str] = Query(None, description="Filter by entry type"),
    min_importance: Optional[int] = Query(None, description="Minimum importance (1-5)"),
    limit: Optional[int] = Query(100, description="Maximum number of entries"),
    db: Session = Depends(get_db)
):
    """
    Get all journal entries for a campaign with optional filtering.
    """
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Build query
    query = db.query(JournalEntry).filter(JournalEntry.campaign_id == campaign_id)
    
    if entry_type:
        query = query.filter(JournalEntry.entry_type == entry_type)
    
    if min_importance:
        query = query.filter(JournalEntry.importance >= min_importance)
    
    # Order by most recent first
    query = query.order_by(JournalEntry.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    entries = query.all()
    
    return [entry.to_dict() for entry in entries]


@router.post("/campaigns/{campaign_id}/journal/entries")
async def create_journal_entry(
    campaign_id: int,
    entry_data: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new journal entry.
    """
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify entry_data.campaign_id matches path param
    if entry_data.campaign_id != campaign_id:
        raise HTTPException(status_code=400, detail="Campaign ID mismatch")
    
    # Create entry
    entry = JournalEntry(
        campaign_id=entry_data.campaign_id,
        chat_session_id=entry_data.chat_session_id,
        chat_message_id=entry_data.chat_message_id,
        entry_type=entry_data.entry_type,
        title=entry_data.title,
        description=entry_data.description,
        npc_id=entry_data.npc_id,
        quest_id=entry_data.quest_id,
        location_name=entry_data.location_name,
        importance=entry_data.importance,
        tags=entry_data.tags,
        involved_characters=entry_data.involved_characters,
        game_session_number=entry_data.game_session_number
    )
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    return entry.to_dict()


@router.put("/journal/entries/{entry_id}")
async def update_journal_entry(
    entry_id: int,
    entry_data: JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing journal entry.
    """
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    # Update fields
    if entry_data.title is not None:
        entry.title = entry_data.title
    if entry_data.description is not None:
        entry.description = entry_data.description
    if entry_data.importance is not None:
        entry.importance = entry_data.importance
    if entry_data.tags is not None:
        entry.tags = entry_data.tags
    
    db.commit()
    db.refresh(entry)
    
    return entry.to_dict()


@router.delete("/journal/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a journal entry.
    """
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"success": True, "message": "Journal entry deleted"}


# ============================================================================
# NPC Endpoints
# ============================================================================

@router.get("/campaigns/{campaign_id}/npcs")
async def get_campaign_npcs(
    campaign_id: int,
    min_importance: Optional[int] = Query(None, description="Minimum importance (1-5)"),
    alive_only: bool = Query(True, description="Only return living NPCs"),
    db: Session = Depends(get_db)
):
    """
    Get all NPCs associated with a campaign.
    """
    # Find campaign's game session
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.game_session_id:
        return []
    
    # Query NPCs
    query = db.query(NPC).filter(NPC.game_session_id == campaign.game_session_id)
    
    if alive_only:
        query = query.filter(NPC.is_alive.is_(True))
    
    if min_importance:
        query = query.filter(NPC.importance >= min_importance)
    
    # Order by importance, then name
    query = query.order_by(NPC.importance.desc(), NPC.name)
    
    npcs = query.all()
    
    return [npc.to_dict() for npc in npcs]


@router.get("/npcs/{npc_id}")
async def get_npc(
    npc_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific NPC by ID.
    """
    npc = db.query(NPC).filter(NPC.id == npc_id).first()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    
    return npc.to_dict()


@router.put("/npcs/{npc_id}")
async def update_npc(
    npc_id: int,
    npc_data: NPCUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing NPC.
    """
    npc = db.query(NPC).filter(NPC.id == npc_id).first()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    
    # Update fields
    if npc_data.description is not None:
        npc.description = npc_data.description
    if npc_data.role is not None:
        npc.role = npc_data.role
    if npc_data.location is not None:
        npc.location = npc_data.location
    if npc_data.personality is not None:
        npc.personality = npc_data.personality
    if npc_data.relationship_to_party is not None:
        npc.relationship_to_party = npc_data.relationship_to_party
    if npc_data.is_alive is not None:
        npc.is_alive = npc_data.is_alive
    if npc_data.importance is not None:
        npc.importance = npc_data.importance
    if npc_data.tags is not None:
        npc.tags = npc_data.tags
    if npc_data.quests_related is not None:
        npc.quests_related = npc_data.quests_related
    
    npc.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(npc)
    
    return npc.to_dict()


# ============================================================================
# Quest Endpoints
# ============================================================================

@router.get("/campaigns/{campaign_id}/quests")
async def get_campaign_quests(
    campaign_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all quests for a campaign.
    """
    # Find campaign's game session
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if not campaign.game_session_id:
        return []
    
    # Query quests
    query = db.query(Quest).filter(Quest.game_session_id == campaign.game_session_id)
    
    if status:
        query = query.filter(Quest.status == status)
    
    quests = query.all()
    
    return [quest.to_dict() for quest in quests]


# ============================================================================
# Statistics & Summary Endpoints
# ============================================================================

@router.get("/campaigns/{campaign_id}/journal/summary")
async def get_journal_summary(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for campaign journal.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Count entries by type
    entry_counts = {}
    for entry_type in ["npc_met", "decision", "quest_update", "location_visited", "combat", "loot", "rest"]:
        count = db.query(JournalEntry).filter(
            JournalEntry.campaign_id == campaign_id,
            JournalEntry.entry_type == entry_type
        ).count()
        entry_counts[entry_type] = count
    
    # Count NPCs
    npc_count = 0
    if campaign.game_session_id:
        npc_count = db.query(NPC).filter(
            NPC.game_session_id == campaign.game_session_id,
            NPC.is_alive.is_(True)
        ).count()
    
    # Count quests
    quest_count = 0
    active_quest_count = 0
    if campaign.game_session_id:
        quest_count = db.query(Quest).filter(
            Quest.game_session_id == campaign.game_session_id
        ).count()
        active_quest_count = db.query(Quest).filter(
            Quest.game_session_id == campaign.game_session_id,
            Quest.status == "in_progress"
        ).count()
    
    # Get unique locations
    locations = db.query(JournalEntry.location_name).filter(
        JournalEntry.campaign_id == campaign_id,
        JournalEntry.location_name.isnot(None)
    ).distinct().all()
    
    return {
        "campaign_id": campaign_id,
        "total_entries": sum(entry_counts.values()),
        "entry_counts": entry_counts,
        "npc_count": npc_count,
        "quest_count": quest_count,
        "active_quest_count": active_quest_count,
        "locations_visited": len(locations),
        "location_names": [loc[0] for loc in locations]
    }
