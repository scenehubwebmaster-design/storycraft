from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database import get_db
from models import Character
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic schemas
class CharacterBase(BaseModel):
    name: str
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None
    motivations: str | None = None
    relationships: Dict[str, Any] | list | None = None

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    """Schema for updating a character"""
    name: str | None = None
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None
    motivations: str | None = None
    relationships: Dict[str, Any] | list | None = None
    portrait_image: str | None = None
    image_prompt: str | None = None
    structured_data: Dict[str, Any] | str | None = None

class CharacterResponse(CharacterBase):
    id: int
    portrait_image: str | None = None
    image_prompt: str | None = None
    generation_log: Dict[str, Any] | list | str | None = None
    structured_data: Dict[str, Any] | str | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[CharacterResponse])
def get_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all characters"""
    characters = db.query(Character).offset(skip).limit(limit).all()
    return characters

@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a specific character by ID"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.post("/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character"""
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.put("/{character_id}", response_model=CharacterResponse)
def update_character(character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)):
    """Update an existing character"""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Only update fields that are provided (not None)
    update_data = character.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

@router.delete("/{character_id}")
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character"""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(db_character)
    db.commit()
    return {"message": "Character deleted successfully"}


# ============================================================================
# D&D 5E ENDPOINTS
# ============================================================================

@router.get("/dnd/classes")
def get_dnd_classes():
    """Get all available D&D 5E classes with full details"""
    from dnd_data import DND_CLASSES
    
    # Return formatted class data
    classes = []
    for class_key, class_info in DND_CLASSES.items():
        classes.append({
            "id": class_key,
            "name": class_info["name"],
            "description": class_info["description"],
            "hit_die": class_info["hit_die"],
            "primary_ability": class_info["primary_ability"],
            "saving_throws": class_info["saving_throws"],
            "spellcaster": class_info.get("spellcaster", False)
        })
    
    return {
        "classes": classes,
        "count": len(classes)
    }


@router.get("/dnd/species")
def get_dnd_species():
    """Get all available D&D 5E species/races with traits"""
    from dnd_data import DND_SPECIES
    
    # Return formatted species data
    species = []
    for species_key, species_info in DND_SPECIES.items():
        species.append({
            "id": species_key,
            "name": species_info["name"],
            "description": species_info["description"],
            "size": species_info["size"],
            "speed": species_info["speed"],
            "traits": species_info["traits"][:3] if len(species_info["traits"]) > 3 else species_info["traits"]  # First 3 traits for preview
        })
    
    return {
        "species": species,
        "count": len(species)
    }


@router.get("/dnd/backgrounds")
def get_dnd_backgrounds():
    """Get all available D&D 5E backgrounds with features"""
    from dnd_data import DND_BACKGROUNDS
    
    # Return formatted background data
    backgrounds = []
    for bg_key, bg_info in DND_BACKGROUNDS.items():
        backgrounds.append({
            "id": bg_key,
            "name": bg_info["name"],
            "description": bg_info["description"],
            "skill_proficiencies": bg_info["skill_proficiencies"],
            "feature": bg_info["feature"],
            "feature_description": bg_info["feature_description"]
        })
    
    return {
        "backgrounds": backgrounds,
        "count": len(backgrounds)
    }


@router.get("/dnd/alignments")
def get_dnd_alignments():
    """Get all D&D 5E alignments"""
    from dnd_data import DND_ALIGNMENTS
    
    return {
        "alignments": DND_ALIGNMENTS,
        "count": len(DND_ALIGNMENTS)
    }


# Pydantic schema for D&D character generation
class DnDCharacterGenerateRequest(BaseModel):
    """Request schema for generating a D&D 5E character"""
    name: str | None = None
    dnd_class: str
    dnd_species: str
    dnd_background: str
    dnd_alignment: str | None = None
    dnd_level: int = 1
    ability_score_method: str = "standard_array"  # or "random"
    
    # Optional: Generate narrative description with AI
    generate_narrative: bool = False
    narrative_provider: str = "groq"  # LLM provider for narrative generation
    narrative_model: str | None = None  # Optional specific model
    use_structured: bool = True  # Use structured output schema
    narrative_style: str = "detailed"  # concise, detailed, dramatic
    narrative_context: str | None = None  # Additional context for narrative generation
    
    # Optional genre/culture context
    genre: str | None = None
    variation: str | None = None
    cultural_origin: str | None = None


@router.post("/dnd/generate", response_model=CharacterResponse)
async def generate_dnd_character(request: DnDCharacterGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate a complete D&D 5E character with stats, equipment, and features.
    Optionally generate narrative description using structured AI output.
    """
    from dnd_generator import generate_dnd_character, format_character_sheet
    from dnd_narrative_prompts import build_dnd_narrative_prompt
    from schemas import DnDCharacterNarrative
    from routers.generation import call_llm_structured
    
    try:
        # Generate D&D character using our generator
        dnd_char = generate_dnd_character(
            class_key=request.dnd_class,
            species_key=request.dnd_species,
            background_key=request.dnd_background,
            alignment=request.dnd_alignment,
            ability_score_method=request.ability_score_method,
            name=request.name,
            level=request.dnd_level
        )
        
        # Generate AI narrative if requested
        narrative_data = None
        if request.generate_narrative:
            try:
                # Build narrative prompt based on D&D stats
                narrative_prompt = build_dnd_narrative_prompt(
                    dnd_character=dnd_char,
                    style=request.narrative_style,
                    additional_context=request.narrative_context
                )
                
                if request.use_structured:
                    # Use structured output for consistent narrative format
                    narrative_data, metadata = await call_llm_structured(
                        prompt=narrative_prompt,
                        provider=request.narrative_provider,
                        schema_model=DnDCharacterNarrative,
                        model=request.narrative_model,
                        max_tokens=3000
                    )
                    
                    # Convert to dict for storage
                    narrative_dict = narrative_data.model_dump() if hasattr(narrative_data, 'model_dump') else narrative_data.dict()
                else:
                    # Use simple text generation (fallback)
                    from routers.llm import LLMProvider
                    narrative_text = await LLMProvider.generate_text(
                        prompt=narrative_prompt,
                        provider=request.narrative_provider,
                        model=request.narrative_model,
                        max_tokens=1500
                    )
                    narrative_dict = {"narrative_text": narrative_text}
                    
            except Exception as narrative_error:
                logger.error(f"Narrative generation failed: {narrative_error}")
                # Continue without narrative rather than failing entire request
                narrative_dict = {"error": str(narrative_error)}
        
        # Prepare description fields (use narrative if available, otherwise defaults)
        if narrative_data:
            description = narrative_dict.get("physical_appearance", dnd_char["class_description"])
            personality = narrative_dict.get("personality_summary", f"Alignment: {dnd_char['alignment']}")
            appearance = narrative_dict.get("physical_appearance", dnd_char["species_description"])
            background_text = narrative_dict.get("backstory", dnd_char["background_description"])
        else:
            description = dnd_char["class_description"]
            personality = f"Alignment: {dnd_char['alignment']}"
            appearance = dnd_char["species_description"]
            background_text = dnd_char["background_description"]
        
        # Create database character record
        db_character = Character(
            name=dnd_char["name"],
            description=description,
            background=background_text,
            personality=personality,
            appearance=appearance,
            
            # D&D specific fields
            is_dnd=True,
            dnd_class=dnd_char["class"],
            dnd_level=dnd_char["level"],
            dnd_species=dnd_char["species"],
            dnd_background=dnd_char["background"],
            dnd_alignment=dnd_char["alignment"],
            dnd_ability_scores=dnd_char["ability_scores"],
            dnd_hit_points=dnd_char["hit_points"],
            dnd_armor_class=dnd_char["armor_class"],
            dnd_initiative=dnd_char["initiative"],
            dnd_speed=dnd_char["speed"],
            dnd_proficiency_bonus=dnd_char["proficiency_bonus"],
            dnd_skills=dnd_char["skill_proficiencies"],
            dnd_proficiencies={
                "saves": dnd_char["saving_throws"],
                "armor": dnd_char["armor_proficiencies"],
                "weapons": dnd_char["weapon_proficiencies"],
                "tools": dnd_char["tool_proficiencies"]
            },
            dnd_features={
                "racial": dnd_char["racial_traits"],
                "class": dnd_char["class_features"],
                "background": {
                    "feature": dnd_char["background_feature"],
                    "description": dnd_char["background_feature_description"]
                }
            },
            dnd_equipment=dnd_char["equipment"],
            dnd_spellcasting=dnd_char["spellcasting"],
            dnd_languages=dnd_char["languages"],
            
            # Store complete character sheet and narrative in generation_log
            generation_log={
                "type": "dnd_5e_character",
                "generator": "dnd_generator",
                "method": request.ability_score_method,
                "narrative_generated": request.generate_narrative,
                "narrative_provider": request.narrative_provider if request.generate_narrative else None,
                "structured_output": request.use_structured if request.generate_narrative else None,
                "timestamp": datetime.utcnow().isoformat(),
                "character_sheet": format_character_sheet(dnd_char),
                "ai_narrative": narrative_dict if narrative_data else None
            }
        )
        
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        
        return db_character
        
    except Exception as e:
        logger.error(f"D&D character generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate D&D character: {str(e)}")


