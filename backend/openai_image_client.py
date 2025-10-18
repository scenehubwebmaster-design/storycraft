"""
OpenAI Image Generation Client
Handles text-to-image generation for character portraits using GPT Image and DALL-E models.
"""
import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not installed. Image generation disabled.")


# Style presets for image generation
STYLE_PRESETS = {
    "realistic": "A professional portrait photograph, 35mm, depth of field, 4K HDR, cinematic quality, professional photography",
    "fantasy_art": "A detailed fantasy art portrait, digital painting, dramatic lighting, vibrant colors, concept art style, trending on artstation",
    "anime": "An anime-style portrait, detailed anime art, manga style, clean lines, vibrant colors, studio quality animation",
    "watercolor": "A watercolor painting portrait, soft brushstrokes, artistic, handcrafted, traditional art style",
    "oil_painting": "A classical oil painting portrait, fine art, renaissance style, dramatic lighting, museum quality",
    "digital_art": "A modern digital art portrait, highly detailed, sharp focus, professional digital illustration, trending on artstation",
    "comic_book": "A comic book style portrait, bold lines, dynamic shading, graphic novel art, professional comic illustration",
    "noir": "A film noir style portrait, black and white, dramatic shadows, high contrast, 1940s style photography"
}


def extract_safe_appearance(text: str) -> str:
    """
    Extract only safe, physical appearance details from character description.
    Removes potentially sensitive content that might trigger content policy.
    
    Args:
        text: Full character description
        
    Returns:
        Sanitized physical appearance description
    """
    # Try to find appearance section
    appearance_markers = [
        "**Physical Appearance:**",
        "**Appearance:**",
        "Physical Appearance:",
        "Appearance:",
        "## Physical Appearance",
        "## Appearance",
    ]
    
    text_lower = text.lower()
    appearance_text = ""
    
    # Find appearance section
    for marker in appearance_markers:
        marker_lower = marker.lower().strip("*:#")
        if marker_lower in text_lower:
            start_idx = text_lower.index(marker_lower)
            remaining = text[start_idx:]
            
            # Extract until next section or double newline
            lines = remaining.split('\n')
            appearance_lines = []
            found_content = False
            
            for line in lines[1:]:  # Skip header
                line_stripped = line.strip()
                if not line_stripped:
                    if found_content:
                        break
                    continue
                # Stop at next section header
                if line_stripped.startswith('**') and line_stripped.endswith(':**'):
                    break
                if line_stripped.startswith('##'):
                    break
                appearance_lines.append(line_stripped)
                found_content = True
            
            appearance_text = ' '.join(appearance_lines)
            break
    
    # If no appearance section found, extract from full text
    if not appearance_text:
        # Take first 300 chars as fallback
        appearance_text = text[:300].strip()
    
    # Clean up markdown and formatting
    appearance_text = appearance_text.replace('**', '').replace('*', '')
    appearance_text = appearance_text.replace('#', '')
    
    # Remove potentially problematic content
    # Keep only physical descriptors
    safe_keywords = [
        'hair', 'eyes', 'skin', 'tall', 'short', 'build', 'face', 'features',
        'complexion', 'physique', 'stature', 'frame', 'appearance', 'look',
        'wearing', 'dressed', 'clothing', 'attire', 'garment', 'robe', 'armor',
        'age', 'years old', 'young', 'middle-aged', 'elderly', 'adult'
    ]
    
    # Split into sentences
    sentences = [s.strip() for s in appearance_text.split('.') if s.strip()]
    
    # Keep only sentences with physical descriptors
    safe_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in safe_keywords):
            # Remove potentially sensitive words
            sensitive_words = ['violence', 'violent', 'weapon', 'blood', 'gore', 
                             'death', 'kill', 'murder', 'sexual', 'nude', 'naked']
            if not any(word in sentence_lower for word in sensitive_words):
                safe_sentences.append(sentence)
    
    if safe_sentences:
        result = '. '.join(safe_sentences) + '.'
    else:
        # Fallback: generic portrait request
        result = "A portrait of a person with distinct features"
    
    return result


def build_styled_prompt(
    character_name: str,
    appearance: str,
    style_preset: Optional[str] = None
) -> str:
    """
    Build a styled prompt for image generation.
    
    Args:
        character_name: Name of the character
        appearance: Physical appearance description
        style_preset: Style preset key from STYLE_PRESETS
        
    Returns:
        Formatted prompt with style
    """
    # Extract safe appearance details
    safe_appearance = extract_safe_appearance(appearance)
    
    # Get style suffix
    if style_preset and style_preset in STYLE_PRESETS:
        style_suffix = STYLE_PRESETS[style_preset]
    else:
        # Default to realistic portrait
        style_suffix = STYLE_PRESETS["realistic"]
    
    # Build prompt - keep it professional and safe
    prompt = f"A portrait of a character: {safe_appearance}. {style_suffix}"
    
    # Limit prompt length (DALL-E has 4000 char limit, GPT Image is more flexible)
    if len(prompt) > 3500:
        max_appearance = 3500 - len(style_suffix) - 50
        safe_appearance = safe_appearance[:max_appearance].rsplit('.', 1)[0] + '.'
        prompt = f"A portrait of a character: {safe_appearance}. {style_suffix}"
    
    logger.info(f"Built safe prompt: {prompt[:150]}...")
    return prompt


