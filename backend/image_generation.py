"""Image generation helpers for landscapes and locations.

Provides generate_landscape_image and generate_location_image which return
{'image_base64': <base64>, 'prompt': <used prompt>, 'provider': <provider>, 'model': <model>}
"""
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def _sanitize_prompt_text(text: Optional[str]) -> str:
    """Sanitize user-provided prompt text by removing markdown and common assistant markup.

    - Remove Suggested Actions blocks (lines starting with 'Suggested Actions:' or fenced blocks)
    - Strip markdown bold/italic/inline code
    - Remove markdown tables (simple | delimited rows)
    - Collapse repeated whitespace and trim
    """
    if not text:
        return ""

    s = str(text)

    # Remove fenced code blocks ```...```
    import re

    s = re.sub(r"```[\s\S]*?```", " ", s)

    # Remove lines that start with 'Suggested Action' or 'Suggested Actions' (case-insensitive)
    s = "\n".join(
        [ln for ln in s.splitlines() if not re.match(r"^\s*Suggested Actions?:", ln, re.I)]
    )

    # Remove markdown tables: lines that contain vertical bars and at least one dash separator line
    lines = s.splitlines()
    cleaned_lines = []
    skip_table = False
    for i, ln in enumerate(lines):
        if skip_table:
            # skip until a blank line or a non-table-looking line
            if not ("|" in ln or re.match(r"^\s*[-:\|\s]+$", ln)):
                skip_table = False
                cleaned_lines.append(ln)
            else:
                continue
            
        elif "|" in ln:
            # Suspect a table row; to be safe, skip consecutive '|' rows
            # If the next line contains only pipes/dashes/separators, treat as table
            next_ln = lines[i + 1] if i + 1 < len(lines) else ""
            if re.match(r"^\s*[-:\|\s]+$", next_ln):
                skip_table = True
                continue
            else:
                # If it's a single inline pipe but looks like narrative, keep it but remove stray pipes
                cleaned_lines.append(ln.replace("|", " "))
        else:
            cleaned_lines.append(ln)

    s = "\n".join(cleaned_lines)

    # Remove bold/italic/inline markdown markers (**bold**, *italic*, __, _, `code`)
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"\*(.*?)\*", r"\1", s)
    s = re.sub(r"__(.*?)__", r"\1", s)
    s = re.sub(r"_(.*?)_", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)

    # Remove stray markdown headers
    s = re.sub(r"^#{1,6}\s*", "", s, flags=re.M)

    # Remove common assistant artifacts like '> **Name** (...' quoting markers
    s = re.sub(r"^>\s*", "", s, flags=re.M)

    # Collapse multiple whitespace/newlines
    s = re.sub(r"\n{2,}", "\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)

    return s.strip()


async def generate_landscape_image(
    prompt: str,
    provider: str = "stablediffusion",
    model: Optional[str] = None,
    aspect_ratio: str = "16:9",
    style: Optional[str] = None,
    use_llm: bool = False,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> Dict:
    """Generate a landscape image using the requested provider."""
    provider = provider.lower()

    if provider in ["stablediffusion", "stable_diffusion", "sd"]:
        # Use local Stable Diffusion client
        from .stablediffusion_client import StableDiffusionClient

        client = StableDiffusionClient()
        # Map aspect ratio to width/height
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "1:1":
            width, height = 1024, 1024
        else:
            width, height = 1024, 768

        # Enhance prompt and negative prompt for Stable Diffusion
        def _enhance_prompt_for_sd(base: str, typ: str = "landscape", style_name: Optional[str] = None):
            base = (base or "").strip()

            # Style presets (can be expanded)
            style_presets = {
                "photorealistic": "photorealistic, ultra-detailed, filmic, natural lighting, realistic textures",
                "cinematic": "cinematic lighting, dramatic composition, volumetric light, widescreen framing",
                "painterly": "painterly brushstrokes, soft edges, oil painting, textured",
                "fantasy": "fantasy art, mystical, ethereal, ornate architecture, magical atmosphere",
                "retro": "vintage color grading, film grain, 35mm photography, nostalgic",
            }

            # Base descriptors tuned for landscapes/locations
            base_descriptors = (
                "ultra-detailed, high resolution, dramatic composition, realistic textures, sharp focus, volumetric lighting, wide angle"
            )

            if typ == "location":
                base_descriptors = (
                    "concept art, detailed environment, atmospheric lighting, intricate architecture, moody shadows, cinematic color grading"
                )

            style_desc = style_presets.get((style_name or "").lower(), "")

            # Combine provided prompt, style descriptors and base descriptors
            positive_parts = [p for p in [base, style_desc, base_descriptors] if p]
            positive = ", ".join(positive_parts)

            # Common negative prompts to avoid typical SD artifacts
            negative = (
                "lowres, text, watermark, signature, poorly drawn, deformed, blurry, oversaturated, mutated, extra limbs, glitch, jpeg artifacts"
            )

            return positive, negative

        # Sanitize incoming prompt to remove markdown and suggested-action artifacts
        clean_prompt = _sanitize_prompt_text(prompt)

        # Optionally ask an LLM to rewrite/summarize the cleaned description into
        # a concise, Stable Diffusion-friendly visual prompt. This helps when
        # the source text is noisy (dialogue, action chips, markdown) and we want
        # the LLM to distill only the visual descriptors.
        if use_llm:
            try:
                # Import dynamically to avoid circular imports at module load time
                from backend.routers.generation import call_llm

                llm_provider_to_use = llm_provider or "groq"
                llm_model_to_use = llm_model or None

                # Build a short instruction for the LLM
                llm_instr = (
                    "You are a professional prompt engineer.\n"
                    "Rewrite the following scene description into a single concise, visual prompt suitable for Stable Diffusion. "
                    "Remove all dialogue, game mechanics, action lists, and markdown. Keep only visual details (subject, clothing, pose, mood, lighting, color and focal point). "
                    "Be explicit about atmosphere and camera framing if present. Output ONLY the cleaned prompt on one line with no markdown or explanation.\n\n"
                    f"Text:\n{clean_prompt}"
                )

                llm_resp, _meta = await call_llm(llm_instr, llm_provider_to_use, llm_model_to_use)
                # call_llm returns (text, metadata)
                if isinstance(llm_resp, tuple):
                    # Defensive: if wrapper returns tuple unexpectedly
                    llm_resp = llm_resp[0]
                summarized = (llm_resp or "").strip()
                if summarized:
                    clean_prompt = summarized
            except Exception:
                # On any LM failure, fall back to the sanitized original prompt
                logger.exception("LLM summarization failed; using sanitized prompt instead")

        prompt_enhanced, negative_prompt = _enhance_prompt_for_sd(clean_prompt, typ="landscape", style_name=style)

        # Default SD generation parameters (tunable)
        steps = 30
        cfg_scale = 7.5
        seed = -1  # -1 instructs the SD client to randomize

        # Call the Stable Diffusion client with richer parameters
        result = client.generate_image(
            prompt=prompt_enhanced,
            negative_prompt=negative_prompt,
            steps=steps,
            width=width,
            height=height,
            cfg_scale=cfg_scale,
            seed=seed,
            model=model,
        )

        # Return canonical 'image_base64' only and include the used prompt
        return {
            "image_base64": result.get("image") or result.get("image_base64"),
            "prompt": prompt_enhanced,
            "negative_prompt": negative_prompt,
            "provider": "stablediffusion",
            "model": model or "local",
        }

    elif provider in ["google", "imagen"]:
        # Use Google Imagen client
        from .imagen_client import generate_character_portrait as imagen_generate

        # Reuse portrait generator but treat prompt as landscape instructions
        res = await imagen_generate(
            character_name="Landscape",
            appearance_text=prompt,
            model=model or "imagen-4.0-fast-generate-001",
            aspect_ratio=aspect_ratio,
        )
        # Return canonical 'image_base64' only
        return {
            "image_base64": res.get("image_base64") or res.get("image"),
            "prompt": res.get("prompt"),
            "provider": "google",
            "model": model or "imagen-4.0-fast-generate-001",
        }

    else:
        raise ValueError(f"Unsupported image provider: {provider}")


async def generate_location_image(
    prompt: str,
    provider: str = "stablediffusion",
    model: Optional[str] = None,
    aspect_ratio: str = "16:9",
    style: Optional[str] = None,
    use_llm: bool = False,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
) -> Dict:
    """Generate a location image. Mirrors landscape function but with different defaults."""
    # For locations we prefer a slightly different prompt tuning
    provider = provider.lower()
    if provider in ["stablediffusion", "stable_diffusion", "sd"]:
        # Delegate to landscape generator but adjust the prompt type
        # by calling the same enhancement routine used above.
        from .stablediffusion_client import StableDiffusionClient

        client = StableDiffusionClient()
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        elif aspect_ratio == "1:1":
            width, height = 1024, 1024
        else:
            width, height = 1024, 768

        def _enhance_prompt_for_sd_location(base: str, style_name: Optional[str] = None):
            base = (base or "").strip()
            descriptors = (
                "concept art, detailed environment, atmospheric lighting, painterly, intricate architecture, moody shadows, cinematic color grading"
            )
            style_presets = {
                "photorealistic": "photorealistic, ultra-detailed, realistic lighting",
                "fantasy": "fantasy art, magical atmosphere, ornate details",
                "painterly": "oil painting, visible brushstrokes, warm palette",
                "cinematic": "cinematic color grading, dramatic lighting, wide lens",
            }
            style_desc = style_presets.get((style_name or "").lower(), "")
            positive_parts = [p for p in [base, style_desc, descriptors] if p]
            positive = ", ".join(positive_parts)
            negative = (
                "lowres, text, watermark, signature, poorly drawn, deformed, blurry, oversaturated, mutated, extra limbs, glitch, jpeg artifacts"
            )
            return positive, negative

        clean_prompt = _sanitize_prompt_text(prompt)

        if use_llm:
            try:
                from backend.routers.generation import call_llm

                llm_provider_to_use = llm_provider or "groq"
                llm_model_to_use = llm_model or None

                llm_instr = (
                    "You are a professional prompt engineer.\n"
                    "Rewrite the following location description into a single concise, visual prompt suitable for Stable Diffusion. "
                    "Remove dialogue, suggested actions, tables, and markdown. Keep only visual details (architecture, lighting, mood, weather, perspective). "
                    "Output ONLY the cleaned prompt on one line with no markdown or explanation.\n\n"
                    f"Text:\n{clean_prompt}"
                )

                llm_resp, _meta = await call_llm(llm_instr, llm_provider_to_use, llm_model_to_use)
                if isinstance(llm_resp, tuple):
                    llm_resp = llm_resp[0]
                summarized = (llm_resp or "").strip()
                if summarized:
                    clean_prompt = summarized
            except Exception:
                logger.exception("LLM summarization failed for location; using sanitized prompt instead")

        prompt_enhanced, negative_prompt = _enhance_prompt_for_sd_location(clean_prompt, style_name=style)

        steps = 30
        cfg_scale = 7.0
        seed = -1

        result = client.generate_image(
            prompt=prompt_enhanced,
            negative_prompt=negative_prompt,
            steps=steps,
            width=width,
            height=height,
            cfg_scale=cfg_scale,
            seed=seed,
            model=model,
        )

        return {
            "image_base64": result.get("image") or result.get("image_base64"),
            "prompt": prompt_enhanced,
            "negative_prompt": negative_prompt,
            "provider": "stablediffusion",
            "model": model or "local",
        }
    # Fallback to existing behavior for other providers
    return await generate_landscape_image(
        prompt=prompt, provider=provider, model=model, aspect_ratio=aspect_ratio
    )
