"""
D&D 5e Dice Rolling System

Handles all dice mechanics including:
- Standard notation parsing (2d6+3, 1d20, etc.)
- Advantage/disadvantage
- Attack rolls with critical hit detection
- Damage rolls with critical damage
- Ability checks vs DC
"""

import re
import random
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class AdvantageType(Enum):
    """Type of advantage for d20 rolls"""
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


@dataclass
class DiceResult:
    """Result of a dice roll"""
    total: int
    rolls: List[int]
    modifier: int
    notation: str
    breakdown: str
    advantage_type: Optional[AdvantageType] = None
    dropped_rolls: Optional[List[int]] = None


@dataclass
class AttackResult:
    """Result of an attack roll"""
    hit: bool
    critical: bool
    natural_roll: int
    total: int
    target_ac: int
    breakdown: str
    advantage_type: AdvantageType


@dataclass
class DamageResult:
    """Result of a damage roll"""
    total: int
    rolls: List[int]
    modifier: int
    critical: bool
    breakdown: str


@dataclass
class CheckResult:
    """Result of an ability check"""
    success: bool
    total: int
    dc: int
    natural_roll: int
    modifier: int
    breakdown: str
    critical_success: bool = False
    critical_failure: bool = False


class DiceRoller:
    """
    D&D 5e compliant dice roller
    
    Supports:
    - d4, d6, d8, d10, d12, d20, d100
    - Notation: XdY+Z or XdY-Z
    - Advantage/disadvantage on d20 rolls
    - Critical hit detection (natural 20)
    - Critical miss detection (natural 1)
    """
    
    VALID_DICE = {4, 6, 8, 10, 12, 20, 100}
    DICE_PATTERN = re.compile(r'^(\d+)d(\d+)([+-]\d+)?$', re.IGNORECASE)
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize dice roller
        
        Args:
            seed: Optional random seed for deterministic testing
        """
        if seed is not None:
            random.seed(seed)
    
    def roll(self, notation: str, advantage: Optional[AdvantageType] = None) -> DiceResult:
        """
        Roll dice using D&D notation
        
        Args:
            notation: Dice notation (e.g., "2d6+3", "1d20", "4d8-2")
            advantage: Optional advantage type for d20 rolls
        
        Returns:
            DiceResult with total, individual rolls, and breakdown
        
        Raises:
            ValueError: If notation is invalid or dice type not supported
        
        Examples:
            >>> roller.roll("2d6+3")
            DiceResult(total=11, rolls=[4, 4], modifier=3, ...)
            
            >>> roller.roll("1d20", advantage=AdvantageType.ADVANTAGE)
            DiceResult(total=18, rolls=[18], dropped_rolls=[12], ...)
        """
        # Parse notation
        count, die_type, modifier = self._parse_notation(notation)
        
        # Validate dice type
        if die_type not in self.VALID_DICE:
            raise ValueError(
                f"Invalid dice type: d{die_type}. "
                f"Valid types: {sorted(self.VALID_DICE)}"
            )
        
        # Handle advantage/disadvantage for d20
        dropped_rolls = None
        if advantage and die_type == 20 and count == 1:
            rolls, dropped_rolls = self._roll_with_advantage(die_type, advantage)
        else:
            rolls = [random.randint(1, die_type) for _ in range(count)]
        
        # Calculate total
        total = sum(rolls) + modifier
        
        # Build breakdown string
        breakdown = self._build_breakdown(rolls, modifier, dropped_rolls, advantage)
        
        return DiceResult(
            total=total,
            rolls=rolls,
            modifier=modifier,
            notation=notation,
            breakdown=breakdown,
            advantage_type=advantage,
            dropped_rolls=dropped_rolls
        )
    
    def roll_with_advantage(self, notation: str = "1d20") -> DiceResult:
        """
        Roll with advantage (2d20, take higher)
        
        Args:
            notation: Dice notation (default: "1d20")
        
        Returns:
            DiceResult with advantage details
        """
        return self.roll(notation, advantage=AdvantageType.ADVANTAGE)
    
    def roll_with_disadvantage(self, notation: str = "1d20") -> DiceResult:
        """
        Roll with disadvantage (2d20, take lower)
        
        Args:
            notation: Dice notation (default: "1d20")
        
        Returns:
            DiceResult with disadvantage details
        """
        return self.roll(notation, advantage=AdvantageType.DISADVANTAGE)
    
    def roll_attack(
        self,
        attack_bonus: int,
        target_ac: int,
        advantage: AdvantageType = AdvantageType.NORMAL
    ) -> AttackResult:
        """
        Roll an attack vs target AC
        
        Args:
            attack_bonus: Attack modifier (proficiency + ability)
            target_ac: Target's armor class
            advantage: Advantage type
        
        Returns:
            AttackResult with hit/miss, critical status
        
        Examples:
            >>> roller.roll_attack(attack_bonus=5, target_ac=15)
            AttackResult(hit=True, critical=False, total=18, ...)
        """
        # Roll d20
        dice_result = self.roll("1d20", advantage=advantage)
        natural_roll = dice_result.rolls[0]
        
        # Calculate total
        total = natural_roll + attack_bonus
        
        # Check for critical hit/miss
        critical = (natural_roll == 20)
        critical_miss = (natural_roll == 1)
        
        # Determine hit (critical always hits, critical miss always misses)
        if critical:
            hit = True
        elif critical_miss:
            hit = False
        else:
            hit = total >= target_ac
        
        # Build breakdown
        breakdown_parts = [f"1d20 ({natural_roll})"]
        if dice_result.dropped_rolls:
            breakdown_parts.append(f"dropped ({dice_result.dropped_rolls[0]})")
        if attack_bonus != 0:
            breakdown_parts.append(f"{attack_bonus:+d}")
        breakdown_parts.append(f"= {total}")
        breakdown_parts.append(f"vs AC {target_ac}")
        
        if critical:
            breakdown_parts.append("CRITICAL HIT!")
        elif critical_miss:
            breakdown_parts.append("CRITICAL MISS!")
        
        breakdown = " ".join(breakdown_parts)
        
        return AttackResult(
            hit=hit,
            critical=critical,
            natural_roll=natural_roll,
            total=total,
            target_ac=target_ac,
            breakdown=breakdown,
            advantage_type=advantage
        )
    
    def roll_damage(self, notation: str, critical: bool = False) -> DamageResult:
        """
        Roll damage dice
        
        Args:
            notation: Damage notation (e.g., "1d8+3", "2d6")
            critical: If True, double the dice (not the modifier)
        
        Returns:
            DamageResult with total damage and breakdown
        
        Examples:
            >>> roller.roll_damage("1d8+3", critical=True)
            DamageResult(total=14, rolls=[5, 6], modifier=3, critical=True, ...)
        """
        # Parse notation
        count, die_type, modifier = self._parse_notation(notation)
        
        # Double dice on critical
        if critical:
            count *= 2
        
        # Roll damage
        rolls = [random.randint(1, die_type) for _ in range(count)]
        total = sum(rolls) + modifier
        
        # Build breakdown
        roll_str = " + ".join(str(r) for r in rolls)
        if modifier != 0:
            breakdown = f"{roll_str} {modifier:+d} = {total}"
        else:
            breakdown = f"{roll_str} = {total}"
        
        if critical:
            breakdown = f"CRITICAL! {breakdown}"
        
        return DamageResult(
            total=total,
            rolls=rolls,
            modifier=modifier,
            critical=critical,
            breakdown=breakdown
        )
    
    def roll_ability_check(
        self,
        modifier: int,
        dc: int,
        advantage: AdvantageType = AdvantageType.NORMAL
    ) -> CheckResult:
        """
        Roll an ability check vs DC
        
        Args:
            modifier: Ability modifier + proficiency (if applicable)
            dc: Difficulty class
            advantage: Advantage type
        
        Returns:
            CheckResult with success/failure
        
        Examples:
            >>> roller.roll_ability_check(modifier=3, dc=15)
            CheckResult(success=True, total=16, dc=15, ...)
        """
        # Roll d20
        dice_result = self.roll("1d20", advantage=advantage)
        natural_roll = dice_result.rolls[0]
        
        # Calculate total
        total = natural_roll + modifier
        
        # Check success
        success = total >= dc
        
        # D&D 5e: Natural 20 on skill checks doesn't auto-succeed (house rule varies)
        # Natural 1 doesn't auto-fail either
        critical_success = (natural_roll == 20)
        critical_failure = (natural_roll == 1)
        
        # Build breakdown
        breakdown_parts = [f"1d20 ({natural_roll})"]
        if dice_result.dropped_rolls:
            adv_type = "advantage" if advantage == AdvantageType.ADVANTAGE else "disadvantage"
            breakdown_parts.append(f"[{adv_type}, dropped {dice_result.dropped_rolls[0]}]")
        if modifier != 0:
            breakdown_parts.append(f"{modifier:+d}")
        breakdown_parts.append(f"= {total}")
        breakdown_parts.append(f"vs DC {dc}")
        breakdown_parts.append("SUCCESS!" if success else "FAILURE")
        
        breakdown = " ".join(breakdown_parts)
        
        return CheckResult(
            success=success,
            total=total,
            dc=dc,
            natural_roll=natural_roll,
            modifier=modifier,
            breakdown=breakdown,
            critical_success=critical_success,
            critical_failure=critical_failure
        )
    
    def _parse_notation(self, notation: str) -> Tuple[int, int, int]:
        """
        Parse dice notation into components
        
        Args:
            notation: Dice notation string
        
        Returns:
            Tuple of (count, die_type, modifier)
        
        Raises:
            ValueError: If notation is invalid
        """
        notation = notation.strip().lower()
        match = self.DICE_PATTERN.match(notation)
        
        if not match:
            raise ValueError(
                f"Invalid dice notation: '{notation}'. "
                "Expected format: XdY or XdY+Z or XdY-Z (e.g., '2d6+3')"
            )
        
        count = int(match.group(1))
        die_type = int(match.group(2))
        modifier_str = match.group(3)
        modifier = int(modifier_str) if modifier_str else 0
        
        if count < 1:
            raise ValueError(f"Dice count must be at least 1, got {count}")
        
        if count > 100:
            raise ValueError(f"Dice count too high: {count} (max 100)")
        
        return count, die_type, modifier
    
    def _roll_with_advantage(
        self,
        die_type: int,
        advantage: AdvantageType
    ) -> Tuple[List[int], List[int]]:
        """
        Roll with advantage or disadvantage
        
        Args:
            die_type: Type of die to roll
            advantage: Advantage type
        
        Returns:
            Tuple of (kept_rolls, dropped_rolls)
        """
        # Roll twice
        roll1 = random.randint(1, die_type)
        roll2 = random.randint(1, die_type)
        
        # Determine which to keep
        if advantage == AdvantageType.ADVANTAGE:
            if roll1 >= roll2:
                return [roll1], [roll2]
            else:
                return [roll2], [roll1]
        else:  # DISADVANTAGE
            if roll1 <= roll2:
                return [roll1], [roll2]
            else:
                return [roll2], [roll1]
    
    def _build_breakdown(
        self,
        rolls: List[int],
        modifier: int,
        dropped_rolls: Optional[List[int]],
        advantage: Optional[AdvantageType]
    ) -> str:
        """Build human-readable breakdown string"""
        parts = []
        
        # Show rolls
        roll_str = " + ".join(str(r) for r in rolls)
        parts.append(roll_str)
        
        # Show dropped rolls if advantage/disadvantage
        if dropped_rolls:
            adv_str = "advantage" if advantage == AdvantageType.ADVANTAGE else "disadvantage"
            parts.append(f"[{adv_str}, dropped {dropped_rolls[0]}]")
        
        # Show modifier
        if modifier != 0:
            parts.append(f"{modifier:+d}")
        
        # Show total
        total = sum(rolls) + modifier
        parts.append(f"= {total}")
        
        return " ".join(parts)


# Convenience functions for common rolls
def roll_d20(advantage: AdvantageType = AdvantageType.NORMAL) -> DiceResult:
    """Quick d20 roll"""
    return DiceRoller().roll("1d20", advantage=advantage)


def roll_initiative(dex_modifier: int) -> int:
    """Roll initiative (d20 + DEX modifier)"""
    result = DiceRoller().roll(f"1d20{dex_modifier:+d}")
    return result.total


def roll_saving_throw(
    modifier: int,
    dc: int,
    advantage: AdvantageType = AdvantageType.NORMAL
) -> CheckResult:
    """Roll a saving throw"""
    return DiceRoller().roll_ability_check(modifier, dc, advantage)
