# Quick Reference: Structured Output API

## Endpoints

### 1. Character Structured Generation

**POST** `/api/generate/character/structured`

**Request Body:**

```json
{
  "themes": ["fantasy", "adventure"],
  "personality_traits": ["brave", "loyal", "sarcastic"],
  "physical_traits": ["tall", "muscular"],
  "archetype": "warrior",
  "custom_details": "A former knight seeking redemption",
  "provider": "openai",
  "model": "gpt-4"
}
```

**Response (CharacterProfile):**

```json
{
  "name": "Sir Aldric Thornheart",
  "age": 34,
  "height": "6 feet 2 inches",
  "build": "muscular and battle-hardened with broad shoulders",
  "hair": "dark brown, cropped short with streaks of premature grey",
  "eyes": "steel blue with a weary, haunted look",
  "distinctive_features": [
    "jagged scar running from left temple to jawline",
    "burn mark on right forearm shaped like a crest",
    "perpetual five o'clock shadow"
  ],
  "physical_description": "Aldric cuts an imposing figure...",
  "personality_traits": [
    "Brave - never backs down from danger",
    "Loyal - fiercely protective of those he cares about",
    "Sarcastic - uses dry humor to deflect emotional pain"
  ],
  "demeanor": "Gruff and standoffish at first...",
  "sense_of_humor": "Dry, self-deprecating wit...",
  "personality_description": "Beneath his hardened exterior...",
  "birthplace": "Thornhold, capital of the fallen kingdom of Arendor",
  "upbringing": "Raised in the royal knights' academy...",
  "formative_events": [
    "Witnessed the fall of Thornhold at age 18",
    "Failed to save his mentor during the siege"
  ],
  "backstory": "Once a decorated knight of the realm...",
  "primary_motivation": "To atone for failing his kingdom...",
  "goals": [
    "Find and eliminate the betrayer who caused the fall",
    "Rebuild the Knights of Thornhold",
    "Protect innocent villagers from bandits"
  ],
  "values": ["Honor above all", "Protecting the weak", "Keeping one's word"],
  "greatest_fear": "That he is fundamentally unworthy of redemption...",
  "emotional_weaknesses": [
    "Survivor's guilt that clouds judgment",
    "Difficulty accepting forgiveness or moving on"
  ],
  "physical_weaknesses": [
    "Old knee injury that flares up in cold weather",
    "Decreased stamina due to age"
  ],
  "skills": [
    "Master swordsman (30+ years training)",
    "Expert tactician and battlefield commander",
    "Skilled horseback rider",
    "Basic field medicine and survival skills"
  ],
  "special_abilities": "None - a skilled but ordinary human warrior",
  "combat_style": "Defensive and tactical, prioritizing protection over aggression...",
  "strengths_description": "Aldric's greatest strength is his unwavering resolve...",
  "key_relationships": [
    {
      "name": "Princess Elara",
      "relationship": "Former charge",
      "description": "The last heir of Arendor whom he failed to save"
    },
    {
      "name": "Finn the Quick",
      "relationship": "Loyal squire",
      "description": "A young thief he saved who now travels with him"
    }
  ],
  "character_arc_potential": "Aldric's journey is one of redemption...",
  "unique_qualities": "What makes Aldric truly memorable is the conflict...",
  "quirks_and_habits": [
    "Polishes his sword every night before sleeping",
    "Always sits with his back to the wall",
    "Gives away most of his earnings to needy families"
  ]
}
```

---

### 2. World Structured Generation

**POST** `/api/generate/world/structured`

**Request Body:**

```json
{
  "themes": ["dark fantasy", "political intrigue"],
  "setting": ["medieval", "low magic"],
  "elements": ["kingdoms", "ancient prophecy"],
  "custom_details": "A dying empire torn by civil war",
  "provider": "google",
  "model": "gemini-2.0-flash"
}
```

**Response (WorldProfile):**

