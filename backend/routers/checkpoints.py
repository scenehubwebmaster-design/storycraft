"""
Campaign Checkpoint System - Save and restore campaign progress

This module provides endpoints for:
- Creating checkpoints with LLM-generated summaries
- Listing checkpoints for a campaign
- Restoring campaign state from checkpoints
- Semantic search across checkpoints via ChromaDB
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime

from ..database import get_db
from .. import models
from ..routers.generation import call_llm

router = APIRouter(prefix="/api/checkpoints", tags=["checkpoints"])


class CreateCheckpointRequest(BaseModel):
    campaign_id: int
    title: Optional[str] = None
    checkpoint_type: str = "manual"  # manual, auto, session_end


class RestoreCheckpointRequest(BaseModel):
    checkpoint_id: int
    restore_party_state: bool = True
    restore_combat_state: bool = False


async def generate_checkpoint_summary(
    campaign: models.Campaign,
    party_members: List[dict],
    recent_messages: List[models.ChatMessage],
    db: Session
) -> str:
    """
    Use LLM to generate a narrative summary of the current campaign state.
    
    This creates a story-like summary that players can read to remember
    what happened in the campaign.
    """
    
    # Build context for summary generation
    party_context = "\n".join([
        f"- {member.get('name', 'Unknown')} (Level {campaign.current_level} {member.get('class', 'Adventurer')}): {member.get('current_hp', 0)}/{member.get('max_hp', 0)} HP"
        for member in party_members
    ])
    
    # Get last 10 messages for context
    recent_conversation = "\n".join([
        f"{msg.role.upper()}: {msg.content[:200]}..."
        for msg in recent_messages[-10:]
    ])
    
    quest_log = campaign.quest_log if hasattr(campaign, 'quest_log') else "[]"
    
    prompt = f"""You are a D&D session recorder. Generate a concise, narrative summary of the current campaign state for players to review later.

Campaign: {campaign.title}
Setting: {campaign.setting or 'Fantasy'}
Current Level: {campaign.current_level}
Location: {campaign.current_location or 'Unknown'}

Party:
{party_context}

Active Quests:
{quest_log}

Recent Events (last few messages):
{recent_conversation}

Write a 2-3 paragraph narrative summary that:
1. Describes where the party is and what they're currently doing
2. Highlights key quest progress and accomplishments
3. Mentions any important NPCs or story threads
4. Notes any urgent situations or cliffhangers

Keep it engaging and story-like, as if you're recapping a TV episode. Focus on STORY, not mechanics."""

    try:
        # Use LM Studio or configured provider
        summary, _ = await call_llm(
            prompt=prompt,
            provider="http://100.120.44.114:1234/v1",
            model="local-model"
        )
        return summary.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate checkpoint summary: {e}")
        # Fallback to basic summary
        return f"Checkpoint created for {campaign.title}. The party is at {campaign.current_location or 'an unknown location'}, level {campaign.current_level}."


async def index_checkpoint_in_chroma(
    checkpoint: models.CampaignCheckpoint,
    db: Session
) -> Optional[str]:
    """
    Index checkpoint summary in ChromaDB for semantic search.
    
    Returns the ChromaDB document ID if successful, None otherwise.
    """
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Initialize ChromaDB client
        chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Get or create collection for checkpoints
        collection = chroma_client.get_or_create_collection(
            name="campaign_checkpoints",
            metadata={"description": "Campaign checkpoint summaries for semantic search"}
        )
        
        # Create unique document ID
        doc_id = f"checkpoint_{checkpoint.id}_{uuid.uuid4().hex[:8]}"
        
        # Index checkpoint
        collection.add(
            documents=[checkpoint.summary],
            metadatas=[{
                "checkpoint_id": checkpoint.id,
                "campaign_id": checkpoint.campaign_id,
                "title": checkpoint.title,
                "location": checkpoint.campaign_state.get("current_location", "unknown"),
                "level": checkpoint.campaign_state.get("current_level", 1),
                "timestamp": checkpoint.created_at.isoformat() if checkpoint.created_at else None,
            }],
            ids=[doc_id]
        )
        
        return doc_id
        
    except Exception as e:
        print(f"[ERROR] Failed to index checkpoint in ChromaDB: {e}")
        return None


