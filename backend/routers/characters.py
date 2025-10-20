from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from ..models import Character
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Basic character schemas
class CharacterBase(BaseModel):
    name: str
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    background: str | None = None
    personality: str | None = None
    appearance: str | None = None
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

    # D&D 5E fields
    is_dnd: bool | None = None
    dnd_class: str | None = None
    dnd_level: int | None = None
    dnd_species: str | None = None
    dnd_background: str | None = None
    dnd_alignment: str | None = None
    dnd_ability_scores: Dict[str, int] | None = None
    dnd_hit_points: int | None = None
    dnd_armor_class: int | None = None
    dnd_initiative: str | None = None
    dnd_speed: int | None = None
    dnd_proficiency_bonus: str | None = None
    dnd_skills: List[str] | None = None
    dnd_proficiencies: Dict[str, Any] | None = None
    dnd_features: Dict[str, Any] | None = None
    dnd_equipment: Dict[str, Any] | None = None
    dnd_spellcasting: Dict[str, Any] | None = None
    dnd_languages: List[str] | None = None
    name_suggestions: List[str] | None = None

    class Config:
        from_attributes = True


class BatchDeleteRequest(BaseModel):
    ids: List[int]


@router.get("/", response_model=List[CharacterResponse])
def get_characters(skip: int = 0, limit: int = 100, exclude_portraits: bool = True, db: Session = Depends(get_db)):
    characters = db.query(Character).filter(Character.is_deleted.is_(False)).offset(skip).limit(limit).all()
    if exclude_portraits:
        result = []
        for character in characters:
            char_dict = CharacterResponse.model_validate(character).model_dump()
            char_dict["portrait_image"] = None
            result.append(char_dict)
        return result
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, exclude_portrait: bool = False, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id, Character.is_deleted.is_(False)).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    if exclude_portrait:
        response_data = CharacterResponse.model_validate(character).model_dump()
        response_data["portrait_image"] = None
        return response_data
    return character


@router.post("/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.put("/{character_id}", response_model=CharacterResponse)
def update_character(character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)):
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    update_data = character.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_character, key, value)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.delete("/{character_id}/")
def delete_character(character_id: int, db: Session = Depends(get_db)):
    db_character = db.query(Character).filter(Character.id == character_id, Character.is_deleted.is_(False)).first()
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found or already deleted")
    db_character.is_deleted = True
    db_character.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Character soft-deleted"}


