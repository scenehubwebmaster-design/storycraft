"""
D&D 5e Combat Manager

Manages combat encounters including:
- Initiative tracking
- Turn order
- Monster stat blocks
- Player character stats
- Attack and damage resolution
- Condition tracking
- Combat state persistence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from .dice_roller import (
    DiceRoller,
    AdvantageType
)

logger = logging.getLogger(__name__)


class CombatantType(Enum):
    """Type of combatant"""
    PLAYER = "player"
    MONSTER = "monster"
    NPC = "npc"


class CombatStatus(Enum):
    """Combat encounter status"""
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class Combatant:
    """Represents a combatant in combat"""
    id: str
    name: str
    type: CombatantType
    
    # Core stats
    max_hp: int
    current_hp: int
    ac: int
    initiative: int
    
    # Modifiers
    dex_modifier: int = 0
    str_modifier: int = 0
    con_modifier: int = 0
    
    # Attack bonuses
    melee_attack_bonus: int = 0
    ranged_attack_bonus: int = 0
    spell_attack_bonus: int = 0
    spell_save_dc: int = 8
    
    # Conditions
    conditions: List[str] = field(default_factory=list)
    
    # Monster-specific
    cr: Optional[float] = None
    
    # Turn tracking
    has_acted: bool = False
    
    # Full stat block (for monsters)
    full_stats: Optional[Dict[str, Any]] = None
    
    def is_alive(self) -> bool:
        """Check if combatant is alive"""
        return self.current_hp > 0
    
    def is_conscious(self) -> bool:
        """Check if combatant is conscious"""
        return self.current_hp > 0 and "unconscious" not in self.conditions
    
    def take_damage(self, amount: int) -> Tuple[int, bool]:
        """
        Apply damage to combatant.
        
        Returns:
            Tuple of (damage_dealt, is_alive)
        """
        actual_damage = min(amount, self.current_hp)
        self.current_hp -= actual_damage
        
        # Check for unconsciousness
        if self.current_hp <= 0:
            self.current_hp = 0
            if "unconscious" not in self.conditions:
                self.conditions.append("unconscious")
        
        return actual_damage, self.is_alive()
    
    def heal(self, amount: int) -> int:
        """
        Heal combatant.
        
        Returns:
            Actual HP healed
        """
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        
        # Remove unconscious if healed above 0
        if self.current_hp > 0 and "unconscious" in self.conditions:
            self.conditions.remove("unconscious")
        
        return self.current_hp - old_hp
    
    def add_condition(self, condition: str):
        """Add a condition"""
        condition_lower = condition.lower()
        if condition_lower not in self.conditions:
            self.conditions.append(condition_lower)
    
    def remove_condition(self, condition: str):
        """Remove a condition"""
        condition_lower = condition.lower()
        if condition_lower in self.conditions:
            self.conditions.remove(condition_lower)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CombatRound:
    """Tracks a single round of combat"""
    round_number: int
    actions: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_action(self, action: Dict[str, Any]):
        """Add an action to this round"""
        self.actions.append(action)


class CombatEncounter:
    """
    Manages a D&D 5e combat encounter.
    
    Features:
    - Initiative tracking and turn order
    - Combatant management
    - Attack resolution
    - Damage application
    - Condition tracking
    - Combat log
    """
    
    def __init__(self, encounter_id: str, session_id: int):
        """
        Initialize combat encounter.
        
        Args:
            encounter_id: Unique identifier for this encounter
            session_id: DM chat session ID
        """
        self.encounter_id = encounter_id
        self.session_id = session_id
        self.status = CombatStatus.PREPARING
        
        self.combatants: Dict[str, Combatant] = {}
        self.turn_order: List[str] = []
        self.current_turn_index: int = 0
        self.current_round: int = 0
        
        self.rounds: List[CombatRound] = []
        self.combat_log: List[str] = []
        
        self.dice_roller = DiceRoller()
    
    def add_combatant(self, combatant: Combatant):
        """Add a combatant to the encounter"""
        self.combatants[combatant.id] = combatant
        logger.info(f"Added combatant: {combatant.name} (Initiative: {combatant.initiative})")
    
    def remove_combatant(self, combatant_id: str):
        """Remove a combatant from the encounter"""
        if combatant_id in self.combatants:
            name = self.combatants[combatant_id].name
            del self.combatants[combatant_id]
            
            # Remove from turn order
            if combatant_id in self.turn_order:
                self.turn_order.remove(combatant_id)
            
            logger.info(f"Removed combatant: {name}")
    
    def sort_initiative(self):
        """Sort combatants by initiative (highest first)"""
        # Sort by initiative, then by DEX modifier if tied
        sorted_combatants = sorted(
            self.combatants.values(),
            key=lambda c: (c.initiative, c.dex_modifier),
            reverse=True
        )
        
        self.turn_order = [c.id for c in sorted_combatants]
        
        # Log initiative order
        order_str = ", ".join([
            f"{self.combatants[cid].name} ({self.combatants[cid].initiative})"
            for cid in self.turn_order
        ])
        self.log(f"Initiative order: {order_str}")
    
    def start_combat(self):
        """Start the combat encounter"""
        if not self.combatants:
            raise ValueError("Cannot start combat with no combatants")
        
        self.sort_initiative()
        self.status = CombatStatus.IN_PROGRESS
        self.current_round = 1
        self.current_turn_index = 0
        
        self.rounds.append(CombatRound(round_number=1))
        
        first_combatant = self.get_current_combatant()
        self.log("Combat started! Round 1 begins.")
        self.log(f"{first_combatant.name}'s turn.")
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it is"""
        if not self.turn_order or self.current_turn_index >= len(self.turn_order):
            return None
        
        combatant_id = self.turn_order[self.current_turn_index]
        return self.combatants.get(combatant_id)
    
    def next_turn(self):
        """Advance to the next turn"""
        current = self.get_current_combatant()
        if current:
            current.has_acted = True
        
        self.current_turn_index += 1
        
        # Check if round is over
        if self.current_turn_index >= len(self.turn_order):
            self.next_round()
        else:
            next_combatant = self.get_current_combatant()
            if next_combatant:
                self.log(f"{next_combatant.name}'s turn.")
    
    def next_round(self):
        """Advance to the next round"""
        self.current_round += 1
        self.current_turn_index = 0
        
        # Reset has_acted flags
        for combatant in self.combatants.values():
            combatant.has_acted = False
        
        # Create new round
        self.rounds.append(CombatRound(round_number=self.current_round))
        
        self.log(f"Round {self.current_round} begins!")
        
        first_combatant = self.get_current_combatant()
        if first_combatant:
            self.log(f"{first_combatant.name}'s turn.")
    
    def make_attack(
        self,
        attacker_id: str,
        target_id: str,
        attack_type: str = "melee",
        advantage: AdvantageType = AdvantageType.NORMAL,
        damage_dice: str = "1d8",
        damage_modifier: int = 0
    ) -> Dict[str, Any]:
        """
        Resolve an attack roll.
        
        Args:
            attacker_id: ID of attacking combatant
            target_id: ID of target combatant
            attack_type: Type of attack (melee, ranged, spell)
            advantage: Advantage type
            damage_dice: Damage dice notation
            damage_modifier: Damage modifier
            
        Returns:
            Dictionary with attack results
        """
        attacker = self.combatants.get(attacker_id)
        target = self.combatants.get(target_id)
        
        if not attacker or not target:
            raise ValueError("Invalid attacker or target")
        
        # Get attack bonus
        if attack_type == "melee":
            attack_bonus = attacker.melee_attack_bonus
        elif attack_type == "ranged":
            attack_bonus = attacker.ranged_attack_bonus
        else:  # spell
            attack_bonus = attacker.spell_attack_bonus
        
        # Roll attack
        attack_result = self.dice_roller.roll_attack(
            attack_bonus=attack_bonus,
            target_ac=target.ac,
            advantage=advantage
        )
        
        result = {
            "attacker": attacker.name,
            "target": target.name,
            "attack_type": attack_type,
            "hit": attack_result.hit,
            "critical": attack_result.critical,
            "attack_roll": attack_result.total,
            "natural_roll": attack_result.natural_roll,
            "target_ac": target.ac,
            "breakdown": attack_result.breakdown,
            "damage_dealt": 0
        }
        
        # If hit, roll damage
        if attack_result.hit:
            damage_notation = f"{damage_dice}{damage_modifier:+d}" if damage_modifier != 0 else damage_dice
            damage_result = self.dice_roller.roll_damage(
                notation=damage_notation,
                critical=attack_result.critical
            )
            
            actual_damage, still_alive = target.take_damage(damage_result.total)
            
            result["damage_dealt"] = actual_damage
            result["damage_breakdown"] = damage_result.breakdown
            result["target_hp_remaining"] = target.current_hp
            result["target_alive"] = still_alive
            
            # Log the attack
            self.log(
                f"{attacker.name} attacks {target.name}: {attack_result.breakdown}"
            )
            self.log(
                f"Damage: {damage_result.breakdown} - {target.name} has {target.current_hp}/{target.max_hp} HP remaining"
            )
            
            if not still_alive:
                self.log(f"{target.name} has fallen!")
        else:
            self.log(
                f"{attacker.name} attacks {target.name}: {attack_result.breakdown} - MISS!"
            )
        
        # Record action
        if self.rounds:
            self.rounds[-1].add_action({
                "type": "attack",
                "result": result
            })
        
        return result
    
    def make_saving_throw(
        self,
        combatant_id: str,
        dc: int,
        ability: str,
        advantage: AdvantageType = AdvantageType.NORMAL
    ) -> Dict[str, Any]:
        """
        Make a saving throw.
        
        Args:
            combatant_id: ID of combatant making save
            dc: Difficulty class
            ability: Ability type (str, dex, con, int, wis, cha)
            advantage: Advantage type
            
        Returns:
            Dictionary with save results
        """
        combatant = self.combatants.get(combatant_id)
        if not combatant:
            raise ValueError("Invalid combatant")
        
        # Get ability modifier
        ability_map = {
            "str": combatant.str_modifier,
            "dex": combatant.dex_modifier,
            "con": combatant.con_modifier,
            "int": 0,  # TODO: Add these to Combatant
            "wis": 0,
            "cha": 0
        }
        modifier = ability_map.get(ability.lower(), 0)
        
        # Roll saving throw
        save_result = self.dice_roller.roll_ability_check(
            modifier=modifier,
            dc=dc,
            advantage=advantage
        )
        
        result = {
            "combatant": combatant.name,
            "ability": ability.upper(),
            "dc": dc,
            "success": save_result.success,
            "total": save_result.total,
            "natural_roll": save_result.natural_roll,
            "breakdown": save_result.breakdown
        }
        
        self.log(
            f"{combatant.name} makes {ability.upper()} save: {save_result.breakdown}"
        )
        
        # Record action
        if self.rounds:
            self.rounds[-1].add_action({
                "type": "saving_throw",
                "result": result
            })
        
        return result
    
    def apply_area_damage(
        self,
        target_ids: List[str],
        damage_dice: str,
        damage_type: str,
        save_dc: Optional[int] = None,
        save_ability: str = "dex",
        half_on_save: bool = True
    ) -> Dict[str, Any]:
        """
        Apply area-of-effect damage (e.g., Fireball).
        
        Args:
            target_ids: IDs of targets in area
            damage_dice: Damage dice notation (e.g., "8d6")
            damage_type: Type of damage (fire, cold, etc.)
            save_dc: DC for saving throw (if applicable)
            save_ability: Ability for save
            half_on_save: Whether successful save halves damage
            
        Returns:
            Dictionary with results for each target
        """
        results = {
            "damage_type": damage_type,
            "damage_dice": damage_dice,
            "save_dc": save_dc,
            "save_ability": save_ability.upper() if save_dc else None,
            "targets": []
        }
        
        # Roll damage once
        damage_result = self.dice_roller.roll_damage(damage_dice)
        base_damage = damage_result.total
        
        self.log(
            f"Area damage ({damage_type}): {damage_result.breakdown}"
        )
        
        # Apply to each target
        for target_id in target_ids:
            target = self.combatants.get(target_id)
            if not target:
                continue
            
            target_result = {
                "name": target.name,
                "damage_dealt": 0,
                "hp_remaining": target.current_hp,
                "alive": True
            }
            
            # Make saving throw if applicable
            if save_dc:
                save_result = self.make_saving_throw(
                    combatant_id=target_id,
                    dc=save_dc,
                    ability=save_ability,
                    advantage=AdvantageType.NORMAL
                )
                
                target_result["save_result"] = save_result
                
                # Calculate damage based on save
                if save_result["success"] and half_on_save:
                    actual_damage = base_damage // 2
                    target_result["saved"] = True
                else:
                    actual_damage = base_damage
                    target_result["saved"] = False
            else:
                actual_damage = base_damage
            
            # Apply damage
            damage_dealt, still_alive = target.take_damage(actual_damage)
            target_result["damage_dealt"] = damage_dealt
            target_result["hp_remaining"] = target.current_hp
            target_result["alive"] = still_alive
            
            self.log(
                f"{target.name} takes {damage_dealt} {damage_type} damage - "
                f"{target.current_hp}/{target.max_hp} HP remaining"
            )
            
            if not still_alive:
                self.log(f"{target.name} has fallen!")
            
            results["targets"].append(target_result)
        
        # Record action
        if self.rounds:
            self.rounds[-1].add_action({
                "type": "area_damage",
                "result": results
            })
        
        return results
    
    def log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        logger.info(f"[Combat {self.encounter_id}] {message}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current combat state"""
        return {
            "encounter_id": self.encounter_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "current_round": self.current_round,
            "current_turn_index": self.current_turn_index,
            "current_combatant": self.get_current_combatant().name if self.get_current_combatant() else None,
            "combatants": {
                cid: c.to_dict() for cid, c in self.combatants.items()
            },
            "turn_order": self.turn_order,
            "combat_log": self.combat_log[-20:],  # Last 20 messages
        }
    
    def is_combat_over(self) -> Tuple[bool, Optional[str]]:
        """
        Check if combat is over.
        
        Returns:
            Tuple of (is_over, reason)
        """
        alive_players = [
            c for c in self.combatants.values()
            if c.type == CombatantType.PLAYER and c.is_alive()
        ]
        alive_monsters = [
            c for c in self.combatants.values()
            if c.type == CombatantType.MONSTER and c.is_alive()
        ]
        
        if not alive_players:
            return True, "All players defeated"
        
        if not alive_monsters:
            return True, "All monsters defeated"
        
        return False, None


class CombatManager:
    """
    Global combat encounter manager.
    
    Manages multiple concurrent combat encounters across different sessions.
    """
    
    def __init__(self):
        self.encounters: Dict[str, CombatEncounter] = {}
    
    def create_encounter(self, encounter_id: str, session_id: int) -> CombatEncounter:
        """Create a new combat encounter"""
        encounter = CombatEncounter(encounter_id, session_id)
        self.encounters[encounter_id] = encounter
        logger.info(f"Created combat encounter: {encounter_id} for session {session_id}")
        return encounter
    
    def get_encounter(self, encounter_id: str) -> Optional[CombatEncounter]:
        """Get an existing encounter"""
        return self.encounters.get(encounter_id)
    
    def end_encounter(self, encounter_id: str):
        """End and remove an encounter"""
        if encounter_id in self.encounters:
            self.encounters[encounter_id].status = CombatStatus.COMPLETED
            del self.encounters[encounter_id]
            logger.info(f"Ended combat encounter: {encounter_id}")
    
    def get_session_encounter(self, session_id: int) -> Optional[CombatEncounter]:
        """Get the active encounter for a session"""
        for encounter in self.encounters.values():
            if encounter.session_id == session_id and encounter.status == CombatStatus.IN_PROGRESS:
                return encounter
        return None


# Global combat manager instance
combat_manager = CombatManager()