async def generate_character_portrait_openai(
    character_name: str,
    appearance_text: str,
    model: str = "gpt-4.1-mini",  # GPT Image model
    size: str = "1024x1024",
    use_dalle: bool = False,
    dalle_model: str = "dall-e-3",
    custom_prompt: Optional[str] = None,
    style_preset: Optional[str] = None,
    quality: str = "standard"
) -> Dict[str, str]:
    """
    Generate a character portrait image using OpenAI GPT Image or DALL-E.
    
    Args:
        character_name: Name of the character
        appearance_text: Physical appearance description
        model: GPT model for Responses API (default: gpt-4.1-mini)
        size: Image size for DALL-E (1024x1024, 1792x1024, 1024x1792)
        use_dalle: If True, use DALL-E instead of GPT Image
        dalle_model: DALL-E model version (dall-e-2 or dall-e-3)
        custom_prompt: Optional custom prompt override
        style_preset: Style preset (realistic, fantasy_art, anime, etc.)
        quality: Image quality (standard or hd) - DALL-E 3 only
        
    Returns:
        Dictionary with:
            - image_base64: Base64 encoded PNG image
            - prompt: The prompt used to generate the image
            - model: Model used for generation
            
    Raises:
        Exception: If OpenAI is not available or generation fails
    """
    if not OPENAI_AVAILABLE:
        raise Exception(
            "Image generation unavailable. Install required package: "
            "pip install openai"
        )
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not configured in environment")
    
    # Build prompt with style
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = build_styled_prompt(character_name, appearance_text, style_preset)
    
    # Get style suffix for potential fallback
    if style_preset and style_preset in STYLE_PRESETS:
        style_suffix = STYLE_PRESETS[style_preset]
    else:
        style_suffix = STYLE_PRESETS["realistic"]
    
    logger.info(f"Generating portrait for {character_name} with OpenAI (style: {style_preset or 'default'})")
    
    try:
        client = OpenAI(api_key=api_key)
        
        if use_dalle:
            # Use DALL-E via Images API
            logger.info(f"Using DALL-E {dalle_model} for generation (quality: {quality})")
            
            # Build kwargs for DALL-E
            dalle_kwargs = {
                "model": dalle_model,
                "prompt": prompt,
                "size": size,
                "n": 1,
                "response_format": "b64_json"
            }
            
            # Only add quality parameter for DALL-E 3
            if dalle_model == "dall-e-3":
                dalle_kwargs["quality"] = quality
            
            response = client.images.generate(**dalle_kwargs)
            
            # Extract base64 image
            image_base64 = response.data[0].b64_json
            model_used = dalle_model
            
        else:
            # Use GPT Image via Responses API
            logger.info(f"Using GPT Image ({model}) for generation")
            
            response = client.responses.create(
                model=model,
                input=f"Generate an image: {prompt}",
                tools=[{"type": "image_generation"}],
            )
            
            # Extract image from response
            image_data = [
                output.result
                for output in response.output
                if output.type == "image_generation_call"
            ]
            
            if not image_data:
                raise Exception("No image was generated in response")
            
            image_base64 = image_data[0]
            model_used = f"{model} (GPT Image)"
        
        logger.info(f"Successfully generated portrait for {character_name}")
        
        return {
            "image_base64": image_base64,
            "prompt": prompt,
            "model": model_used
        }
        
    except Exception as e:
        error_str = str(e)
        logger.error(f"Failed to generate image for {character_name}: {error_str}")
        
        # Check if it's a content policy violation
        if "safety system" in error_str.lower() or "content_policy_violation" in error_str.lower():
            logger.warning("Content policy violation detected. Trying with generic safe prompt...")
            
            # Try again with a very safe, generic prompt
            try:
                safe_prompt = f"A professional portrait photograph of a person, {style_suffix}"
                logger.info(f"Retrying with safe prompt: {safe_prompt}")
                
                if use_dalle:
                    dalle_kwargs = {
                        "model": dalle_model,
                        "prompt": safe_prompt,
                        "size": size,
                        "n": 1,
                        "response_format": "b64_json"
                    }
                    if dalle_model == "dall-e-3":
                        dalle_kwargs["quality"] = quality
                    
                    response = client.images.generate(**dalle_kwargs)
                    image_base64 = response.data[0].b64_json
                    model_used = dalle_model
                else:
                    response = client.responses.create(
                        model=model,
                        input=f"Generate an image: {safe_prompt}",
                        tools=[{"type": "image_generation"}],
                    )
                    image_data = [
                        output.result
                        for output in response.output
                        if output.type == "image_generation_call"
                    ]
                    if not image_data:
                        raise Exception("No image was generated in fallback attempt")
                    image_base64 = image_data[0]
                    model_used = f"{model} (GPT Image)"
                
                logger.info("Successfully generated portrait with safe fallback prompt")
                return {
                    "image_base64": image_base64,
                    "prompt": safe_prompt + " (Note: Original prompt was modified for safety)",
                    "model": model_used
                }
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {str(fallback_error)}")
                raise Exception(
                    f"Content policy violation. The character description contains content "
                    f"that doesn't meet OpenAI's safety guidelines. Please try: 1) Using Google Imagen instead, "
                    f"2) Simplifying the character description, or 3) Focusing only on visual appearance details. "
                    f"Original error: {error_str}"
                )
        
        raise Exception(f"OpenAI image generation failed: {error_str}")


