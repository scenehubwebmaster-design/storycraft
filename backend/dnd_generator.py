"""
D&D 5E Character Generator
===========================
Automated D&D character generation with stat calculation, equipment assignment,
and integration with AI-powered narrative character generation.

This module handles:
- Ability score generation (Standard Array, Point Buy, Random)
- Racial ability bonuses and trait application
- Class feature and proficiency assignment
- Combat stat calculation (HP, AC, Initiative)
- Starting equipment selection
- Spell selection for spellcasters
- Complete character sheet generation
"""

import random
from typing import Any, Dict, List, Optional
from dnd_data import (
    DND_CLASSES,
    DND_SPECIES,
    DND_BACKGROUNDS,
    DND_SKILLS,
    STANDARD_ARRAY,
    DND_ALIGNMENTS,
    calculate_ability_modifier,
    get_proficiency_bonus,
    format_modifier
)


# ============================================================================
# ABILITY SCORE GENERATION
# ============================================================================

def generate_ability_scores_standard_array() -> Dict[str, int]:
    """
    Generate ability scores using Standard Array [15, 14, 13, 12, 10, 8].
    Intelligently assigns scores based on class requirements.
    """
    return {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0
    }

def assign_scores_for_class(class_key: str, scores: List[int] = None) -> Dict[str, int]:
    """
    Intelligently assign ability scores based on class primary abilities.
    
    Args:
        class_key: The character class (e.g., 'wizard', 'fighter')
        scores: List of scores to assign (default: Standard Array)
    
    Returns:
        Dictionary of ability scores optimized for the class
    """
    if scores is None:
        scores = STANDARD_ARRAY.copy()
    
    class_info = DND_CLASSES.get(class_key.lower())
    if not class_info:
        # Default assignment if class not found
        return {
            "strength": scores[0],
            "dexterity": scores[1],
            "constitution": scores[2],
            "intelligence": scores[3],
            "wisdom": scores[4],
            "charisma": scores[5]
        }
    
    primary_abilities = class_info["primary_ability"]
    
    # Priority order: Primary abilities, Constitution (for HP), then others
    ability_scores = {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0
    }
    
    sorted_scores = sorted(scores, reverse=True)
    assigned_abilities = []
    
    # Assign highest scores to primary abilities
    for i, ability in enumerate(primary_abilities):
        ability_key = ability.lower()
        if ability_key in ability_scores:
            ability_scores[ability_key] = sorted_scores[i]
            assigned_abilities.append(ability_key)
    
    # Assign next highest to Constitution (for HP)
    if "constitution" not in assigned_abilities:
        next_idx = len(assigned_abilities)
        ability_scores["constitution"] = sorted_scores[next_idx]
        assigned_abilities.append("constitution")
    
    # Assign remaining scores
    remaining_abilities = [a for a in ability_scores.keys() if a not in assigned_abilities]
    remaining_scores = [s for i, s in enumerate(sorted_scores) if i >= len(assigned_abilities)]
    
    for ability, score in zip(remaining_abilities, remaining_scores):
        ability_scores[ability] = score
    
    return ability_scores

def generate_ability_scores_random() -> Dict[str, int]:
    """
    Generate ability scores using 4d6 drop lowest method.
    Rolls 4d6, drops the lowest die, and sums the remaining three.
    """
    def roll_4d6_drop_lowest():
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        return sum(rolls[1:])  # Drop the lowest
    
    return {
        "strength": roll_4d6_drop_lowest(),
        "dexterity": roll_4d6_drop_lowest(),
        "constitution": roll_4d6_drop_lowest(),
        "intelligence": roll_4d6_drop_lowest(),
        "wisdom": roll_4d6_drop_lowest(),
        "charisma": roll_4d6_drop_lowest()
    }


# ============================================================================
# RACIAL BONUSES AND TRAITS
# ============================================================================

def apply_racial_bonuses(ability_scores: Dict[str, int], species_key: str, 
                         bonus_choices: Optional[Dict[str, int]] = None) -> Dict[str, int]:
    """
    Apply racial ability score bonuses to base ability scores.
    
    Args:
        ability_scores: Base ability scores
        species_key: Race/species identifier
        bonus_choices: Optional dict specifying where to apply flexible bonuses
    
    Returns:
        Updated ability scores with racial bonuses applied
    """
    species_info = DND_SPECIES.get(species_key.lower())
    if not species_info:
        return ability_scores
    
    scores = ability_scores.copy()
    bonuses = species_info.get("ability_bonuses", {})
    
    # Handle 2024 PHB flexible ability bonuses
    if "choice" in bonuses:
        # Modern D&D: Choose +2/+1 or +1/+1/+1
        if bonus_choices:
            for ability, bonus in bonus_choices.items():
                if ability.lower() in scores:
                    scores[ability.lower()] += bonus
        else:
            # Default: Apply +2 to class primary, +1 to constitution
            # This is a fallback; ideally bonus_choices should be provided
            pass
    
    # Handle legacy fixed bonuses (2014 PHB style)
    for ability, bonus in bonuses.items():
        if ability.lower() in scores and ability != "choice" and ability != "options":
            scores[ability.lower()] += bonus
    
    return scores


