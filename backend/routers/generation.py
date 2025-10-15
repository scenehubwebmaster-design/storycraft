"""
AI Generation Router - Endpoints for intelligent story element creation.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
import json

from database import get_db
from models import Character, Story, World, Scene, Chapter, Location
from schemas import (
    CharacterGenerationRequest,
    StoryGenerationRequest,
    WorldGenerationRequest,
    SceneGenerationRequest,
    ChapterGenerationRequest,
    LocationGenerationRequest,
    CampaignGenerationRequest,
    GenerationResponse,
    PromptOptionsResponse,
    ImageGenerationRequest
)
from prompts import (
    PromptTemplates,
    THEMES,
    PERSONALITY_TRAITS,
    PHYSICAL_TRAITS,
    EMOTIONAL_TRAITS,
    TONES,
    SETTINGS,
    STORY_LENGTHS,
    PLOT_STRUCTURES,
    WORLD_ELEMENTS,
    CHARACTER_ARCHETYPES,
    CONFLICT_TYPES
)
from routers.llm import LLMProvider
from rate_limiter import rate_limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generation"])


async def call_llm(prompt: str, provider: str, model: str = None) -> tuple[str, Dict[str, Any]]:
    """
    Call the specified LLM provider and return the response.
    Returns (response_text, metadata)
    Includes rate limiting.
    """
    try:
        # Estimate tokens
        estimated_tokens = len(prompt) // 4 + 2000  # Assume max 2000 tokens output
        
        # Check rate limits
        rate_limit_error = rate_limiter.check_rate_limit(provider, estimated_tokens)
        if rate_limit_error:
            logger.warning(f"Rate limit exceeded for {provider}: {rate_limit_error}")
            raise HTTPException(
                status_code=429,
                detail=rate_limit_error
            )
        
        if provider.lower() == "openai":
            response_text = await LLMProvider.generate_openai(prompt, model or "gpt-4")
            metadata = {"model": model or "gpt-4", "provider": "openai"}
        elif provider.lower() == "anthropic":
            response_text = await LLMProvider.generate_anthropic(prompt, model or "claude-3-5-sonnet-20241022")
            metadata = {"model": model or "claude-3-5-sonnet-20241022", "provider": "anthropic"}
        elif provider.lower() == "google":
            response_text = await LLMProvider.generate_google(prompt, model or "gemini-2.0-flash")
            metadata = {"model": model or "gemini-2.0-flash", "provider": "google"}
        elif provider.lower() == "groq":
            response_text = await LLMProvider.generate_groq(prompt, model or "llama-3.3-70b-versatile")
            metadata = {"model": model or "llama-3.3-70b-versatile", "provider": "groq"}
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Record successful request
        actual_tokens = len(response_text) // 4
        rate_limiter.record_request(provider, actual_tokens)
        
        return response_text, metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")


@router.get("/options", response_model=PromptOptionsResponse)
async def get_prompt_options():
    """Get all available prompt options for the UI"""
    logger.info("GET /api/generate/options - Fetching prompt options")
    return PromptOptionsResponse(
        themes=THEMES,
        personality_traits=PERSONALITY_TRAITS,
        physical_traits=PHYSICAL_TRAITS,
        emotional_traits=EMOTIONAL_TRAITS,
        tones=TONES,
        settings=SETTINGS,
        story_lengths=STORY_LENGTHS,
        plot_structures=PLOT_STRUCTURES,
        world_elements=WORLD_ELEMENTS,
        character_archetypes=CHARACTER_ARCHETYPES,
        conflict_types=CONFLICT_TYPES
    )


@router.post("/character", response_model=GenerationResponse)
async def generate_character(request: CharacterGenerationRequest):
    """Generate a character using AI"""
    # Build prompt
    if request.base_content and request.refinement_instructions:
        prompt = PromptTemplates.refinement_prompt(
            request.base_content,
            request.refinement_instructions
        )
    else:
        prompt = PromptTemplates.character_prompt(
            themes=request.themes,
            personality_traits=request.personality_traits,
            physical_traits=request.physical_traits,
            archetype=request.archetype,
            custom_details=request.custom_details
        )
    
    # Generate with LLM
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/character/save")
async def save_character(
    name: str,
    content: str,
    story_id: int = None,
    db: Session = Depends(get_db)
):
    """Save a generated character to the database"""
    try:
        # Parse content to extract fields (basic implementation)
        character = Character(
            name=name,
            description=content,
            story_id=story_id,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        
        return {"id": character.id, "message": "Character saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save character: {str(e)}")


@router.post("/character/generate-portrait")
async def generate_character_portrait(request: ImageGenerationRequest):
    """
    Generate a character portrait using Google Imagen.
    
    This endpoint generates a portrait image based on the character's appearance
    description using Google's Imagen model.
    """
    try:
        from imagen_client import generate_character_portrait
        
        result = await generate_character_portrait(
            character_name=request.character_name,
            appearance_text=request.appearance_text,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            custom_prompt=request.custom_prompt
        )
        
        return {
            "image_base64": result["image_base64"],
            "prompt": result["prompt"],
            "model": request.model,
            "aspect_ratio": request.aspect_ratio,
            "message": "Portrait generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Portrait generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate portrait: {str(e)}"
        )


@router.post("/character/save-portrait")
async def save_character_portrait(
    character_id: int,
    image_base64: str,
    image_prompt: str,
    db: Session = Depends(get_db)
):
    """Save generated portrait to existing character"""
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Update character with portrait
        character.portrait_image = image_base64
        character.image_prompt = image_prompt
        character.updated_at = datetime.now()
        
        db.commit()
        db.refresh(character)
        
        return {"message": "Portrait saved successfully", "character_id": character_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save portrait: {str(e)}")


@router.post("/story", response_model=GenerationResponse)
async def generate_story(request: StoryGenerationRequest):
    """Generate a story outline using AI"""
    if request.base_content and request.refinement_instructions:
        prompt = PromptTemplates.refinement_prompt(
            request.base_content,
            request.refinement_instructions
        )
    else:
        prompt = PromptTemplates.story_prompt(
            themes=request.themes,
            tone=request.tone,
            length=request.length,
            plot_structure=request.plot_structure,
            conflict_type=request.conflict_type,
            custom_details=request.custom_details
        )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/story/save")
async def save_story(
    title: str,
    content: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Save a generated story to the database"""
    try:
        story = Story(
            title=title,
            description=description or content[:500],  # First 500 chars as description
            content=content,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(story)
        db.commit()
        db.refresh(story)
        
        return {"id": story.id, "message": "Story saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save story: {str(e)}")


@router.post("/world", response_model=GenerationResponse)
async def generate_world(request: WorldGenerationRequest):
    """Generate a world using AI"""
    if request.base_content and request.refinement_instructions:
        prompt = PromptTemplates.refinement_prompt(
            request.base_content,
            request.refinement_instructions
        )
    else:
        prompt = PromptTemplates.world_prompt(
            themes=request.themes,
            setting=request.setting,
            elements=request.elements,
            custom_details=request.custom_details
        )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/world/save")
async def save_world(
    name: str,
    content: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Save a generated world to the database"""
    try:
        world = World(
            name=name,
            description=description or content[:500],
            lore=content,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(world)
        db.commit()
        db.refresh(world)
        
        return {"id": world.id, "message": "World saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save world: {str(e)}")


@router.post("/scene", response_model=GenerationResponse)
async def generate_scene(request: SceneGenerationRequest):
    """Generate a scene using AI"""
    if request.base_content and request.refinement_instructions:
        prompt = PromptTemplates.refinement_prompt(
            request.base_content,
            request.refinement_instructions
        )
    else:
        prompt = PromptTemplates.scene_prompt(
            story_context=request.story_context,
            characters=request.characters,
            setting=request.setting,
            purpose=request.purpose,
            tone=request.tone,
            custom_details=request.custom_details
        )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/scene/save")
async def save_scene(
    title: str,
    content: str,
    chapter_id: int,
    order: int = 0,
    db: Session = Depends(get_db)
):
    """Save a generated scene to the database"""
    try:
        scene = Scene(
            title=title,
            content=content,
            chapter_id=chapter_id,
            order=order,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(scene)
        db.commit()
        db.refresh(scene)
        
        return {"id": scene.id, "message": "Scene saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save scene: {str(e)}")


@router.post("/chapter", response_model=GenerationResponse)
async def generate_chapter(request: ChapterGenerationRequest):
    """Generate a chapter using AI"""
    prompt = PromptTemplates.chapter_prompt(
        story_outline=request.story_outline,
        chapter_number=request.chapter_number,
        previous_summary=request.previous_summary,
        characters=request.characters,
        plot_points=request.plot_points,
        custom_details=request.custom_details
    )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/chapter/save")
async def save_chapter(
    title: str,
    content: str,
    story_id: int,
    order: int = 0,
    db: Session = Depends(get_db)
):
    """Save a generated chapter to the database"""
    try:
        chapter = Chapter(
            title=title,
            content=content,
            story_id=story_id,
            order=order,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
        
        return {"id": chapter.id, "message": "Chapter saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save chapter: {str(e)}")


@router.post("/location", response_model=GenerationResponse)
async def generate_location(request: LocationGenerationRequest):
    """Generate a location using AI"""
    prompt = PromptTemplates.location_prompt(
        world_context=request.world_context,
        location_type=request.location_type,
        importance=request.importance,
        themes=request.themes,
        custom_details=request.custom_details
    )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


@router.post("/location/save")
async def save_location(
    name: str,
    content: str,
    world_id: int,
    db: Session = Depends(get_db)
):
    """Save a generated location to the database"""
    try:
        location = Location(
            name=name,
            description=content,
            world_id=world_id,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content)
            }])
        )
        
        db.add(location)
        db.commit()
        db.refresh(location)
        
        return {"id": location.id, "message": "Location saved successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save location: {str(e)}")


@router.post("/campaign", response_model=GenerationResponse)
async def generate_campaign(request: CampaignGenerationRequest):
    """Generate a D&D campaign using AI"""
    prompt = PromptTemplates.campaign_prompt(
        themes=request.themes,
        tone=request.tone,
        session_count=request.session_count,
        player_count=request.player_count,
        level_range=request.level_range,
        custom_details=request.custom_details
    )
    
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )
