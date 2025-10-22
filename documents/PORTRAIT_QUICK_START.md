# Character Portrait Generation - Quick Start Guide

## Setup (One-time)

### 1. Install Dependencies

```bash
cd backend
pip install google-genai pillow
```

### 2. Configure Google API Key

Add to `backend/.env`:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key: https://aistudio.google.com/apikey

### 3. Run Database Migration

```bash
cd backend
python migrate_add_portrait.py
```

Expected output:

```
Starting database migration...
Adding portrait image support to characters table

✓ portrait_image column added
✓ image_prompt column added

✓ Migration completed successfully!
```

## Usage

### Step 1: Generate Character Text (using Groq)

1. Navigate to **Create → Character**
2. Select traits and themes
3. Click **"Generate with AI"**
4. Wait for Groq to generate character description

### Step 2: Generate Portrait (using Google Imagen)

1. Enter **Character Name** in the text field
2. Click **"Generate Portrait"** button
3. Wait 3-5 seconds for Imagen to generate image
4. Portrait appears below the button

### Step 3: Save Character

1. Review generated content
2. Optionally refine or edit
3. Click **"Save Character"**
4. Character saved with portrait to database

## UI Flow

```
┌─────────────────────────────────────┐
│  Step 2: Review & Save              │
├─────────────────────────────────────┤
│                                     │
│  Character Name: [Text Input]      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Character Portrait         │   │
│  │  [Generate Portrait Button] │   │
│  │                             │   │
│  │  [Portrait Image Preview]   │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Character Content Display]       │
│                                     │
│  [Save Character Button]           │
└─────────────────────────────────────┘
```

## Example

### Input Character Traits

- **Themes**: Fantasy, Medieval
- **Archetype**: The Warrior
- **Personality**: Brave, Honorable, Stoic
- **Physical**: Tall, Muscular, Scarred
- **Custom**: "A veteran knight who has seen many battles"

### Generated Character (by Groq)

```
**Name**: Ragnar Blackwood

**Appearance**: A towering man in his early 30s with broad shoulders
and a muscular build. Short, dark hair with streaks of silver at the
temples. A prominent scar runs across his left cheek, a reminder of
past battles. Wears battle-worn leather armor with silver studs.

**Personality**: Stoic and honorable, speaks little but acts decisively...
```

### Generated Portrait (by Imagen)

**Prompt Used**:

```
A professional portrait photograph of a towering man in his early 30s
with broad shoulders and a muscular build, short dark hair with streaks
of silver at the temples, a prominent scar runs across his left cheek,
wearing battle-worn leather armor with silver studs, 35mm portrait,
depth of field, 4K HDR, cinematic quality, professional photography
```

**Result**: High-quality 3:4 portrait image displayed in UI

## Troubleshooting

### Portrait button is disabled

**Cause**: Character name field is empty

**Solution**: Enter a name in the "Character Name" field

### "Failed to generate portrait. Make sure Google API key is configured."

**Cause**: Missing or invalid GOOGLE_API_KEY

**Solution**:

1. Check `backend/.env` has correct API key
2. Verify key is valid at https://aistudio.google.com/apikey
3. Restart backend server

### Portrait generation takes too long

**Cause**: Using Ultra model or slow network

**Solution**:

- Fast model (default): 2-3 seconds
- Standard model: 5-7 seconds
- Ultra model: 10-15 seconds
- Check internet connection

### Portrait doesn't match character

**Cause**: Appearance description unclear or too short

**Solution**:

1. Refine character description to be more specific
2. Regenerate character with better physical trait selection
3. Try generating portrait again

### Image doesn't display

**Cause**: Base64 encoding issue or API error

**Solution**:

1. Check browser console for errors
2. Verify backend logs for Imagen errors
3. Try regenerating portrait

## Tips for Best Results

### 1. Be Specific with Physical Traits

✅ **Good**: "Tall, muscular warrior with short black hair, scar on left cheek"

❌ **Bad**: "A warrior"

### 2. Include Clothing/Armor Details

✅ **Good**: "Wearing battle-worn leather armor with silver studs"

❌ **Bad**: "Wearing armor"

### 3. Add Age and Build

✅ **Good**: "A man in his early 30s, broad-shouldered, athletic build"

❌ **Bad**: "A man"

### 4. Use Custom Details Field

Add specific details in the custom field:

```
Include:
- Prominent facial scar
- Silver-studded leather armor
- Weathered appearance from years of battle
- Short, practical hairstyle
```

## Cost Estimate

### Per Character Portrait

- **Fast Model** (default): ~$0.02
- **Standard Model**: ~$0.05
- **Ultra Model**: ~$0.10

### Typical Usage

- **10 characters/month**: ~$0.20 (Fast model)
- **50 characters/month**: ~$1.00 (Fast model)
- **100 characters/month**: ~$2.00 (Fast model)

**Note**: These are estimates. Actual costs may vary based on Google's pricing.

## Feature Comparison

| Feature      | Groq (Text)            | Google Imagen (Portrait) |
| ------------ | ---------------------- | ------------------------ |
| Speed        | ⚡ Very Fast (1-2s)    | 🐢 Moderate (3-5s)       |
| Cost         | ✅ Free                | 💰 ~$0.02/image          |
| Restrictions | ✅ None                | ⚠️ Content policy        |
| Quality      | ✅ Excellent text      | ✅ High-quality images   |
| Best For     | Character descriptions | Character portraits      |

## Next Steps

1. ✅ Generate your first character with portrait
2. 📝 Experiment with different traits and styles
3. 💾 Save characters to build your story world
4. 🎨 Try different prompt variations
5. 📖 Read full docs in CHARACTER_PORTRAIT_GENERATION.md

## Need Help?

- **Full Documentation**: [CHARACTER_PORTRAIT_GENERATION.md](./CHARACTER_PORTRAIT_GENERATION.md)
- **Image Generation Guide**: [IMAGE_GENERATION.md](./IMAGE_GENERATION.md)
- **Google Safety Info**: [GOOGLE_SAFETY_QUICK_REF.md](./GOOGLE_SAFETY_QUICK_REF.md)
- **API Reference**: See CHARACTER_PORTRAIT_GENERATION.md → API Reference section

## Keyboard Shortcuts (Future)

- `Ctrl + G`: Generate character text
- `Ctrl + P`: Generate portrait
- `Ctrl + S`: Save character

(Not yet implemented - coming in future update)
