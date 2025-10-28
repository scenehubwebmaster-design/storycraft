"""
MCP Server for D&D Character Sheets

Provides a Model Context Protocol interface for the DM AI to query
character sheet data. This allows the DM to reference character stats,
abilities, spells, and equipment on-demand rather than loading everything
into context upfront.

Usage:
    python -m backend.mcp_character_sheets

MCP Tools:
    - get_character_sheet(character_id): Get full character sheet
    - get_character_abilities(character_id): Get ability scores and modifiers
    - get_character_spells(character_id): Get spell list and casting info
    - get_character_equipment(character_id): Get weapons, armor, and gear
    - get_character_features(character_id): Get class and racial features
    - search_characters(name): Search for characters by name
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ensure backend module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
from backend.models import Character


class CharacterSheetMCP:
    """MCP Server for querying D&D character sheets"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def get_character_sheet(self, character_id: int) -> Dict[str, Any]:
        """Get complete character sheet for a given character ID"""
        char = self.db.query(Character).filter(Character.id == character_id).first()
        if not char:
            return {"error": f"Character {character_id} not found"}
        
        return {
            "id": char.id,
            "name": char.name,
            "class": char.dnd_class,
            "level": char.dnd_level,
            "species": char.dnd_species,
            "background": char.dnd_background,
            "alignment": char.dnd_alignment,
            "ac": char.dnd_armor_class,
            "hp": {
                "max": char.dnd_hit_points_max or char.dnd_hit_points,
                "current": char.dnd_hit_points_current,
                "temporary": char.dnd_temporary_hp
            },
            "speed": char.dnd_speed,
            "initiative": char.dnd_initiative,
            "proficiency_bonus": char.dnd_proficiency_bonus,
            "ability_scores": char.dnd_ability_scores,
            "ability_modifiers": char.dnd_ability_modifiers,
            "skills": char.dnd_skills,
            "proficiencies": char.dnd_proficiencies,
            "equipment": char.dnd_equipment,
            "spellcasting": char.dnd_spellcasting,
            "features": char.dnd_features,
            "languages": char.dnd_languages,
            "conditions": char.dnd_conditions,
            "resources": char.dnd_resources,
            "personality": char.structured_data.get("personality_traits") if char.structured_data else None,
            "ideals": char.structured_data.get("ideals") if char.structured_data else None,
            "bonds": char.structured_data.get("bonds") if char.structured_data else None,
            "flaws": char.structured_data.get("flaws") if char.structured_data else None,
        }
    
    def get_character_abilities(self, character_id: int) -> Dict[str, Any]:
        """Get ability scores and modifiers only"""
        char = self.db.query(Character).filter(Character.id == character_id).first()
        if not char:
            return {"error": f"Character {character_id} not found"}
        
        return {
            "character_name": char.name,
            "ability_scores": char.dnd_ability_scores,
            "ability_modifiers": char.dnd_ability_modifiers,
            "proficiency_bonus": char.dnd_proficiency_bonus,
        }
    
    def get_character_spells(self, character_id: int) -> Dict[str, Any]:
        """Get spellcasting info and spell list"""
        char = self.db.query(Character).filter(Character.id == character_id).first()
        if not char:
            return {"error": f"Character {character_id} not found"}
        
        if not char.dnd_spellcasting:
            return {"character_name": char.name, "spellcaster": False}
        
        return {
            "character_name": char.name,
            "spellcaster": True,
            "spellcasting_ability": char.dnd_spellcasting.get("ability"),
            "spell_save_dc": char.dnd_spellcasting.get("dc"),
            "spell_attack_bonus": char.dnd_spellcasting.get("attack"),
            "spells_known": char.dnd_spellcasting.get("spells_known", []),
            "spell_slots": char.dnd_spellcasting.get("spell_slots", {}),
        }
    
    def get_character_equipment(self, character_id: int) -> Dict[str, Any]:
        """Get weapons, armor, and gear"""
        char = self.db.query(Character).filter(Character.id == character_id).first()
        if not char:
            return {"error": f"Character {character_id} not found"}
        
        return {
            "character_name": char.name,
            "weapons": char.dnd_equipment.get("weapons", []) if char.dnd_equipment else [],
            "armor": char.dnd_equipment.get("armor", []) if char.dnd_equipment else [],
            "gear": char.dnd_equipment.get("gear", []) if char.dnd_equipment else [],
        }
    
    def get_character_features(self, character_id: int) -> Dict[str, Any]:
        """Get class features and racial traits"""
        char = self.db.query(Character).filter(Character.id == character_id).first()
        if not char:
            return {"error": f"Character {character_id} not found"}
        
        return {
            "character_name": char.name,
            "class_features": char.dnd_features.get("class", []) if char.dnd_features else [],
            "racial_traits": char.dnd_features.get("racial", []) if char.dnd_features else [],
            "background_feature": char.dnd_features.get("background", {}) if char.dnd_features else {},
        }
    
    def search_characters(self, name: str) -> List[Dict[str, Any]]:
        """Search for characters by name (partial match)"""
        chars = self.db.query(Character).filter(
            Character.name.ilike(f"%{name}%"),
            ~Character.is_deleted
        ).all()
        
        return [
            {
                "id": char.id,
                "name": char.name,
                "class": char.dnd_class,
                "level": char.dnd_level,
                "species": char.dnd_species,
            }
            for char in chars
        ]
    
    def close(self):
        """Close database connection"""
        self.db.close()


