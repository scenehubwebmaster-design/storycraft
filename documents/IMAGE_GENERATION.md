# Image Generation Capabilities

## Overview

This document outlines the image generation capabilities available through our LLM providers. Currently, we have **text generation** for characters, stories, worlds, scenes, and locations. This guide explores adding **image generation** for visual character portraits and scene illustrations.

## Provider Capabilities

### 🚫 Groq - Vision Only (No Image Generation)

**Status**: Groq does **NOT** support text-to-image generation

**What Groq DOES Support**:

- ✅ **Image Understanding** (Vision): Analyze uploaded images
- ✅ **Visual Question Answering**: Ask questions about images
- ✅ **OCR**: Extract text from images
- ✅ **Multi-turn conversations** with images

**Models with Vision**:

- `meta-llama/llama-4-scout-17b-16e-instruct` (128K context)
- `meta-llama/llama-4-maverick-17b-128e-instruct` (128K context)

**Limitations**:

- ❌ Cannot generate images from text
- ❌ No text-to-image models available
- ✅ Can only consume and analyze images

**Use Cases**:

- Analyze uploaded character art
- Extract details from reference images
- Describe scenes from uploaded photos
- Multi-modal content understanding

---

### ✅ Google Imagen - Full Text-to-Image Generation

**Status**: Google Imagen **FULLY SUPPORTS** text-to-image generation

**What Google DOES Support**:

- ✅ **Text-to-Image Generation**: Create images from text prompts
- ✅ **High-fidelity output**: Realistic and artistic images
- ✅ **Multiple models**: Imagen 3 and Imagen 4 (Ultra, Standard, Fast)
- ✅ **Batch generation**: 1-4 images per request
- ✅ **Configurable aspect ratios**: 1:1, 3:4, 4:3, 9:16, 16:9
- ✅ **Resolution options**: 1K and 2K (Standard/Ultra only)
- ✅ **Text in images**: Generate text within images (up to 25 chars)
- ✅ **SynthID watermarks**: All images include invisible watermarks

**Available Models**:

| Model                           | Description                   | Best For          |
| ------------------------------- | ----------------------------- | ----------------- |
| `imagen-4.0-generate-001`       | Standard quality, balanced    | General use       |
| `imagen-4.0-ultra-generate-001` | Highest quality, slower       | Premium portraits |
| `imagen-4.0-fast-generate-001`  | Fast generation, good quality | Rapid iteration   |
| `imagen-3.0-generate-002`       | Previous generation, stable   | Budget option     |

**Configuration Options**:

```python
{
  "numberOfImages": 1-4,           # Number of images to generate
  "imageSize": "1K" or "2K",       # Resolution (Standard/Ultra only)
  "aspectRatio": "1:1",            # 1:1, 3:4, 4:3, 9:16, 16:9
  "personGeneration": "allow_adult" # Control people generation
}
```

**Person Generation Settings**:

- `"dont_allow"`: Block all people
- `"allow_adult"`: Adults only (default)
- `"allow_all"`: Adults and children (not allowed in EU/UK)

---

## Implementation Plan for Character Image Generation

### Phase 1: Backend Infrastructure

#### 1. Create `backend/imagen_client.py`

```python
"""
Google Imagen Image Generation Client
Handles text-to-image generation for character portraits and scenes.
"""
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from google import genai
    IMAGEN_AVAILABLE = True
except ImportError:
    IMAGEN_AVAILABLE = False


async def generate_character_image(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
    aspect_ratio: str = "1:1",
    num_images: int = 1
) -> List[bytes]:
    """
    Generate character portrait images from text prompt.

    Args:
        prompt: Descriptive text prompt
        model: Imagen model to use
        aspect_ratio: Image aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)
        num_images: Number of images to generate (1-4)

    Returns:
        List of image bytes
    """
    if not IMAGEN_AVAILABLE:
        raise Exception("Google GenAI client not installed")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("Google API key not configured")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config={
            "number_of_images": num_images,
            "aspect_ratio": aspect_ratio,
            "person_generation": "allow_adult",  # For character portraits
        }
    )

    images = []
    for generated_image in response.generated_images:
        # Get image bytes
        images.append(generated_image.image._pil_image)

    return images
```

#### 2. Add route in `backend/routers/generation.py`

