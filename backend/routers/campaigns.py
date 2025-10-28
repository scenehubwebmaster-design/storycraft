"""
Campaign Management API Router
Handles D&D campaign CRUD operations, party management, and combat tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from ..database import get_db
from ..models import Campaign, CampaignCharacter, Character, ChatSession, GameSession, PartyMember

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


# ============================================================================
# SCHEMAS
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: Optional[str] = None
    setting: Optional[str] = None
    difficulty: Optional[str] = "Normal"
    campaign_type: Optional[str] = "short_adventure"
    starting_level: int = 1
    chat_session_id: Optional[int] = None


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    current_level: Optional[int] = None
    current_scene_type: Optional[str] = None
    current_location: Optional[str] = None
    quest_log: Optional[list] = None
    npc_tracker: Optional[dict] = None
    session_notes: Optional[list] = None


class AddCharacterRequest(BaseModel):
    character_id: int


class UpdateCharacterStateRequest(BaseModel):
    current_hp: Optional[int] = None
    current_resources: Optional[dict] = None
    status: Optional[str] = None
    conditions: Optional[list] = None
    position_in_initiative: Optional[int] = None


class InitiativeEntry(BaseModel):
    character_id: int
    character_name: str
    initiative: int
    current_hp: int
    max_hp: int
    ac: int
    conditions: List[str] = []


class DamageRequest(BaseModel):
    character_id: int
    damage: int
    damage_type: Optional[str] = "normal"


class HealRequest(BaseModel):
    character_id: int
    healing: int


# ============================================================================
# CAMPAIGN CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=dict)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new D&D campaign with associated GameSession"""
    
    # Validate chat_session_id if provided
    if campaign.chat_session_id:
        chat_session = db.query(ChatSession).filter(ChatSession.id == campaign.chat_session_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    
    new_campaign = Campaign(
        title=campaign.title,
        description=campaign.description,
        setting=campaign.setting,
        difficulty=campaign.difficulty,
        campaign_type=campaign.campaign_type,
        starting_level=campaign.starting_level,
        current_level=campaign.starting_level,
        chat_session_id=campaign.chat_session_id,
        quest_log=json.dumps([]),
        npc_tracker=json.dumps({}),
        session_notes=json.dumps([])
    )
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    # Create associated GameSession for DM game-chat endpoint
    game_session = None
    if campaign.chat_session_id:
        game_session = GameSession(
            chat_session_id=campaign.chat_session_id,
            campaign_name=campaign.title,
            current_location=None,
            current_scene=None,
            game_state={
                "campaign_id": new_campaign.id,
                "current_scene_type": "roleplay",
                "session_start": datetime.utcnow().isoformat()
            },
            party_level=campaign.starting_level,
            session_notes=None
        )
        db.add(game_session)
        db.commit()
        db.refresh(game_session)
    
    # Return campaign with game_session_id
    result = new_campaign.to_dict()
    if game_session:
        result["game_session_id"] = game_session.id
    
    return result


@router.get("/", response_model=List[dict])
async def list_campaigns(
    chat_session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all campaigns, optionally filtered by chat_session_id"""
    query = db.query(Campaign)
    
    if chat_session_id is not None:
        query = query.filter(Campaign.chat_session_id == chat_session_id)
    
    campaigns = query.order_by(Campaign.updated_at.desc()).all()
    return [c.to_dict() for c in campaigns]


@router.get("/{campaign_id}", response_model=dict)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get a specific campaign with party details"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Include party details
    result = campaign.to_dict()
    result["party"] = []
    
    for cc in campaign.campaign_characters:
        char = db.query(Character).filter(Character.id == cc.character_id).first()
        if char:
            result["party"].append({
                "campaign_character_id": cc.id,
                "character_id": char.id,
                "name": char.name,
                "dnd_class": char.dnd_class,
                "dnd_level": char.dnd_level,
                "dnd_species": char.dnd_species,
                "portrait_image": char.portrait_image,
                "current_hp": cc.current_hp or char.dnd_hit_points_current or char.dnd_hit_points_max,
                "max_hp": char.dnd_hit_points_max,
                "armor_class": char.dnd_armor_class,
                "current_resources": cc.current_resources,
                "status": cc.status,
                "conditions": cc.conditions,
                "position_in_initiative": cc.position_in_initiative,
            })
    
    return result


@router.patch("/{campaign_id}", response_model=dict)
async def update_campaign(campaign_id: int, updates: CampaignUpdate, db: Session = Depends(get_db)):
    """Update campaign details"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    update_data = updates.dict(exclude_unset=True)
    
    # Handle JSON fields
    if "quest_log" in update_data:
        update_data["quest_log"] = json.dumps(update_data["quest_log"])
    if "npc_tracker" in update_data:
        update_data["npc_tracker"] = json.dumps(update_data["npc_tracker"])
    if "session_notes" in update_data:
        update_data["session_notes"] = json.dumps(update_data["session_notes"])
    
    for key, value in update_data.items():
        setattr(campaign, key, value)
    
    campaign.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign)
    
    return campaign.to_dict()


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a campaign and all associated data"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    db.delete(campaign)
    db.commit()
    
    return {"message": f"Campaign '{campaign.title}' deleted successfully"}


# ============================================================================
# PARTY MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/{campaign_id}/party/add", response_model=dict)
async def add_character_to_campaign(
    campaign_id: int,
    request: AddCharacterRequest,
    db: Session = Depends(get_db)
):
    """Add a character to the campaign party"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    character = db.query(Character).filter(Character.id == request.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Only D&D characters can be added to campaigns")
    
    # Check if already in party
    existing = db.query(CampaignCharacter).filter(
        CampaignCharacter.campaign_id == campaign_id,
        CampaignCharacter.character_id == request.character_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Character already in this campaign")
    
    # Initialize character state
    campaign_char = CampaignCharacter(
        campaign_id=campaign_id,
        character_id=request.character_id,
        current_hp=character.dnd_hit_points_current or character.dnd_hit_points_max,
        current_resources=json.dumps(character.dnd_resources or {}),
        status='active',
        conditions=json.dumps([])
    )
    
    db.add(campaign_char)
    db.commit()
    db.refresh(campaign_char)
    
    # Also add to GameSession party_members if campaign has a game session
    # Find the game session by chat_session_id and checking game_state for campaign_id
    if campaign.chat_session_id:
        # Get all game sessions for this chat session
        game_sessions = db.query(GameSession).filter(
            GameSession.chat_session_id == campaign.chat_session_id
        ).all()
        
        # Find the one with matching campaign_id in game_state
        game_session = None
        for gs in game_sessions:
            if gs.game_state and gs.game_state.get('campaign_id') == campaign_id:
                game_session = gs
                break
        
        if game_session:
            # Check if already in game session party
            existing_party_member = db.query(PartyMember).filter(
                PartyMember.game_session_id == game_session.id,
                PartyMember.character_id == request.character_id
            ).first()
            
            if not existing_party_member:
                party_member = PartyMember(
                    game_session_id=game_session.id,
                    character_id=request.character_id,
                    current_hp=character.dnd_hit_points_current or character.dnd_hit_points_max or 10,
                    max_hp=character.dnd_hit_points_max or 10,
                    temp_hp=0,
                    conditions=[],
                    is_active=True
                )
                db.add(party_member)
                db.commit()
    
    return {
        "message": f"{character.name} added to campaign",
        "campaign_character": campaign_char.to_dict()
    }


@router.delete("/{campaign_id}/party/{character_id}")
async def remove_character_from_campaign(
    campaign_id: int,
    character_id: int,
    db: Session = Depends(get_db)
):
    """Remove a character from the campaign party"""
    campaign_char = db.query(CampaignCharacter).filter(
        CampaignCharacter.campaign_id == campaign_id,
        CampaignCharacter.character_id == character_id
    ).first()
    
    if not campaign_char:
        raise HTTPException(status_code=404, detail="Character not in this campaign")
    
    db.delete(campaign_char)
    db.commit()
    
    return {"message": "Character removed from campaign"}


@router.patch("/{campaign_id}/party/{character_id}", response_model=dict)
async def update_character_state(
    campaign_id: int,
    character_id: int,
    updates: UpdateCharacterStateRequest,
    db: Session = Depends(get_db)
):
    """Update a character's current state in the campaign"""
    campaign_char = db.query(CampaignCharacter).filter(
        CampaignCharacter.campaign_id == campaign_id,
        CampaignCharacter.character_id == character_id
    ).first()
    
    if not campaign_char:
        raise HTTPException(status_code=404, detail="Character not in this campaign")
    
    update_data = updates.dict(exclude_unset=True)
    
    # Handle JSON fields
    if "current_resources" in update_data:
        update_data["current_resources"] = json.dumps(update_data["current_resources"])
    if "conditions" in update_data:
        update_data["conditions"] = json.dumps(update_data["conditions"])
    
    for key, value in update_data.items():
        setattr(campaign_char, key, value)
    
    campaign_char.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(campaign_char)
    
    return campaign_char.to_dict()


@router.get("/{campaign_id}/party", response_model=List[dict])
async def get_campaign_party(campaign_id: int, db: Session = Depends(get_db)):
    """Get full party details with current state"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    party = []
    for cc in campaign.campaign_characters:
        char = db.query(Character).filter(Character.id == cc.character_id).first()
        if char:
            party.append({
                "campaign_character_id": cc.id,
                "character_id": char.id,
                "name": char.name,
                "dnd_class": char.dnd_class,
                "dnd_level": char.dnd_level,
                "dnd_species": char.dnd_species,
                "dnd_background": char.dnd_background,
                "portrait_image": char.portrait_image,
                "current_hp": cc.current_hp,
                "max_hp": char.dnd_hit_points_max,
                "temp_hp": 0,  # TODO: Add to schema
                "armor_class": char.dnd_armor_class,
                "initiative": char.dnd_initiative,
                "speed": char.dnd_speed,
                "ability_scores": char.dnd_ability_scores,
                "ability_modifiers": char.dnd_ability_modifiers,
                "skills": char.dnd_skills,
                "spellcasting": char.dnd_spellcasting,
                "features": char.dnd_features,
                "equipment": char.dnd_equipment,
                "current_resources": json.loads(cc.current_resources) if cc.current_resources else {},
                "status": cc.status,
                "conditions": json.loads(cc.conditions) if cc.conditions else [],
                "position_in_initiative": cc.position_in_initiative,
            })
    
    return party


# ============================================================================
# COMBAT & INITIATIVE TRACKING
# ============================================================================

@router.post("/{campaign_id}/combat/start")
async def start_combat(campaign_id: int, db: Session = Depends(get_db)):
    """Start combat mode for the campaign"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.current_scene_type = 'combat'
    db.commit()
    
    return {"message": "Combat started", "scene_type": "combat"}


@router.post("/{campaign_id}/combat/end")
async def end_combat(campaign_id: int, db: Session = Depends(get_db)):
    """End combat mode"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign.current_scene_type = 'roleplay'
    
    # Clear initiative order
    for cc in campaign.campaign_characters:
        cc.position_in_initiative = None
    
    db.commit()
    
    return {"message": "Combat ended", "scene_type": "roleplay"}


@router.post("/{campaign_id}/combat/initiative", response_model=List[dict])
async def set_initiative_order(
    campaign_id: int,
    initiative_list: List[InitiativeEntry],
    db: Session = Depends(get_db)
):
    """Set initiative order for combat"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Sort by initiative (highest first)
    sorted_initiative = sorted(initiative_list, key=lambda x: x.initiative, reverse=True)
    
    # Update positions
    for idx, entry in enumerate(sorted_initiative):
        cc = db.query(CampaignCharacter).filter(
            CampaignCharacter.campaign_id == campaign_id,
            CampaignCharacter.character_id == entry.character_id
        ).first()
        
        if cc:
            cc.position_in_initiative = idx + 1
    
    db.commit()
    
    return [entry.dict() for entry in sorted_initiative]


@router.post("/{campaign_id}/combat/damage")
async def apply_damage(
    campaign_id: int,
    damage_req: DamageRequest,
    db: Session = Depends(get_db)
):
    """Apply damage to a character"""
    cc = db.query(CampaignCharacter).filter(
        CampaignCharacter.campaign_id == campaign_id,
        CampaignCharacter.character_id == damage_req.character_id
    ).first()
    
    if not cc:
        raise HTTPException(status_code=404, detail="Character not in campaign")
    
    char = db.query(Character).filter(Character.id == damage_req.character_id).first()
    
    new_hp = max(0, cc.current_hp - damage_req.damage)
    cc.current_hp = new_hp
    
    # Update status
    if new_hp == 0:
        cc.status = 'unconscious'
    
    db.commit()
    
    return {
        "character_id": damage_req.character_id,
        "character_name": char.name,
        "damage_taken": damage_req.damage,
        "current_hp": new_hp,
        "max_hp": char.dnd_hit_points_max,
        "status": cc.status
    }


@router.post("/{campaign_id}/combat/heal")
async def apply_healing(
    campaign_id: int,
    heal_req: HealRequest,
    db: Session = Depends(get_db)
):
    """Apply healing to a character"""
    cc = db.query(CampaignCharacter).filter(
        CampaignCharacter.campaign_id == campaign_id,
        CampaignCharacter.character_id == heal_req.character_id
    ).first()
    
    if not cc:
        raise HTTPException(status_code=404, detail="Character not in campaign")
    
    char = db.query(Character).filter(Character.id == heal_req.character_id).first()
    
    new_hp = min(char.dnd_hit_points_max, cc.current_hp + heal_req.healing)
    cc.current_hp = new_hp
    
    # Update status if revived
    if new_hp > 0 and cc.status == 'unconscious':
        cc.status = 'active'
    
    db.commit()
    
    return {
        "character_id": heal_req.character_id,
        "character_name": char.name,
        "healing_received": heal_req.healing,
        "current_hp": new_hp,
        "max_hp": char.dnd_hit_points_max,
        "status": cc.status
    }
