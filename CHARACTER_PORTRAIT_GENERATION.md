# Character Portrait Generation with Google Imagen

## Overview

This feature allows users to generate AI-powered character portraits using Google's Imagen 4.0 model after creating a character with Groq's text generation. This combines the best of both worlds:

- **Groq (Llama)**: Fast, unrestricted text generation for character descriptions
- **Google Imagen**: High-quality portrait generation based on character appearance

## How It Works

### Workflow

1. **Generate Character** (using Groq)
   - User selects traits, themes, and archetypes
   - Groq generates detailed character description with appearance details
   - Character content is displayed in the Review & Save step

2. **Generate Portrait** (using Google Imagen)
   - User clicks "Generate Portrait" button
   - Backend extracts physical appearance from character description
   - Builds optimized Imagen prompt following best practices
   - Imagen generates 3:4 portrait-style image
   - Image is displayed as Base64 encoded PNG

3. **Save Character**
   - User saves character to database
   - Portrait image is stored as Base64 in `portrait_image` column
   - Image prompt is stored in `image_prompt` column

## Architecture

### Backend Components

#### `backend/imagen_client.py`

- **`extract_character_appearance(content)`**: Extracts appearance section from text
- **`build_character_image_prompt(name, appearance)`**: Builds optimized Imagen prompt
- **`generate_character_portrait(name, appearance_text, model, aspect_ratio, custom_prompt)`**: Main generation function

#### `backend/routers/generation.py`

- **`POST /api/generate/character/generate-portrait`**: Generate portrait endpoint
  - Request: `ImageGenerationRequest` (character_name, appearance_text, model, aspect_ratio)
  - Response: `{ image_base64, prompt, model, aspect_ratio, message }`
- **`POST /api/generate/character/save-portrait`**: Save portrait to character (future)

#### `backend/models.py`

- **Character Model** additions:
  - `portrait_image` (Text): Base64 encoded PNG image data
  - `image_prompt` (Text): Prompt used to generate the image

### Frontend Components

#### `frontend/src/routes/create/character.jsx`

- **Portrait Generation UI**:
  - "Generate Portrait" button in Step 2 (Review & Save)
  - Portrait preview with Base64 image display
  - Error handling for generation failures
  - Loading state with CircularProgress

### Database Schema

```sql
ALTER TABLE characters ADD COLUMN portrait_image TEXT;
ALTER TABLE characters ADD COLUMN image_prompt TEXT;
```

**Migration**: `backend/migrate_add_portrait.py`

## Configuration

### Required Environment Variables

```bash
# .env
GOOGLE_API_KEY=your_google_api_key_here
```

### Required Python Packages

```bash
pip install google-genai pillow
```

### Models Available

- `imagen-4.0-fast-generate-001` (default) - Fast generation, good quality
- `imagen-4.0-generate-001` - Standard quality, balanced
- `imagen-4.0-ultra-generate-001` - Highest quality, slower

## Prompt Engineering

The system follows Imagen best practices:

### Prompt Structure

```
A professional [style] of [appearance description],
35mm portrait, depth of field, 4K HDR, cinematic quality, professional photography
```

### Example Prompts

**Input Appearance**:

> A tall, muscular warrior in his early 30s with short black hair, a prominent scar across his left cheek, wearing battle-worn leather armor with silver studs.

**Generated Prompt**:

```
A professional portrait photograph of a tall, muscular warrior in his early 30s
with short black hair, a prominent scar across his left cheek, wearing battle-worn
leather armor with silver studs, 35mm portrait, depth of field, 4K HDR,
cinematic quality, professional photography
```

### Quality Modifiers

- **Portrait style**: 35mm portrait
- **Depth**: depth of field
- **Quality**: 4K HDR, cinematic quality, professional photography
- **Aspect ratio**: 3:4 (vertical portrait orientation)

## API Reference

### Generate Character Portrait

**Endpoint**: `POST /api/generate/character/generate-portrait`

**Request Body**:

```json
{
  "character_name": "Ragnar Blackwood",
  "appearance_text": "Full character description with appearance details...",
  "model": "imagen-4.0-fast-generate-001",
  "aspect_ratio": "3:4",
  "custom_prompt": null
}
```

