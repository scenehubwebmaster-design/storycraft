"""
Image generation helpers for landscapes and locations.

Provides generate_landscape_image and generate_location_image which return
{'image': <base64>, 'prompt': <used prompt>, 'provider': <provider>, 'model': <model>}
"""
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


async def generate_landscape_image(prompt: str, provider: str = "stablediffusion", model: Optional[str] = None, aspect_ratio: str = "16:9") -> Dict:
    """Generate a landscape image using the requested provider."""
    provider = provider.lower()
    if provider in ["stablediffusion", "stable_diffusion", "sd"]:
        # Use local Stable Diffusion client
        from stablediffusion_client import StableDiffusionClient

        client = StableDiffusionClient()
        # Map aspect ratio to width/height
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "1:1":
            width, height = 1024, 1024
        else:
            width, height = 1024, 768

        result = client.generate_image(prompt=prompt, negative_prompt="", steps=30, width=width, height=height)
        return {"image": result["image"], "prompt": prompt, "provider": "stablediffusion", "model": model or "local"}

    elif provider in ["google", "imagen"]:
        # Use Google Imagen client
        from imagen_client import generate_character_portrait as imagen_generate
        # Reuse portrait generator but treat prompt as landscape instructions
        res = await imagen_generate(character_name="Landscape", appearance_text=prompt, model=model or "imagen-4.0-fast-generate-001", aspect_ratio=aspect_ratio)
        return {"image": res["image_base64"], "prompt": res["prompt"], "provider": "google", "model": model or "imagen-4.0-fast-generate-001"}

    else:
        raise ValueError(f"Unsupported image provider: {provider}")


async def generate_location_image(prompt: str, provider: str = "stablediffusion", model: Optional[str] = None, aspect_ratio: str = "16:9") -> Dict:
    """Generate a location image. Mirrors landscape function but with different defaults."""
    return await generate_landscape_image(prompt=prompt, provider=provider, model=model, aspect_ratio=aspect_ratio)
