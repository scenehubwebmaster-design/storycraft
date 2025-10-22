"""
Game Session API Router

REST endpoints for D&D game session management:
- POST   /api/game/sessions          - Create new game session
- GET    /api/game/sessions          - List game sessions
- GET    /api/game/sessions/{id}     - Get session details
- PUT    /api/game/sessions/{id}     - Update game state
- DELETE /api/game/sessions/{id}     - End game session
- POST   /api/game/sessions/{id}/party  - Add character to party
- GET    /api/game/sessions/{id}/party  - Get party status
- PUT    /api/game/sessions/{id}/party/{char_id}/hp - Update character HP
- GET    /api/game/sessions/{id}/events - Get event log
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

try:
    from ..database import get_db
    from ..game.session_manager import SessionManager
    from ..game.dice_roller import DiceRoller, AdvantageType
    from ..game.combat_engine import CombatEngine, CombatantData
except ImportError:
    from backend.database import get_db
    from backend.game.session_manager import SessionManager
    from backend.game.dice_roller import DiceRoller, AdvantageType
    from backend.game.combat_engine import CombatEngine, CombatantData


router = APIRouter(prefix="/api/game", tags=["game"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request model for creating a new game session"""
    campaign_name: str = Field(..., description="Name of the campaign")
    chat_session_id: int = Field(..., description="Associated chat session ID")
    party_level: int = Field(default=1, ge=1, le=20, description="Starting party level")
    initial_location: Optional[str] = Field(None, description="Starting location")
    initial_scene: Optional[str] = Field(None, description="Opening scene description")


class UpdateStateRequest(BaseModel):
    """Request model for updating game state"""
    state: Dict[str, Any] = Field(..., description="Game state data")
    merge: bool = Field(default=True, description="Merge with existing state or replace")


class AddPartyMemberRequest(BaseModel):
    """Request model for adding a character to the party"""
    character_id: int = Field(..., description="ID of character to add to party")


class UpdateHPRequest(BaseModel):
    """Request model for updating character HP"""
    current_hp: int = Field(..., ge=0, description="New current HP")
    temp_hp: Optional[int] = Field(None, ge=0, description="New temporary HP")


class GameSessionResponse(BaseModel):
    """Response model for game session"""
    id: int
    chat_session_id: int
    campaign_name: str
    current_location: Optional[str]
    current_scene: Optional[str]
    game_state: Optional[Dict[str, Any]]
    party_level: int
    session_notes: Optional[str]
    created_at: str
    updated_at: str
    party_members: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True


class PartyMemberResponse(BaseModel):
    """Response model for party member"""
    id: int
    game_session_id: int
    character_id: int
    character_name: Optional[str]
    current_hp: int
    max_hp: int
    temp_hp: int
    conditions: Optional[List[str]]
    position: Optional[Dict[str, Any]]
    is_active: bool
    joined_at: str
    
    class Config:
        from_attributes = True


class GameEventResponse(BaseModel):
    """Response model for game event"""
    id: int
    game_session_id: int
    event_type: str
    description: str
    game_state_snapshot: Optional[Dict[str, Any]]
    turn_number: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/sessions", response_model=GameSessionResponse, status_code=status.HTTP_201_CREATED)