@router.get("/{character_id}/dnd-sheet")
def get_dnd_character_sheet(character_id: int, db: Session = Depends(get_db)):
    """
    Get a formatted D&D character sheet for a character.
    Returns both JSON data and formatted text sheet.
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Character is not a D&D character")
    
    from dnd_generator import format_character_sheet
    
    # Reconstruct character dict from database fields
    char_dict = {
        "name": character.name,
        "level": character.dnd_level,
        "class": character.dnd_class,
        "species": character.dnd_species,
        "background": character.dnd_background,
        "alignment": character.dnd_alignment,
        "ability_scores": character.dnd_ability_scores,
        "ability_modifiers": {
            ability: (score - 10) // 2 
            for ability, score in character.dnd_ability_scores.items()
        },
        "hit_points": character.dnd_hit_points,
        "hit_dice": f"1d{character.dnd_hit_points}",  # Simplified
        "armor_class": character.dnd_armor_class,
        "initiative": character.dnd_initiative,
        "speed": character.dnd_speed,
        "proficiency_bonus": character.dnd_proficiency_bonus,
        "saving_throws": character.dnd_proficiencies.get("saves", []) if character.dnd_proficiencies else [],
        "skill_proficiencies": character.dnd_skills or [],
        "languages": character.dnd_languages or [],
        "equipment": character.dnd_equipment or {},
        "spellcasting": character.dnd_spellcasting,
        "racial_traits": character.dnd_features.get("racial", []) if character.dnd_features else [],
        "class_features": character.dnd_features.get("class", []) if character.dnd_features else [],
        "background_feature": character.dnd_features.get("background", {}).get("feature", "") if character.dnd_features else "",
        "background_feature_description": character.dnd_features.get("background", {}).get("description", "") if character.dnd_features else "",
        "class_description": character.description or "",
        "species_description": character.appearance or "",
        "background_description": character.background or ""
    }
    
    return {
        "character_id": character.id,
        "character_data": char_dict,
        "formatted_sheet": format_character_sheet(char_dict),
        "created_at": character.created_at,
        "updated_at": character.updated_at
    }


@router.put("/{character_id}/dnd-stats")
def update_dnd_stats(character_id: int, stats: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Update D&D stats for a character (e.g., after leveling up, taking damage, etc.)
    """
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Character is not a D&D character")
    
    # Update allowed D&D fields
    allowed_fields = [
        "dnd_level", "dnd_hit_points", "dnd_armor_class", 
        "dnd_ability_scores", "dnd_equipment", "dnd_spellcasting",
        "dnd_skills", "dnd_proficiencies", "dnd_features"
    ]
    
    for field, value in stats.items():
        if field in allowed_fields and hasattr(character, field):
            setattr(character, field, value)
    
    db.commit()
    db.refresh(character)
    
    return {
        "message": "D&D stats updated successfully",
        "character_id": character.id,
        "updated_fields": list(stats.keys())
    }