@router.post("/bulk-delete/")
def bulk_delete_characters(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    ids = request.ids or []
    if not ids:
        raise HTTPException(status_code=400, detail="No character IDs provided")
    try:
        chars = db.query(Character).filter(Character.id.in_(ids), Character.is_deleted.is_(False)).all()
        if not chars:
            return {"deleted": [], "requested": ids}
        deleted_ids = []
        for c in chars:
            c.is_deleted = True
            c.deleted_at = datetime.utcnow()
            deleted_ids.append(c.id)
        db.commit()
        return {"deleted": deleted_ids}
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk delete failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete characters")


@router.post("/restore/")
def restore_characters(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    ids = request.ids or []
    if not ids:
        raise HTTPException(status_code=400, detail="No character IDs provided")
    try:
        chars = db.query(Character).filter(Character.id.in_(ids), Character.is_deleted.is_(True)).all()
        restored = []
        for c in chars:
            c.is_deleted = False
            c.deleted_at = None
            restored.append(c.id)
        db.commit()
        return {"restored": restored}
    except Exception as e:
        db.rollback()
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore characters")


@router.get("/{character_id}/portrait/")
def get_character_portrait(character_id: int, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id, Character.is_deleted.is_(False)).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"portrait_image": character.portrait_image, "image_prompt": character.image_prompt}


# ---------------------------------------------------------------------------
# D&D helpers and endpoints
# ---------------------------------------------------------------------------


@router.get("/dnd/classes/")
def get_dnd_classes():
    from dnd_data import DND_CLASSES
    classes = []
    for class_key, class_info in DND_CLASSES.items():
        classes.append({
            "id": class_key,
            "name": class_info["name"],
            "description": class_info["description"],
            "hit_die": class_info["hit_die"],
            "primary_ability": class_info["primary_ability"],
            "saving_throws": class_info["saving_throws"],
            "spellcaster": class_info.get("spellcaster", False),
        })
    return {"classes": classes, "count": len(classes)}


@router.get("/dnd/species/")
def get_dnd_species():
    from dnd_data import DND_SPECIES
    species = []
    for species_key, species_info in DND_SPECIES.items():
        species.append({
            "id": species_key,
            "name": species_info["name"],
            "description": species_info["description"],
            "size": species_info["size"],
            "speed": species_info["speed"],
            "traits": species_info["traits"][:3] if len(species_info["traits"]) > 3 else species_info["traits"],
        })
    return {"species": species, "count": len(species)}


@router.get("/dnd/backgrounds/")
def get_dnd_backgrounds():
    from dnd_data import DND_BACKGROUNDS
    backgrounds = []
    for bg_key, bg_info in DND_BACKGROUNDS.items():
        backgrounds.append({
            "id": bg_key,
            "name": bg_info["name"],
            "description": bg_info["description"],
            "skill_proficiencies": bg_info["skill_proficiencies"],
            "feature": bg_info["feature"],
            "feature_description": bg_info["feature_description"],
        })
    return {"backgrounds": backgrounds, "count": len(backgrounds)}


@router.get("/dnd/alignments/")
def get_dnd_alignments():
    from dnd_data import DND_ALIGNMENTS
    return {"alignments": DND_ALIGNMENTS, "count": len(DND_ALIGNMENTS)}


# Pydantic schema for D&D character generation
class DnDCharacterGenerateRequest(BaseModel):
    name: str | None = None
    dnd_class: str
    dnd_species: str
    dnd_background: str
    dnd_alignment: str | None = None
    dnd_level: int = 1
    ability_score_method: str = "standard_array"
    generate_narrative: bool = False
    narrative_provider: str = "groq"
    narrative_model: str | None = None
    use_structured: bool = True
    narrative_style: str | None = None
    narrative_context: str | None = None
    genre: str | None = None
    variation: str | None = None
    cultural_origin: str | None = None


@router.post("/dnd/generate", response_model=CharacterResponse)
@router.post("/dnd/generate/", response_model=CharacterResponse)
async def generate_dnd_character(request: DnDCharacterGenerateRequest, db: Session = Depends(get_db)):
    from dnd_generator import generate_dnd_character, format_character_sheet
    from dnd_narrative_prompts import build_dnd_narrative_prompt
    from schemas import DnDCharacterNarrative

    try:
        # Generate base D&D character
        dnd_char = generate_dnd_character(
            class_key=request.dnd_class,
            species_key=request.dnd_species,
            background_key=request.dnd_background,
            alignment=request.dnd_alignment,
            ability_score_method=request.ability_score_method,
            name=request.name,
            level=request.dnd_level,
        )

        narrative_dict: Dict[str, Any] | None = None
        if request.generate_narrative:
            try:
                narrative_prompt = build_dnd_narrative_prompt(
                    dnd_character=dnd_char,
                    style=request.narrative_style,
                    additional_context=request.narrative_context,
                )

                if request.use_structured:
                    from .generation import call_llm_with_retries_and_clarifier

                    authoritative = {
                        "character_name": dnd_char.get("name"),
                        "dnd_class": dnd_char.get("class"),
                        "dnd_species": dnd_char.get("species"),
                        "dnd_level": dnd_char.get("level"),
                    }

                    narrative_obj, metadata = await call_llm_with_retries_and_clarifier(
                        base_prompt=narrative_prompt,
                        provider=request.narrative_provider,
                        schema_model=DnDCharacterNarrative,
                        model=request.narrative_model,
                        max_attempts=3,
                        initial_temperature=0.95,
                        retry_temperature=0.6,
                        authoritative_fields=authoritative,
                    )

                    narrative_dict = (
                        narrative_obj.model_dump()
                        if hasattr(narrative_obj, "model_dump")
                        else (narrative_obj.dict() if hasattr(narrative_obj, "dict") else dict(narrative_obj))
                    )
                else:
                    from ..routers.llm import LLMProvider

                    narrative_text = await LLMProvider.generate_text(
                        prompt=narrative_prompt,
                        provider=request.narrative_provider,
                        model=request.narrative_model,
                        max_tokens=1500,
                    )
                    narrative_dict = {"narrative_text": narrative_text}

            except Exception as narrative_error:
                logger.error(f"Narrative generation failed: {narrative_error}")
                narrative_dict = {"error": str(narrative_error)}

        # If we have structured narrative, normalize common key variants and log keys
        if narrative_dict and isinstance(narrative_dict, dict) and "error" not in narrative_dict:
            try:
                # physical_description or appearance -> character_appearance
                if "physical_description" in narrative_dict and "character_appearance" not in narrative_dict:
                    narrative_dict["character_appearance"] = narrative_dict.pop("physical_description")
                if "appearance" in narrative_dict and "character_appearance" not in narrative_dict:
                    narrative_dict["character_appearance"] = narrative_dict.pop("appearance")

                # backstory -> character_backstory
                if "backstory" in narrative_dict and "character_backstory" not in narrative_dict:
                    narrative_dict["character_backstory"] = narrative_dict.pop("backstory")

                # personality -> personality_traits (coerce string -> list)
                if "personality" in narrative_dict and "personality_traits" not in narrative_dict:
                    val = narrative_dict.pop("personality")
                    if isinstance(val, str):
                        traits = [t.strip() for t in val.replace('\n', ',').split(',') if t.strip()]
                        narrative_dict["personality_traits"] = traits[:2] if len(traits) >= 2 else traits
                    elif isinstance(val, list):
                        narrative_dict["personality_traits"] = val[:2]
            except Exception as _norm_err:
                logger.debug(f"Normalization failed: {_norm_err}")

            try:
                logger.info("D&D narrative keys received: %s", list(narrative_dict.keys()))
            except Exception:
                logger.info("D&D narrative received (non-dict payload)")

        # If structured generation produced no or incomplete physical traits,
        # attempt a small, tightly-scoped fallback LLM call that returns only
        # the minimal JSON with skin/eyes/hair so the frontend retains the
        # Physical Traits section even when the full structured output failed.
        try:
            missing_traits = []
            for t in ("skin", "eyes", "hair"):
                if not narrative_dict or t not in narrative_dict or not narrative_dict.get(t):
                    missing_traits.append(t)

            if missing_traits and request.generate_narrative and request.use_structured:
                try:
                    from .generation import call_llm_with_retries_and_clarifier

                    # Build a minimal prompt that asks for a JSON object with
                    # the three physical trait keys. Include a tiny context so
                    # the model can produce species-appropriate traits.
                    ctx_parts = []
                    if dnd_char.get("name"):
                        ctx_parts.append(f"name: {dnd_char.get('name')}")
                    if dnd_char.get("class"):
                        ctx_parts.append(f"class: {dnd_char.get('class')}")
                    if dnd_char.get("species"):
                        ctx_parts.append(f"species: {dnd_char.get('species')}")
                    ctx = ", ".join(ctx_parts)

                    fallback_prompt = (
                        "Return a JSON object with exactly these keys: \"skin\", \"eyes\", \"hair\". "
                        "Each value should be a short, micro-detailed phrase (3-10 words) useful for UI display and portrait generation. "
                        "Do NOT include additional keys. Values must be unique from one another and descriptive."
                    )
                    if ctx:
                        fallback_prompt += f" Context: {ctx}."

                    # Use the same provider/model but low temperature and small output
                    fallback_text, fallback_meta = await call_llm_with_retries_and_clarifier(
                        base_prompt=fallback_prompt,
                        provider=request.narrative_provider,
                        schema_model=None,
                        model=request.narrative_model,
                        max_attempts=2,
                        initial_temperature=0.3,
                        retry_temperature=0.1,
                    )

                    # call_llm_with_retries_and_clarifier returns (text, metadata) when
                    # schema_model is None. Try to parse JSON out of it using a
                    # robust extractor that tolerates surrounding commentary.
                    try:
                        from ..name_generation_utils import extract_json_from_text

                        if isinstance(fallback_text, str):
                            parsed = extract_json_from_text(fallback_text)
                        else:
                            parsed = dict(fallback_text)
                        if not narrative_dict:
                            narrative_dict = {}
                        # Merge only the requested trait keys
                        for k in ("skin", "eyes", "hair"):
                            if k in parsed and parsed.get(k):
                                narrative_dict[k] = parsed.get(k)

                        # Record that fallback was used
                        narrative_dict["_fallback_physical_traits"] = {
                            "used": True,
                            "provider": fallback_meta.get("provider") if isinstance(fallback_meta, dict) else None,
                            "raw": parsed,
                        }
                        # If we previously recorded an error (e.g. structured generation failed),
                        # but the fallback provided physical traits, clear the error so the
                        # narrative_dict will be persisted into `structured_data` on save.
                        try:
                            if narrative_dict.get("_fallback_physical_traits", {}).get("used"):
                                narrative_dict.pop("error", None)
                        except Exception:
                            pass
                    except Exception as _je:
                        logger.warning(f"Fallback physical-traits JSON parse failed: {_je}")

                except Exception as _fb_err:
                    logger.warning(f"Physical-traits fallback failed: {_fb_err}")
        except Exception:
            # Swallow any unexpected errors in fallback logic; don't block main flow
            logger.exception("Unexpected error in physical-traits fallback logic")

        # Map narrative -> legacy fields and save
        if narrative_dict and isinstance(narrative_dict, dict) and "error" not in narrative_dict:
            llm_name = narrative_dict.get("character_name")
            canonical_name = dnd_char.get("name")
            if llm_name and canonical_name and llm_name != canonical_name:
                existing = narrative_dict.get("name_suggestions") or []
                if isinstance(llm_name, list):
                    for nm in llm_name:
                        if nm and nm != canonical_name and nm not in existing:
                            existing.append(nm)
                else:
                    if llm_name != canonical_name and llm_name not in existing:
                        existing.append(llm_name)
                narrative_dict["name_suggestions"] = existing
                character_name = canonical_name
                narrative_dict.pop("character_name", None)
            else:
                character_name = narrative_dict.get("character_name", canonical_name)

            description = narrative_dict.get("character_appearance", dnd_char.get("class_description"))
            personality = narrative_dict.get("personality_traits", f"Alignment: {dnd_char.get('alignment')}")
            if isinstance(personality, list):
                personality = ", ".join(personality)
            appearance = narrative_dict.get("character_appearance", dnd_char.get("species_description"))
            background_text = narrative_dict.get("character_backstory", dnd_char.get("background_description"))
        else:
            character_name = dnd_char.get("name")
            description = dnd_char.get("class_description")
            personality = f"Alignment: {dnd_char.get('alignment')}"
            appearance = dnd_char.get("species_description")
            background_text = dnd_char.get("background_description")

        db_character = Character(
            name=character_name,
            description=description,
            background=background_text,
            personality=personality,
            appearance=appearance,
            # D&D specific fields
            is_dnd=True,
            dnd_class=dnd_char.get("class"),
            dnd_level=dnd_char.get("level"),
            dnd_species=dnd_char.get("species"),
            dnd_background=dnd_char.get("background"),
            dnd_alignment=dnd_char.get("alignment"),
            dnd_ability_scores=dnd_char.get("ability_scores"),
            dnd_hit_points=dnd_char.get("hit_points"),
            dnd_armor_class=dnd_char.get("armor_class"),
            dnd_initiative=dnd_char.get("initiative"),
            dnd_speed=dnd_char.get("speed"),
            dnd_proficiency_bonus=dnd_char.get("proficiency_bonus"),
            dnd_skills=dnd_char.get("skill_proficiencies"),
            dnd_proficiencies={
                "saves": dnd_char.get("saving_throws"),
                "armor": dnd_char.get("armor_proficiencies"),
                "weapons": dnd_char.get("weapon_proficiencies"),
                "tools": dnd_char.get("tool_proficiencies"),
            },
            dnd_features={
                "racial": dnd_char.get("racial_traits"),
                "class": dnd_char.get("class_features"),
                "background": {
                    "feature": dnd_char.get("background_feature"),
                    "description": dnd_char.get("background_feature_description"),
                },
            },
            dnd_equipment=dnd_char.get("equipment"),
            dnd_spellcasting=dnd_char.get("spellcasting"),
            dnd_languages=dnd_char.get("languages"),
            structured_data=narrative_dict if (narrative_dict and "error" not in narrative_dict) else None,
            generation_log={
                "type": "dnd_5e_character",
                "generator": "dnd_generator",
                "method": request.ability_score_method,
                "narrative_generated": request.generate_narrative,
                "narrative_provider": request.narrative_provider if request.generate_narrative else None,
                "structured_output": request.use_structured if request.generate_narrative else None,
                "timestamp": datetime.utcnow().isoformat(),
                "character_sheet": format_character_sheet(dnd_char),
                "ai_narrative": narrative_dict if narrative_dict else None,
            },
        )

        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character

    except Exception as e:
        logger.error(f"D&D character generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate D&D character: {str(e)}")


@router.get("/{character_id}/dnd-sheet/")
def get_dnd_character_sheet(character_id: int, db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Character is not a D&D character")
    from dnd_generator import format_character_sheet

    char_dict = {
        "name": character.name,
        "level": character.dnd_level,
        "class": character.dnd_class,
        "species": character.dnd_species,
        "background": character.dnd_background,
        "alignment": character.dnd_alignment,
        "ability_scores": character.dnd_ability_scores,
        "ability_modifiers": {ability: (score - 10) // 2 for ability, score in (character.dnd_ability_scores or {}).items()},
        "hit_points": character.dnd_hit_points,
        "hit_dice": f"1d{character.dnd_hit_points}",
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
        "background_description": character.background or "",
    }
    return {"character_id": character.id, "character_data": char_dict, "formatted_sheet": format_character_sheet(char_dict), "created_at": character.created_at, "updated_at": character.updated_at}


@router.put("/{character_id}/dnd-stats/")
def update_dnd_stats(character_id: int, stats: Dict[str, Any], db: Session = Depends(get_db)):
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    if not character.is_dnd:
        raise HTTPException(status_code=400, detail="Character is not a D&D character")
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
    return {"message": "D&D stats updated successfully", "character_id": character.id, "updated_fields": list(stats.keys())}
