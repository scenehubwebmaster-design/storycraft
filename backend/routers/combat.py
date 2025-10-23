"""
Combat API Router

REST endpoints for D&D 5e combat system integration with AI DM.

Endpoints:
- POST /combat/encounters - Create new combat encounter
- GET /combat/encounters/{encounter_id} - Get encounter state
- POST /combat/encounters/{encounter_id}/combatants - Add combatant
- POST /combat/encounters/{encounter_id}/start - Start combat
- POST /combat/encounters/{encounter_id}/attack - Make attack
- POST /combat/encounters/{encounter_id}/save - Make saving throw
- POST /combat/encounters/{encounter_id}/area-damage - Apply area damage
- POST /combat/encounters/{encounter_id}/next-turn - Advance turn
- DELETE /combat/encounters/{encounter_id} - End encounter
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import asyncio

from ..database import get_db
from ..game.combat_manager import (
    combat_manager,
    Combatant,
    CombatantType,
    AdvantageType
)
from ..services.dnd_mcp_client import DndMcpClient

logger = logging.getLogger(__name__)
router = APIRouter()


# Request schemas
class CreateEncounterRequest(BaseModel):
    session_id: int
    encounter_name: Optional[str] = None


class AddCombatantRequest(BaseModel):
    combatant_id: str
    name: str
    type: str  # player, monster, npc
    max_hp: int
    current_hp: int
    ac: int
    dex_modifier: int = 0
    str_modifier: int = 0
    con_modifier: int = 0
    melee_attack_bonus: int = 0
    ranged_attack_bonus: int = 0
    spell_attack_bonus: int = 0
    spell_save_dc: int = 8
    cr: Optional[float] = None
    full_stats: Optional[Dict[str, Any]] = None


class AddPlayerFromCharacterRequest(BaseModel):
    character_id: int
    initiative_roll: Optional[int] = None


class AddMonsterRequest(BaseModel):
    monster_name: str
    count: int = 1
    initiative_rolls: Optional[List[int]] = None


class AttackRequest(BaseModel):
    attacker_id: str
    target_id: str
    attack_type: str = "melee"  # melee, ranged, spell
    advantage: Optional[str] = None  # advantage, disadvantage
    damage_dice: str = "1d8"
    damage_modifier: int = 0


class SavingThrowRequest(BaseModel):
    combatant_id: str
    dc: int
    ability: str  # str, dex, con, int, wis, cha
    advantage: Optional[str] = None


class AreaDamageRequest(BaseModel):
    target_ids: List[str]
    damage_dice: str
    damage_type: str
    save_dc: Optional[int] = None
    save_ability: str = "dex"
    half_on_save: bool = True


@router.post("/encounters")
async def create_encounter(request: CreateEncounterRequest):
    """
    Create a new combat encounter.
    
    Returns:
        encounter_id: Unique identifier for the encounter
    """
    try:
        encounter_id = f"combat_{request.session_id}_{int(asyncio.get_event_loop().time())}"
        combat_manager.create_encounter(encounter_id, request.session_id)
        
        return {
            "encounter_id": encounter_id,
            "session_id": request.session_id,
            "status": "preparing",
            "message": "Combat encounter created. Add combatants before starting."
        }
    except Exception as e:
        logger.error(f"Failed to create encounter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/encounters/{encounter_id}")
async def get_encounter(encounter_id: str):
    """Get the current state of a combat encounter."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    return encounter.get_state()