```json
{
  "name": "The Sundered Empire of Valdoria",
  "world_type": "Dark Medieval Fantasy",
  "tagline": "Where dying kingdoms feast on each other's bones",
  "overview": "Valdoria was once a mighty empire...",
  "age": "Ancient - over 800 years since the First Unification",
  "origin_story": "Legend tells that eight warring kingdoms...",
  "major_historical_events": [
    {
      "event": "The First Unification",
      "era": "Year 0 of the Imperial Calendar",
      "description": "Eight kingdoms united under Emperor Valdor I"
    },
    {
      "event": "The Sundering",
      "era": "Year 783",
      "description": "Emperor Aldrus III dies without heir, civil war erupts"
    }
  ],
  "current_era": "The Age of Blood (Year 812)",
  "history_summary": "Valdoria's history is one of cycles...",
  "size_and_scale": "Continental empire spanning roughly 2 million square miles",
  "climate_zones": [
    "Northern Tundra - perpetually frozen wastes",
    "Central Highlands - temperate but rocky terrain",
    "Southern Plains - fertile farmlands",
    "Eastern Marshlands - swampy and disease-ridden",
    "Western Coasts - storm-battered cliffs"
  ],
  "major_regions": [
    {
      "name": "The Imperial Heartland",
      "description": "War-torn center of the empire, contested by three factions"
    },
    {
      "name": "The Free Cities",
      "description": "Independent city-states profiting from the chaos"
    }
  ],
  "natural_wonders": [
    "The Shattered Peaks - mountains split by ancient magic",
    "The Weeping Woods - forest that literally cries at night",
    "The Glass Desert - sand fused into glass by a fallen star"
  ],
  "geography_summary": "Valdoria's diverse geography reflects its fractured state...",
  "dominant_species": "Humans (98%), with small populations of dwarves and halflings",
  "population_estimate": "Approximately 40 million, down from 60 million before the civil war",
  "major_civilizations": [
    {
      "name": "The Legitimists",
      "description": "Supporters of Princess Seraphina, claiming blood right to the throne"
    },
    {
      "name": "The New Order",
      "description": "Military junta led by General Thorne, believing in meritocracy"
    },
    {
      "name": "The People's Covenant",
      "description": "Democratic movement seeking to abolish the monarchy"
    }
  ],
  "languages": [
    "High Valdorian - language of nobility and law",
    "Common Tongue - trade language spoken by all",
    "Old Imperial - dead language of scholars and mages"
  ],
  "religions_and_beliefs": [
    "The Church of the Eight Saints - official imperial religion",
    "Ancestral Worship - common among rural folk",
    "The Sundered Faith - apocalyptic cult gaining followers"
  ],
  "cultural_norms": [
    "Blood oaths are sacred and binding",
    "Nobles wear house colors at all times",
    "Deserters are branded and cast out",
    "Hospitality laws protect guests even in wartime"
  ],
  "culture_summary": "Valdorian culture is steeped in tradition and rigid hierarchy...",
  "power_system": "Low Magic - rare and often dangerous",
  "power_level": "Rare and limited, feared more than revered",
  "limitations": "Magic is unpredictable, requires blood sacrifice, and often corrupts the user",
  "notable_artifacts": [
    "The Crown of Eight Stars - grants legitimacy to the true emperor",
    "The Shattered Sword - legendary weapon broken in the Sundering",
    "The Oracle's Eye - scrying stone that shows possible futures"
  ],
  "major_conflicts": [
    "The Three-Way Civil War - Legitimists vs. New Order vs. People's Covenant",
    "Border skirmishes with northern barbarian tribes",
    "Economic collapse and widespread famine"
  ],
  "central_themes": "Power corrupts, the cycle of violence, the cost of ambition",
  "current_threats": "The Sundered Faith cult grows in power, foreign invasion looms, ancient evils awaken",
  "legends_and_myths": "The prophecy of the Chosen One who will reunite the empire...",
  "unsolved_mysteries": "What really killed Emperor Aldrus III? Why did the last court mage disappear?",
  "prophecies": "When the Shattered Sword is reforged, the true heir will be revealed",
  "lore_summary": "Valdoria's lore is rich with tragedy and dark secrets...",
  "adventure_hooks": [
    "Hired to escort a noble through enemy territory",
    "Discover evidence of the Chosen One's identity",
    "Uncover a conspiracy to assassinate all three faction leaders",
    "Find a piece of the Shattered Sword"
  ],
  "notable_locations": [
    {
      "name": "The Hollow Throne",
      "type": "Abandoned Palace",
      "description": "The Imperial Palace, now a haunted ruin contested by all factions"
    },
    {
      "name": "Crossroads Keep",
      "type": "Neutral Ground",
      "description": "The only place where all factions meet for parley"
    }
  ],
  "unique_aspects": "Valdoria is perfect for stories of political intrigue, moral ambiguity, and desperate heroes..."
}
```

---

## Supported Providers

| Provider          | Models                                                           | Native Structured Output |
| ----------------- | ---------------------------------------------------------------- | ------------------------ |
| **OpenAI**        | gpt-4, gpt-4-turbo, gpt-3.5-turbo                                | ✅ Yes                   |
| **Google/Gemini** | gemini-2.0-flash, gemini-2.5-pro                                 | ✅ Yes                   |
| **Groq**          | llama-3.3-70b-versatile, openai/gpt-oss-20b, openai/gpt-oss-120b | ✅ Yes                   |
| **Anthropic**     | claude-3-5-sonnet-20241022                                       | ⚠️ Prompt-based only     |

---

## Comparison: Structured vs. Free-form

| Aspect            | Free-form (`/character`, `/world`) | Structured (`/character/structured`, `/world/structured`) |
| ----------------- | ---------------------------------- | --------------------------------------------------------- |
| **Response Type** | Plain text (markdown/formatted)    | Validated JSON (Pydantic model)                           |
| **Completeness**  | ⚠️ May be incomplete/cut off       | ✅ Guaranteed all fields filled                           |
| **Structure**     | ❌ Variable format                 | ✅ Consistent schema                                      |
| **Specificity**   | ⚠️ May be vague                    | ✅ Concrete, specific details                             |
| **Tokens Used**   | Lower (~1500-2000)                 | Higher (~3000-4000)                                       |
| **Cost**          | Lower                              | Higher                                                    |
| **Use Case**      | Quick generation, creative freedom | Production, database storage, UI display                  |

