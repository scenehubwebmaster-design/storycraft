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
            
            # Gradio API format for txt2img endpoint (fn_index 124)
            # Build complete parameter array (71 parameters total)
            data = []
            data.append({})  # 0. parameter_47 (Label) - empty dict
            data.append(prompt)  # 1. Prompt
            data.append(negative_prompt)  # 2. Negative prompt
            data.append([])  # 3. Styles - empty list
            data.append(1)  # 4. Batch count
            data.append(1)  # 5. Batch size
            data.append(cfg_scale)  # 6. CFG Scale
            data.append(height)  # 7. Height
            data.append(width)  # 8. Width
            data.append(False)  # 9. Hires. fix
            data.append(0.7)  # 10. Denoising strength
            data.append(2.0)  # 11. Upscale by
            data.append("")  # 12. Upscaler
            data.append(0)  # 13. Hires steps
            data.append(0)  # 14. Resize width to
            data.append(0)  # 15. Resize height to
            data.append("")  # 16. Checkpoint (empty = use current)
            data.append("")  # 17. Hires sampling method
            data.append("")  # 18. Hires schedule type
            data.append("")  # 19. Hires prompt
            data.append("")  # 20. Hires negative prompt
            data.append([])  # 21. Override settings
            data.append("None")  # 22. Script
            data.append(steps)  # 23. Sampling steps
            data.append("")  # 24. Sampling method (empty = default)
            data.append("")  # 25. Schedule type
            data.append(False)  # 26. Refiner
            data.append("")  # 27. Checkpoint (refiner)
            data.append(0.5)  # 28. Switch at
            data.append(seed)  # 29. Seed
            data.append(False)  # 30. Extra
            data.append(-1)  # 31. Variation seed
            data.append(0)  # 32. Variation strength
            data.append(0)  # 33. Resize seed from width
            data.append(0)  # 34. Resize seed from height
            data.append(False)  # 35. Model Keyword Enabled
            data.append("")  # 36. Keyword placement
            data.append("")  # 37. Multiple keywords
            data.append("")  # 38. Textual Inversion
            data.append("")  # 39. Keyword order
            data.append("")  # 40. Model
            data.append(1.0)  # 41. multiplier
            data.append("")  # 42. keywords
            data.append(False)  # 43. NegPiP
            
            # Script parameters (44-70) - all defaults for "None" script
            for _ in range(44, 71):
                if _ in [44, 45, 49, 50, 62, 63, 64, 65, 66, 67, 68, 70]:
                    data.append(False)  # Checkboxes
                elif _ in [48, 69]:
                    data.append(0)  # Margins
                elif _ in [46, 47, 51]:
                    data.append("")  # Radio buttons
                elif _ in [55, 58, 61]:
                    data.append([])  # Dropdown lists
                else:
                    data.append("")  # Text/dropdown strings
            
            payload = {
                "fn_index": 124,  # txt2img endpoint
                "data": data
            }
            
            response = requests.post(
                f"{self.base_url}/api/predict",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated image from Gradio response
            # Format: {"data": [[image_array], info_text, html, html]}
            if "data" in result and len(result["data"]) > 0:
                images_array = result["data"][0]  # Gallery output
                
                if not images_array or len(images_array) == 0:
                    # Check for error in HTML output
                    if len(result["data"]) > 3:
                        error_html = result["data"][3]
                        if "error" in error_html.lower():
                            raise ValueError(f"Generation failed: {error_html[:200]}")
                    raise ValueError("No images generated")
                
                # Get first image from gallery
                first_image = images_array[0]
                
                # Handle different response formats
                if isinstance(first_image, dict):
                    # Gradio returns {"name": "path/to/file.png", "data": None, "is_file": True}
                    # Need to fetch the file from the server
                    if "name" in first_image and "is_file" in first_image:
                        file_path = first_image["name"]
                        # Remove query string if present
                        if "?" in file_path:
                            file_path = file_path.split("?")[0]
                        
                        # Build URL to fetch the file
                        # Gradio serves files at /file=<path>
                        file_url = f"{self.base_url}/file={file_path}"
                        
                        logger.info(f"Fetching generated image from: {file_url}")
                        img_response = requests.get(file_url, timeout=30)
                        img_response.raise_for_status()
                        
                        import base64
                        base64_image = base64.b64encode(img_response.content).decode("utf-8")
                        
                    elif "data" in first_image and first_image["data"] is not None:
                        # Direct base64 in data field
                        base64_image = first_image["data"]
                        # Remove data URI prefix if present
                        if base64_image.startswith("data:"):
                            base64_image = base64_image.split(",", 1)[1]
                    elif "url" in first_image:
                        # URL field
                        img_url = first_image["url"]
                        if not img_url.startswith("http"):
                            img_url = f"{self.base_url}{img_url}"
                        img_response = requests.get(img_url, timeout=30)
                        img_response.raise_for_status()
                        import base64
                        base64_image = base64.b64encode(img_response.content).decode("utf-8")
                    else:
                        raise ValueError(f"Unknown image format: {first_image.keys()}")
                elif isinstance(first_image, str):
                    # Direct base64 string or URL
                    base64_image = first_image
                else:
                    raise ValueError(f"Unexpected image type: {type(first_image)}")
                
                # Get generation info if available
                info_text = result["data"][1] if len(result["data"]) > 1 else ""
                
                # Normalize to 'image_base64' while keeping 'image' alias
                return {
                    "image_base64": base64_image,
                    "info": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "steps": steps,
                        "seed": seed,
                        "cfg_scale": cfg_scale,
                        "size": f"{width}x{height}",
                        "model": "Stable Diffusion (Local)",
                        "generation_info": info_text[:500] if info_text else ""
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
    
    # The generate_image() function returns a dict containing 'image_base64'
    # (base64-encoded PNG) and 'info'. Return the base64 image string so callers
    # receive the expected (image_base64, prompt) tuple.
    if isinstance(result, dict) and "image_base64" in result:
        return result["image_base64"], full_prompt
    # Fallback: if older format returns raw image bytes or uses 'image' key,
    # try to handle that gracefully.
    if isinstance(result, dict) and "image" in result:
        return result["image"], full_prompt
    raise Exception("Unexpected Stable Diffusion client response format")