async def generate_portrait_with_provider(
    character_name: str,
    appearance_text: str,
    provider: str = "openai",
    model: Optional[str] = None,
    aspect_ratio: str = "3:4",
    custom_prompt: Optional[str] = None,
    style_preset: Optional[str] = None,
    quality: str = "standard"
) -> Dict[str, str]:
    """
    Unified interface for portrait generation across providers.
    
    Args:
        character_name: Name of the character
        appearance_text: Physical appearance description
        provider: Image provider ("openai", "google", "stablediffusion")
        model: Model to use (provider-specific)
        aspect_ratio: Aspect ratio for Google Imagen or DALL-E size
        custom_prompt: Optional custom prompt override
        style_preset: Style preset (realistic, fantasy_art, anime, etc.)
        quality: Image quality (standard, hd) - DALL-E 3 only, or (draft, standard, high) for SD
        
    Returns:
        Dictionary with image_base64, prompt, and model
    """
    if provider.lower() == "stablediffusion":
        # Use local Stable Diffusion
        from stablediffusion_client import generate_portrait_with_sd
        
        logger.info(f"Using Stable Diffusion for {character_name} portrait")
        
        # Build prompt with style if not custom
        if custom_prompt:
            prompt = custom_prompt
        else:
            safe_appearance = extract_safe_appearance(appearance_text)
            prompt = f"{character_name}, {safe_appearance}"
        
        # Map style_preset to SD styles
        sd_style = style_preset if style_preset else "photorealistic"
        
        # Generate using SD
        image_base64, full_prompt = generate_portrait_with_sd(
            character_description=prompt,
            style=sd_style,
            quality=quality if quality in ["draft", "standard", "high"] else "standard"
        )
        
        return {
            "image_base64": image_base64,
            "prompt": full_prompt,
            "model": "Stable Diffusion (Local)"
        }
    
    elif provider.lower() == "openai":
        # Determine if we should use DALL-E or GPT Image
        use_dalle = model and "dall-e" in model.lower()
        
        if use_dalle:
            # DALL-E model specified
            dalle_model = model if model else "dall-e-3"
            
            # Map aspect ratio to DALL-E sizes
            size_map = {
                "1:1": "1024x1024",
                "3:4": "1024x1792",  # Portrait
                "4:3": "1792x1024",  # Landscape
                "16:9": "1792x1024",
                "9:16": "1024x1792",
            }
            size = size_map.get(aspect_ratio, "1024x1024")
            
            return await generate_character_portrait_openai(
                character_name=character_name,
                appearance_text=appearance_text,
                use_dalle=True,
                dalle_model=dalle_model,
                size=size,
                custom_prompt=custom_prompt,
                style_preset=style_preset,
                quality=quality
            )
        else:
            # Use GPT Image (default)
            gpt_model = model if model else "gpt-4.1-mini"
            
            return await generate_character_portrait_openai(
                character_name=character_name,
                appearance_text=appearance_text,
                model=gpt_model,
                use_dalle=False,
                custom_prompt=custom_prompt,
                style_preset=style_preset,
                quality=quality
            )
    
    elif provider.lower() == "google":
        # Use Google Imagen
        from imagen_client import generate_character_portrait
        
        imagen_model = model if model else "imagen-4.0-fast-generate-001"
        
        # For Google, we can enhance the prompt with style
        if style_preset and not custom_prompt:
            # Build styled prompt for Google
            styled_prompt = build_styled_prompt(character_name, appearance_text, style_preset)
            custom_prompt = styled_prompt
        
        return await generate_character_portrait(
            character_name=character_name,
            appearance_text=appearance_text,
            model=imagen_model,
            aspect_ratio=aspect_ratio,
            custom_prompt=custom_prompt
        )
    
    else:
        raise Exception(f"Unknown image provider: {provider}")