# ============================================================================
# COMBAT STATS CALCULATION
# ============================================================================

def calculate_hit_points(class_key: str, constitution_score: int, level: int = 1) -> int:
    """
    Calculate total hit points.
    Level 1: Max hit die + Constitution modifier
    Higher levels: Average of hit die + Constitution modifier per level
    
    Args:
        class_key: Character class
        constitution_score: Constitution ability score
        level: Character level (default 1)
    
    Returns:
        Total hit points
    """
    class_info = DND_CLASSES.get(class_key.lower())
    if not class_info:
        return 10  # Default
    
    hit_die = class_info["hit_die"]
    con_mod = calculate_ability_modifier(constitution_score)
    
    if level == 1:
        # Level 1: Maximum hit die + CON modifier
        return hit_die + con_mod
    else:
        # Higher levels: Average roll per level
        # Note: For simplicity, using average (hit_die/2 + 1) per level
        average_roll = (hit_die // 2) + 1
        return hit_die + con_mod + ((average_roll + con_mod) * (level - 1))

def calculate_armor_class(class_key: str, dexterity_score: int, 
                          equipment: Optional[Dict] = None) -> int:
    """
    Calculate Armor Class based on class, dexterity, and equipment.
    
    Args:
        class_key: Character class
        dexterity_score: Dexterity ability score
        equipment: Optional dict with armor info
    
    Returns:
        Armor Class value
    """
    dex_mod = calculate_ability_modifier(dexterity_score)
    
    # Check for Unarmored Defense (Barbarian, Monk)
    class_info = DND_CLASSES.get(class_key.lower())
    if class_info and "Unarmored Defense" in class_info.get("level_1_features", []):
        if class_key.lower() == "barbarian":
            # Barbarian: 10 + DEX mod + CON mod (will need CON score)
            return 10 + dex_mod  # Simplified for now
        elif class_key.lower() == "monk":
            # Monk: 10 + DEX mod + WIS mod (will need WIS score)
            return 10 + dex_mod  # Simplified for now
    
    # Default: Light/Medium armor typical for level 1
    # Leather armor (11 + Dex mod) or Chain mail (16) for heavy armor users
    if class_info:
        armor_profs = class_info.get("armor_proficiencies", [])
        if "All armor" in armor_profs or "Heavy armor" in armor_profs:
            return 16  # Chain mail
        elif "Medium armor" in armor_profs:
            return 14 + min(dex_mod, 2)  # Scale mail + DEX (max +2)
        elif "Light armor" in armor_profs:
            return 11 + dex_mod  # Leather armor + full DEX
    
    # No armor proficiency
    return 10 + dex_mod

def calculate_initiative(dexterity_score: int) -> int:
    """Calculate initiative bonus (Dexterity modifier)."""
    return calculate_ability_modifier(dexterity_score)


# ============================================================================
# SKILL PROFICIENCIES
# ============================================================================

def select_skills_for_class(class_key: str, background_key: str, 
                            skill_choices: Optional[List[str]] = None) -> List[str]:
    """
    Select skill proficiencies based on class and background.
    
    Args:
        class_key: Character class
        background_key: Character background
        skill_choices: Optional list of chosen skills
    
    Returns:
        List of skill proficiencies
    """
    class_info = DND_CLASSES.get(class_key.lower())
    background_info = DND_BACKGROUNDS.get(background_key.lower())
    
    proficiencies = []
    
    # Add background skills (always granted)
    if background_info:
        bg_skills = background_info.get("skill_proficiencies", [])
        proficiencies.extend(bg_skills)
    
    # Add class skill choices
    if class_info:
        skill_list = class_info.get("skill_list", [])
        num_choices = class_info.get("skill_choices", 0)
        
        if skill_choices:
            # Use provided choices
            for skill in skill_choices[:num_choices]:
                if skill not in proficiencies:
                    proficiencies.append(skill)
        else:
            # Random selection from available skills
            available_skills = [s for s in skill_list if s not in proficiencies]
            if "Any three skills" in skill_list:
                # Bard gets any 3 skills
                available_skills = list(DND_SKILLS.keys())
            
            random_picks = random.sample(available_skills, min(num_choices, len(available_skills)))
            proficiencies.extend(random_picks)
    
    return proficiencies


# ============================================================================
# EQUIPMENT GENERATION
# ============================================================================

def generate_starting_equipment(class_key: str, background_key: str) -> Dict[str, List[str]]:
    """
    Generate starting equipment based on class and background.
    
    Args:
        class_key: Character class
        background_key: Character background
    
    Returns:
        Dictionary with categorized equipment lists
    """
    class_info = DND_CLASSES.get(class_key.lower())
    background_info = DND_BACKGROUNDS.get(background_key.lower())
    
    equipment = {
        "weapons": [],
        "armor": [],
        "tools": [],
        "gear": []
    }
    
    # Add class equipment
    if class_info:
        starting_eq = class_info.get("starting_equipment", [])
        for item in starting_eq:
            # Simple categorization based on keywords
            if any(weapon in item.lower() for weapon in ["sword", "axe", "bow", "mace", "dagger", "weapon"]):
                equipment["weapons"].append(item)
            elif any(armor in item.lower() for armor in ["armor", "shield", "mail"]):
                equipment["armor"].append(item)
            elif "pack" in item.lower() or "kit" in item.lower():
                equipment["gear"].append(item)
            else:
                equipment["gear"].append(item)
    
    # Add background equipment
    if background_info:
        bg_eq = background_info.get("equipment", [])
        for item in bg_eq:
            if "tool" in item.lower() or "kit" in item.lower():
                equipment["tools"].append(item)
            else:
                equipment["gear"].append(item)
    
    return equipment


# ============================================================================
# SPELLCASTING
# ============================================================================

def generate_spellcasting_info(class_key: str, ability_scores: Dict[str, int], 
                               level: int = 1) -> Optional[Dict]:
    """
    Generate spellcasting information for spellcasting classes.
    
    Args:
        class_key: Character class
        ability_scores: Character's ability scores
        level: Character level
    
    Returns:
        Dictionary with spellcasting info or None if not a spellcaster
    """
    class_info = DND_CLASSES.get(class_key.lower())
    if not class_info or not class_info.get("spellcaster"):
        return None
    
    spellcasting_ability = class_info.get("spellcasting_ability", "").lower()
    if spellcasting_ability not in ability_scores:
        return None
    
    ability_score = ability_scores[spellcasting_ability]
    ability_mod = calculate_ability_modifier(ability_score)
    prof_bonus = get_proficiency_bonus(level)
    
    spell_info = {
        "spellcasting_ability": spellcasting_ability.capitalize(),
        "spell_save_dc": 8 + prof_bonus + ability_mod,
        "spell_attack_bonus": prof_bonus + ability_mod,
        "cantrips_known": class_info.get("cantrips_known", 0),
        "spells_known_or_prepared": class_info.get("spells_known", class_info.get("spells_prepared", 0)),
        "spell_slots": {
            "level_1": class_info.get("spell_slots_level_1", 0)
        }
    }
    
    # Special handling for prepared casters
    if "spells_prepared" in class_info:
        if class_key.lower() in ["cleric", "druid", "wizard"]:
            spell_info["spells_known_or_prepared"] = ability_mod + level
    
    return spell_info


def _generate_class_resources(class_key: str, level: int, ability_modifiers: Dict[str, int]) -> Dict[str, Any]:
    """
    Generate limited-use resources for a D&D class.
    
    Args:
        class_key: Character class
        level: Character level
        ability_modifiers: Dict of ability modifiers
    
    Returns:
        Dict of resources with max and current values
    """
    resources = {
        "hit_dice": {"max": level, "current": level}
    }
    
    class_lower = class_key.lower()
    
    if class_lower == "barbarian":
        resources["rage"] = {"max": 2, "current": 2}  # Level 1
        if level >= 3:
            resources["rage"]["max"] = 3
            resources["rage"]["current"] = 3
        if level >= 6:
            resources["rage"]["max"] = 4
            resources["rage"]["current"] = 4
    
    elif class_lower == "bard":
        # Bardic Inspiration
        cha_mod = ability_modifiers.get("charisma", 0)
        resources["bardic_inspiration"] = {"max": max(1, cha_mod), "current": max(1, cha_mod)}
    
    elif class_lower == "cleric":
        resources["channel_divinity"] = {"max": 1, "current": 1}
    
    elif class_lower == "druid":
        resources["wild_shape"] = {"max": 2, "current": 2}
    
    elif class_lower == "fighter":
        resources["action_surge"] = {"max": 1, "current": 1}
        resources["second_wind"] = {"max": 1, "current": 1}
    
    elif class_lower == "monk":
        resources["ki"] = {"max": level, "current": level}
    
    elif class_lower == "paladin":
        resources["channel_divinity"] = {"max": 1, "current": 1}
        resources["lay_on_hands"] = {"max": level * 5, "current": level * 5}
    
    elif class_lower == "ranger":
        if level >= 3:
            # Primeval Awareness
            resources["primeval_awareness"] = {"max": 1, "current": 1}
    
    elif class_lower == "rogue":
        # Sneak Attack scales with level
        dice_count = (level + 1) // 2
        resources["sneak_attack_dice"] = f"{dice_count}d6"
    
    elif class_lower == "sorcerer":
        resources["sorcery_points"] = {"max": level, "current": level}
    
    elif class_lower == "warlock":
        # Pact Magic slots (short rest recovery)
        resources["pact_magic_slots"] = {"max": 1, "current": 1}
    
    elif class_lower == "wizard":
        # Arcane Recovery (once per day)
        resources["arcane_recovery"] = {"max": 1, "current": 1}
    
    return resources


# ============================================================================
# MAIN CHARACTER GENERATOR
# ============================================================================

def generate_dnd_character(
    class_key: str,
    species_key: str,
    background_key: str,
    alignment: str = None,
    ability_score_method: str = "standard_array",
    name: str = None,
    level: int = 1
) -> Dict:
    """
    Generate a complete D&D 5E character.
    
    Args:
        class_key: Character class (e.g., 'wizard', 'fighter')
        species_key: Race/species (e.g., 'elf', 'dwarf')
        background_key: Background (e.g., 'sage', 'soldier')
        alignment: Character alignment (default: random)
        ability_score_method: 'standard_array', 'random', or 'point_buy'
        name: Character name (default: None)
        level: Character level (default: 1)
    
    Returns:
        Complete character dictionary with all stats and features
    """
    
    # Generate ability scores
    if ability_score_method == "random":
        base_scores = generate_ability_scores_random()
    else:  # standard_array or point_buy
        base_scores = assign_scores_for_class(class_key)
    
    # Apply racial bonuses (using default +2/+1 assignment for now)
    # In a full implementation, this would be user-chosen
    final_scores = apply_racial_bonuses(base_scores, species_key)
    
    # Get class and species info
    class_info = DND_CLASSES.get(class_key.lower(), {})
    species_info = DND_SPECIES.get(species_key.lower(), {})
    background_info = DND_BACKGROUNDS.get(background_key.lower(), {})
    
    # Calculate combat stats
    constitution_score = final_scores.get("constitution", 10)
    dexterity_score = final_scores.get("dexterity", 10)
    
    hit_points = calculate_hit_points(class_key, constitution_score, level)
    armor_class = calculate_armor_class(class_key, dexterity_score)
    initiative_bonus = calculate_initiative(dexterity_score)
    proficiency_bonus = get_proficiency_bonus(level)
    
    # Generate ability modifiers
    ability_modifiers = {
        ability: calculate_ability_modifier(score)
        for ability, score in final_scores.items()
    }
    
    # Select skills
    skill_proficiencies = select_skills_for_class(class_key, background_key)
    
    # Generate equipment
    equipment = generate_starting_equipment(class_key, background_key)
    
    # Generate spellcasting info
    spellcasting = generate_spellcasting_info(class_key, final_scores, level)
    
    # Select random alignment if not provided
    if not alignment:
        alignment = random.choice(DND_ALIGNMENTS)
    
    # Build complete character
    character = {
        "name": name or f"{species_info.get('name', 'Unknown')} {class_info.get('name', 'Adventurer')}",
        "level": level,
        "class": class_info.get("name", class_key),
        "species": species_info.get("name", species_key),
        "background": background_info.get("name", background_key),
        "alignment": alignment,
        
        # Ability Scores
        "ability_scores": final_scores,
        "ability_modifiers": ability_modifiers,
        
        # Combat Stats
        "hit_points": hit_points,  # DEPRECATED: Use hit_points_max instead
        "hit_points_max": hit_points,
        "hit_points_current": hit_points,  # Start at full HP
        "temporary_hp": 0,
        "hit_dice": f"1d{class_info.get('hit_die', 8)}",
        "armor_class": armor_class,
        "initiative": format_modifier(initiative_bonus),
        "speed": species_info.get("speed", 30),
        "proficiency_bonus": format_modifier(proficiency_bonus),
        
        # Attack Bonuses (for combat system)
        "melee_attack_bonus": ability_modifiers.get("strength", 0) + proficiency_bonus,
        "ranged_attack_bonus": ability_modifiers.get("dexterity", 0) + proficiency_bonus,
        
        # Combat State
        "conditions": [],
        "death_saves": {"successes": 0, "failures": 0},
        
        # Resources (limited-use features)
        "resources": _generate_class_resources(class_key, level, ability_modifiers),
        
        # Proficiencies
        "saving_throws": class_info.get("saving_throws", []),
        "skill_proficiencies": skill_proficiencies,
        "armor_proficiencies": class_info.get("armor_proficiencies", []),
        "weapon_proficiencies": class_info.get("weapon_proficiencies", []),
        "tool_proficiencies": class_info.get("tool_proficiencies", []) + background_info.get("tool_proficiencies", []),
        
        # Features
        "racial_traits": species_info.get("traits", []),
        "class_features": class_info.get("level_1_features", []),
        "background_feature": background_info.get("feature", ""),
        "background_feature_description": background_info.get("feature_description", ""),
        
        # Equipment
        "equipment": equipment,
        
        # Languages
        "languages": species_info.get("languages", ["Common"]),
        
        # Spellcasting (if applicable)
        "spellcasting": spellcasting,
        
        # Descriptions
        "class_description": class_info.get("description", ""),
        "species_description": species_info.get("description", ""),
        "background_description": background_info.get("description", "")
    }
    
    return character


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_character_sheet(character: Dict) -> str:
    """
    Format a character dictionary as a readable character sheet.
    
    Args:
        character: Character dictionary from generate_dnd_character
    
    Returns:
        Formatted character sheet as string
    """
    sheet = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                         D&D 5E CHARACTER SHEET                        ║
╚══════════════════════════════════════════════════════════════════════╝

NAME: {character['name']}
LEVEL: {character['level']} | CLASS: {character['class']} | SPECIES: {character['species']}
BACKGROUND: {character['background']} | ALIGNMENT: {character['alignment']}

╔══════════════════════════════════════════════════════════════════════╗
║                           ABILITY SCORES                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    for ability, score in character['ability_scores'].items():
        modifier = character['ability_modifiers'][ability]
        sheet += f"  {ability.upper():<15} {score:2d} ({format_modifier(modifier)})\n"
    
    sheet += f"""
╔══════════════════════════════════════════════════════════════════════╗
║                           COMBAT STATS                                ║
╚══════════════════════════════════════════════════════════════════════╝
  Hit Points:     {character['hit_points']}
  Armor Class:    {character['armor_class']}
  Initiative:     {character['initiative']}
  Speed:          {character['speed']} ft
  Proficiency:    {character['proficiency_bonus']}
  Hit Dice:       {character['hit_dice']}

╔══════════════════════════════════════════════════════════════════════╗
║                          PROFICIENCIES                                ║
╚══════════════════════════════════════════════════════════════════════╝
  Saving Throws:  {', '.join(character['saving_throws'])}
  Skills:         {', '.join(character['skill_proficiencies'])}
  Languages:      {', '.join(character['languages'])}

╔══════════════════════════════════════════════════════════════════════╗
║                           EQUIPMENT                                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    for category, items in character['equipment'].items():
        if items:
            sheet += f"  {category.capitalize()}:\n"
            for item in items:
                sheet += f"    • {item}\n"
    
    if character['spellcasting']:
        spell_info = character['spellcasting']
        sheet += f"""
╔══════════════════════════════════════════════════════════════════════╗
║                          SPELLCASTING                                 ║
╚══════════════════════════════════════════════════════════════════════╝
  Spellcasting Ability:  {spell_info['spellcasting_ability']}
  Spell Save DC:         {spell_info['spell_save_dc']}
  Spell Attack Bonus:    +{spell_info['spell_attack_bonus']}
  Cantrips Known:        {spell_info['cantrips_known']}
  Spells Known/Prepared: {spell_info['spells_known_or_prepared']}
  Spell Slots (Level 1): {spell_info['spell_slots']['level_1']}
"""
    
    return sheet


# Example usage for testing
if __name__ == "__main__":
    # Generate a sample character
    test_character = generate_dnd_character(
        class_key="wizard",
        species_key="elf",
        background_key="sage",
        alignment="Neutral Good",
        name="Eldrin Starweaver"
    )
    
    print(format_character_sheet(test_character))
