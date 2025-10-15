"""
Google Imagen Image Generation Client
Handles text-to-image generation for character portraits.
"""
import os
import logging
import base64
from typing import Optional, Dict
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage  # noqa: F401 - Used for type checking
    IMAGEN_AVAILABLE = True
except ImportError:
    IMAGEN_AVAILABLE = False
    logger.warning("Google GenAI or PIL not installed. Image generation disabled.")


def extract_character_appearance(content: str) -> str:
    """
    Extract physical appearance description from generated character content.
    
    Args:
        content: Full character description text
        
    Returns:
        Extracted appearance description
    """
    # Look for common appearance section markers
    markers = [
        "**Appearance:**",
        "**Physical Appearance:**",
        "**Physical Description:**",
        "Appearance:",
        "Physical Appearance:",
        "Physical Description:",
    ]
    
    # Try to find appearance section
    content_lower = content.lower()
    for marker in markers:
        marker_lower = marker.lower().strip("*:")
        if marker_lower in content_lower:
            # Find the start of the appearance section
            start_idx = content_lower.index(marker_lower)
            # Find the end (next section or newline break)
            remaining = content[start_idx:]
            
            # Find next section marker (usually **Something:** or \n\n)
            lines = remaining.split('\n')
            appearance_lines = []
            found_content = False
            
            for line in lines[1:]:  # Skip the header line
                line = line.strip()
                if not line:
                    if found_content:
                        break  # End of section
                    continue
                if line.startswith('**') and line.endswith(':**'):
                    break  # Next section
                appearance_lines.append(line)
                found_content = True
            
            if appearance_lines:
                return ' '.join(appearance_lines)
    
    # Fallback: return first 200 characters
    return content[:200].strip()


def build_character_image_prompt(
    character_name: str,
    appearance: str,
    style: str = "portrait photograph"
) -> str:
    """
    Build optimized Imagen prompt from character appearance.
    
    Follows Imagen best practices:
    - Subject first (portrait photograph)
    - Clear character description
    - Context and style
    - Quality modifiers
    
    Args:
        character_name: Name of the character
        appearance: Physical appearance description
        style: Photography/art style (default: portrait photograph)
        
    Returns:
        Optimized prompt string
    """
    # Clean up appearance text
    appearance = appearance.strip()
    
    # Remove markdown formatting
    appearance = appearance.replace('**', '').replace('*', '')
    
    # Build prompt following Imagen guidelines
    prompt_parts = [
        f"A professional {style} of",
        appearance,
        "35mm portrait, depth of field, 4K HDR, cinematic quality, professional photography"
    ]
    
    prompt = ' '.join(prompt_parts)
    
    # Limit to 480 tokens (roughly 1920 characters, be conservative)
    if len(prompt) > 1800:
        # Truncate appearance but keep modifiers
        max_appearance_length = 1800 - len(prompt_parts[0]) - len(prompt_parts[2]) - 10
        appearance_truncated = appearance[:max_appearance_length].rsplit('.', 1)[0] + '.'
        prompt_parts[1] = appearance_truncated
        prompt = ' '.join(prompt_parts)
    
    logger.info(f"Built image prompt: {prompt[:100]}...")
    return prompt


async def generate_character_portrait(
    character_name: str,
    appearance_text: str,
    model: str = "imagen-4.0-fast-generate-001",
    aspect_ratio: str = "3:4",
    custom_prompt: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate a character portrait image using Google Imagen.
    
    Args:
        character_name: Name of the character
        appearance_text: Physical appearance description
        model: Imagen model to use (fast/standard/ultra)
        aspect_ratio: Image aspect ratio (3:4 for portrait)
        custom_prompt: Optional custom prompt override
        
    Returns:
        Dictionary with:
            - image_base64: Base64 encoded PNG image
            - prompt: The prompt used to generate the image
            
    Raises:
        Exception: If Imagen is not available or generation fails
    """
    if not IMAGEN_AVAILABLE:
        raise Exception(
            "Image generation unavailable. Install required packages: "
            "pip install google-genai pillow"
        )
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY not configured in environment")
    
    # Build or use custom prompt
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = build_character_image_prompt(character_name, appearance_text)
    
    logger.info(f"Generating portrait for {character_name} with model {model}")
    
    try:
        # Initialize Imagen client
        client = genai.Client(api_key=api_key)
        
        # Generate image
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
                person_generation="allow_adult",  # For character portraits
            )
        )
        
        # Get the first generated image
        if not response.generated_images:
            raise Exception("No images were generated")
        
        generated_image = response.generated_images[0]
        
        # Convert PIL Image to base64
        pil_image = generated_image.image._pil_image
        
        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Encode to base64
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        logger.info(f"Successfully generated portrait for {character_name}")
        
        return {
            "image_base64": image_base64,
            "prompt": prompt
        }
        
    except Exception as e:
        logger.error(f"Failed to generate image for {character_name}: {str(e)}")
        raise Exception(f"Image generation failed: {str(e)}")
