"""
D&D 5e Combat Engine

Handles all combat mechanics including:
- Initiative rolling and tracking
- Turn order management
- Attack resolution
- Damage calculation and HP tracking
- Combat state management
- Victory/defeat conditions
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

try:
    from ..models import GameSession, CombatEncounter, CombatParticipant, PartyMember
    from .dice_roller import DiceRoller, AdvantageType, AttackResult, DamageResult
    from .session_manager import SessionManager
except ImportError:
    from backend.models import GameSession, CombatEncounter, CombatParticipant, PartyMember
    from backend.game.dice_roller import DiceRoller, AdvantageType, AttackResult, DamageResult
    from backend.game.session_manager import SessionManager


@dataclass
class CombatantData:
    """Data for a combat participant"""
    name: str
    initiative_bonus: int
    max_hp: int
    current_hp: int
    ac: int
    is_player: bool
    character_id: Optional[int] = None  # For player characters
    monster_type: Optional[str] = None  # For monsters


@dataclass
class CombatState:
    """Current state of combat"""
    combat_id: int
    round_number: int
    current_turn: int
    turn_order: List[Dict]
    is_active: bool
    participants: List[Dict]


@dataclass
class CombatAction:
    """Result of a combat action"""
    success: bool
    description: str
    damage: Optional[int] = None
    target_hp_remaining: Optional[int] = None
    target_defeated: bool = False
    critical: bool = False


class CombatEngine:
    """
    D&D 5e combat encounter management
    
    Handles initiative, turn tracking, attack resolution,
    and combat state persistence.
    """
    
    def __init__(self, db: Session, dice_roller: Optional[DiceRoller] = None):
        """
        Initialize combat engine
        
        Args:
            db: Database session
            dice_roller: Optional dice roller (creates new if not provided)
        """
        self.db = db
        self.dice = dice_roller or DiceRoller()
        self.session_mgr = SessionManager(db)
    
    def start_combat(
        self,
        game_session_id: int,
        participants: List[CombatantData],
        location: Optional[str] = None
    ) -> CombatEncounter:
        """
        Start a new combat encounter
        
        1. Roll initiative for all participants
        2. Create combat_encounter record
        3. Create combat_participant records
        4. Sort by initiative (ties broken by DEX/initiative_bonus)
        5. Set current turn to highest initiative
        6. Log combat start event
        
        Args:
            game_session_id: ID of the game session
            participants: List of combatants with stats
            location: Optional combat location description
        
        Returns:
            CombatEncounter object
        
        Example:
            >>> participants = [
            ...     CombatantData(
            ...         name="Garrick",
            ...         initiative_bonus=2,
            ...         max_hp=24,
            ...         current_hp=24,
            ...         ac=18,
            ...         is_player=True,
            ...         character_id=123
            ...     ),
            ...     CombatantData(
            ...         name="Goblin",
            ...         initiative_bonus=2,
            ...         max_hp=7,
            ...         current_hp=7,
            ...         ac=15,
            ...         is_player=False,
            ...         monster_type="goblin"
            ...     )
            ... ]
            >>> combat = engine.start_combat(session_id, participants)
        """
        # Roll initiative for each participant
        initiative_rolls = []
        for p in participants:
            roll = self.dice.roll(f"1d20{p.initiative_bonus:+d}")
            initiative_rolls.append({
                'participant': p,
                'initiative': roll.total,
                'roll_breakdown': roll.breakdown
            })
        
        # Sort by initiative (highest first), ties broken by bonus
        initiative_rolls.sort(
            key=lambda x: (x['initiative'], x['participant'].initiative_bonus),
            reverse=True
        )
        
        # Build turn order JSON
        turn_order = [
            {
                'name': ir['participant'].name,
                'initiative': ir['initiative'],
                'is_player': ir['participant'].is_player
            }
            for ir in initiative_rolls
        ]
        
        # Create combat encounter
        combat = CombatEncounter(
            game_session_id=game_session_id,
            location=location,
            turn_order=turn_order,
            current_turn=0,  # Start with first in initiative order
            round_number=1,
            is_active=True
        )
        self.db.add(combat)
        self.db.flush()  # Get combat ID
        
        # Create combat participants
        for ir in initiative_rolls:
            p = ir['participant']
            participant = CombatParticipant(
                combat_encounter_id=combat.id,
                name=p.name,
                character_id=p.character_id,
                monster_type=p.monster_type,
                initiative=ir['initiative'],
                max_hp=p.max_hp,
                current_hp=p.current_hp,
                ac=p.ac,
                is_player=p.is_player,
                conditions=[]
            )
            self.db.add(participant)
        
        self.db.commit()
        self.db.refresh(combat)
        
        # Log combat start
        init_descriptions = [
            f"{ir['participant'].name}: {ir['roll_breakdown']}"
            for ir in initiative_rolls
        ]
        self.session_mgr.log_event(
            game_session_id=game_session_id,
            event_type="combat_start",
            description=f"Combat started! Initiative order:\n" + "\n".join(init_descriptions),
            state_snapshot={
                'combat_id': combat.id,
                'location': location,
                'turn_order': turn_order,
                'participant_count': len(participants)
            },
            turn_number=0
        )
        
        return combat
    
    def process_attack(
        self,
        combat_id: int,
        attacker_id: int,
        target_id: int,
        weapon_damage: str,
        attack_bonus: int,
        advantage: AdvantageType = AdvantageType.NORMAL
    ) -> CombatAction:
        """
        Process an attack action
        
        1. Roll attack (d20 + bonus vs AC)
        2. On hit: roll damage
        3. On crit: double damage dice
        4. Apply damage to target HP
        5. Update combat_participant HP
        6. Update party_member HP if PC
        7. Check for death (HP <= 0)
        8. Log attack event
        9. Return detailed result
        
        Args:
            combat_id: ID of the combat encounter
            attacker_id: ID of attacking combat_participant
            target_id: ID of target combat_participant
            weapon_damage: Damage dice notation (e.g., "1d8+3")
            attack_bonus: Attack modifier (proficiency + ability)
            advantage: Advantage type
        
        Returns:
            CombatAction with attack results
        """
        # Get attacker and target
        attacker = self.db.query(CombatParticipant).get(attacker_id)
        target = self.db.query(CombatParticipant).get(target_id)
        
        if not attacker or not target:
            return CombatAction(
                success=False,
                description="Invalid attacker or target"
            )
        
        # Roll attack
        attack_result = self.dice.roll_attack(
            attack_bonus=attack_bonus,
            target_ac=target.ac,
            advantage=advantage
        )
        
        # Miss
        if not attack_result.hit:
            description = f"{attacker.name} attacks {target.name}: {attack_result.breakdown} - MISS!"
            
            # Log miss
            self._log_combat_action(
                combat_id=combat_id,
                attacker=attacker.name,
                target=target.name,
                action="attack_miss",
                details=attack_result.breakdown
            )
            
            return CombatAction(
                success=True,
                description=description,
                damage=0,
                target_hp_remaining=target.current_hp
            )
        
        # Hit - roll damage
        damage_result = self.dice.roll_damage(
            notation=weapon_damage,
            critical=attack_result.critical
        )
        
        # Apply damage
        new_hp = max(0, target.current_hp - damage_result.total)
        target.current_hp = new_hp
        
        # Update party member HP if player
        if target.is_player and target.character_id:
            party_member = self.db.query(PartyMember).filter(
                PartyMember.character_id == target.character_id,
                PartyMember.combat_encounter_id == combat_id
            ).first()
            
            if party_member:
                party_member.current_hp = new_hp
        
        self.db.commit()
        
        # Check for defeat
        defeated = (new_hp <= 0)
        
        # Build description
        hit_type = "CRITICAL HIT!" if attack_result.critical else "HIT!"
        description = (
            f"{attacker.name} attacks {target.name}: "
            f"{attack_result.breakdown} - {hit_type}\n"
            f"Damage: {damage_result.breakdown}\n"
            f"{target.name}: {target.current_hp + damage_result.total} HP → {new_hp} HP"
        )
        
        if defeated:
            description += f"\n💀 {target.name} is defeated!"
        
        # Log attack
        self._log_combat_action(
            combat_id=combat_id,
            attacker=attacker.name,
            target=target.name,
            action="attack_hit",
            details={
                'attack_roll': attack_result.breakdown,
                'damage_roll': damage_result.breakdown,
                'damage': damage_result.total,
                'critical': attack_result.critical,
                'target_hp': new_hp,
                'defeated': defeated
            }
        )
        
        return CombatAction(
            success=True,
            description=description,
            damage=damage_result.total,
            target_hp_remaining=new_hp,
            target_defeated=defeated,
            critical=attack_result.critical
        )
    
    def next_turn(self, combat_id: int) -> CombatState:
        """
        Advance to next turn
        
        1. Increment turn counter
        2. If end of initiative order, increment round
        3. Process conditions (duration tracking)
        4. Set current_turn to next participant
        5. Skip defeated participants
        6. Log turn change event
        
        Args:
            combat_id: ID of the combat encounter
        
        Returns:
            Updated combat state
        """
        combat = self.db.query(CombatEncounter).get(combat_id)
        
        if not combat or not combat.is_active:
            raise ValueError(f"Combat {combat_id} not found or not active")
        
        # Get participants
        participants = self.db.query(CombatParticipant).filter(
            CombatParticipant.combat_encounter_id == combat_id,
            CombatParticipant.current_hp > 0  # Only alive participants
        ).all()
        
        if len(participants) == 0:
            # No participants left, end combat
            return self.end_combat(combat_id, "all_defeated")
        
        # Increment turn
        combat.current_turn += 1
        
        # Check if round ended
        if combat.current_turn >= len(combat.turn_order):
            combat.current_turn = 0
            combat.round_number += 1
            
            # Log new round
            self._log_combat_action(
                combat_id=combat_id,
                attacker="System",
                target="",
                action="new_round",
                details=f"Round {combat.round_number} begins"
            )
        
        self.db.commit()
        
        # Get current turn participant name
        current_participant_name = combat.turn_order[combat.current_turn]['name']
        
        # Log turn change
        self._log_combat_action(
            combat_id=combat_id,
            attacker="System",
            target="",
            action="turn_change",
            details=f"Turn: {current_participant_name}"
        )
        
        return self.get_combat_state(combat_id)
    
    def end_combat(self, combat_id: int, outcome: str) -> CombatState:
        """
        End combat encounter
        
        1. Mark combat as completed
        2. Award XP (if victory)
        3. Reset temp HP
        4. Clear combat conditions
        5. Log combat end event
        
        Args:
            combat_id: ID of the combat encounter
            outcome: Outcome description ("victory", "defeat", "fled", etc.)
        
        Returns:
            Final combat state
        """
        combat = self.db.query(CombatEncounter).get(combat_id)
        
        if not combat:
            raise ValueError(f"Combat {combat_id} not found")
        
        combat.is_active = False
        
        # Get all participants for final state
        participants = self.db.query(CombatParticipant).filter(
            CombatParticipant.combat_encounter_id == combat_id
        ).all()
        
        # Clear temp HP and conditions
        for p in participants:
            p.temp_hp = 0
            p.conditions = []
            
            # Update party member if player
            if p.is_player and p.character_id:
                party_member = self.db.query(PartyMember).filter(
                    PartyMember.character_id == p.character_id
                ).first()
                
                if party_member:
                    party_member.temp_hp = 0
                    party_member.conditions = []
        
        self.db.commit()
        
        # Log combat end
        self._log_combat_action(
            combat_id=combat_id,
            attacker="System",
            target="",
            action="combat_end",
            details={
                'outcome': outcome,
                'rounds': combat.round_number,
                'survivors': [p.name for p in participants if p.current_hp > 0]
            }
        )
        
        return self.get_combat_state(combat_id)
    
    def get_combat_state(self, combat_id: int) -> CombatState:
        """
        Get current combat state
        
        Returns:
            - Turn order
            - Current turn
            - Round number
            - All participant HP/conditions
        
        Args:
            combat_id: ID of the combat encounter
        
        Returns:
            Current combat state
        """
        combat = self.db.query(CombatEncounter).get(combat_id)
        
        if not combat:
            raise ValueError(f"Combat {combat_id} not found")
        
        # Get all participants
        participants = self.db.query(CombatParticipant).filter(
            CombatParticipant.combat_encounter_id == combat_id
        ).order_by(CombatParticipant.initiative.desc()).all()
        
        participant_data = [
            {
                'id': p.id,
                'name': p.name,
                'initiative': p.initiative,
                'current_hp': p.current_hp,
                'max_hp': p.max_hp,
                'temp_hp': p.temp_hp,
                'ac': p.ac,
                'is_player': p.is_player,
                'conditions': p.conditions or [],
                'defeated': p.current_hp <= 0
            }
            for p in participants
        ]
        
        return CombatState(
            combat_id=combat.id,
            round_number=combat.round_number,
            current_turn=combat.current_turn,
            turn_order=combat.turn_order,
            is_active=combat.is_active,
            participants=participant_data
        )
    
    def _log_combat_action(
        self,
        combat_id: int,
        attacker: str,
        target: str,
        action: str,
        details: any
    ):
        """Log combat action to game events"""
        combat = self.db.query(CombatEncounter).get(combat_id)
        
        if combat:
            description = f"{attacker} → {target}: {action}"
            if isinstance(details, str):
                description += f" - {details}"
            
            self.session_mgr.log_event(
                game_session_id=combat.game_session_id,
                event_type=f"combat_{action}",
                description=description,
                state_snapshot={
                    'combat_id': combat_id,
                    'action': action,
                    'details': details if isinstance(details, dict) else str(details)
                },
                turn_number=combat.round_number
            )