def create_game_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new game session
    
    Creates a new D&D game session linked to a chat session. The game session
    tracks party state, locations, quests, and all game-related data.
    
    Returns:
        GameSession with empty party (use POST /sessions/{id}/party to add characters)
    """
    manager = SessionManager(db)
    
    try:
        session = manager.create_session(
            campaign_name=request.campaign_name,
            chat_session_id=request.chat_session_id,
            party_level=request.party_level,
            initial_location=request.initial_location,
            initial_scene=request.initial_scene
        )
        
        return GameSessionResponse(
            id=session.id,
            chat_session_id=session.chat_session_id,
            campaign_name=session.campaign_name,
            current_location=session.current_location,
            current_scene=session.current_scene,
            game_state=session.game_state,
            party_level=session.party_level,
            session_notes=session.session_notes,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions", response_model=List[GameSessionResponse])
def list_game_sessions(
    chat_session_id: Optional[int] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List game sessions
    
    Query parameters:
        chat_session_id: Filter by chat session ID (optional)
        limit: Maximum sessions to return (default: 20)
    
    Returns:
        List of game sessions ordered by created_at descending
    """
    manager = SessionManager(db)
    sessions = manager.list_sessions(chat_session_id=chat_session_id, limit=limit)
    
    return [
        GameSessionResponse(
            id=s.id,
            chat_session_id=s.chat_session_id,
            campaign_name=s.campaign_name,
            current_location=s.current_location,
            current_scene=s.current_scene,
            game_state=s.game_state,
            party_level=s.party_level,
            session_notes=s.session_notes,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=GameSessionResponse)
def get_game_session(
    session_id: int,
    include_party: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get game session details
    
    Path parameters:
        session_id: ID of the game session
    
    Query parameters:
        include_party: Include party member details (default: true)
    
    Returns:
        Game session with optional party member details
    """
    manager = SessionManager(db)
    session = manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    
    response_data = {
        "id": session.id,
        "chat_session_id": session.chat_session_id,
        "campaign_name": session.campaign_name,
        "current_location": session.current_location,
        "current_scene": session.current_scene,
        "game_state": session.game_state,
        "party_level": session.party_level,
        "session_notes": session.session_notes,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }
    
    if include_party:
        response_data["party_members"] = manager.get_party_status(session_id)
    
    return GameSessionResponse(**response_data)


@router.put("/sessions/{session_id}", response_model=GameSessionResponse)
def update_game_state(
    session_id: int,
    request: UpdateStateRequest,
    db: Session = Depends(get_db)
):
    """
    Update game state
    
    Updates the game state JSON. Can merge with existing state or replace entirely.
    
    Path parameters:
        session_id: ID of the game session
    
    Request body:
        state: Dictionary of state data to save
        merge: If true, merge with existing state; if false, replace (default: true)
    
    Returns:
        Updated game session
    """
    manager = SessionManager(db)
    
    try:
        session = manager.save_state(
            game_session_id=session_id,
            state_dict=request.state,
            merge=request.merge
        )
        
        return GameSessionResponse(
            id=session.id,
            chat_session_id=session.chat_session_id,
            campaign_name=session.campaign_name,
            current_location=session.current_location,
            current_scene=session.current_scene,
            game_state=session.game_state,
            party_level=session.party_level,
            session_notes=session.session_notes,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def end_game_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    End a game session
    
    Marks the session as ended and deactivates all party members.
    This is a soft delete - the session and all data remain in the database.
    
    Path parameters:
        session_id: ID of the game session
    
    Returns:
        204 No Content on success
    """
    manager = SessionManager(db)
    
    if not manager.end_session(session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    
    return None


@router.post("/sessions/{session_id}/party", response_model=PartyMemberResponse, status_code=status.HTTP_201_CREATED)
def add_party_member(
    session_id: int,
    request: AddPartyMemberRequest,
    db: Session = Depends(get_db)
):
    """
    Add a character to the party
    
    Adds an existing character to the game session's party. The character's
    HP will be initialized from their D&D character sheet (dnd_hit_points).
    
    Path parameters:
        session_id: ID of the game session
    
    Request body:
        character_id: ID of character to add
    
    Returns:
        PartyMember with initialized HP and status
    """
    manager = SessionManager(db)
    
    try:
        party_member = manager.add_party_member(
            game_session_id=session_id,
            character_id=request.character_id
        )
        
        return PartyMemberResponse(**party_member.to_dict())
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions/{session_id}/party", response_model=List[PartyMemberResponse])
def get_party_status(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get party status
    
    Returns current status of all active party members including HP,
    conditions, and position.
    
    Path parameters:
        session_id: ID of the game session
    
    Returns:
        List of party members with current status
    """
    manager = SessionManager(db)
    party_status = manager.get_party_status(session_id)
    
    return [PartyMemberResponse(**pm) for pm in party_status]


@router.put("/sessions/{session_id}/party/{character_id}/hp", response_model=PartyMemberResponse)
def update_character_hp(
    session_id: int,
    character_id: int,
    request: UpdateHPRequest,
    db: Session = Depends(get_db)
):
    """
    Update character HP
    
    Updates a party member's current HP and optional temporary HP.
    HP changes are logged to the event log.
    
    Path parameters:
        session_id: ID of the game session
        character_id: ID of the character
    
    Request body:
        current_hp: New current HP value (0 to max_hp)
        temp_hp: New temporary HP (optional)
    
    Returns:
        Updated party member with new HP values
    """
    manager = SessionManager(db)
    
    try:
        party_member = manager.update_party_hp(
            game_session_id=session_id,
            character_id=character_id,
            new_hp=request.current_hp,
            temp_hp=request.temp_hp
        )
        
        return PartyMemberResponse(**party_member.to_dict())
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions/{session_id}/events", response_model=List[GameEventResponse])
def get_event_log(
    session_id: int,
    event_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get event log
    
    Returns chronological log of game events for the session.
    Events include session creation, party changes, HP changes, combat, etc.
    
    Path parameters:
        session_id: ID of the game session
    
    Query parameters:
        event_type: Filter by event type (optional)
        limit: Maximum events to return (default: 50)
    
    Returns:
        List of game events in chronological order
    """
    manager = SessionManager(db)
    events = manager.get_event_log(
        game_session_id=session_id,
        event_type=event_type,
        limit=limit
    )
    
    return [
        GameEventResponse(
            id=e.id,
            game_session_id=e.game_session_id,
            event_type=e.event_type,
            description=e.description,
            game_state_snapshot=e.game_state_snapshot,
            turn_number=e.turn_number,
            created_at=e.created_at.isoformat()
        )
        for e in events
    ]


# ============================================================================
# DICE ROLLING
# ============================================================================

class RollDiceRequest(BaseModel):
    """Request model for dice rolls"""
    notation: str = Field(..., description="Dice notation (e.g., '2d6+3', '1d20')")
    advantage: Optional[str] = Field(None, description="'advantage' or 'disadvantage'")
    purpose: Optional[str] = Field(None, description="Purpose of the roll (e.g., 'Attack roll', 'Perception check')")
    character_id: Optional[int] = Field(None, description="Character making the roll (for logging)")


class RollDiceResponse(BaseModel):
    """Response model for dice rolls"""
    total: int
    rolls: List[int]
    modifier: int
    notation: str
    breakdown: str
    advantage_type: Optional[str] = None
    dropped_rolls: Optional[List[int]] = None
    purpose: Optional[str] = None


@router.post("/sessions/{session_id}/roll", response_model=RollDiceResponse)
def roll_dice(
    session_id: int,
    request: RollDiceRequest,
    db: Session = Depends(get_db)
):
    """
    Roll dice and log to game events
    
    Path parameters:
        session_id: ID of the game session
    
    Request body:
    {
        "notation": "2d6+3",
        "advantage": "advantage",  // Optional: "advantage" or "disadvantage"
        "purpose": "Attack roll",  // Optional: Description of the roll
        "character_id": 123        // Optional: Character making the roll
    }
    
    Response:
    {
        "total": 11,
        "rolls": [4, 4],
        "modifier": 3,
        "notation": "2d6+3",
        "breakdown": "4 + 4 + 3 = 11",
        "advantage_type": "advantage",
        "dropped_rolls": [2],
        "purpose": "Attack roll"
    }
    
    Returns:
        Dice roll result with breakdown
    """
    try:
        # Parse advantage type
        advantage_type = None
        if request.advantage:
            if request.advantage.lower() == "advantage":
                advantage_type = AdvantageType.ADVANTAGE
            elif request.advantage.lower() == "disadvantage":
                advantage_type = AdvantageType.DISADVANTAGE
            else:
                raise ValueError(f"Invalid advantage type: {request.advantage}")
        
        # Roll dice
        roller = DiceRoller()
        result = roller.roll(request.notation, advantage=advantage_type)
        
        # Log to game events
        manager = SessionManager(db)
        description = request.purpose or f"Rolled {request.notation}"
        if request.character_id:
            description = f"Character {request.character_id}: {description}"
        
        manager.log_event(
            game_session_id=session_id,
            event_type="dice_roll",
            description=f"{description} → {result.breakdown}",
            state_snapshot={
                "notation": request.notation,
                "result": result.total,
                "breakdown": result.breakdown,
                "character_id": request.character_id
            }
        )
        
        return RollDiceResponse(
            total=result.total,
            rolls=result.rolls,
            modifier=result.modifier,
            notation=result.notation,
            breakdown=result.breakdown,
            advantage_type=result.advantage_type.value if result.advantage_type else None,
            dropped_rolls=result.dropped_rolls,
            purpose=request.purpose
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class CombatantRequest(BaseModel):
    """Request model for combat participant"""
    name: str
    initiative_bonus: int
    max_hp: int
    current_hp: int
    ac: int
    is_player: bool
    character_id: Optional[int] = None
    monster_type: Optional[str] = None


class StartCombatRequest(BaseModel):
    """Request model for starting combat"""
    participants: List[CombatantRequest]
    location: Optional[str] = None


class AttackRequest(BaseModel):
    """Request model for attack action"""
    attacker_id: int
    target_id: int
    weapon_damage: str = Field(..., description="Damage notation (e.g., '1d8+3')")
    attack_bonus: int
    advantage: Optional[str] = None


class CombatStateResponse(BaseModel):
    """Response model for combat state"""
    combat_id: int
    round_number: int
    current_turn: int
    turn_order: List[Dict]
    is_active: bool
    participants: List[Dict]


class AttackResponse(BaseModel):
    """Response model for attack action"""
    success: bool
    description: str
    damage: Optional[int] = None
    target_hp_remaining: Optional[int] = None
    target_defeated: bool = False
    critical: bool = False


@router.post("/sessions/{session_id}/combat/start", response_model=CombatStateResponse)
def start_combat(
    session_id: int,
    request: StartCombatRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new combat encounter
    
    Rolls initiative for all participants, creates combat records,
    and returns the initial combat state with turn order.
    
    Request:
    {
        "participants": [
            {
                "name": "Garrick",
                "initiative_bonus": 2,
                "max_hp": 24,
                "current_hp": 24,
                "ac": 18,
                "is_player": true,
                "character_id": 123
            },
            {
                "name": "Goblin",
                "initiative_bonus": 2,
                "max_hp": 7,
                "current_hp": 7,
                "ac": 15,
                "is_player": false,
                "monster_type": "goblin"
            }
        ],
        "location": "Dark forest clearing"
    }
    
    Returns combat state with initiative order
    """
    try:
        # Convert to CombatantData
        combatants = [
            CombatantData(
                name=p.name,
                initiative_bonus=p.initiative_bonus,
                max_hp=p.max_hp,
                current_hp=p.current_hp,
                ac=p.ac,
                is_player=p.is_player,
                character_id=p.character_id,
                monster_type=p.monster_type
            )
            for p in request.participants
        ]
        
        # Start combat
        engine = CombatEngine(db)
        combat = engine.start_combat(
            game_session_id=session_id,
            participants=combatants,
            location=request.location
        )
        
        # Get combat state
        state = engine.get_combat_state(combat.id)
        
        return CombatStateResponse(**state.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions/{session_id}/combat/{combat_id}", response_model=CombatStateResponse)
def get_combat_state(
    session_id: int,
    combat_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current combat state
    
    Returns turn order, current turn, round number, and all participant statuses.
    """
    try:
        engine = CombatEngine(db)
        state = engine.get_combat_state(combat_id)
        
        return CombatStateResponse(**state.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/sessions/{session_id}/combat/{combat_id}/attack", response_model=AttackResponse)
def process_attack(
    session_id: int,
    combat_id: int,
    request: AttackRequest,
    db: Session = Depends(get_db)
):
    """
    Process an attack action
    
    Rolls attack vs AC, calculates damage on hit, updates HP,
    and checks for defeat.
    
    Request:
    {
        "attacker_id": 1,
        "target_id": 2,
        "weapon_damage": "1d8+3",
        "attack_bonus": 5,
        "advantage": "advantage"  // Optional: "advantage" or "disadvantage"
    }
    
    Returns attack results and updated HP
    """
    try:
        # Parse advantage
        advantage_type = AdvantageType.NORMAL
        if request.advantage:
            if request.advantage.lower() == "advantage":
                advantage_type = AdvantageType.ADVANTAGE
            elif request.advantage.lower() == "disadvantage":
                advantage_type = AdvantageType.DISADVANTAGE
        
        # Process attack
        engine = CombatEngine(db)
        result = engine.process_attack(
            combat_id=combat_id,
            attacker_id=request.attacker_id,
            target_id=request.target_id,
            weapon_damage=request.weapon_damage,
            attack_bonus=request.attack_bonus,
            advantage=advantage_type
        )
        
        return AttackResponse(**result.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/{session_id}/combat/{combat_id}/next-turn", response_model=CombatStateResponse)
def next_turn(
    session_id: int,
    combat_id: int,
    db: Session = Depends(get_db)
):
    """
    Advance to next turn in combat
    
    Increments turn counter, starts new round if needed,
    and returns updated combat state.
    """
    try:
        engine = CombatEngine(db)
        state = engine.next_turn(combat_id)
        
        return CombatStateResponse(**state.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/{session_id}/combat/{combat_id}/end", response_model=CombatStateResponse)
def end_combat(
    session_id: int,
    combat_id: int,
    outcome: str = "completed",
    db: Session = Depends(get_db)
):
    """
    End combat encounter
    
    Marks combat as inactive, clears temp HP and conditions,
    and logs final state.
    
    Query params:
        outcome: Outcome description ("victory", "defeat", "fled", etc.)
    """
    try:
        engine = CombatEngine(db)
        state = engine.end_combat(combat_id, outcome)
        
        return CombatStateResponse(**state.__dict__)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