**Response**:

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "A professional portrait photograph of...",
  "model": "imagen-4.0-fast-generate-001",
  "aspect_ratio": "3:4",
  "message": "Portrait generated successfully"
}
```

**Error Responses**:

- `500`: Image generation unavailable (missing packages)
- `500`: GOOGLE_API_KEY not configured
- `500`: Imagen API error (safety filters, quota, etc.)

## Cost Considerations

### Google Imagen Pricing

- **Fast Model**: ~$0.02 per image
- **Standard Model**: ~$0.05 per image
- **Ultra Model**: ~$0.10 per image

### Optimization Strategies

1. **Use Fast Model by Default**: Good quality, lowest cost
2. **One Image per Character**: Generate single portrait (not 4)
3. **Cache Images**: Store as Base64 in database, no repeated generations
4. **User Control**: Only generate when user clicks button

## Safety Considerations

### Google's Content Policies

Imagen enforces content policies:

- No explicit content
- No violence/gore
- No hate speech
- All images include SynthID watermarks

### Our Approach

1. **Groq for Text**: Use Groq (no restrictions) for character descriptions
2. **Imagen for Images**: Use Imagen only for portrait generation
3. **Clean Prompts**: Extract appearance only, remove violent/dark elements
4. **Error Handling**: Clear messages if Imagen blocks a prompt

### Safety Filter Handling

Unlike Gemini text generation, Imagen safety filters are less aggressive for character portraits. However, if blocked:

1. **Fallback**: Character is saved without portrait
2. **Error Message**: "Failed to generate portrait. Make sure Google API key is configured."
3. **Retry**: User can try again with different name/appearance

## User Experience

### Success Flow

1. User fills out character creation form
2. Clicks "Generate with AI" (Groq generates text)
3. Reviews generated character description
4. Enters character name
5. Clicks "Generate Portrait" (Imagen generates image)
6. Portrait displays below button
7. Clicks "Save Character" (saves to database with portrait)

### Error Handling

- **Missing Name**: "Please enter a character name first"
- **API Key Missing**: "Make sure Google API key is configured"
- **Generation Failed**: Shows specific error from Imagen
- **Close Button**: Users can dismiss errors and continue

### Visual Design

- **Portrait Section**: Separate Paper component with dark background
- **Image Display**: Centered, max 500px height, rounded corners, shadow
- **Caption**: "Generated with Google Imagen" below image
- **Responsive**: Scales to container width

## Testing

### Manual Testing Steps

1. **Setup**:

   ```bash
   # Backend
   cd backend
   pip install google-genai pillow
   export GOOGLE_API_KEY=your_key
   python main.py

   # Frontend
   cd frontend
   npm run dev
   ```

2. **Test Character Creation**:
   - Navigate to "Create Character"
   - Select traits and themes
   - Generate character with Groq
   - Verify text generation works

3. **Test Portrait Generation**:
   - Enter character name: "Test Character"
   - Click "Generate Portrait"
   - Verify portrait appears
   - Check console for any errors

4. **Test Database**:
   - Save character
   - Query database:
     ```sql
     SELECT id, name, portrait_image, image_prompt FROM characters;
     ```
   - Verify portrait_image contains Base64 data

### Error Testing

1. **Missing API Key**:
   - Remove GOOGLE_API_KEY from .env
   - Try generating portrait
   - Should show config error

2. **Invalid Prompt**:
   - Generate character with very short description
   - Try portrait generation
   - Should handle gracefully

3. **Network Issues**:
   - Disconnect internet
   - Try portrait generation
   - Should show connection error

## Future Enhancements

### Phase 1: Complete (Current)

- ✅ Basic portrait generation
- ✅ Base64 storage in database
- ✅ Frontend UI integration
- ✅ Error handling
- ✅ Imagen prompt optimization

### Phase 2: Advanced Features

- [ ] Multiple portrait variations (generate 4 images)
- [ ] Image selection gallery
- [ ] Style presets (realistic, anime, comic, painting)
- [ ] Aspect ratio selection (1:1, 3:4, 4:3)
- [ ] Model selection (Fast/Standard/Ultra)
- [ ] Custom prompt override in UI

### Phase 3: File Storage

- [ ] Save images as files (storage/images/characters/)
- [ ] Serve images via /api/images/characters/<filename>
- [ ] Thumbnail generation
- [ ] CDN integration

### Phase 4: Batch Generation

- [ ] Generate portraits for all characters
- [ ] Background job processing
- [ ] Progress tracking
- [ ] Queue management

## Troubleshooting

### Common Issues

**Issue**: "Image generation unavailable"

- **Cause**: Missing Python packages
- **Solution**: `pip install google-genai pillow`

**Issue**: "GOOGLE_API_KEY not configured"

- **Cause**: Missing API key in .env
- **Solution**: Add `GOOGLE_API_KEY=your_key` to backend/.env

**Issue**: "Failed to generate portrait"

- **Cause**: Imagen safety filters blocked prompt
- **Solution**: Character saved without portrait, try rephrasing appearance

**Issue**: Portrait not displaying

- **Cause**: Base64 encoding issue
- **Solution**: Check browser console for errors, verify API response

**Issue**: Slow generation

- **Cause**: Using Ultra model or network latency
- **Solution**: Switch to Fast model (default)

## Technical Notes

### Base64 Image Storage

**Pros**:

- Simple implementation
- No file system management
- Easy to display in React
- Works with any database

**Cons**:

- Increases database size (~33% overhead)
- Not efficient for large images
- No caching benefits

**When to Switch to File Storage**:

- More than 1000 characters with portraits
- Performance issues with large payloads
- Need CDN/caching
- Want thumbnail generation

### Image Size

- **Resolution**: 1K (1024px) by default
- **Aspect Ratio**: 3:4 (portrait orientation)
- **File Size**: ~100-300KB per PNG
- **Base64 Size**: ~130-400KB in database

## Documentation Links

- [Google Imagen API](https://ai.google.dev/gemini-api/docs/imagen)
- [Imagen Prompt Guide](https://ai.google.dev/gemini-api/docs/imagen#prompt-writing-basics)
- [Google GenAI Python SDK](https://github.com/google-gemini/generative-ai-python)
- [IMAGE_GENERATION.md](./IMAGE_GENERATION.md) - Full implementation guide

## Credits

- **Text Generation**: Groq (Llama 3.3 70B, Llama 4 Scout)
- **Image Generation**: Google Imagen 4.0
- **Frontend**: React + Material-UI
- **Backend**: FastAPI + SQLAlchemy
