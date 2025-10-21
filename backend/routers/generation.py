"""
AI Generation Router - Endpoints for intelligent story element creation.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Type, Optional, List
import json
from pydantic import BaseModel

from ..database import get_db
from ..models import Character, Story, World, Scene, Chapter, Location
from ..schemas import (
    CharacterGenerationRequest,
    StoryGenerationRequest,
    WorldGenerationRequest,
    SceneGenerationRequest,
    ChapterGenerationRequest,
    LocationGenerationRequest,
    LocationImageRequest,
    SaveLocationRequest,
    CampaignGenerationRequest,
    GenerationResponse,
    PromptOptionsResponse,
    ImageGenerationRequest,
    CharacterProfile,
    WorldProfile,
)
from ..prompts import (
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
    CONFLICT_TYPES,
)
from ..prompt_variations import (
    list_all_variation_names,
    build_enhanced_character_prompt,
)
from ..cultural_modules import (
    list_cultural_origin_names,
    build_culturally_enhanced_prompt,
)
from .llm import LLMProvider
from ..rate_limiter import rate_limiter
from ..structured_output_utils import (
    get_schema_for_provider,
    parse_structured_response,
    supports_structured_outputs,
    get_structured_output_prompt,
)
from ..model_capabilities import supports_model_structured, get_model_output_limit
from ..structured_normalizer import normalize_and_validate
import asyncio
from ..audit import write_audit_event
from ..name_generation_utils import (
    extract_json_array_from_text,
    needs_retry_from_text,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generate", tags=["generation"])

# Simple in-memory circuit-breaker state per provider to avoid hammering a rate-limited provider
_provider_circuit = {}


async def call_llm_with_provider_fallback(prompt: str, providers: list[str], model: str | None = None, max_retries: int = 2):
    """Try a list of providers in order. On transient errors (HTTP 429), backoff and try the next provider.

    Returns (response_text, metadata)
    """
    last_exc = None
    for prov in providers:
        # If provider is tripped in the circuit breaker, skip it for a short duration
        state = _provider_circuit.get(prov, {})
        if state.get('tripped'):
            # skip provider if still in cooldown
            if state.get('resume_at', 0) > asyncio.get_event_loop().time():
                logger.info(f"Skipping provider {prov} due to circuit open until {state.get('resume_at')}")
                continue
            else:
                # reset circuit for this provider
                _provider_circuit.pop(prov, None)

        attempts = 0
        backoff = 1.0
        while attempts <= max_retries:
            attempts += 1
            try:
                text, metadata = await call_llm(prompt, prov, model)
                return text, metadata
            except HTTPException as he:
                # Only handle 429 as transient; otherwise bubble up
                detail = getattr(he, 'detail', None)
                if isinstance(detail, dict) and detail.get('error') == 'rate_limit_exceeded':
                    last_exc = he
                    logger.warning(f"Provider {prov} rate-limited: {detail}")
                    # trip circuit for this provider for a short cooldown
                    cooldown = min(30, int(backoff * 5))
                    _provider_circuit[prov] = {'tripped': True, 'resume_at': asyncio.get_event_loop().time() + cooldown}
                    break  # try next provider
                else:
                    # non-rate-limit HTTPException: rethrow
                    raise
            except Exception as e:
                last_exc = e
                logger.exception(f"Error calling provider {prov}: {e}")
                await asyncio.sleep(backoff)
                backoff *= 2

    # If we exhausted providers, raise the last exception
    if last_exc:
        raise last_exc
    raise HTTPException(status_code=500, detail="LLM providers exhausted")


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
        from sqlalchemy import text

        row = db.execute(
            text("SELECT world_map FROM worlds WHERE id = :wid"),
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
        from sqlalchemy import text

        row = db.execute(
            text("SELECT world_map FROM worlds WHERE id = :wid"),
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
            from ..image_generation import generate_location_image
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
        
        prov = provider.lower()
        # Simple provider-canonicalization
        if prov == "openai":
            response_text = await LLMProvider.generate_openai(prompt, model or "gpt-4")
            metadata = {"model": model or "gpt-4", "provider": "openai"}
        elif prov == "anthropic":
            response_text = await LLMProvider.generate_anthropic(prompt, model or "claude-3-5-sonnet-20241022")
            metadata = {"model": model or "claude-3-5-sonnet-20241022", "provider": "anthropic"}
        elif prov == "google":
            response_text = await LLMProvider.generate_google(prompt, model or "gemini-2.0-flash")
            metadata = {"model": model or "gemini-2.0-flash", "provider": "google"}
        elif prov == "groq":
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


async def call_llm_with_retries_and_clarifier(
    base_prompt: str,
    provider: str,
    schema_model: Type[BaseModel] | None = None,
    model: Optional[str] = None,
    max_attempts: int = 3,
    initial_temperature: float = 0.95,
    retry_temperature: float = 0.6,
    authoritative_fields: Optional[Dict[str, Any]] = None,
):
    """
    Helper that calls structured LLM output with a retry loop and an appended clarifier
    when the model returns conflicting authoritative fields.

    Returns a tuple: (parsed_structured_model_or_dict, metadata)
    If schema_model is provided the returned structured object will be the parsed Pydantic model.
    """
    attempt = 0
    prompt = base_prompt
    last_exc = None
    last_structured = None
    last_metadata = None

    while attempt < max_attempts:
        attempt += 1
        try:
            # Use structured helper when schema_model is provided
            if schema_model:
                # Use provider fallback-aware call for structured requests
                structured_obj, metadata = await call_llm_structured_inner(
                    prompt=prompt,
                    provider=provider,
                    schema_model=schema_model,
                    model=model,
                    max_tokens=3000,
                    temperature=(initial_temperature if attempt == 1 else retry_temperature),
                )

                # Convert to dict for validation checks
                structured_dict = (
                    structured_obj.model_dump()
                    if hasattr(structured_obj, "model_dump")
                    else (structured_obj.dict() if hasattr(structured_obj, "dict") else dict(structured_obj))
                )

                # If authoritative fields supplied, check for conflicts
                conflict = False
                if authoritative_fields:
                    for key, val in authoritative_fields.items():
                        if val is None:
                            continue
                        llm_val = structured_dict.get(key)
                        if llm_val is not None and str(llm_val) != str(val):
                            conflict = True
                            break

                if not conflict:
                    return structured_obj, metadata

                # Save last seen structured output so we can return it if retries
                # are exhausted but we still want to surface suggestions to callers.
                last_structured = structured_obj
                last_metadata = metadata

                # If conflict, append clarifier and retry
                clarifier_lines = [
                    "\n\nCLARIFICATION: The following fields were provided by the system and MUST be preserved exactly:",
                ]
                for k, v in (authoritative_fields or {}).items():
                    clarifier_lines.append(f"- {k}: {v}")
                clarifier_lines.append(
                    "Do NOT change or replace these values. If you cannot comply, return the JSON with an explicit field 'validation_failed': true and do not invent alternatives."
                )
                prompt = prompt + "\n" + "\n".join(clarifier_lines)
                # loop to retry with reduced temperature
                continue
            else:
                # Fallback to plain text LLM call
                text, metadata = await call_llm(prompt, provider, model)
                return text, metadata

        except Exception as e:
            last_exc = e
            logger.exception("call_llm_with_retries_and_clarifier attempt failed")
            # On error, reduce temperature and retry if attempts remain
            if attempt >= max_attempts:
                break
            prompt = prompt + "\n\nCLARIFICATION: Please respond in valid JSON and preserve authoritative fields if provided."  

    # If we reach here, either last attempt raised or conflicts remained
    if last_exc:
        raise last_exc
    # If we never had an exception but we did receive a structured object, return
    # it so callers can preserve authoritative fields and record name suggestions.
    if last_structured is not None:
        logger.warning("LLM structured generation returned conflicting authoritative fields after retries; returning last result and letting caller handle suggestions")
        return last_structured, last_metadata

    # Otherwise fail hard
    raise HTTPException(status_code=500, detail="LLM structured generation failed after retries")


async def call_llm_structured_inner(**kwargs):
    """
    Thin wrapper that reuses existing structured output utilities.
    This isolates the internal implementation so our higher-level helper can call it.
    Expected kwargs: prompt, provider, schema_model, model, max_tokens, temperature
    Returns (parsed_model_or_dict, metadata)
    """
    from ..structured_output_utils import parse_structured_response, get_structured_output_prompt

    prompt = kwargs.get("prompt")
    provider = kwargs.get("provider")
    schema_model = kwargs.get("schema_model")
    model = kwargs.get("model")
    max_tokens = kwargs.get("max_tokens", 3000)
    temperature = kwargs.get("temperature", 0.9)

    # If a project-level helper `call_llm_structured` exists (e.g., tests patch
    # backend.routers.generation.call_llm_structured), prefer calling it so
    # callers and tests can override the structured behavior. It should return
    # (parsed_obj, metadata). We try kwargs-first (most flexible) then fall
    # back to positional forms to support a variety of test helpers.
    existing = globals().get("call_llm_structured")
    if existing and callable(existing):
        # Avoid accidentally recursing into this wrapper if someone overwrote the
        # name with the same function object; however, calling the original
        # structured implementation is acceptable as a fallback.
        try:
            parsed, metadata = await existing(
                prompt=prompt,
                provider=provider,
                schema_model=schema_model,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return parsed, metadata
        except TypeError:
            # Try common positional signature
            try:
                parsed, metadata = await existing(prompt, provider, schema_model, model, max_tokens, temperature)
                return parsed, metadata
            except TypeError:
                # Try minimal signature (prompt, provider)
                try:
                    parsed, metadata = await existing(prompt, provider)
                    return parsed, metadata
                except TypeError:
                    # Give up on calling the existing helper and fallthrough to
                    # our own fallback implementation below.
                    logger.debug("Existing call_llm_structured helper refused all tried signatures; falling back to local implementation")

    # Build provider-specific prompt wrapper if needed. For providers that do not
    # support structured outputs natively, get_structured_output_prompt returns
    # a schema-aware instruction; we append the user's prompt before that schema
    # instruction so the model has context plus a strict schema to follow.
    # Guard against non-Pydantic schema_model objects used in tests by checking
    # for the Pydantic marker method before attempting to convert to JSON schema.
    if schema_model is None:
        raise ValueError("schema_model is required for structured calls")

    if not hasattr(schema_model, "model_json_schema"):
        # The provided schema_model doesn't look like a Pydantic model. In
        # testing scenarios this can be expected when tests supply fake classes
        # — raise a clear error so test patches can be adjusted, or rely on the
        # earlier attempt to call a patched helper.
        raise TypeError("schema_model does not appear to be a Pydantic model; ensure call_llm_structured is patched in tests or provide a real Pydantic model")

    schema_prompt = get_structured_output_prompt(schema_model)
    wrapped_prompt = f"{prompt}\n\n{schema_prompt}"

    # Call raw LLM with provider fallback: try the requested provider first,
    # then fall back to other providers if rate-limited.
    providers_to_try = [provider]
    # Append a safe secondary provider list (order of preference)
    for p in ("openai", "google", "anthropic", "groq"):
        if p not in providers_to_try:
            providers_to_try.append(p)

    text, metadata = await call_llm_with_provider_fallback(wrapped_prompt, providers_to_try, model=model, max_retries=1)

    # Parse into schema_model
    parsed = parse_structured_response(text, schema_model)
    return parsed, metadata


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
        from ..openai_image_client import generate_portrait_with_provider

        result = await generate_portrait_with_provider(
            character_name=request.character_name,
            appearance_text=request.appearance_text,
            provider=request.provider,
            model=request.model,
            aspect_ratio=request.aspect_ratio,
            custom_prompt=request.custom_prompt,
            style_preset=request.style_preset,
            quality=request.quality,
        )

        return {
            "image_base64": result.get("image_base64"),
            "prompt": result.get("prompt"),
            "model": result.get("model"),
            "provider": request.provider,
            "aspect_ratio": request.aspect_ratio,
            "style_preset": request.style_preset,
            "quality": request.quality,
            "message": "Portrait generated successfully",
        }

    except Exception as e:
        logger.error(f"Portrait generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate portrait: {str(e)}",
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


class FullStoryRequest(BaseModel):
    """Request to generate a full story package: world, characters, and story."""
    world_id: Optional[int] = None
    world_themes: Optional[List[str]] = None
    character_count: int = 3
    character_provider: str = "test"
    character_model: Optional[str] = None
    story_provider: str = "openai"
    story_model: Optional[str] = None
    story_length: Optional[str] = "medium"
    # Additional freeform details to include in prompts
    custom_details: Optional[str] = None


@router.post("/story/full-generate/")
async def generate_full_story(request: FullStoryRequest, db: Session = Depends(get_db)):
    """Generate a full story package.

    Flow:
    - If world_id provided and world has structured_data, use that; otherwise generate a structured world.
    - Generate N structured characters using the world's context.
    - Generate a story using the world overview and brief character bios as context.
    """
    try:
        # Resolve or create world profile
        world_profile = None
        if request.world_id:
            world = db.query(World).filter(World.id == request.world_id).first()
            if world and getattr(world, "structured_data", None):
                # If structured_data stored as dict, use directly; else leave for generation
                try:
                    world_profile = world.structured_data
                except Exception:
                    world_profile = None

        # If no profile available, call structured generator
        if not world_profile:
            # Build world prompt using structured template if available, otherwise fall back
            if hasattr(PromptTemplates, "world_structured_prompt") and callable(getattr(PromptTemplates, "world_structured_prompt")):
                wprompt = PromptTemplates.world_structured_prompt(
                    themes=request.world_themes,
                    setting=None,
                    elements=None,
                    custom_details=request.custom_details,
                )
            else:
                # Fallback to the compat world prompt
                wprompt = PromptTemplates.world_prompt(
                    themes=request.world_themes,
                    setting=None,
                    elements=None,
                    custom_details=request.custom_details,
                )
            wp, wmeta = await call_llm_structured(
                prompt=wprompt,
                provider=request.story_provider,
                schema_model=WorldProfile,
                model=request.story_model,
                max_tokens=3000,
            )
            # Convert to dict for downstream usage
            world_profile = wp.model_dump() if hasattr(wp, "model_dump") else (wp.dict() if hasattr(wp, "dict") else dict(wp))

        # Generate characters
        characters = []
        for i in range(max(1, min(10, int(request.character_count)))):
            # Add world context into the character prompt
            world_context_details = (f"World context: {world_profile.get('name', '')}. "
                                     f"Overview: {world_profile.get('overview', '')}. "
                                     f"Include role hooks for stories.")
            # Use structured template when available, otherwise fall back to enhanced builder or compat prompt
            if hasattr(PromptTemplates, "character_structured_prompt") and callable(getattr(PromptTemplates, "character_structured_prompt")):
                char_prompt = PromptTemplates.character_structured_prompt(
                    themes=None,
                    personality_traits=None,
                    physical_traits=None,
                    archetype=None,
                    custom_details=world_context_details
                )
            else:
                try:
                    char_prompt = build_enhanced_character_prompt(themes=None, personality_traits=None, physical_traits=None, archetype=None, custom_details=world_context_details)
                except Exception:
                    char_prompt = PromptTemplates.character_prompt(custom_details=world_context_details)
            try:
                cp, cmap = await call_llm_structured(
                    prompt=char_prompt,
                    provider=request.character_provider,
                    schema_model=CharacterProfile,
                    model=request.character_model,
                    max_tokens=2500,
                )
                cdict = cp.model_dump() if hasattr(cp, "model_dump") else (cp.dict() if hasattr(cp, "dict") else dict(cp))
            except Exception as ce:
                # On failure, fabricate a minimal character entry as fallback
                logging.warning(f"Character structured generation failed: {ce}")
                cdict = {
                    "name": f"Unnamed_{i+1}",
                    "age": 30,
                    "physical_description": "Unknown",
                    "personality_description": "Underspecified",
                    "primary_motivation": "Unknown",
                }
            characters.append(cdict)

        # Build story prompt including world overview and brief character bios
        char_summaries = []
        for c in characters:
            name = c.get("name") or c.get("character_name") or "Unknown"
            motive = c.get("primary_motivation") or c.get("goals", [None])[0] or "driven"
            brief = f"{name}: {motive}."
            char_summaries.append(brief)

        story_context = (
            f"World: {world_profile.get('name','Unknown')}\nOverview: {world_profile.get('overview', world_profile.get('lore',''))}\n\n"
            + "Characters:\n" + "\n".join(char_summaries)
        )

        story_prompt = PromptTemplates.story_prompt(
            themes=request.world_themes,
            tone=None,
            length=request.story_length,
            plot_structure=None,
            conflict_type=None,
            custom_details=(request.custom_details or "") + "\n\nContext:\n" + story_context,
        )

        story_text, story_meta = await call_llm(story_prompt, request.story_provider, request.story_model)

        return {
            "world": world_profile,
            "characters": characters,
            "story": {
                "content": story_text,
                "prompt_used": story_prompt,
                "provider": story_meta.get("provider"),
                "model": story_meta.get("model"),
            }
        }

    except Exception as e:
        logging.exception("Full story generation failed")
        raise HTTPException(status_code=500, detail=f"Full story generation failed: {str(e)}")


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
@router.post("/world/save")
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
@router.post("/location/", response_model=GenerationResponse)
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
@router.post("/location/save")
async def save_location(request: SaveLocationRequest, db: Session = Depends(get_db)):
    """Save a generated location to the database"""
    try:
        # Support either creating a new location or updating an existing one
        if request.location_id:
            # Update existing
            loc = db.query(Location).filter(Location.id == request.location_id).first()
            if not loc:
                raise HTTPException(status_code=404, detail="Location not found")
            if request.name:
                loc.name = request.name
            if request.content:
                loc.description = request.content
            if request.location_image:
                loc.location_image = request.location_image
            if request.image_prompt:
                loc.image_prompt = request.image_prompt
            if request.coordinates:
                loc.coordinates = request.coordinates
            loc.updated_at = datetime.now()
            db.commit()
            db.refresh(loc)
            return {"id": loc.id, "message": "Location updated successfully"}

        # Create new location
        if not (request.name and request.content and request.world_id):
            raise HTTPException(status_code=422, detail="name, content and world_id are required to create a location")

        location = Location(
            name=request.name,
            description=request.content,
            world_id=request.world_id,
            location_image=request.location_image,
            image_prompt=request.image_prompt,
            coordinates=request.coordinates,
            generation_log=json.dumps([{
                "timestamp": datetime.now().isoformat(),
                "action": "created",
                "content_length": len(request.content or "")
            }])
        )
        
        db.add(location)
        db.commit()
        db.refresh(location)
        
        return {"id": location.id, "message": "Location saved successfully"}
    except HTTPException:
        # Let FastAPI handle HTTPExceptions (validation/404/etc.) as-is
        raise
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
    # Ensure response_text/metadata exist so we never hit UnboundLocalError
    response_text: str = ""
    metadata: Dict[str, Any] = {}

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
    
        # Determine a sensible max output token budget based on model capabilities.
        # If the caller passed a max_tokens, use it as an upper bound; otherwise
        # derive a recommended budget from known model limits.
        model_limit = get_model_output_limit(provider, model, default=max_tokens if isinstance(max_tokens, int) else 3000)
        initial_max_tokens = min(max_tokens, model_limit) if isinstance(max_tokens, int) else model_limit

        # Check if provider supports structured outputs globally AND the
        # specific model is known to accept structured params. This avoids
        # sending `response_format` to models that will reject it.
        if supports_structured_outputs(provider) and supports_model_structured(provider, model):
            # Get provider-specific schema format
            schema = get_schema_for_provider(schema_model, provider)

            # Call provider with structured output. Add a small retry/backoff for transient 429 rate-limit errors
            last_exc = None
            structured_param_unsupported = False
            for attempt in range(3):
                try:
                    if provider.lower() == "openai":
                        response_text = await LLMProvider.generate_openai(
                            prompt, 
                            model or "gpt-4", 
                            max_tokens=initial_max_tokens,
                            temperature=temperature,
                            response_format=schema
                        )
                        metadata = {"model": model or "gpt-4", "provider": "openai", "structured": True}
                    elif provider.lower() == "google" or provider.lower() == "gemini":
                        response_text = await LLMProvider.generate_google(
                            prompt,
                            model or "gemini-2.0-flash",
                            max_tokens=initial_max_tokens,
                            temperature=temperature,
                            response_schema=schema
                        )
                        metadata = {"model": model or "gemini-2.0-flash", "provider": "google", "structured": True}
                    elif provider.lower() == "groq":
                        # Use Llama 4 Scout which supports structured outputs (json_schema)
                        response_text = await LLMProvider.generate_groq(
                            prompt,
                            model or "meta-llama/llama-4-scout-17b-16e-instruct",
                            max_tokens=initial_max_tokens,
                            temperature=temperature,
                            response_format=schema
                        )
                        metadata = {"model": model or "meta-llama/llama-4-scout-17b-16e-instruct", "provider": "groq", "structured": True}
                    else:
                        raise ValueError(f"Unsupported provider: {provider}")

                    # Successful call, break retry loop
                    break
                except Exception as exc:
                    # Provider SDKs (openai.BadRequestError, httpx errors, etc.) may raise
                    # provider-specific exceptions rather than FastAPI HTTPException.
                    last_exc = exc
                    # Attempt to extract a status code if present on the exception
                    status = None
                    try:
                        status = getattr(exc, 'status_code', None) or getattr(exc, 'http_status', None)
                    except Exception:
                        status = None

                    detail_str = str(exc).lower()

                    # If provider explicitly rejected the structured 'response_format' param,
                    # treat this as an unsupported feature and break to the prompt-based fallback.
                    if 'response_format' in detail_str or 'json_schema' in detail_str:
                        logger.warning(f"Provider {provider} rejected structured parameter (message contains 'response_format' or 'json_schema'). Falling back to prompt-based structured generation.")
                        structured_param_unsupported = True
                        # Audit the structured-param rejection for analysis
                        try:
                            write_audit_event('structured_param_rejection', {
                                'provider': provider,
                                'model': model,
                                'error': detail_str[:1000]
                            })
                        except Exception:
                            logger.debug('Failed to write audit event for structured_param_rejection')
                        break

                    # If rate-limited, retry with backoff
                    if status == 429 or 'rate limit' in detail_str or 'too many requests' in detail_str:
                        wait = 1.5 * (2 ** attempt)
                        logger.warning(f"Structured provider {provider} rate-limited (attempt {attempt+1}), sleeping {wait}s before retry")
                        await asyncio.sleep(wait)
                        continue

                    # Otherwise re-raise to be handled by outer logic
                    raise
            else:
                # Retries exhausted
                if last_exc:
                    raise last_exc

            # If the structured param is unsupported, switch to prompt-based flow
            if structured_param_unsupported:
                logger.info("Switching to prompt-based structured fallback due to provider/model capability.")
                # Record audit event for switching modes
                try:
                    write_audit_event('structured_fallback_switch', {
                        'provider': provider,
                        'model': model,
                        'prompt_snippet': prompt[:800]
                    })
                except Exception:
                    logger.debug('Failed to write audit event for structured_fallback_switch')
                enhanced_prompt = get_structured_output_prompt(schema_model) + "\n\n" + prompt
                if provider.lower() == "openai":
                    response_text = await LLMProvider.generate_openai(enhanced_prompt, model or "gpt-4", max_tokens=3000)
                    metadata = {"provider": "openai", "model": model or "gpt-4", "structured": False}
                elif provider.lower() == "google":
                    response_text = await LLMProvider.generate_google(enhanced_prompt, model or "gemini-2.0-flash", max_tokens=3000)
                    metadata = {"provider": "google", "model": model or "gemini-2.0-flash", "structured": False}
                elif provider.lower() == "groq":
                    # Groq generally supports structured outputs but if we hit this path, do plain completion
                    response_text = await LLMProvider.generate_groq(enhanced_prompt, model or "meta-llama/llama-4-scout-17b-16e-instruct", max_tokens=3000)
                    metadata = {"provider": "groq", "model": model or "meta-llama/llama-4-scout-17b-16e-instruct", "structured": False}
                else:
                    # If we reach here with an unknown provider, use the
                    # centralized call_llm helper to perform a plain completion
                    # with the enhanced prompt. This prevents hard failures for
                    # providers that weren't explicitly enumerated above.
                    logger.info(f"Provider {provider} not explicitly enumerated for structured fallback; using call_llm")
                    response_text, metadata = await call_llm(enhanced_prompt, provider, model)
                    metadata = metadata or {}
                    metadata.update({"structured": False})
            else:
                # Fallback for providers without native structured output support.
                # Build the enhanced schema prompt and call the generic
                # `call_llm` helper so provider-specific plumbing is centralized.
                logger.info(f"Provider {provider} doesn't support structured outputs, using prompt-based approach")
                enhanced_prompt = get_structured_output_prompt(schema_model) + "\n\n" + prompt

                # Use the generic call_llm wrapper which already implements
                # provider-specific behavior and will return text+metadata.
                response_text, metadata = await call_llm(enhanced_prompt, provider, model)
                metadata = metadata or {}
                metadata.update({"structured": False})
        
        # Defensive: if provider returned an empty or whitespace-only response,
        # attempt a prompt-based plain completion fallback before parsing.
        if not response_text or not str(response_text).strip():
            logger.error("Structured provider returned empty response; attempting prompt-based plain completion fallback")
            try:
                enhanced_prompt = get_structured_output_prompt(schema_model) + "\n\n" + prompt
                # Use the generic call_llm wrapper to leverage provider-specific codepaths
                response_text, metadata = await call_llm(enhanced_prompt, provider, model)
                metadata = metadata or {}
                metadata.update({"structured": False})
            except Exception:
                logger.exception("Prompt-based plain completion fallback also failed for empty structured response")
                # Continue; parsing below will raise and be handled by existing error handlers
                response_text = response_text or ""

        # Parse and validate the response (normalize first for json_object outputs)
        try:
            # If our metadata indicates we used json_object mode or plain structured=False,
            # attempt normalization before strict parsing.
            try:
                if isinstance(metadata, dict) and (metadata.get('json_object_mode') or metadata.get('structured') is False):
                    parsed_model = normalize_and_validate(response_text, schema_model, provider=provider, model_name=model)
                else:
                    parsed_model = parse_structured_response(response_text, schema_model)
            except Exception:
                # If normalization didn't succeed, fall back to the strict parser which will
                # raise a JSON/validation error to trigger the fallback flow below.
                parsed_model = parse_structured_response(response_text, schema_model)
        except Exception as validation_error:
            # Ensure we capture useful diagnostics for investigation
            err_str = str(validation_error)
            resp_excerpt = (response_text or "")[:2000]
            logger.error(f"Structured output validation failed: {err_str}")
            logger.error(f"Response length: {len(response_text or '')}, excerpt: {resp_excerpt[:500]}...")
            # Audit the validation failure with truncated payload to avoid massive logs
            try:
                write_audit_event('structured_validation_failure', {
                    'provider': provider,
                    'model': model,
                    'error': err_str[:1000],
                    'response_excerpt': resp_excerpt
                })
            except Exception:
                logger.debug('Failed to write audit event for structured_validation_failure')
            # If validation failed, attempt a fallback: for providers/models that
            # don't accept native structured params (e.g., OpenAI models without
            # response_format support), construct a schema-enforcing prompt and
            # call the provider with a plain chat completion, then parse the JSON.
            try:
                logger.info("Attempting prompt-based structured fallback after validation error")
                schema_prompt = get_structured_output_prompt(schema_model)
                enhanced_prompt = schema_prompt + "\n\n" + prompt
                # Call plain LLM (provider-specific) without structured params
                if provider.lower() == "openai":
                    text = await LLMProvider.generate_openai(enhanced_prompt, model or "gpt-4", max_tokens=3000)
                    response_text = text
                    metadata = {"provider": "openai", "model": model or "gpt-4", "structured": False}
                elif provider.lower() == "google":
                    text = await LLMProvider.generate_google(enhanced_prompt, model or "gemini-2.0-flash", max_tokens=3000)
                    response_text = text
                    metadata = {"provider": "google", "model": model or "gemini-2.0-flash", "structured": False}
                
                # Groq-specific improvement: if structured json_schema failed, try json_object mode
                elif provider.lower() == "groq":
                    # First attempt Groq JSON Object Mode which guarantees syntactically valid JSON
                    try:
                        # Audit that we're switching to json_object mode
                        try:
                            write_audit_event('structured_switch_to_json_object', {
                                'provider': provider,
                                'model': model,
                                'reason': str(validation_error)[:1000]
                            })
                        except Exception:
                            logger.debug('Failed to write audit for structured_switch_to_json_object')

                        # Use response_format type json_object
                        json_object_format = {"type": "json_object"}
                        text = await LLMProvider.generate_groq(enhanced_prompt, model or 'meta-llama/llama-4-scout-17b-16e-instruct', max_tokens=3000, response_format=json_object_format)
                        response_text = text
                        metadata = {'provider': 'groq', 'model': model or 'meta-llama/llama-4-scout-17b-16e-instruct', 'structured': False, 'json_object_mode': True}
                    except Exception:
                        logger.warning('Groq json_object mode attempt failed, falling back to plain completion')
                        # Fallback to plain completion if json_object mode fails
                        text = await LLMProvider.generate_groq(enhanced_prompt, model or 'meta-llama/llama-4-scout-17b-16e-instruct', max_tokens=3000)
                        response_text = text
                        metadata = {'provider': 'groq', 'model': model or 'meta-llama/llama-4-scout-17b-16e-instruct', 'structured': False}
                else:
                    # Re-raise original validation error for unsupported fallback
                    raise HTTPException(status_code=500, detail=f"Failed to parse structured output: {str(validation_error)}")

                parsed_model = parse_structured_response(response_text, schema_model)
                return parsed_model, metadata
            except Exception as fallback_err:
                # Primary prompt-based fallback failed; attempt recovery strategies.
                logger.error(f"Prompt-based structured fallback failed: {fallback_err}")
                try:
                    write_audit_event('structured_fallback_failed', {
                        'provider': provider,
                        'model': model,
                        'error': str(fallback_err)[:1000],
                        'response_excerpt': (response_text or '')[:2000]
                    })
                except Exception:
                    logger.debug('Failed to write audit event for structured_fallback_failed')

                # Strategy 1: increased max_tokens retry — pick a larger budget up to a sane cap
                # Use model_limit to guide how much larger we should request.
                # We'll attempt at most one enlarged retry (model_limit * 1.5 or +2000, whichever is larger),
                # but never exceed a hard cap of 16000 tokens to avoid runaway requests.
                try:
                    suggested = int(max(model_limit * 1.5, (max_tokens or 0) + 2000))
                except Exception:
                    suggested = (max_tokens + 2000) if isinstance(max_tokens, int) else (model_limit + 2000)
                larger_max = min(suggested, 16000)
                try:
                    logger.info('Attempting increased max_tokens retry for prompt-based fallback')
                    if provider.lower() == 'openai':
                        text2 = await LLMProvider.generate_openai(enhanced_prompt, model or 'gpt-4', max_tokens=larger_max)
                        response_text = text2
                        metadata = {'provider': 'openai', 'model': model or 'gpt-4', 'structured': False}
                    elif provider.lower() == 'google':
                        text2 = await LLMProvider.generate_google(enhanced_prompt, model or 'gemini-2.0-flash', max_tokens=larger_max)
                        response_text = text2
                        metadata = {'provider': 'google', 'model': model or 'gemini-2.0-flash', 'structured': False}
                    elif provider.lower() == 'groq':
                        text2 = await LLMProvider.generate_groq(enhanced_prompt, model or 'meta-llama/llama-4-scout-17b-16e-instruct', max_tokens=larger_max)
                        response_text = text2
                        metadata = {'provider': 'groq', 'model': model or 'meta-llama/llama-4-scout-17b-16e-instruct', 'structured': False}
                    else:
                        response_text, metadata = await call_llm(enhanced_prompt, provider, model)
                        metadata = metadata or {}
                        metadata.update({'structured': False})

                    parsed_model = parse_structured_response(response_text, schema_model)
                    try:
                        write_audit_event('structured_max_tokens_retry_success', {
                            'provider': provider,
                            'model': model,
                            'response_excerpt': (response_text or '')[:2000]
                        })
                    except Exception:
                        logger.debug('Failed to write audit event for structured_max_tokens_retry_success')
                    return parsed_model, metadata
                except Exception:
                    logger.exception('Increased max_tokens retry did not produce valid JSON')

                # Strategy 2: request the model to continue/complete the partial JSON
                try:
                    cont_prompt = (
                        "The previous response appears to be a partial or malformed JSON object. "
                        "Here is the exact partial output (do not include any extra text):\n\n" + (response_text or '') + "\n\n"
                        "Please return ONLY the complete, valid JSON object that corrects or finishes the partial output above. "
                        "Do not include any explanatory text or code fences."
                    )
                    logger.info('Sending continuation prompt to provider to complete truncated JSON')
                    cont_text, cont_meta = await call_llm(cont_prompt, provider, model)
                    parsed_model = parse_structured_response(cont_text, schema_model)
                    try:
                        write_audit_event('structured_continuation_success', {
                            'provider': provider,
                            'model': model,
                            'response_excerpt': (cont_text or '')[:2000]
                        })
                    except Exception:
                        logger.debug('Failed to write audit event for structured_continuation_success')
                    return parsed_model, (cont_meta or metadata)
                except Exception as cont_err:
                    logger.error(f'Continuation attempt failed: {cont_err}')
                    try:
                        write_audit_event('structured_continuation_failure', {
                            'provider': provider,
                            'model': model,
                            'error': str(cont_err)[:1000],
                            'continuation_excerpt': (cont_text or '')[:2000] if 'cont_text' in locals() else ''
                        })
                    except Exception:
                        logger.debug('Failed to write audit event for structured_continuation_failure')
                    # Re-raise to surface the combined failure
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to parse structured output: {str(validation_error)}; fallback error: {str(fallback_err)}; continuation error: {str(cont_err)}"
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
    # Build prompt using structured output optimized template (compat-safe)
    try:
        if hasattr(PromptTemplates, "character_structured_prompt") and callable(getattr(PromptTemplates, "character_structured_prompt")):
            prompt = PromptTemplates.character_structured_prompt(
                themes=request.themes,
                personality_traits=request.personality_traits,
                physical_traits=request.physical_traits,
                archetype=request.archetype,
                custom_details=request.custom_details
            )
        else:
            prompt = build_enhanced_character_prompt(themes=request.themes, personality_traits=request.personality_traits, physical_traits=request.physical_traits, archetype=request.archetype, custom_details=request.custom_details)
    except Exception:
        prompt = PromptTemplates.character_prompt(
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
@router.post("/world/structured/", response_model=WorldProfile)
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
        from ..prompts import build_landscape_prompt
        from ..image_generation import generate_landscape_image

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
            "image_base64": image_data.get("image_base64") or image_data.get("image"),
            "prompt": image_data.get("prompt") or prompt,
            "provider": image_data.get("provider"),
            "model": image_data.get("model"),
        }
    except Exception as e:
        logger.error(f"Landscape generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate landscape: {str(e)}")


@router.post("/location/generate-image/")
@router.post("/location/generate-image")
async def generate_location_image_endpoint(request: LocationImageRequest):
    """
    Generate an image for a location (city, dungeon, etc.)
    Accepts a JSON body matching LocationImageRequest for client-friendly POSTs.
    """
    try:
        from ..prompts import build_location_image_prompt
        from ..image_generation import generate_location_image

        prompt, negative = build_location_image_prompt(
            request.location_name,
            request.location_type,
            request.description,
            request.time_of_day,
            request.weather,
            request.style_preset,
        )

        image_data = await generate_location_image(
            prompt=prompt,
            provider=request.provider,
            model=request.model,
            aspect_ratio="16:9",
        )

        return {
            "image_base64": image_data.get("image_base64") or image_data.get("image"),
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
    # Optional convenience fields (frontend may send these at top-level)
    species: Optional[str] = None
    background: Optional[str] = None
    dnd_class: Optional[str] = None
    dnd_level: Optional[int] = None
    dnd_ability_scores: Optional[dict] = None


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

        # Defensive retrieval of commonly used legacy fields. Some LLMs or
        # parsing steps may produce empty strings or omit optional fields.
        # Use fallbacks where sensible so legacy fields are not blank.
        phys = getattr(character_profile, "physical_description", None) or structured_dict.get("physical_description") or ""
        pers = getattr(character_profile, "personality_description", None) or structured_dict.get("personality_description") or ""
        backstory = getattr(character_profile, "backstory", None) or structured_dict.get("backstory") or ""
        motivation = getattr(character_profile, "primary_motivation", None) or structured_dict.get("primary_motivation") or ""
        relationships = getattr(character_profile, "key_relationships", None) or structured_dict.get("key_relationships") or []

        # Compose a description from available pieces. If both parts are empty,
        # fall back to backstory or leave description empty (null in DB).
        composed_description = "".join([s for s in [phys.strip(), pers.strip()] if s])
        if not composed_description and backstory:
            composed_description = (backstory or "").strip()

        # Log which keys we received to aid debugging when fields are missing
        try:
            logger.debug(f"Structured keys received for {character_profile.name}: {list(structured_dict.keys())}")
        except Exception:
            logger.debug("Structured keys received: (failed to list keys)")

        # Helper: try multiple possible keys in structured_dict and return the first present
        def get_first(d: dict, candidates: list, default=None):
            for k in candidates:
                if k in d and d[k] is not None and d[k] != "":
                    return d[k]
            return default

        # Create character with both legacy fields and structured data
        # Derive D&D-specific legacy fields from structured data when present
        # Prefer top-level convenience fields on the request if provided by frontend
        dnd_class = request.dnd_class or get_first(structured_dict, ["dnd_class", "class", "character_class", "class_name"])
        dnd_level = (request.dnd_level if getattr(request, "dnd_level", None) is not None
                     else get_first(structured_dict, ["dnd_level", "level", "character_level"]))
        dnd_species = request.species or get_first(structured_dict, ["dnd_species", "species", "race", "character_race"])
        dnd_background = request.background or get_first(structured_dict, ["dnd_background", "background", "background_name"])
        dnd_alignment = get_first(structured_dict, ["dnd_alignment", "alignment"])
        dnd_ability_scores = request.dnd_ability_scores or get_first(structured_dict, ["dnd_ability_scores", "ability_scores", "abilities"])
        dnd_hp = get_first(structured_dict, ["dnd_hit_points", "hit_points", "hp"])
        dnd_ac = get_first(structured_dict, ["dnd_armor_class", "armor_class", "ac"])
        dnd_initiative = get_first(structured_dict, ["dnd_initiative", "initiative"])
        dnd_proficiency = get_first(structured_dict, ["dnd_proficiency_bonus", "proficiency_bonus", "proficiency"])
        dnd_skills = get_first(structured_dict, ["dnd_skills", "skills"])
        dnd_proficiencies = get_first(structured_dict, ["dnd_proficiencies", "proficiencies"])
        dnd_features = get_first(structured_dict, ["dnd_features", "features"])
        dnd_equipment = get_first(structured_dict, ["dnd_equipment", "equipment"])
        dnd_spellcasting = get_first(structured_dict, ["dnd_spellcasting", "spellcasting"])
        dnd_languages = get_first(structured_dict, ["dnd_languages", "languages"])

        is_dnd_flag = bool(dnd_species or dnd_class or dnd_background or dnd_ability_scores)

        # Debug log which source provided key values (convenience vs structured)
        try:
            logger.debug("D&D convenience fields from request: %s", {
                "species": request.species,
                "background": request.background,
                "dnd_class": request.dnd_class,
                "dnd_level": request.dnd_level,
                "dnd_ability_scores": request.dnd_ability_scores,
            })
        except Exception:
            pass

        character = Character(
            name=character_profile.name,
            # Legacy fields for backward compatibility
            description=composed_description or None,
            background=backstory or None,
            personality=pers or None,
            appearance=phys or None,
            motivations=motivation or None,
            relationships=relationships,  # Already a list of dicts or empty list
            # New structured data field
            structured_data=structured_dict,
            # Portrait data
            portrait_image=portrait_image,
            image_prompt=image_prompt,
            # D&D legacy columns (populate when structured profile contains them)
            is_dnd=is_dnd_flag,
            dnd_class=dnd_class,
            dnd_level=(int(dnd_level) if isinstance(dnd_level, (int, str)) and str(dnd_level).isdigit() else None),
            dnd_species=dnd_species,
            dnd_background=dnd_background,
            dnd_alignment=dnd_alignment,
            dnd_ability_scores=dnd_ability_scores,
            dnd_hit_points=(int(dnd_hp) if isinstance(dnd_hp, (int, str)) and str(dnd_hp).isdigit() else None),
            dnd_armor_class=(int(dnd_ac) if isinstance(dnd_ac, (int, str)) and str(dnd_ac).isdigit() else None),
            dnd_initiative=dnd_initiative,
            dnd_proficiency_bonus=dnd_proficiency,
            dnd_skills=dnd_skills,
            dnd_proficiencies=dnd_proficiencies,
            dnd_features=dnd_features,
            dnd_equipment=dnd_equipment,
            dnd_spellcasting=dnd_spellcasting,
            dnd_languages=dnd_languages,
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
            from ..models import Story
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
            from ..models import Story
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

