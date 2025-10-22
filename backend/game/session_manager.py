"""
Session Manager for D&D Game System

Handles game session lifecycle:
- Creating new game sessions
- Managing party members
- Tracking game state
- Loading/saving session data
"""

from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from ..models import (
        GameSession,
        PartyMember,
        Quest,
        GameEvent,
        GameLocation,
        NPC,
        Character,
        ChatSession
    )
except ImportError:
    from backend.models import (
        GameSession,
        PartyMember,
        Quest,
        GameEvent,
        GameLocation,
        NPC,
        Character,
        ChatSession
    )


class SessionManager:
    """Manages D&D game session lifecycle and state"""

    def __init__(self, db: Session):
        """
        Initialize SessionManager with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_session(
        self,
        campaign_name: str,
        chat_session_id: int,
        party_level: int = 1,
        initial_location: Optional[str] = None,
        initial_scene: Optional[str] = None
    ) -> GameSession:
        """
        Create a new game session
        
        Args:
            campaign_name: Name of the campaign
            chat_session_id: ID of the associated chat session
            party_level: Starting level for the party (default: 1)
            initial_location: Starting location description
            initial_scene: Opening scene text
            
        Returns:
            GameSession object
            
        Example:
            >>> session = manager.create_session(
            ...     campaign_name="Lost Mine of Phandelver",
            ...     chat_session_id=123,
            ...     party_level=1,
            ...     initial_location="Neverwinter",
            ...     initial_scene="You meet in a tavern..."
            ... )
        """
        # Verify chat session exists
        chat_session = self.db.query(ChatSession).filter(
            ChatSession.id == chat_session_id
        ).first()
        
        if not chat_session:
            raise ValueError(f"ChatSession {chat_session_id} not found")
        
        # Create game session
        game_session = GameSession(
            chat_session_id=chat_session_id,
            campaign_name=campaign_name,
            party_level=party_level,
            current_location=initial_location,
            current_scene=initial_scene,
            game_state={"initialized": True, "turn": 0}
        )
        
        self.db.add(game_session)
        self.db.commit()
        self.db.refresh(game_session)
        
        # Log creation event
        self.log_event(
            game_session_id=game_session.id,
            event_type="session_created",
            description=f"Campaign '{campaign_name}' started at level {party_level}"
        )
        
        return game_session

    def add_party_member(
        self,
        game_session_id: int,
        character_id: int
    ) -> PartyMember:
        """
        Add a character to the party
        
        Args:
            game_session_id: ID of the game session
            character_id: ID of the character to add
            
        Returns:
            PartyMember object
            
        Raises:
            ValueError: If session or character not found, or character already in party
        """
        # Verify game session exists
        game_session = self.db.query(GameSession).filter(
            GameSession.id == game_session_id
        ).first()
        
        if not game_session:
            raise ValueError(f"GameSession {game_session_id} not found")
        
        # Verify character exists
        character = self.db.query(Character).filter(
            Character.id == character_id
        ).first()
        
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Check if already in party
        existing = self.db.query(PartyMember).filter(
            PartyMember.game_session_id == game_session_id,
            PartyMember.character_id == character_id,
            PartyMember.is_active == True
        ).first()
        
        if existing:
            raise ValueError(f"Character {character.name} already in party")
        
        # Get HP from character's D&D data or default to 10
        max_hp = character.dnd_hit_points if character.dnd_hit_points else 10
        
        # Create party member
        party_member = PartyMember(
            game_session_id=game_session_id,
            character_id=character_id,
            current_hp=max_hp,
            max_hp=max_hp,
            temp_hp=0,
            conditions=[],
            position=None,
            is_active=True
        )
        
        self.db.add(party_member)
        self.db.commit()
        self.db.refresh(party_member)
        
        # Log event
        self.log_event(
            game_session_id=game_session_id,
            event_type="party_member_joined",
            description=f"{character.name} joined the party (HP: {max_hp})"
        )
        
        return party_member

    def get_party_status(self, game_session_id: int) -> List[Dict[str, Any]]:
        """
        Get current status of all party members
        
        Args:
            game_session_id: ID of the game session
            
        Returns:
            List of party member status dictionaries
        """
        party_members = self.db.query(PartyMember).filter(
            PartyMember.game_session_id == game_session_id,
            PartyMember.is_active == True
        ).all()
        
        return [pm.to_dict() for pm in party_members]

    def update_party_hp(
        self,
        game_session_id: int,
        character_id: int,
        new_hp: int,
        temp_hp: Optional[int] = None
    ) -> PartyMember:
        """
        Update a party member's hit points
        
        Args:
            game_session_id: ID of the game session
            character_id: ID of the character
            new_hp: New current HP value
            temp_hp: New temporary HP (optional)
            
        Returns:
            Updated PartyMember object
            
        Raises:
            ValueError: If party member not found
        """
        party_member = self.db.query(PartyMember).filter(
            PartyMember.game_session_id == game_session_id,
            PartyMember.character_id == character_id,
            PartyMember.is_active == True
        ).first()
        
        if not party_member:
            raise ValueError(f"Character {character_id} not in active party")
        
        old_hp = party_member.current_hp
        party_member.current_hp = max(0, min(new_hp, party_member.max_hp))
        
        if temp_hp is not None:
            party_member.temp_hp = max(0, temp_hp)
        
        self.db.commit()
        self.db.refresh(party_member)
        
        # Log HP change
        change = party_member.current_hp - old_hp
        sign = "+" if change > 0 else ""
        self.log_event(
            game_session_id=game_session_id,
            event_type="hp_change",
            description=f"{party_member.character.name}: {old_hp} → {party_member.current_hp} ({sign}{change})"
        )
        
        return party_member

    def save_state(
        self,
        game_session_id: int,
        state_dict: Dict[str, Any],
        merge: bool = True
    ) -> GameSession:
        """
        Save game state
        
        Args:
            game_session_id: ID of the game session
            state_dict: State data to save (will be stored as JSON)
            merge: If True, merge with existing state; if False, replace entirely
            
        Returns:
            Updated GameSession object
        """
        game_session = self.db.query(GameSession).filter(
            GameSession.id == game_session_id
        ).first()
        
        if not game_session:
            raise ValueError(f"GameSession {game_session_id} not found")
        
        if merge and game_session.game_state:
            # Merge with existing state
            current_state = game_session.game_state
            current_state.update(state_dict)
            game_session.game_state = current_state
        else:
            # Replace state entirely
            game_session.game_state = state_dict
        
        game_session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(game_session)
        
        return game_session

    def load_state(self, game_session_id: int) -> Dict[str, Any]:
        """
        Load game state
        
        Args:
            game_session_id: ID of the game session
            
        Returns:
            Game state dictionary
        """
        game_session = self.db.query(GameSession).filter(
            GameSession.id == game_session_id
        ).first()
        
        if not game_session:
            raise ValueError(f"GameSession {game_session_id} not found")
        
        return game_session.game_state or {}

    def get_session(self, game_session_id: int, include_relationships: bool = False) -> Optional[GameSession]:
        """
        Get game session by ID
        
        Args:
            game_session_id: ID of the game session
            include_relationships: Whether to include related data in response
            
        Returns:
            GameSession object or None if not found
        """
        session = self.db.query(GameSession).filter(
            GameSession.id == game_session_id
        ).first()
        
        return session

    def list_sessions(
        self,
        chat_session_id: Optional[int] = None,
        limit: int = 20
    ) -> List[GameSession]:
        """
        List game sessions
        
        Args:
            chat_session_id: Filter by chat session ID (optional)
            limit: Maximum number of sessions to return
            
        Returns:
            List of GameSession objects
        """
        query = self.db.query(GameSession)
        
        if chat_session_id:
            query = query.filter(GameSession.chat_session_id == chat_session_id)
        
        query = query.order_by(GameSession.created_at.desc()).limit(limit)
        
        return query.all()

    def end_session(self, game_session_id: int) -> bool:
        """
        End a game session (soft delete - marks as inactive in game_state)
        
        Args:
            game_session_id: ID of the game session
            
        Returns:
            True if successful, False if session not found
        """
        game_session = self.db.query(GameSession).filter(
            GameSession.id == game_session_id
        ).first()
        
        if not game_session:
            return False
        
        # Mark as ended in state
        state = game_session.game_state or {}
        state["ended"] = True
        state["ended_at"] = datetime.utcnow().isoformat()
        game_session.game_state = state
        game_session.updated_at = datetime.utcnow()
        
        # Deactivate all party members
        self.db.query(PartyMember).filter(
            PartyMember.game_session_id == game_session_id
        ).update({"is_active": False})
        
        # Log event
        self.log_event(
            game_session_id=game_session_id,
            event_type="session_ended",
            description=f"Campaign '{game_session.campaign_name}' ended"
        )
        
        self.db.commit()
        
        return True

    def log_event(
        self,
        game_session_id: int,
        event_type: str,
        description: str,
        state_snapshot: Optional[Dict[str, Any]] = None,
        turn_number: Optional[int] = None
    ) -> GameEvent:
        """
        Log a game event for audit trail and session journal
        
        Args:
            game_session_id: ID of the game session
            event_type: Type of event (e.g., "combat", "dialogue", "exploration")
            description: Human-readable description
            state_snapshot: Optional snapshot of game state at this moment
            turn_number: Optional turn number
            
        Returns:
            GameEvent object
        """
        event = GameEvent(
            game_session_id=game_session_id,
            event_type=event_type,
            description=description,
            game_state_snapshot=state_snapshot,
            turn_number=turn_number
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        return event

    def get_event_log(
        self,
        game_session_id: int,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[GameEvent]:
        """
        Get event log for a session
        
        Args:
            game_session_id: ID of the game session
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of GameEvent objects in chronological order
        """
        query = self.db.query(GameEvent).filter(
            GameEvent.game_session_id == game_session_id
        )
        
        if event_type:
            query = query.filter(GameEvent.event_type == event_type)
        
        query = query.order_by(GameEvent.created_at.asc()).limit(limit)
        
        return query.all()
