# Migration Guide: Adding Dynamic Model Selection to Creators

This guide shows how to add the new dynamic model selection feature to the remaining creator pages (Story, World, Scene, Location).

## Files Already Updated

- ✅ Character Creator (`frontend/src/routes/create/character.jsx`)

## Files to Update

- Story Creator (`frontend/src/routes/create/story.jsx`)
- World Creator (`frontend/src/routes/create/world.jsx`)
- Scene Creator (`frontend/src/routes/create/scene.jsx`)
- Location Creator (`frontend/src/routes/create/location.jsx`)

## Step-by-Step Migration

### 1. Add Import

Add ModelSelector import to the top of the file:

```javascript
import ModelSelector from "../../components/ModelSelector";
```

### 2. Add Model State

Add model state variable alongside provider (around line 50-60):

```javascript
const [provider, setProvider] = useState("groq"); // Change default to groq
const [model, setModel] = useState(""); // Add this line
```

### 3. Update API Calls

Add model parameter to all API calls:

**In handleGenerate():**

```javascript
const response = await axios.post(`${API_URL}/api/generate/{type}`, {
  // ... other parameters
  provider,
  model: model || null, // Add this line
});
```

**In handleRefine():**

```javascript
const response = await axios.post(`${API_URL}/api/generate/{type}`, {
  base_content: generatedContent,
  refinement_instructions: refinementInstructions,
  provider,
  model: model || null, // Add this line
});
```

### 4. Replace Provider Selector

Replace the old FormControl/Select section with ModelSelector:

**OLD CODE:**

```javascript
<Grid size={{ xs: 12 }}>
  <FormControl fullWidth>
    <InputLabel>AI Provider</InputLabel>
    <Select
      value={provider}
      onChange={(e) => setProvider(e.target.value)}
      label="AI Provider"
    >
      <MenuItem value="openai">OpenAI (GPT)</MenuItem>
      <MenuItem value="anthropic">Anthropic (Claude)</MenuItem>
      <MenuItem value="google">Google (Gemini)</MenuItem>
      <MenuItem value="groq">Groq (Llama)</MenuItem>
    </Select>
  </FormControl>
</Grid>
```

**NEW CODE:**

```javascript
<Grid size={{ xs: 12 }}>
  <ModelSelector
    provider={provider}
    model={model}
    onProviderChange={setProvider}
    onModelChange={setModel}
    contentType="{type}" // Change to: "story", "world", "scene", or "location"
  />
</Grid>
```

### 5. Content Type Mapping

Use the correct contentType for each creator:

- `contentType="character"` - Character Creator ✅ DONE
- `contentType="story"` - Story Creator
- `contentType="world"` - World Creator
- `contentType="scene"` - Scene Creator
- `contentType="location"` - Location Creator

## Task Complexity & Recommended Models

The system automatically recommends models based on content type:

| Content Type | Complexity | Groq Recommendation     | Google Recommendation |
| ------------ | ---------- | ----------------------- | --------------------- |
| Character    | medium     | llama-3.3-70b-versatile | gemini-2.5-flash      |
| Story        | complex    | llama-4-scout-17b-16e   | gemini-2.5-flash      |
| World        | complex    | llama-4-scout-17b-16e   | gemini-2.5-flash      |
| Scene        | medium     | llama-3.3-70b-versatile | gemini-2.5-flash      |
| Location     | simple     | llama-3.1-8b-instant    | gemini-2.0-flash      |

## Benefits

Once migrated, each creator will have:

✅ **Dynamic Model Selection** - Real-time model fetching from APIs
✅ **Rate Limit Display** - Shows quotas for informed decisions  
✅ **Smart Recommendations** - Task-appropriate model suggestions
✅ **Provider Status** - Visual availability indicators
✅ **Better UX** - Badges, tooltips, and detailed info boxes

## Testing

After migration, test each creator:

1. Navigate to the creator page
2. Verify provider dropdown shows availability badges
3. Select a provider and verify models load
4. Check that recommended model is auto-selected
5. Verify rate limits display correctly
6. Test generation with the selected model
7. Verify model parameter is sent to API

## Notes

- Default provider is now "groq" (fastest free tier)
- Models auto-load when provider changes
- Recommended model auto-selects if none chosen
- Rate limits formatted for readability (e.g., "30 req/min • 12K tok/min • 1K req/day")