```python
@router.post("/character/image")
async def generate_character_image(
    character_id: int,
    prompt: Optional[str] = None,
    model: str = "imagen-4.0-generate-001",
    aspect_ratio: str = "1:1",
    num_images: int = 1
):
    """
    Generate image for an existing character.

    Uses character description to create prompt if not provided.
    """
    # Get character from database
    character = get_character_by_id(character_id)

    # Build prompt from character data if not provided
    if not prompt:
        prompt = build_character_image_prompt(character)

    # Generate images
    images = await generate_character_image(
        prompt=prompt,
        model=model,
        aspect_ratio=aspect_ratio,
        num_images=num_images
    )

    # Save images to storage
    image_urls = []
    for idx, image in enumerate(images):
        url = save_character_image(character_id, image, idx)
        image_urls.append(url)

    return {
        "character_id": character_id,
        "images": image_urls,
        "prompt": prompt,
        "model": model
    }
```

#### 3. Prompt Engineering Helper

```python
def build_character_image_prompt(character: Dict) -> str:
    """
    Build optimized Imagen prompt from character data.

    Follows Imagen best practices:
    - Subject first
    - Context and background
    - Style specification
    - Quality modifiers
    """
    prompt_parts = []

    # Start with photo type
    prompt_parts.append("A professional portrait photograph of")

    # Add character basics
    if character.get("age"):
        prompt_parts.append(f"a {character['age']}-year-old")
    if character.get("gender"):
        prompt_parts.append(character["gender"])

    # Add physical description
    if character.get("appearance"):
        prompt_parts.append(character["appearance"])

    # Add context
    if character.get("background"):
        prompt_parts.append(f"in a {character['background']} setting")

    # Add style modifiers
    prompt_parts.append("35mm portrait")
    prompt_parts.append("depth of field")
    prompt_parts.append("studio lighting")
    prompt_parts.append("4K HDR")
    prompt_parts.append("professional quality")

    return ", ".join(prompt_parts)
```

### Phase 2: Frontend Integration

#### 1. Character Creator Enhancement

```jsx
// Add to character.jsx
const [showImageGenerator, setShowImageGenerator] = useState(false);
const [generatedImages, setGeneratedImages] = useState([]);
const [generatingImage, setGeneratingImage] = useState(false);

const handleGenerateImage = async () => {
  setGeneratingImage(true);

  try {
    const response = await axios.post(
      `${API_URL}/api/generate/character/image`,
      {
        character_id: savedCharacterId,
        aspect_ratio: "3:4", // Portrait orientation
        num_images: 4,
      }
    );

    setGeneratedImages(response.data.images);
    setSuccess("Character images generated successfully!");
  } catch (err) {
    setError(err.response?.data?.detail || "Failed to generate images");
  } finally {
    setGeneratingImage(false);
  }
};
```

#### 2. Image Gallery Component

```jsx
// frontend/src/components/ImageGallery.jsx
import { Box, ImageList, ImageListItem, Button } from "@mui/material";

export default function ImageGallery({ images, onSelect }) {
  return (
    <Box>
      <ImageList cols={2} gap={8}>
        {images.map((image, idx) => (
          <ImageListItem key={idx}>
            <img src={image} alt={`Generated ${idx + 1}`} />
            <Button onClick={() => onSelect(image)}>Select</Button>
          </ImageListItem>
        ))}
      </ImageList>
    </Box>
  );
}
```

### Phase 3: Database Schema

```sql
-- Add images table
CREATE TABLE character_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  character_id INTEGER NOT NULL,
  image_url TEXT NOT NULL,
  prompt TEXT NOT NULL,
  model TEXT NOT NULL,
  aspect_ratio TEXT,
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (character_id) REFERENCES characters(id)
);

-- Index for fast lookups
CREATE INDEX idx_character_images_character
ON character_images(character_id);
```

### Phase 4: Storage Strategy

```python
# backend/storage.py
import os
from pathlib import Path
from PIL import Image
import uuid

STORAGE_DIR = Path("storage/images/characters")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def save_character_image(
    character_id: int,
    image: Image.Image,
    index: int = 0
) -> str:
    """
    Save character image to filesystem.

    Returns: URL path to image
    """
    # Generate unique filename
    filename = f"character_{character_id}_{uuid.uuid4().hex[:8]}_{index}.png"
    filepath = STORAGE_DIR / filename

    # Save image
    image.save(filepath, "PNG")

    # Return URL
    return f"/api/images/characters/{filename}"
```

---

## Imagen Prompt Best Practices

### Structure

1. **Subject**: What/who you want (character, scene)
2. **Context**: Background, setting, environment
3. **Style**: Photography style, art style, medium
4. **Quality Modifiers**: Resolution, lighting, detail level

### Character Portrait Template

```
A [photography style] of a [age] [gender] [description],
[clothing/accessories], [facial features], [hair style],
in a [setting/background], [lighting], [camera settings],
[quality modifiers]
```

### Examples

**Fantasy Warrior**:

