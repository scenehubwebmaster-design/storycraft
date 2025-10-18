"""
Stable Diffusion Local API Client

This client interfaces with a local Stable Diffusion WebUI running on Gradio.
The API uses numbered endpoints (fn_index) for different functions.
"""

import os
import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class StableDiffusionClient:
    """Client for local Stable Diffusion WebUI API"""
    
    def __init__(self):
        self.base_url = os.getenv("STABLEDIFFUSION_API_URL", "http://192.168.250.14:7861")
        self.timeout = 120  # SD can take a while
        
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 30,
        seed: int = -1,
        width: int = 512,
        height: int = 512,
        cfg_scale: float = 7.0,
        model: Optional[str] = None
    ) -> Dict:
        """
        Generate an image using Stable Diffusion
        
        Args:
            prompt: Text description of the image to generate
            negative_prompt: Things to avoid in the image
            steps: Number of sampling steps (1-150, default 30)
            seed: Random seed (-1 for random)
            width: Image width (64-2048, default 512)
            height: Image height (64-2048, default 512)
            cfg_scale: Classifier Free Guidance scale (how closely to follow prompt)
            model: Model checkpoint to use (optional)
            
        Returns:
            Dict with 'image' (base64 string) and 'info' (generation details)
        """
        try:
            logger.info(f"Generating SD image with prompt: {prompt[:100]}...")
            
            # Gradio API format for prediction
            # fn_index 2 is the txt2img generation endpoint
            payload = {
                "fn_index": 2,
                "data": [
                    prompt,           # Prompt
                    negative_prompt,  # Negative prompt
                    steps,            # Sampling steps
                    seed,             # Seed
                    False             # NegPiP (negative prompt in pipeline)
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/api/predict",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated image from Gradio response
            # Format: {"data": [<image_base64>, <generation_info>]}
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]
                
                # Handle different response formats
                if isinstance(image_data, dict):
                    # Format: {"name": "...", "data": "base64...", ...}
                    base64_image = image_data.get("data", "")
                elif isinstance(image_data, str):
                    # Direct base64 string
                    base64_image = image_data
                else:
                    raise ValueError("Unexpected image data format")
                
                return {
                    "image": base64_image,
                    "info": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "steps": steps,
                        "seed": seed,
                        "model": "Stable Diffusion (Local)"
                    }
                }
            else:
                raise ValueError("No image data in response")
                
        except requests.exceptions.Timeout:
            logger.error("Stable Diffusion request timed out")
            raise Exception("Image generation timed out. Try reducing steps or image size.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Stable Diffusion API error: {str(e)}")
            raise Exception(f"Failed to connect to Stable Diffusion server: {str(e)}")
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {str(e)}")
            raise Exception(f"Image generation failed: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available SD models"""
        try:
            # fn_index 0 returns the current model dropdown options
            response = requests.post(
                f"{self.base_url}/api/predict",
                json={"fn_index": 0, "data": []},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract model list from response
            if "data" in result:
                return result["data"]
            return []
        except Exception as e:
            logger.error(f"Failed to get SD models: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """Test if SD server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


def generate_portrait_with_sd(
    character_description: str,
    style: str = "photorealistic",
    quality: str = "standard"
) -> tuple[str, str]:
    """
    Generate a character portrait using local Stable Diffusion
    
    Args:
        character_description: Description of the character
        style: Art style (photorealistic, fantasy, anime, etc.)
        quality: Quality preset (draft/standard/high)
        
    Returns:
        Tuple of (base64_image_data, prompt_used)
    """
    client = StableDiffusionClient()
    
    # Build enhanced prompt based on style
    style_prompts = {
        "photorealistic": "professional photography, highly detailed, realistic, 8k uhd, studio lighting",
        "fantasy": "fantasy art, detailed, magical, ethereal, high quality",
        "anime": "anime style, cel shaded, vibrant colors, high quality",
        "oil_painting": "oil painting, classical art style, detailed brushstrokes",
        "digital_art": "digital art, concept art, detailed, artstation quality"
    }
    
    style_suffix = style_prompts.get(style, style_prompts["photorealistic"])
    
    # Quality settings
    quality_settings = {
        "draft": {"steps": 20, "width": 512, "height": 512},
        "standard": {"steps": 30, "width": 768, "height": 768},
        "high": {"steps": 50, "width": 1024, "height": 1024}
    }
    
    settings = quality_settings.get(quality, quality_settings["standard"])
    
    # Build full prompt
    full_prompt = f"portrait of {character_description}, {style_suffix}, centered composition, professional quality"
    
    # Negative prompt to avoid common issues
    negative_prompt = "low quality, blurry, distorted, deformed, ugly, bad anatomy, extra limbs, extra fingers, mutation, disfigured"
    
    # Generate
    result = client.generate_image(
        prompt=full_prompt,
        negative_prompt=negative_prompt,
        steps=settings["steps"],
        width=settings["width"],
        height=settings["height"],
        cfg_scale=7.5
    )
    
    return result["image"], full_prompt
