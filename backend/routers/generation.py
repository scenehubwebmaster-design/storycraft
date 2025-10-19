"""
AI Generation Router - Endpoints for intelligent story element creation.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Type, Optional
import json
from pydantic import BaseModel

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
    ImageGenerationRequest,
    CharacterProfile,
    WorldProfile,
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
from prompt_variations import (
    list_all_variation_names,
    build_enhanced_character_prompt,
)
from cultural_modules import (
    list_cultural_origin_names,
    build_culturally_enhanced_prompt,
)
from routers.llm import LLMProvider
from rate_limiter import rate_limiter
from structured_output_utils import (
    get_schema_for_provider,
    parse_structured_response,
    supports_structured_outputs,
    get_structured_output_prompt,
)
from name_generation_utils import (
    extract_json_array_from_text,
    needs_retry_from_text,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generation"])


class RegionCropRequest(BaseModel):
    world_id: int
    # Either percent bounds (x1%,y1%,x2%,y2%) in 0-100 or lat/lng bounds dict
    percent_bounds: Optional[Dict[str, float]] = None
    latlng_bounds: Optional[Dict[str, float]] = None
    upscale: Optional[int] = 1  # integer upscale multiplier


@router.post('/region/crop/')
def crop_region(request: RegionCropRequest, db: Session = Depends(get_db)):
    """Crop a region out of the world's map image.

    Accepts either percent_bounds = {x1:float,y1:float,x2:float,y2:float} where
    coordinates are percents (0-100) relative to the original image width/height,
    or latlng_bounds which will be handled as fallback for geospatial maps.
    Returns base64 PNG image of the cropped region.
    """
    try:
        # Avoid selecting all model columns (some DBs may be missing migrated columns)
        # Query only the world_map column directly to be resilient against schema drift
        row = db.execute(
            "SELECT world_map FROM worlds WHERE id = :wid",
            {"wid": request.world_id}
        ).fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail='World or world_map not found')

        import base64
        from io import BytesIO
        from PIL import Image

        img_b64 = row[0]
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(BytesIO(img_bytes)).convert('RGBA')
        w, h = img.size

        if request.percent_bounds:
            pb = request.percent_bounds
            x1 = max(0, min(100, pb.get('x1', 0))) / 100.0
            y1 = max(0, min(100, pb.get('y1', 0))) / 100.0
            x2 = max(0, min(100, pb.get('x2', 100))) / 100.0
            y2 = max(0, min(100, pb.get('y2', 100))) / 100.0
            left = int(x1 * w)
            top = int(y1 * h)
            right = int(x2 * w)
            bottom = int(y2 * h)
        elif request.latlng_bounds:
            # We don't have a real coordinate reference; treat lat/lng as percent placeholders
            lb = request.latlng_bounds
            # Expect keys: lat_min, lng_min, lat_max, lng_max mapped to percent-like 0-100
            left = int(max(0, min(100, lb.get('lng_min', 0))) / 100.0 * w)
            top = int(max(0, min(100, lb.get('lat_min', 0))) / 100.0 * h)
            right = int(max(0, min(100, lb.get('lng_max', 100))) / 100.0 * w)
            bottom = int(max(0, min(100, lb.get('lat_max', 100))) / 100.0 * h)
        else:
            raise HTTPException(status_code=400, detail='No bounds provided')

        # Clamp
        left = max(0, min(left, w - 1))
        right = max(left + 1, min(right, w))
        top = max(0, min(top, h - 1))
        bottom = max(top + 1, min(bottom, h))

        cropped = img.crop((left, top, right, bottom))
        if request.upscale and request.upscale > 1:
            new_w = cropped.width * request.upscale
            new_h = cropped.height * request.upscale
            cropped = cropped.resize((new_w, new_h), Image.LANCZOS)

        out_buf = BytesIO()
        cropped.save(out_buf, format='PNG')
        out_b64 = base64.b64encode(out_buf.getvalue()).decode('utf-8')

        return { 'image_base64': out_b64, 'width': cropped.width, 'height': cropped.height }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Region cropping failed')
        raise HTTPException(status_code=500, detail=f'Region cropping error: {str(e)}')


class CropAndGenerateRequest(BaseModel):
    world_id: int
    percent_bounds: Optional[Dict[str, float]] = None
    latlng_bounds: Optional[Dict[str, float]] = None
    upscale: Optional[int] = 1
    prompt: Optional[str] = None
    provider: Optional[str] = 'stablediffusion'
    model: Optional[str] = None


@router.post('/region/crop-and-generate/')
async def crop_and_generate(request: CropAndGenerateRequest, db: Session = Depends(get_db)):
    """Crop a region and then call the image generation helper to stylize/enhance it.

    Returns the generated image_base64 and metadata.
    """
    try:
        # Reuse crop logic: fetch world_map
        row = db.execute(
            "SELECT world_map FROM worlds WHERE id = :wid",
            {"wid": request.world_id}
        ).fetchone()
        if not row or not row[0]:
            raise HTTPException(status_code=404, detail='World or world_map not found')

        import base64
        from io import BytesIO
        from PIL import Image

        img_b64 = row[0]
        img_bytes = base64.b64decode(img_b64)
        img = Image.open(BytesIO(img_bytes)).convert('RGBA')
        w, h = img.size

        if request.percent_bounds:
            pb = request.percent_bounds
            x1 = max(0, min(100, pb.get('x1', 0))) / 100.0
            y1 = max(0, min(100, pb.get('y1', 0))) / 100.0
            x2 = max(0, min(100, pb.get('x2', 100))) / 100.0
            y2 = max(0, min(100, pb.get('y2', 100))) / 100.0
            left = int(x1 * w)
            top = int(y1 * h)
            right = int(x2 * w)
            bottom = int(y2 * h)
        elif request.latlng_bounds:
            lb = request.latlng_bounds
            left = int(max(0, min(100, lb.get('lng_min', 0))) / 100.0 * w)
            top = int(max(0, min(100, lb.get('lat_min', 0))) / 100.0 * h)
            right = int(max(0, min(100, lb.get('lng_max', 100))) / 100.0 * w)
            bottom = int(max(0, min(100, lb.get('lat_max', 100))) / 100.0 * h)
        else:
            raise HTTPException(status_code=400, detail='No bounds provided')

        # Clamp and crop
        left = max(0, min(left, w - 1))
        right = max(left + 1, min(right, w))
        top = max(0, min(top, h - 1))
        bottom = max(top + 1, min(bottom, h))

        cropped = img.crop((left, top, right, bottom))
        if request.upscale and request.upscale > 1:
            new_w = cropped.width * request.upscale
            new_h = cropped.height * request.upscale
            cropped = cropped.resize((new_w, new_h), Image.LANCZOS)

        # Convert cropped image to base64 so generation helper can use it if needed
        out_buf = BytesIO()
        cropped.save(out_buf, format='PNG')
        crop_b64 = base64.b64encode(out_buf.getvalue()).decode('utf-8')

        # Now call the image generation helper to stylize/enhance using prompt
        gen_result = {}
        try:
            from image_generation import generate_location_image
            prompt_text = request.prompt or 'A detailed view of the selected region, detailed and high-resolution.'
            gen_result = await generate_location_image(prompt=prompt_text, provider=request.provider or 'stablediffusion', model=request.model)
            final_image = gen_result.get('image') or crop_b64
            return {
                'image_base64': final_image,
                'crop_base64': crop_b64,
                'provider': gen_result.get('provider'),
                'prompt_used': gen_result.get('prompt')
            }
        except Exception as gen_err:
            logger.exception('Image provider failed during crop-and-generate')
            # Return the cropped image as fallback and include error message
            return {
                'image_base64': crop_b64,
                'crop_base64': crop_b64,
                'provider': None,
                'prompt_used': request.prompt,
                'error': str(gen_err)
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Crop and generate failed')
        raise HTTPException(status_code=500, detail=f'Crop-and-generate error: {str(e)}')


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


@router.get("/options/", response_model=PromptOptionsResponse)
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


@router.get("/variations/")
async def get_prompt_variations():
    """Get all available prompt variations organized by genre.
    
    Returns 30 variations total:
    - 10 Fantasy variations (High Fantasy, Dark Fantasy, Urban Fantasy, etc.)
    - 10 Sci-Fi variations (Space Opera, Cyberpunk, Hard Sci-Fi, etc.)
    - 10 Historical variations (Ancient, Medieval, Renaissance, etc.)
    """
    logger.info("GET /api/generate/variations - Fetching prompt variations")
    return list_all_variation_names()


@router.get("/cultural-origins/")
async def get_cultural_origins():
    """Get all available cultural origins for character generation, organized by region.
    
    Returns 50+ cultural origins across:
    - African cultures (West African, East African, North African, etc.)
    - Asian cultures (Chinese, Japanese, Indian, Southeast Asian, etc.)
    - Middle Eastern cultures (Arabian, Persian, Turkish, etc.)
    - European cultures (Mediterranean, Nordic, Celtic, etc.)
    - Americas cultures (Indigenous, Mesoamerican, Caribbean, etc.)
    - Pacific cultures (Polynesian, Aboriginal Australian, Maori, etc.)
    
    All content is in English for accessibility while maintaining cultural authenticity.
    """
    try:
        logger.info("GET /api/generate/cultural-origins - Fetching cultural origins")
        result = list_cultural_origin_names()
        logger.info(f"Successfully fetched {len(result)} cultural origins")
        return result
    except Exception as e:
        logger.error(f"Error fetching cultural origins: {e}", exc_info=True)
        raise


@router.post("/character", response_model=GenerationResponse)
async def generate_character(request: CharacterGenerationRequest):
    """Generate a character using AI with optional genre-specific variations.
    
    Supports 30 prompt variations across 3 genres:
    - Fantasy: high_fantasy, dark_fantasy, urban_fantasy, cozy_fantasy, sword_and_sorcery, etc.
    - Sci-Fi: space_opera, cyberpunk, hard_sci_fi, post_apocalyptic_sci_fi, etc.
    - Historical: ancient_civilizations, medieval_period, renaissance, victorian_era, etc.
    
    Use GET /api/generate/variations to see all available options.
    """
    # Build prompt
    if request.base_content and request.refinement_instructions:
        prompt = PromptTemplates.refinement_prompt(
            request.base_content,
            request.refinement_instructions
        )
    else:
        # Build base prompt
        base_prompt = PromptTemplates.character_prompt(
            themes=request.themes,
            personality_traits=request.personality_traits,
            physical_traits=request.physical_traits,
            archetype=request.archetype,
            custom_details=request.custom_details
        )
        
        # Enhance with genre variation if specified
        if request.genre and request.variation:
            logger.info(f"Enhancing prompt with {request.genre}/{request.variation}")
            prompt = build_enhanced_character_prompt(base_prompt, request.genre, request.variation)
        else:
            prompt = base_prompt
        
        # Further enhance with cultural origin if specified
        if request.cultural_origin:
            logger.info(f"Adding cultural depth with {request.cultural_origin}")
            prompt = build_culturally_enhanced_prompt(prompt, request.cultural_origin)
    
    # Generate with LLM
    content, metadata = await call_llm(prompt, request.provider, request.model)
    
    # Add variation info to metadata
    if request.genre and request.variation:
        metadata["genre"] = request.genre
        metadata["variation"] = request.variation
    if request.cultural_origin:
        metadata["cultural_origin"] = request.cultural_origin
    
    return GenerationResponse(
        content=content,
        prompt_used=prompt,
        provider=request.provider,
        model=metadata.get("model", "unknown"),
        timestamp=datetime.now(),
        tokens_used=metadata.get("tokens", None),
        generation_metadata=metadata
    )


class NameGenerationRequest(BaseModel):
    provider: str = "groq"
    model: Optional[str] = None
    # Context fields (optional) to influence naming
    species: Optional[str] = None
    background: Optional[str] = None
    class_name: Optional[str] = None


@router.post("/names/")
async def generate_names(request: NameGenerationRequest):
    """Generate and return a validated list of 6 distinct name options.

    This endpoint will call the configured LLM provider, parse the JSON
    array from the response, and retry up to 3 times if near-duplicate
    names are detected.
    """
    # Build D&D-specific prompt when context is provided, otherwise use generic
    try:
        if request.species or request.class_name or request.background:
            from dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect
            builder = DnDNarrativePromptBuilder({
                "dnd_species": request.species or "human",
                "dnd_class": request.class_name or "commoner",
                "dnd_background": request.background or "common"
            })
            prompt = builder.build_prompt(NarrativeAspect.NAME)
        else:
            # Generic name prompt
            prompt = (
                "Generate 6 distinct character names in JSON array format. "
                "Return an array of objects with keys: first_name, surname, title, formal, origin, meaning. "
                "Avoid obvious shared stems and ensure phonetic variety."
            )

        max_attempts = 3
        attempt = 0
        last_error = None

        while attempt < max_attempts:
            attempt += 1
            response_text, metadata = await call_llm(prompt, request.provider, request.model)

            # Try to parse JSON array
            try:
                options = extract_json_array_from_text(response_text)
            except Exception as e:
                last_error = e
                # If parse failed, retry
                continue

            # Check for near-duplicates
            retry_needed, pairs = needs_retry_from_text(response_text)
            if not retry_needed:
                return {"names": options, "provider": metadata.get("provider"), "model": metadata.get("model"), "attempts": attempt}

            # If retry needed and attempts remain, loop to try again
            last_error = RuntimeError(f"Duplicate name pairs detected: {pairs}")

        # If we exit loop, all attempts failed
        raise HTTPException(status_code=500, detail=f"Failed to generate distinct names after {max_attempts} attempts: {str(last_error)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Name generation failed")
        raise HTTPException(status_code=500, detail=f"Name generation error: {str(e)}")


@router.post("/character/save/")
async def save_character(
    name: str,
    content: str,
    portrait_image: str = None,
    image_prompt: str = None,
    story_id: int = None,
    db: Session = Depends(get_db)
):
    """Save a generated character to the database"""
    try:
        logger.info(f"Saving character: {name}, content length: {len(content)}, story_id: {story_id}, has_portrait: {portrait_image is not None}")
        
        # Parse content to extract fields (basic implementation)
        character = Character(
            name=name,
            description=content,
            portrait_image=portrait_image,
            image_prompt=image_prompt,
            # Note: story_id is not a direct field in Character model
            # Characters are linked to stories via many-to-many relationship
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(content),
                "has_portrait": portrait_image is not None
            }])
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        
        # If story_id is provided, link the character to the story
        # This would require additional logic to add to story_characters table
        
        logger.info(f"Character saved successfully with ID: {character.id}")
        return {"id": character.id, "message": "Character saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save character: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save character: {str(e)}")


@router.post("/character/generate-portrait/")
async def generate_character_portrait_endpoint(request: ImageGenerationRequest):
    """
    Generate a character portrait using OpenAI (GPT Image/DALL-E) or Google Imagen.
    
    This endpoint generates a portrait image based on the character's appearance
    description using the specified provider.
    
    Providers:
    - "openai": GPT Image (gpt-4.1-mini) or DALL-E (dall-e-2, dall-e-3)
    - "google": Google Imagen (imagen-4.0-fast/standard/ultra)
    
    Style Presets:
    - realistic: Professional portrait photograph
    - fantasy_art: Fantasy digital painting
    - anime: Anime/manga style
    - watercolor: Watercolor painting
    - oil_painting: Classical oil painting
    - digital_art: Modern digital illustration
    - comic_book: Comic book style
    - noir: Film noir black and white
    """
    try:
        from openai_image_client import generate_portrait_with_provider
        
        result = await generate_portrait_with_provider(
            character_name=request.character_name,
            appearance_text=request.appearance_text,
            provider=request.provider,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            custom_prompt=request.custom_prompt,
            style_preset=request.style_preset,
            quality=request.quality
        )
        
        return {
            "image_base64": result["image_base64"],
            "prompt": result["prompt"],
            "model": result["model"],
            "provider": request.provider,
            "aspect_ratio": request.aspect_ratio,
            "style_preset": request.style_preset,
            "quality": request.quality,
            "message": "Portrait generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Portrait generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate portrait: {str(e)}"
        )


@router.post("/character/save-portrait/")
async def save_character_portrait(
    request: dict,
    db: Session = Depends(get_db)
):
    """Save generated portrait to existing character"""
    try:
        character_id = request.get("character_id")
        image_base64 = request.get("image_base64")
        image_prompt = request.get("image_prompt")
        
        if not character_id:
            raise HTTPException(status_code=400, detail="character_id is required")
        
        character = db.query(Character).filter(Character.id == character_id).first()
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Update character with portrait
        if image_base64:
            character.portrait_image = image_base64
        if image_prompt:
            character.image_prompt = image_prompt
        character.updated_at = datetime.now()
        
        db.commit()
        db.refresh(character)
        
        return {"message": "Portrait saved successfully", "character_id": character_id}
        
    except HTTPException:
        raise
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


@router.post("/story/save/")
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


@router.post("/world/save/")
async def save_world(
    name: str,
    content: str,
    world_image: str = None,
    image_prompt: str = None,
    world_map: str = None,
    description: str = None,
    db: Session = Depends(get_db)
):
    """Save a generated world to the database"""
    try:
        world = World(
            name=name,
            description=description or content[:500],
            lore=content,
            world_image=world_image,
            image_prompt=image_prompt,
            world_map=world_map,
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


@router.post("/scene/save/")
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


@router.post("/chapter/save/")
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


@router.post("/location/save/")
async def save_location(
    name: str,
    content: str,
    world_id: int,
    location_image: str = None,
    image_prompt: str = None,
    coordinates: str | None = None,
    db: Session = Depends(get_db)
):
    """Save a generated location to the database"""
    try:
        location = Location(
            name=name,
            description=content,
            world_id=world_id,
            location_image=location_image,
            image_prompt=image_prompt,
            coordinates=coordinates,
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


async def call_llm_structured(
    prompt: str,
    provider: str,
    schema_model: Type[BaseModel],
    model: str = None,
    max_tokens: int = 3000,
    temperature: float = 0.9
) -> tuple[BaseModel, Dict[str, Any]]:
    """
    Call the specified LLM provider with structured output support.
    Returns (parsed_model_instance, metadata)
    
    Args:
        prompt: The generation prompt
        provider: LLM provider name (openai, google, groq, anthropic)
        schema_model: Pydantic model class for structured output (CharacterProfile or WorldProfile)
        model: Optional specific model name
        max_tokens: Maximum tokens for response (default 3000 for structured outputs)
        temperature: Temperature for generation (default 0.9 for creativity)
    
    Returns:
        Tuple of (validated Pydantic model instance, metadata dict)
    
    Raises:
        HTTPException: If rate limit exceeded, validation fails, or generation fails
    """
    try:
        # Estimate tokens (higher for structured outputs)
        estimated_tokens = len(prompt) // 4 + max_tokens
        
        # Check rate limits
        rate_limit_error = rate_limiter.check_rate_limit(provider, estimated_tokens)
        if rate_limit_error:
            logger.warning(f"Rate limit exceeded for {provider}: {rate_limit_error}")
            raise HTTPException(
                status_code=429,
                detail=rate_limit_error
            )
        
        # Check if provider supports structured outputs
        if supports_structured_outputs(provider):
            # Get provider-specific schema format
            schema = get_schema_for_provider(schema_model, provider)
            
            # Call provider with structured output
            if provider.lower() == "openai":
                response_text = await LLMProvider.generate_openai(
                    prompt, 
                    model or "gpt-4", 
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format=schema
                )
                metadata = {"model": model or "gpt-4", "provider": "openai", "structured": True}
            elif provider.lower() == "google" or provider.lower() == "gemini":
                response_text = await LLMProvider.generate_google(
                    prompt,
                    model or "gemini-2.0-flash",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_schema=schema
                )
                metadata = {"model": model or "gemini-2.0-flash", "provider": "google", "structured": True}
            elif provider.lower() == "groq":
                # Use Llama 4 Scout which supports structured outputs (json_schema)
                # Supported models: meta-llama/llama-4-scout-17b-16e-instruct, meta-llama/llama-4-maverick-17b-128e-instruct
                # See: https://console.groq.com/docs/structured-outputs#supported-models
                response_text = await LLMProvider.generate_groq(
                    prompt,
                    model or "meta-llama/llama-4-scout-17b-16e-instruct",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format=schema
                )
                metadata = {"model": model or "meta-llama/llama-4-scout-17b-16e-instruct", "provider": "groq", "structured": True}
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        else:
            # Fallback for providers without native structured output support (e.g., Anthropic)
            logger.info(f"Provider {provider} doesn't support structured outputs, using prompt-based approach")
            enhanced_prompt = get_structured_output_prompt(schema_model) + "\n\n" + prompt
            
            if provider.lower() == "anthropic":
                response_text = await LLMProvider.generate_anthropic(
                    enhanced_prompt,
                    model or "claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                metadata = {"model": model or "claude-3-5-sonnet-20241022", "provider": "anthropic", "structured": False}
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        # Parse and validate the response
        try:
            parsed_model = parse_structured_response(response_text, schema_model)
        except Exception as validation_error:
            logger.error(f"Structured output validation failed: {str(validation_error)}")
            logger.error(f"Response content: {response_text[:500]}...")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse structured output: {str(validation_error)}"
            )
        
        # Record successful request
        actual_tokens = len(response_text) // 4
        rate_limiter.record_request(provider, actual_tokens)
        
        return parsed_model, metadata
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Structured LLM generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Structured LLM generation failed: {str(e)}")


@router.post("/character/structured", response_model=CharacterProfile)
async def generate_character_structured(request: CharacterGenerationRequest):
    """
    Generate a character using AI with structured output.
    
    This endpoint uses structured output schemas to guarantee that ALL fields
    in the CharacterProfile are populated with complete, specific details.
    This prevents issues like incomplete generation or missing sections.
    
    Supported providers:
    - OpenAI (gpt-4, gpt-4-turbo, gpt-3.5-turbo) - Native structured output
    - Google/Gemini (gemini-2.0-flash, gemini-2.5-pro) - Native structured output
    - Groq (openai/gpt-oss-20b, openai/gpt-oss-120b, kimi/kimi-8-02, llama-4-maverick, llama-4-scout) - Native structured output
    - Anthropic (claude-3-5-sonnet) - Prompt-based structured output
    
    Returns a fully validated CharacterProfile with all required fields populated.
    """
    # Build prompt using structured output optimized template
    prompt = PromptTemplates.character_structured_prompt(
        themes=request.themes,
        personality_traits=request.personality_traits,
        physical_traits=request.physical_traits,
        archetype=request.archetype,
        custom_details=request.custom_details
    )
    
    # Generate with structured output
    character_profile, metadata = await call_llm_structured(
        prompt=prompt,
        provider=request.provider,
        schema_model=CharacterProfile,
        model=request.model,
        max_tokens=3500  # Higher token limit for comprehensive character profiles
    )
    
    logger.info(f"Generated structured character profile using {metadata.get('provider')} - {metadata.get('model')}")
    
    # Return the validated CharacterProfile directly
    # The FastAPI response_model will serialize it to JSON
    return character_profile


@router.post("/world/structured", response_model=WorldProfile)
async def generate_world_structured(request: WorldGenerationRequest):
    """
    Generate a world using AI with structured output.
    
    This endpoint uses structured output schemas to guarantee that ALL fields
    in the WorldProfile are populated with rich, immersive details.
    This ensures comprehensive worldbuilding with no missing sections.
    
    Supported providers:
    - OpenAI (gpt-4, gpt-4-turbo, gpt-3.5-turbo) - Native structured output
    - Google/Gemini (gemini-2.0-flash, gemini-2.5-pro) - Native structured output
    - Groq (openai/gpt-oss-20b, openai/gpt-oss-120b, kimi/kimi-8-02, llama-4-maverick, llama-4-scout) - Native structured output
    - Anthropic (claude-3-5-sonnet) - Prompt-based structured output
    
    Returns a fully validated WorldProfile with all required fields populated.
    """
    # Build prompt using structured output optimized template
    prompt = PromptTemplates.world_structured_prompt(
        themes=request.themes,
        setting=request.setting,
        elements=request.elements,
        custom_details=request.custom_details
    )
    
    # Generate with structured output
    world_profile, metadata = await call_llm_structured(
        prompt=prompt,
        provider=request.provider,
        schema_model=WorldProfile,
        model=request.model,
        max_tokens=4000  # Higher token limit for comprehensive world profiles
    )
    
    logger.info(f"Generated structured world profile using {metadata.get('provider')} - {metadata.get('model')}")
    
    # Return the validated WorldProfile directly
    # The FastAPI response_model will serialize it to JSON
    return world_profile


@router.post("/world/generate-landscape/")
async def generate_world_landscape(
    world_name: str,
    description: str,
    landscape_type: str = "overview",
    provider: str = "stablediffusion",
    model: str | None = None,
    style_preset: str = "fantasy-art",
):
    """
    Generate a landscape image for a world
    """
    try:
        from prompts import build_landscape_prompt
        from image_generation import generate_landscape_image

        prompt, negative = build_landscape_prompt(
            world_name, description, landscape_type, style_preset
        )

        image_data = await generate_landscape_image(
            prompt=prompt,
            provider=provider,
            model=model,
            aspect_ratio="16:9" if landscape_type == "overview" else "1:1",
        )

        return {
            "image_base64": image_data.get("image"),
            "prompt": image_data.get("prompt") or prompt,
            "provider": image_data.get("provider"),
            "model": image_data.get("model"),
        }
    except Exception as e:
        logger.error(f"Landscape generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate landscape: {str(e)}")


@router.post("/location/generate-image/")
async def generate_location_image_endpoint(
    location_name: str,
    location_type: str,
    description: str,
    time_of_day: str = "day",
    weather: str = "clear",
    provider: str = "stablediffusion",
    model: str | None = None,
    style_preset: str = "realistic",
):
    """
    Generate an image for a location (city, dungeon, etc.)
    """
    try:
        from prompts import build_location_image_prompt
        from image_generation import generate_location_image

        prompt, negative = build_location_image_prompt(
            location_name, location_type, description, time_of_day, weather, style_preset
        )

        image_data = await generate_location_image(
            prompt=prompt,
            provider=provider,
            model=model,
            aspect_ratio="16:9",
        )

        return {
            "image_base64": image_data.get("image"),
            "prompt": image_data.get("prompt") or prompt,
            "provider": image_data.get("provider"),
            "model": image_data.get("model"),
        }
    except Exception as e:
        logger.error(f"Location image generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate location image: {str(e)}")


class CharacterSaveRequest(BaseModel):
    """Request model for saving a structured character with optional portrait"""
    character_profile: CharacterProfile
    portrait_image: Optional[str] = None
    image_prompt: Optional[str] = None
    story_id: Optional[int] = None


@router.post("/character/structured/save/")
async def save_structured_character(
    request: CharacterSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save a structured character profile to the database.
    
    This endpoint accepts a full CharacterProfile object and stores it in the database
    with both legacy fields (for backward compatibility) and the full structured_data JSON.
    
    Args:
        request: CharacterSaveRequest containing character_profile and optional portrait data
        db: Database session
    
    Returns:
        Dictionary with character ID and success message
    """
    character_profile = request.character_profile
    portrait_image = request.portrait_image
    image_prompt = request.image_prompt
    story_id = request.story_id
    
    try:
        logger.info(f"Saving structured character: {character_profile.name}")
        
        # Convert CharacterProfile to dict for JSON storage
        structured_dict = character_profile.model_dump()
        
        # Create character with both legacy fields and structured data
        character = Character(
            name=character_profile.name,
            # Legacy fields for backward compatibility
            description=character_profile.physical_description + "\n\n" + character_profile.personality_description,
            background=character_profile.backstory,
            personality=character_profile.personality_description,
            appearance=character_profile.physical_description,
            motivations=character_profile.primary_motivation,
            relationships=character_profile.key_relationships,  # Already a list of dicts
            # New structured data field
            structured_data=structured_dict,
            # Portrait data
            portrait_image=portrait_image,
            image_prompt=image_prompt,
            generation_log=[{
                "timestamp": datetime.now().isoformat(),
                "action": "created_structured",
                "provider": "structured_generation",
                "has_portrait": portrait_image is not None
            }]
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        
        # Link to story if provided
        if story_id:
            from models import Story
            story = db.query(Story).filter(Story.id == story_id).first()
            if story:
                story.characters.append(character)
                db.commit()
                logger.info(f"Linked character {character.id} to story {story_id}")
        
        logger.info(f"Structured character saved successfully with ID: {character.id}")
        return {
            "id": character.id,
            "message": "Structured character saved successfully",
            "structured": True
        }
    
    except Exception as e:
        logger.error(f"Failed to save structured character: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save structured character: {str(e)}"
        )


@router.post("/world/structured/save/")
async def save_structured_world(
    world_profile: WorldProfile,
    story_id: int = None,
    world_image: str | None = None,
    image_prompt: str | None = None,
    world_map: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Save a structured world profile to the database.
    
    This endpoint accepts a full WorldProfile object and stores it in the database
    with both legacy fields (for backward compatibility) and the full structured_data JSON.
    
    Args:
        world_profile: Validated WorldProfile from structured generation
        story_id: Optional story ID to link the world to
        db: Database session
    
    Returns:
        Dictionary with world ID and success message
    """
    try:
        logger.info(f"Saving structured world: {world_profile.name}")
        
        # Convert WorldProfile to dict for JSON storage
        structured_dict = world_profile.model_dump()
        
        # Create world with both legacy fields and structured data
        world = World(
            name=world_profile.name,
            # Legacy fields for backward compatibility
            description=world_profile.overview,
            lore=world_profile.lore_summary,
            history=world_profile.history_summary,
            geography=world_profile.geography_summary,
            culture=world_profile.culture_summary,
            magic_system=world_profile.power_system + " (" + world_profile.power_level + ")",
            technology_level=world_profile.world_type,
            # New structured data field
            structured_data=structured_dict,
            world_image=world_image,
            image_prompt=image_prompt,
            world_map=world_map,
            generation_log=[{
                "timestamp": datetime.now().isoformat(),
                "action": "created_structured",
                "provider": "structured_generation"
            }]
        )
        
        db.add(world)
        db.commit()
        db.refresh(world)
        
        # Link to story if provided
        if story_id:
            from models import Story
            story = db.query(Story).filter(Story.id == story_id).first()
            if story:
                story.worlds.append(world)
                db.commit()
                logger.info(f"Linked world {world.id} to story {story_id}")
        
        logger.info(f"Structured world saved successfully with ID: {world.id}")
        return {
            "id": world.id,
            "message": "Structured world saved successfully",
            "structured": True
        }
    
    except Exception as e:
        logger.error(f"Failed to save structured world: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save structured world: {str(e)}"
        )


# ============================================================================
# D&D NARRATIVE GENERATION ENDPOINTS
# ============================================================================

class DnDNarrativeRequest(BaseModel):
    """Request for generating D&D character narrative aspects"""
    character_id: int
    aspect: str  # appearance, personality, backstory, etc.
    style: str = "detailed"  # concise, detailed, dramatic, poetic, gritty
    custom_context: Optional[str] = None
    provider: str = "groq"
    model: Optional[str] = None


@router.post("/dnd/narrative/")
async def generate_dnd_narrative(request: DnDNarrativeRequest, db: Session = Depends(get_db)):
    """
    Generate AI-enhanced narrative aspects for a D&D character.
    
    Aspects include: appearance, personality, backstory, motivations, quirks,
    voice, beliefs, relationships, fears, dreams, secrets, name
    
    The prompts are context-aware and informed by the character's D&D stats,
    class, species, background, and alignment.
    """
    from dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect, NarrativeStyle
    
    try:
        # Get character from database
        character = db.query(Character).filter(Character.id == request.character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        if not character.is_dnd:
            raise HTTPException(status_code=400, detail="Character is not a D&D character")
        
        # Build character data dict
        character_data = {
            "name": character.name,
            "dnd_class": character.dnd_class,
            "dnd_species": character.dnd_species,
            "dnd_background": character.dnd_background,
            "dnd_alignment": character.dnd_alignment,
            "dnd_level": character.dnd_level,
            "dnd_ability_scores": character.dnd_ability_scores or {},
        }
        
        # Validate aspect
        try:
            aspect_enum = NarrativeAspect(request.aspect.lower())
        except ValueError:
            valid_aspects = [a.value for a in NarrativeAspect]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid aspect '{request.aspect}'. Valid options: {', '.join(valid_aspects)}"
            )
        
        # Validate style
        try:
            style_enum = NarrativeStyle(request.style.lower())
        except ValueError:
            valid_styles = [s.value for s in NarrativeStyle]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style '{request.style}'. Valid options: {', '.join(valid_styles)}"
            )
        
        # Build prompt
        builder = DnDNarrativePromptBuilder(character_data)
        prompt = builder.build_prompt(
            aspect=aspect_enum,
            style=style_enum,
            custom_context=request.custom_context
        )
        
        # Generate with LLM
        llm_provider = LLMProvider()
        
        # Use provided model or default for provider
        model = request.model
        if not model:
            if request.provider == "groq":
                model = "llama-3.3-70b-versatile"
            elif request.provider == "google":
                model = "gemini-2.0-flash-exp"
            elif request.provider == "openai":
                model = "gpt-4o-mini"
        
        result = await llm_provider.generate_text(
            provider=request.provider,
            model=model,
            prompt=prompt,
            max_tokens=800
        )
        
        generated_text = result.get("text") or result.get("content") or ""
        
        return {
            "aspect": request.aspect,
            "style": request.style,
            "content": generated_text,
            "prompt_used": prompt,
            "character_id": character.id,
            "character_name": character.name,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"D&D narrative generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate D&D narrative: {str(e)}"
        )


class BulkDnDNarrativeRequest(BaseModel):
    """Request for generating multiple D&D narrative aspects at once"""
    character_id: int
    aspects: list[str]  # List of aspects to generate
    style: str = "detailed"
    custom_context: Optional[str] = None
    provider: str = "groq"
    model: Optional[str] = None


@router.post("/dnd/narrative/bulk/")
async def generate_bulk_dnd_narrative(request: BulkDnDNarrativeRequest, db: Session = Depends(get_db)):
    """
    Generate multiple AI-enhanced narrative aspects for a D&D character in one request.
    
    This endpoint generates all requested aspects in parallel for efficiency.
    """
    from dnd_narrative_prompts import DnDNarrativePromptBuilder, NarrativeAspect, NarrativeStyle
    import asyncio
    
    try:
        # Get character from database
        character = db.query(Character).filter(Character.id == request.character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        if not character.is_dnd:
            raise HTTPException(status_code=400, detail="Character is not a D&D character")
        
        # Build character data dict
        character_data = {
            "name": character.name,
            "dnd_class": character.dnd_class,
            "dnd_species": character.dnd_species,
            "dnd_background": character.dnd_background,
            "dnd_alignment": character.dnd_alignment,
            "dnd_level": character.dnd_level,
            "dnd_ability_scores": character.dnd_ability_scores or {},
        }
        
        # Validate aspects
        aspect_enums = []
        for aspect in request.aspects:
            try:
                aspect_enums.append(NarrativeAspect(aspect.lower()))
            except ValueError:
                valid_aspects = [a.value for a in NarrativeAspect]
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid aspect '{aspect}'. Valid options: {', '.join(valid_aspects)}"
                )
        
        # Validate style
        try:
            style_enum = NarrativeStyle(request.style.lower())
        except ValueError:
            valid_styles = [s.value for s in NarrativeStyle]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style '{request.style}'. Valid options: {', '.join(valid_styles)}"
            )
        
        # Build all prompts
        builder = DnDNarrativePromptBuilder(character_data)
        prompts = {}
        for aspect_enum in aspect_enums:
            prompts[aspect_enum.value] = builder.build_prompt(
                aspect=aspect_enum,
                style=style_enum,
                custom_context=request.custom_context
            )
        
        # Generate all aspects in parallel
        llm_provider = LLMProvider()
        
        # Use provided model or default for provider
        model = request.model
        if not model:
            if request.provider == "groq":
                model = "llama-3.3-70b-versatile"
            elif request.provider == "google":
                model = "gemini-2.0-flash-exp"
            elif request.provider == "openai":
                model = "gpt-4o-mini"
        
        async def generate_aspect(aspect_name: str, prompt: str):
            result = await llm_provider.generate_text(
                provider=request.provider,
                model=model,
                prompt=prompt,
                max_tokens=800
            )
            return {
                "aspect": aspect_name,
                "content": result.get("text") or result.get("content") or "",
            }
        
        # Generate all in parallel
        tasks = [generate_aspect(aspect, prompt) for aspect, prompt in prompts.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        narratives = {}
        errors = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Aspect generation failed: {str(result)}")
                errors[str(result)] = str(result)
            else:
                narratives[result["aspect"]] = result["content"]
        
        return {
            "character_id": character.id,
            "character_name": character.name,
            "style": request.style,
            "narratives": narratives,
            "errors": errors if errors else None,
            "success_count": len(narratives),
            "total_count": len(request.aspects),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk D&D narrative generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate D&D narratives: {str(e)}"
        )


@router.get("/dnd/narrative/aspects/")
async def get_narrative_aspects():
    """Get list of available D&D narrative aspects that can be generated"""
    from dnd_narrative_prompts import NarrativeAspect
    
    aspects = []
    for aspect in NarrativeAspect:
        aspects.append({
            "id": aspect.value,
            "name": aspect.value.replace("_", " ").title(),
            "description": get_aspect_description(aspect.value)
        })
    
    return {
        "aspects": aspects,
        "count": len(aspects)
    }


@router.get("/dnd/narrative/styles/")
async def get_narrative_styles():
    """Get list of available narrative generation styles"""
    from dnd_narrative_prompts import NarrativeStyle
    
    styles = []
    for style in NarrativeStyle:
        styles.append({
            "id": style.value,
            "name": style.value.title(),
            "description": get_style_description(style.value)
        })
    
    return {
        "styles": styles,
        "count": len(styles)
    }


def get_aspect_description(aspect: str) -> str:
    """Get description for a narrative aspect"""
    descriptions = {
        "appearance": "Physical description including body build, facial features, distinctive marks, and typical attire",
        "personality": "Core personality traits, behavioral patterns, social tendencies, and emotional characteristics",
        "backstory": "Origin story, formative experiences, key relationships, and path to becoming an adventurer",
        "motivations": "Primary goals, desires, ambitions, and what drives the character to adventure",
        "quirks": "Unique habits, mannerisms, speech patterns, and memorable behavioral traits",
        "voice": "Speaking style, vocabulary, accent, common phrases, and vocal characteristics",
        "beliefs": "Moral code, religious views, political leanings, and personal philosophy",
        "relationships": "Important connections to family, mentors, rivals, and social groups",
        "fears": "Deep-seated fears, phobias, insecurities, and vulnerabilities",
        "dreams": "Ultimate aspirations, ideal future vision, and legacy desires",
        "secrets": "Hidden aspects, past mistakes, concealed knowledge, and guarded information",
        "name": "Character name with cultural and background-appropriate naming conventions",
    }
    return descriptions.get(aspect, "Character narrative aspect")


def get_style_description(style: str) -> str:
    """Get description for a narrative style"""
    descriptions = {
        "concise": "Brief, to-the-point descriptions focusing on essential details",
        "detailed": "Rich, comprehensive descriptions with vivid imagery and context",
        "dramatic": "Epic, theatrical storytelling with heightened emotion and stakes",
        "poetic": "Lyrical, metaphorical language with artistic flair",
        "gritty": "Dark, realistic, grounded descriptions emphasizing harsh realities",
    }
    return descriptions.get(style, "Narrative writing style")