---

## Error Handling

### Common Errors

#### 1. Validation Error (500)

```json
{
  "detail": "Failed to parse structured output: 1 validation error for CharacterProfile\nage\n  Input should be a valid integer [type=int_type]"
}
```

**Cause:** LLM returned invalid data type (e.g., string instead of integer)
**Solution:** Try again or use a different provider/model

#### 2. Rate Limit Error (429)

```json
{
  "detail": "Rate limit exceeded for openai: Daily token limit reached (1000000/1000000)"
}
```

**Cause:** Too many requests in short time
**Solution:** Wait or use a different provider

#### 3. API Key Error (500)

```json
{
  "detail": "OpenAI API key not configured"
}
```

**Cause:** Missing environment variable
**Solution:** Set `OPENAI_API_KEY` in `.env` file

---

## Best Practices

### 1. **Choose the Right Provider**

- **Production:** OpenAI `gpt-4` (most reliable)
- **Development:** Google `gemini-2.0-flash` (fast, cheap)
- **High Volume:** Groq `llama-3.3-70b-versatile` (fast inference)

### 2. **Optimize Token Usage**

- Use specific `custom_details` to guide generation
- Avoid redundant trait lists (pick 3-5 most important)
- Consider free-form for creative exploration, structured for final versions

### 3. **Handle Validation Errors**

- Implement retry logic (different provider or temperature)
- Fall back to free-form generation if structured fails repeatedly
- Log validation errors for monitoring

### 4. **Frontend Integration**

```typescript
// Example: Fetch structured character
const response = await fetch("/api/generate/character/structured", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    themes: ["fantasy"],
    archetype: "warrior",
    provider: "openai",
    model: "gpt-4",
  }),
});

const characterProfile = await response.json();
// characterProfile is now a fully typed CharacterProfile object
console.log(characterProfile.name); // "Sir Aldric Thornheart"
console.log(characterProfile.age); // 34
```

---

## Testing

Run the test suite:

```bash
cd backend
python test_structured_output.py
```

Expected output:

```
🧪 STRUCTURED OUTPUT TESTING SUITE
================================================================================
🔑 Checking API Keys:
   ✅ openai: Configured
   ✅ google: Configured
   ✅ groq: Configured

================================================================================
TESTING STRUCTURED CHARACTER GENERATION
================================================================================
📝 Request: groq / llama-3.3-70b-versatile
⏳ Generating character profile...
✅ SUCCESS! Generated CharacterProfile
🔍 Validation Check:
   ✅ All 30 fields populated!
💾 Full profile saved to: test_character_output.json

================================================================================
TESTING STRUCTURED WORLD GENERATION
================================================================================
📝 Request: groq / llama-3.3-70b-versatile
⏳ Generating world profile...
✅ SUCCESS! Generated WorldProfile
🔍 Validation Check:
   ✅ All 40 fields populated!
💾 Full profile saved to: test_world_output.json

================================================================================
TEST SUMMARY
================================================================================
   Character Generation: ✅ PASSED
   World Generation:     ✅ PASSED

🎉 All tests passed! Structured output is working correctly.
```

---

## FAQ

### Q: When should I use structured vs. free-form generation?

**A:** Use structured for:

- Production character/world profiles
- Database storage
- Consistent UI display
- Guaranteed completeness

Use free-form for:

- Creative exploration
- One-off quick generations
- When you need unusual formats (poems, scripts, etc.)

### Q: Why does structured generation cost more tokens?

**A:** Structured output requires the LLM to fill many specific fields, which typically results in longer, more detailed responses. The schema also adds overhead.

### Q: Can I customize the schema fields?

**A:** Yes! Modify `CharacterProfile` or `WorldProfile` in `backend/schemas.py`. Remember to update the corresponding prompt templates in `backend/prompts.py`.

### Q: What if validation fails repeatedly?

**A:** Try:

1. Different provider (OpenAI is most reliable)
2. Different model (gpt-4 > gpt-3.5-turbo)
3. Adjust prompt to be more specific
4. Fall back to free-form generation

### Q: How do I add a new structured generation type (e.g., SceneProfile)?

**A:** Follow this pattern:

1. Create Pydantic model in `schemas.py` (e.g., `SceneProfile`)
2. Add structured prompt method in `prompts.py` (e.g., `scene_structured_prompt`)
3. Add endpoint in `generation.py` (e.g., `/scene/structured`)
4. Test with `test_structured_output.py`

---

## Additional Resources

- **Implementation Guide:** `IMPLEMENTATION_PHASE_3-5_COMPLETE.md`
- **Schemas:** `backend/schemas.py`
- **Prompts:** `backend/prompts.py`
- **Utilities:** `backend/structured_output_utils.py`
- **Test Suite:** `backend/test_structured_output.py`
