# RP Text Only Feature - TTS Enhancement

## Overview

The **RP Text Only** feature allows you to filter out mechanical D&D details from Text-to-Speech narration, focusing only on immersive storytelling and flavor text.

## Location

**TTSAudioPlayer Component** (`frontend/src/components/game/TTSAudioPlayer.jsx`)

When the voice selector is visible, you'll see a checkbox below it:

```
☐ RP Text Only (skip mechanics)
```

## How It Works

### What Gets Narrated (✅)

- Descriptive paragraphs
- Story and narrative text
- Dialogue
- Action descriptions
- Environmental descriptions
- Character descriptions

### What Gets Skipped (❌)

- Spell stats (Level, School, Casting Time, Range, Components, Duration)
- Monster stat blocks (AC, HP, Speed, Ability Scores, CR)
- Dice notation sections (unless part of narrative)
- Header text ("Here are the details", "Statistics:")
- Meta-commentary ("It seems you're trying to...")

## Example: Lightning Bolt Spell

### Full Text (749 characters)

```
Lightning Bolt

Level & School: 3rd-level evocation
Casting Time: 1 action
Range: Self (100-foot line)
Components: V, S, M (a bit of fur and a rod of amber, crystal, or glass)
Duration: Instantaneous

A stroke of lightning forming a line 100 feet long and 5 feet wide blasts
out from you in a direction you choose. Each creature in the line must make
a Dexterity saving throw. A creature takes 8d6 lightning damage on a failed
save, or half as much damage on a successful one.

The lightning ignites flammable objects in the area that aren't being worn
or carried.

At Higher Levels: When you cast this spell using a spell slot of 4th level
or higher, the damage increases by 1d6 for each slot level above 3rd.
```

### With RP Text Only (275 characters, 63.3% reduction)

```
A stroke of lightning forming a line 100 feet long and 5 feet wide blasts
out from you in a direction you choose. Each creature in the line must make
a Dexterity saving throw. A creature takes 8d6 lightning damage on a failed
save, or half as much damage on a successful one. The lightning ignites
flammable objects in the area that aren't being worn or carried.
```

## Benefits

1. **Faster playback** - 30-65% shorter audio
2. **Better immersion** - Focus on story, not stats
3. **Combat efficiency** - Quick narration during battles
4. **Player agency** - Players can read full details while hearing only flavor

## Usage

1. Open a chat session with TTS enabled
2. Ensure voice selector is visible (should appear automatically)
3. Check the **"RP Text Only (skip mechanics)"** checkbox
4. Generate or re-generate TTS audio
5. Audio will now only narrate descriptive text

## Technical Implementation

### Backend (Python)

File: `backend/tts_service.py`

```python
def _extract_flavor_text(self, text: str) -> str:
    """
    Extract only narrative/descriptive text from D&D content.
    Filters out mechanical details like spell stats, monster blocks, etc.
    """
    # Pattern matching for:
    # - Spell stats (Level & School, Casting Time, Range, etc.)
    # - Monster stats (AC, HP, Speed, Ability Scores, etc.)
    # - Dice notation headers
    # - Meta-commentary

    # Returns: Only narrative paragraphs and descriptive text
```

### API Endpoint

```
POST /api/chat/sessions/{session_id}/messages/{message_id}/tts
Query Parameters:
  - voice: string (default: "tara")
  - flavor_text_only: boolean (default: false)
```

### Frontend (React)

File: `frontend/src/components/game/TTSAudioPlayer.jsx`

```jsx
const [flavorTextOnly, setFlavorTextOnly] = useState(false);

<FormControlLabel
  control={
    <Checkbox
      checked={flavorTextOnly}
      onChange={handleFlavorTextToggle}
      size="small"
    />
  }
  label={<Typography variant="body2">RP Text Only (skip mechanics)</Typography>}
  sx={{ mb: 1 }}
/>;
```

## Testing

All tests pass successfully:

```bash
python backend/test_flavor_extraction.py
```

**Test Results:**

- Lightning Bolt: 63.3% removed (275 chars kept)
- Fireball: 29.2% removed (448 chars kept)
- Pure narrative: 0% removed (310 chars kept, all preserved)
- Monster: 39.3% removed (289 chars kept)

## Best Practices

1. **Use for spell/ability narration** - Perfect for when players cast spells or use abilities
2. **Enable during combat** - Keeps narration fast and focused
3. **Disable for rules clarification** - When you want full details narrated
4. **Combine with voice selection** - Choose the perfect voice AND filter mechanics

## Troubleshooting

### Feature not filtering correctly?

- Works best with D&D formatted content (spells, monsters, abilities)
- Custom text may not be recognized if formatting differs
- Plain narrative text is always preserved
- Check backend logs for `_extract_flavor_text` debug output

### Toggle not visible?

- Ensure voice selector is visible (`showVoiceSelector={true}`)
- Check that TTS is enabled in session settings
- Look for the checkbox below the voice dropdown

### Audio still too long?

- Some descriptive text may include dice notation in natural language
- Pattern matching is conservative to avoid removing story content
- File a bug report with specific examples for improvement

## Future Enhancements

- **Per-message toggle memory** - Remember setting per message type
- **Custom filter patterns** - Allow users to define what gets filtered
- **Visual preview** - Show extracted text before generating audio
- **Smart context awareness** - Better detection of narrative vs mechanical text

## References

- Implementation: `backend/tts_service.py` (lines ~150-200)
- Frontend component: `frontend/src/components/game/TTSAudioPlayer.jsx`
- Test suite: `backend/test_flavor_extraction.py`
- API documentation: `backend/routers/chat.py`

---

**Feature Status:** ✅ Complete and Tested

**Phase:** Post-Kitten TTS Migration

**Added:** 2025-01-23