```
A professional portrait photograph of a 30-year-old male warrior,
wearing intricate leather armor with silver details, strong jawline,
short dark hair with a scar across his left eyebrow, holding a sword,
in a medieval castle background, dramatic lighting, 35mm portrait,
depth of field, 4K HDR, cinematic quality
```

**Sci-Fi Pilot**:

```
A high-quality portrait of a 25-year-old female pilot,
wearing a sleek space suit with glowing blue accents, confident expression,
tied-back red hair, tech visor on forehead, futuristic cockpit background,
neon lighting, 50mm lens, soft focus, professional photography,
detailed, 4K resolution
```

**Mystery Detective**:

```
A film noir style portrait of a 40-year-old detective,
wearing a trench coat and fedora, weathered features, five o'clock shadow,
smoking a cigarette, dark urban alley background, moody lighting,
black and white photography, 35mm, dramatic shadows, vintage film grain
```

### Style Modifiers

**Photography Styles**:

- `professional portrait photograph`
- `studio photo`
- `street photography`
- `35mm portrait`
- `film noir`
- `polaroid portrait`

**Lighting**:

- `natural lighting`
- `dramatic lighting`
- `golden hour`
- `studio lighting`
- `soft focus`
- `moody lighting`

**Quality**:

- `4K HDR`
- `professional quality`
- `high detail`
- `cinematic quality`
- `sharp focus`
- `depth of field`

**Camera Settings**:

- `35mm portrait` (standard portraits)
- `50mm lens` (natural perspective)
- `85mm portrait` (compressed, flattering)
- `macro lens` (close-up details)
- `wide angle` (environmental)

---

## Rate Limits & Pricing

### Google Imagen (Free Tier)

**Note**: Imagen is currently **NOT included** in the free tier. It requires paid access.

- **Pricing**: Pay-per-image generation
- **Estimated Cost**: ~$0.02-0.10 per image (varies by model)
- **Models**:
  - Fast: Lowest cost, fastest
  - Standard: Medium cost, good quality
  - Ultra: Highest cost, best quality

### Groq (Not Applicable)

- Groq does not offer image generation

---

## Implementation Roadmap

### Milestone 1: Basic Integration ✅ Ready

- [x] Document Imagen API capabilities
- [ ] Create `imagen_client.py` with basic generation
- [ ] Add `/api/generate/character/image` endpoint
- [ ] Test single image generation
- [ ] Handle errors and API limits

### Milestone 2: Character Integration

- [ ] Add "Generate Portrait" button to Character Creator
- [ ] Build prompt from character data automatically
- [ ] Display generated images in gallery
- [ ] Allow selecting primary image
- [ ] Save image references to database

### Milestone 3: Advanced Features

- [ ] Multiple image variants (4 at once)
- [ ] Custom prompt overrides
- [ ] Style presets (realistic, anime, comic, painting)
- [ ] Aspect ratio selection
- [ ] Model selection (Fast/Standard/Ultra)
- [ ] Regenerate with variations

### Milestone 4: Scene Images

- [ ] Generate scene illustrations
- [ ] Generate location images
- [ ] Generate world map visuals
- [ ] Batch generation for stories

### Milestone 5: Polish

- [ ] Image caching
- [ ] CDN integration
- [ ] Thumbnail generation
- [ ] Download options
- [ ] Sharing capabilities

---

## Safety Considerations

### Google Imagen Safety

- All images include **SynthID watermarks** (invisible)
- Person generation controlled by `personGeneration` setting
- Content policy enforcement:
  - No explicit content
  - No violence/gore
  - No hate speech
  - No impersonation
  - No copyrighted characters

### Prompt Filtering

- Imagen may reject prompts that violate policies
- Suggest rephrasing if blocked
- Provide alternative styles
- Offer text-only fallback

---

## Alternative: Groq for Vision Analysis

While Groq cannot **generate** images, it excels at **analyzing** them:

```python
# Analyze uploaded character art
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this character in detail for a character sheet."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": uploaded_image_url
                    }
                }
            ]
        }
    ]
)

character_description = response.choices[0].message.content
```

**Use Case**: User uploads reference art → Groq extracts character details → Auto-fills character form

---

## Conclusion

- ✅ **Google Imagen**: Full text-to-image generation, perfect for character portraits
- ❌ **Groq**: Vision analysis only, no image generation
- 🚀 **Recommended**: Use Google Imagen for generating character images
- 💡 **Bonus**: Use Groq to analyze uploaded reference images and extract character details

### Next Steps

1. Set up Google Imagen API access (requires paid account)
2. Implement basic image generation endpoint
3. Add UI to Character Creator
4. Test with various prompts
5. Expand to scenes and locations

---

**Note**: Image generation with Imagen requires a Google Cloud account with billing enabled. The free tier does not include Imagen API access.