@router.post("/encounters/{encounter_id}/combatants")
async def add_combatant(encounter_id: str, request: AddCombatantRequest):
    """Add a combatant to the encounter."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    try:
        combatant_type = CombatantType[request.type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid combatant type: {request.type}")
    
    # Roll initiative if not provided
    from ..game.dice_roller import roll_initiative
    initiative = roll_initiative(request.dex_modifier)
    
    combatant = Combatant(
        id=request.combatant_id,
        name=request.name,
        type=combatant_type,
        max_hp=request.max_hp,
        current_hp=request.current_hp,
        ac=request.ac,
        initiative=initiative,
        dex_modifier=request.dex_modifier,
        str_modifier=request.str_modifier,
        con_modifier=request.con_modifier,
        melee_attack_bonus=request.melee_attack_bonus,
        ranged_attack_bonus=request.ranged_attack_bonus,
        spell_attack_bonus=request.spell_attack_bonus,
        spell_save_dc=request.spell_save_dc,
        cr=request.cr,
        full_stats=request.full_stats
    )
    
    encounter.add_combatant(combatant)
    
    return {
        "message": f"Added {combatant.name} with initiative {initiative}",
        "combatant": combatant.to_dict()
    }


@router.post("/encounters/{encounter_id}/players/{character_id}")
async def add_player_from_character(
    encounter_id: str,
    character_id: int,
    request: AddPlayerFromCharacterRequest,
    db: Session = Depends(get_db)
):
    """Add a player character from the database to the encounter."""
    from ..models import Character
    
    encounter = combat_manager.get_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    # Fetch character
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Parse D&D stats
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Character must be a D&D 5e character")
    
    # Use stored ability modifiers if available, otherwise calculate
    if character.dnd_ability_modifiers:
        ability_modifiers = character.dnd_ability_modifiers
        dex_mod = ability_modifiers.get("dexterity", 0)
        str_mod = ability_modifiers.get("strength", 0)
        con_mod = ability_modifiers.get("constitution", 0)
    else:
        # Fallback: calculate from ability scores
        ability_scores = character.dnd_ability_scores or {}
        dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
        str_mod = (ability_scores.get("strength", 10) - 10) // 2
        con_mod = (ability_scores.get("constitution", 10) - 10) // 2
    
    # Roll initiative
    from ..game.dice_roller import roll_initiative
    initiative = request.initiative_roll if request.initiative_roll else roll_initiative(dex_mod)
    
    # Use stored combat values with intelligent fallbacks
    max_hp = character.dnd_hit_points_max or character.dnd_hit_points or 10
    current_hp = character.dnd_hit_points_current or max_hp
    
    # Create combatant
    combatant = Combatant(
        id=f"player_{character_id}",
        name=character.name,
        type=CombatantType.PLAYER,
        max_hp=max_hp,
        current_hp=current_hp,
        ac=character.dnd_armor_class or 10,
        initiative=initiative,
        dex_modifier=dex_mod,
        str_modifier=str_mod,
        con_modifier=con_mod,
        # Use pre-calculated attack bonuses if available
        melee_attack_bonus=character.dnd_melee_attack_bonus if character.dnd_melee_attack_bonus is not None else str_mod + (2 + ((character.dnd_level or 1) - 1) // 4),
        ranged_attack_bonus=character.dnd_ranged_attack_bonus if character.dnd_ranged_attack_bonus is not None else dex_mod + (2 + ((character.dnd_level or 1) - 1) // 4),
        spell_attack_bonus=0,  # TODO: Calculate from spellcasting ability
        spell_save_dc=8 + (2 + ((character.dnd_level or 1) - 1) // 4),
        conditions=character.dnd_conditions or [],
        full_stats={
            "character_id": character_id,
            "class": character.dnd_class,
            "level": character.dnd_level or 1,
            "species": character.dnd_species,
            "ability_scores": character.dnd_ability_scores or {},
            "resources": character.dnd_resources or {},
            "temporary_hp": character.dnd_temporary_hp or 0,
            "death_saves": character.dnd_death_saves or {"successes": 0, "failures": 0}
        }
    )
    
    encounter.add_combatant(combatant)
    
    return {
        "message": f"Added player {character.name} with initiative {initiative}",
        "combatant": combatant.to_dict()
    }


@router.post("/encounters/{encounter_id}/monsters")
async def add_monsters(encounter_id: str, request: AddMonsterRequest):
    """
    Add monster(s) to the encounter by fetching from D&D MCP.
    
    Automatically rolls initiative for each monster.
    """
    encounter = combat_manager.get_encounter(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    # Fetch monster stats from MCP
    mcp_client = DndMcpClient()
    try:
        monster_data = await mcp_client.get_monster(request.monster_name)
        
        if not monster_data:
            raise HTTPException(
                status_code=404,
                detail=f"Monster '{request.monster_name}' not found in D&D database"
            )
        
        added_monsters = []
        
        for i in range(request.count):
            # Parse monster stats
            ac = monster_data.get("armor_class", 10)
            if isinstance(ac, list) and len(ac) > 0:
                ac = ac[0].get("value", 10)
            
            hp_data = monster_data.get("hit_points", {})
            if isinstance(hp_data, dict):
                max_hp = hp_data.get("max", 10)
            else:
                max_hp = hp_data or 10
            
            # Get ability modifiers
            dex = monster_data.get("dexterity", 10)
            str_val = monster_data.get("strength", 10)
            con = monster_data.get("constitution", 10)
            
            dex_mod = (dex - 10) // 2
            str_mod = (str_val - 10) // 2
            con_mod = (con - 10) // 2
            
            # Calculate proficiency bonus from CR
            cr = monster_data.get("challenge_rating", 0)
            if isinstance(cr, str):
                # Handle fractional CRs like "1/2", "1/4"
                if "/" in cr:
                    num, denom = cr.split("/")
                    cr = float(num) / float(denom)
                else:
                    cr = float(cr)
            
            prof_bonus = 2 if cr < 5 else (2 + ((int(cr) - 1) // 4))
            
            # Get attack bonus from actions
            melee_bonus = str_mod + prof_bonus
            ranged_bonus = dex_mod + prof_bonus
            
            # Roll initiative (or use provided)
            from ..game.dice_roller import roll_initiative
            if request.initiative_rolls and i < len(request.initiative_rolls):
                initiative = request.initiative_rolls[i]
            else:
                initiative = roll_initiative(dex_mod)
            
            # Create unique ID for multiple monsters
            monster_id = f"monster_{request.monster_name.lower().replace(' ', '_')}_{i+1}"
            monster_name = request.monster_name if request.count == 1 else f"{request.monster_name} {i+1}"
            
            combatant = Combatant(
                id=monster_id,
                name=monster_name,
                type=CombatantType.MONSTER,
                max_hp=max_hp,
                current_hp=max_hp,
                ac=ac,
                initiative=initiative,
                dex_modifier=dex_mod,
                str_modifier=str_mod,
                con_modifier=con_mod,
                melee_attack_bonus=melee_bonus,
                ranged_attack_bonus=ranged_bonus,
                cr=cr,
                full_stats=monster_data
            )
            
            encounter.add_combatant(combatant)
            added_monsters.append(combatant.to_dict())
        
        return {
            "message": f"Added {request.count} {request.monster_name}(s) to combat",
            "monsters": added_monsters
        }
        
    except Exception as e:
        logger.error(f"Failed to add monsters: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await mcp_client.close()


@router.post("/encounters/{encounter_id}/start")
async def start_combat(encounter_id: str):
    """Start the combat encounter."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    try:
        encounter.start_combat()
        
        return {
            "message": "Combat started!",
            "state": encounter.get_state()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/encounters/{encounter_id}/attack")
async def make_attack(encounter_id: str, request: AttackRequest):
    """Make an attack roll."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    # Parse advantage
    advantage = AdvantageType.NORMAL
    if request.advantage:
        advantage = AdvantageType[request.advantage.upper()]
    
    try:
        result = encounter.make_attack(
            attacker_id=request.attacker_id,
            target_id=request.target_id,
            attack_type=request.attack_type,
            advantage=advantage,
            damage_dice=request.damage_dice,
            damage_modifier=request.damage_modifier
        )
        
        return result
    except Exception as e:
        logger.error(f"Attack failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encounters/{encounter_id}/save")
async def make_saving_throw(encounter_id: str, request: SavingThrowRequest):
    """Make a saving throw."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    # Parse advantage
    advantage = AdvantageType.NORMAL
    if request.advantage:
        advantage = AdvantageType[request.advantage.upper()]
    
    try:
        result = encounter.make_saving_throw(
            combatant_id=request.combatant_id,
            dc=request.dc,
            ability=request.ability,
            advantage=advantage
        )
        
        return result
    except Exception as e:
        logger.error(f"Saving throw failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encounters/{encounter_id}/area-damage")
async def apply_area_damage(encounter_id: str, request: AreaDamageRequest):
    """Apply area-of-effect damage (e.g., Fireball)."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    try:
        result = encounter.apply_area_damage(
            target_ids=request.target_ids,
            damage_dice=request.damage_dice,
            damage_type=request.damage_type,
            save_dc=request.save_dc,
            save_ability=request.save_ability,
            half_on_save=request.half_on_save
        )
        
        return result
    except Exception as e:
        logger.error(f"Area damage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encounters/{encounter_id}/next-turn")
async def next_turn(encounter_id: str):
    """Advance to the next turn."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    encounter.next_turn()
    
    # Check if combat is over
    is_over, reason = encounter.is_combat_over()
    
    if is_over:
        combat_manager.end_encounter(encounter_id)
        return {
            "message": f"Combat ended: {reason}",
            "combat_over": True,
            "reason": reason,
            "final_state": encounter.get_state()
        }
    
    return {
        "message": "Turn advanced",
        "combat_over": False,
        "state": encounter.get_state()
    }


@router.delete("/encounters/{encounter_id}")
async def end_encounter(encounter_id: str):
    """End a combat encounter."""
    encounter = combat_manager.get_encounter(encounter_id)
    
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    final_state = encounter.get_state()
    combat_manager.end_encounter(encounter_id)
    
    return {
        "message": "Combat encounter ended",
        "final_state": final_state
    }


@router.get("/session/{session_id}/active-encounter")
async def get_session_encounter(session_id: int):
    """Get the active combat encounter for a session (if any)."""
    encounter = combat_manager.get_session_encounter(session_id)
    
    if not encounter:
        return {
            "active_encounter": False,
            "message": "No active combat encounter"
        }
    
    return {
        "active_encounter": True,
        "encounter_id": encounter.encounter_id,
        "state": encounter.get_state()
    }