# MCP Protocol Interface
def handle_mcp_request(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool requests"""
    mcp = CharacterSheetMCP()
    
    try:
        if tool == "get_character_sheet":
            return mcp.get_character_sheet(arguments["character_id"])
        elif tool == "get_character_abilities":
            return mcp.get_character_abilities(arguments["character_id"])
        elif tool == "get_character_spells":
            return mcp.get_character_spells(arguments["character_id"])
        elif tool == "get_character_equipment":
            return mcp.get_character_equipment(arguments["character_id"])
        elif tool == "get_character_features":
            return mcp.get_character_features(arguments["character_id"])
        elif tool == "search_characters":
            return {"characters": mcp.search_characters(arguments["name"])}
        else:
            return {"error": f"Unknown tool: {tool}"}
    finally:
        mcp.close()


if __name__ == "__main__":
    # Simple CLI for testing
    print("Character Sheet MCP Server")
    print("Available commands:")
    print("  sheet <id> - Get full character sheet")
    print("  abilities <id> - Get ability scores")
    print("  spells <id> - Get spell list")
    print("  equipment <id> - Get equipment")
    print("  features <id> - Get class/racial features")
    print("  search <name> - Search for characters")
    print()
    
    mcp = CharacterSheetMCP()
    
    try:
        while True:
            command = input("> ").strip().split()
            if not command:
                continue
            
            action = command[0]
            
            if action == "exit":
                break
            elif action == "sheet" and len(command) > 1:
                result = mcp.get_character_sheet(int(command[1]))
                print(json.dumps(result, indent=2))
            elif action == "abilities" and len(command) > 1:
                result = mcp.get_character_abilities(int(command[1]))
                print(json.dumps(result, indent=2))
            elif action == "spells" and len(command) > 1:
                result = mcp.get_character_spells(int(command[1]))
                print(json.dumps(result, indent=2))
            elif action == "equipment" and len(command) > 1:
                result = mcp.get_character_equipment(int(command[1]))
                print(json.dumps(result, indent=2))
            elif action == "features" and len(command) > 1:
                result = mcp.get_character_features(int(command[1]))
                print(json.dumps(result, indent=2))
            elif action == "search" and len(command) > 1:
                result = mcp.search_characters(" ".join(command[1:]))
                print(json.dumps(result, indent=2))
            else:
                print("Invalid command")
    finally:
        mcp.close()