@router.post("/")
async def create_checkpoint(
    req: CreateCheckpointRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new checkpoint for a campaign.
    
    This captures the complete campaign state, generates an LLM summary,
    and optionally indexes it in ChromaDB for semantic search.
    """
    
    # Verify campaign exists
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == req.campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get party members
    party_members = []
    if hasattr(campaign, 'campaign_characters'):
        for cc in campaign.campaign_characters:
            if cc.character:
                party_members.append({
                    "character_id": cc.character_id,
                    "name": cc.character.name,
                    "class": cc.character.dnd_class,
                    "level": cc.character.dnd_level or 1,
                    "current_hp": cc.current_hp or cc.character.dnd_hit_points_current,
                    "max_hp": cc.character.dnd_hit_points_max,
                    "status": cc.status,
                    "conditions": cc.conditions,
                    "resources": cc.current_resources,
                })
    
    # Get recent messages from chat session
    recent_messages = []
    if campaign.chat_session_id:
        recent_messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == campaign.chat_session_id,
            models.ChatMessage.is_deleted.is_(False)
        ).order_by(models.ChatMessage.message_index.desc()).limit(20).all()
        recent_messages.reverse()  # Chronological order
    
    # Generate title if not provided
    title = req.title or f"{campaign.title} - Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    
    # Generate LLM summary
    summary = await generate_checkpoint_summary(
        campaign=campaign,
        party_members=party_members,
        recent_messages=recent_messages,
        db=db
    )
    
    # Build campaign state snapshot
    campaign_state = {
        "title": campaign.title,
        "description": campaign.description,
        "setting": campaign.setting,
        "difficulty": campaign.difficulty,
        "campaign_type": campaign.campaign_type,
        "current_level": campaign.current_level,
        "current_location": campaign.current_location,
        "current_scene_type": campaign.current_scene_type,
        "quest_log": campaign.quest_log,
        "npc_tracker": campaign.npc_tracker,
    }
    
    # Get recent game events
    recent_events = []
    game_session = db.query(models.GameSession).filter(
        models.GameSession.chat_session_id == campaign.chat_session_id
    ).first()
    
    if game_session:
        events = db.query(models.GameEvent).filter(
            models.GameEvent.session_id == game_session.id
        ).order_by(models.GameEvent.created_at.desc()).limit(20).all()
        recent_events = [e.event_data for e in events]
        recent_events.reverse()
    
    # Check for active combat
    combat_state = None
    if game_session:
        active_combat = db.query(models.CombatEncounter).filter(
            models.CombatEncounter.game_session_id == game_session.id,
            models.CombatEncounter.is_active.is_(True)
        ).first()
        
        if active_combat:
            combat_state = active_combat.to_dict()
    
    # Create checkpoint
    checkpoint = models.CampaignCheckpoint(
        campaign_id=campaign.id,
        chat_session_id=campaign.chat_session_id,
        title=title,
        summary=summary,
        checkpoint_type=req.checkpoint_type,
        campaign_state=campaign_state,
        party_state=party_members,
        combat_state=combat_state,
        quest_state=campaign.quest_log,
        npc_state=campaign.npc_tracker,
        recent_events=recent_events,
        message_count=len(recent_messages),
    )
    
    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)
    
    # Index in ChromaDB (non-blocking, best effort)
    try:
        chroma_doc_id = await index_checkpoint_in_chroma(checkpoint, db)
        if chroma_doc_id:
            checkpoint.chroma_doc_id = chroma_doc_id
            db.commit()
            db.refresh(checkpoint)
    except Exception as e:
        print(f"[WARN] ChromaDB indexing failed (non-critical): {e}")
    
    return {
        "checkpoint": checkpoint.to_dict(),
        "message": f"Checkpoint '{title}' created successfully"
    }


@router.get("/campaign/{campaign_id}")
async def list_checkpoints(
    campaign_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all checkpoints for a campaign, most recent first.
    """
    
    checkpoints = db.query(models.CampaignCheckpoint).filter(
        models.CampaignCheckpoint.campaign_id == campaign_id
    ).order_by(models.CampaignCheckpoint.created_at.desc()).limit(limit).all()
    
    return {
        "checkpoints": [cp.to_dict() for cp in checkpoints],
        "count": len(checkpoints)
    }


@router.get("/{checkpoint_id}")
async def get_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed checkpoint information.
    """
    
    checkpoint = db.query(models.CampaignCheckpoint).filter(
        models.CampaignCheckpoint.id == checkpoint_id
    ).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    return checkpoint.to_dict()


@router.post("/restore")
async def restore_checkpoint(
    req: RestoreCheckpointRequest,
    db: Session = Depends(get_db)
):
    """
    Restore campaign state from a checkpoint.
    
    This updates the campaign and party member states to match the checkpoint.
    Optionally restores combat state.
    """
    
    # Get checkpoint
    checkpoint = db.query(models.CampaignCheckpoint).filter(
        models.CampaignCheckpoint.id == req.checkpoint_id
    ).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Get campaign
    campaign = db.query(models.Campaign).filter(
        models.Campaign.id == checkpoint.campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Restore campaign state
    campaign_state = checkpoint.campaign_state
    campaign.current_level = campaign_state.get("current_level", campaign.current_level)
    campaign.current_location = campaign_state.get("current_location", campaign.current_location)
    campaign.current_scene_type = campaign_state.get("current_scene_type", campaign.current_scene_type)
    campaign.quest_log = campaign_state.get("quest_log", campaign.quest_log)
    campaign.npc_tracker = campaign_state.get("npc_tracker", campaign.npc_tracker)
    
    # Restore party member states
    if req.restore_party_state and checkpoint.party_state:
        for party_member in checkpoint.party_state:
            char_id = party_member.get("character_id")
            if not char_id:
                continue
            
            # Find or create campaign_character entry
            cc = db.query(models.CampaignCharacter).filter(
                models.CampaignCharacter.campaign_id == campaign.id,
                models.CampaignCharacter.character_id == char_id
            ).first()
            
            if cc:
                cc.current_hp = party_member.get("current_hp")
                cc.status = party_member.get("status", "active")
                cc.conditions = party_member.get("conditions")
                cc.current_resources = party_member.get("resources")
    
    # Restore combat if requested
    if req.restore_combat_state and checkpoint.combat_state:
        # TODO: Implement combat restoration
        # This would recreate the combat encounter and participants
        pass
    
    db.commit()
    db.refresh(campaign)
    
    return {
        "message": f"Campaign restored to checkpoint: {checkpoint.title}",
        "campaign": campaign.to_dict()
    }


@router.delete("/{checkpoint_id}")
async def delete_checkpoint(
    checkpoint_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a checkpoint.
    """
    
    checkpoint = db.query(models.CampaignCheckpoint).filter(
        models.CampaignCheckpoint.id == checkpoint_id
    ).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    # Remove from ChromaDB if indexed
    if checkpoint.chroma_doc_id:
        try:
            import chromadb
            from chromadb.config import Settings
            
            chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            collection = chroma_client.get_collection("campaign_checkpoints")
            collection.delete(ids=[checkpoint.chroma_doc_id])
        except Exception as e:
            print(f"[WARN] Failed to remove checkpoint from ChromaDB: {e}")
    
    db.delete(checkpoint)
    db.commit()
    
    return {"message": "Checkpoint deleted successfully"}
