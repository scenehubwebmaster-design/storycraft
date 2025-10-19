# World Generation System - Implementation Plan

**Date:** October 18, 2025  
**Status:** 📋 PLANNING

## Overview

Implement a robust AI-powered world generation system that creates rich, detailed fantasy/sci-fi worlds with:

- AI-generated lore (history, geography, culture, magic systems)
- Stable Diffusion generated landscapes, cities, and locations
- Hierarchical structure (World → Locations → Sub-locations)
- Integration with character and story systems

## Database Schema Analysis

### Existing Tables

**`worlds` table:**

```sql
- id: INTEGER (PK)
- name: VARCHAR(255) NOT NULL
- description: TEXT
- history: TEXT
- geography: TEXT
- culture: TEXT
- magic_system: TEXT
- technology_level: VARCHAR(100)
- created_at: DATETIME
- updated_at: DATETIME
- structured_data: TEXT  -- JSON field for additional data
```

**`locations` table:**

```sql
- id: INTEGER (PK)
- world_id: INTEGER (FK → worlds.id) NOT NULL
- name: VARCHAR(255) NOT NULL
- description: TEXT
- location_type: VARCHAR(100)  -- city, town, dungeon, wilderness, etc.
- created_at: DATETIME
- updated_at: DATETIME
```

### Recommended Schema Additions

**Add to `worlds` table** (via migration):

```sql
ALTER TABLE worlds ADD COLUMN world_image TEXT;  -- Base64 landscape image
ALTER TABLE worlds ADD COLUMN world_map TEXT;     -- Base64 map image
ALTER TABLE worlds ADD COLUMN image_prompt TEXT;  -- Prompt used for generation
ALTER TABLE worlds ADD COLUMN climate VARCHAR(100);
ALTER TABLE worlds ADD COLUMN population_level VARCHAR(50);  -- sparse, moderate, dense
ALTER TABLE worlds ADD COLUMN danger_level VARCHAR(50);      -- safe, moderate, dangerous
```

**Add to `locations` table** (via migration):

```sql
ALTER TABLE locations ADD COLUMN location_image TEXT;  -- Base64 image
ALTER TABLE locations ADD COLUMN image_prompt TEXT;
ALTER TABLE locations ADD COLUMN parent_location_id INTEGER;  -- For sub-locations
ALTER TABLE locations ADD COLUMN coordinates VARCHAR(50);     -- For map positioning
ALTER TABLE locations ADD COLUMN notable_features TEXT;
ALTER TABLE locations ADD COLUMN inhabitants TEXT;
```

## Backend API Implementation

### 1. World Generation Endpoint

**File:** `backend/routers/generation.py`

```python
@router.post("/world/")
async def generate_world(
    name: str | None = None,
    world_type: str = "fantasy",  # fantasy, sci-fi, modern, post-apocalyptic
    size: str = "medium",  # small, medium, large, continent, planet
    climate: str | None = None,
    magic_level: str = "medium",  # none, low, medium, high
    tech_level: str = "medieval",
    cultural_inspiration: str | None = None,
    custom_details: str | None = None,
    provider: str = "groq",
    model: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Generate a complete world with AI
    """
    # Build prompt based on parameters
    prompt = build_world_generation_prompt(
        name=name,
        world_type=world_type,
        size=size,
        climate=climate,
        magic_level=magic_level,
        tech_level=tech_level,
        cultural_inspiration=cultural_inspiration,
        custom_details=custom_details
    )

    # Generate world data using LLM
    world_data = await generate_world_content(
        prompt=prompt,
        provider=provider,
        model=model
    )

    return {
        "name": world_data["name"],
        "description": world_data["description"],
        "history": world_data["history"],
        "geography": world_data["geography"],
        "culture": world_data["culture"],
        "magic_system": world_data["magic_system"],
        "technology_level": world_data["technology_level"],
        "structured_data": world_data.get("structured_data", {})
    }
```

### 2. World Landscape Generation

**File:** `backend/routers/generation.py`

```python
@router.post("/world/generate-landscape/")
async def generate_world_landscape(
    world_name: str,
    description: str,
    landscape_type: str = "overview",  # overview, region, map
    provider: str = "stable_diffusion",
    model: str | None = None,
    style_preset: str = "fantasy-art",
):
    """
    Generate a landscape image for a world
    """
    # Build image prompt
    prompt = build_landscape_prompt(
        world_name=world_name,
        description=description,
        landscape_type=landscape_type,
        style_preset=style_preset
    )

    # Generate image using Stable Diffusion
    image_data = await generate_landscape_image(
        prompt=prompt,
        provider=provider,
        model=model,
        aspect_ratio="16:9" if landscape_type == "overview" else "1:1"
    )

    return {
        "image_base64": image_data["image"],
        "prompt": image_data["prompt"]
    }
```

### 3. Location Generation

**File:** `backend/routers/generation.py`

```python
@router.post("/location/")
async def generate_location(
    world_id: int,
    location_type: str,  # city, town, village, dungeon, wilderness, etc.
    size: str = "medium",
    notable_features: list[str] | None = None,
    custom_details: str | None = None,
    provider: str = "groq",
    model: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Generate a location within a world
    """
    # Get world context
    world = db.query(World).filter(World.id == world_id).first()
    if not world:
        raise HTTPException(status_code=404, detail="World not found")

    # Generate location data
    location_data = await generate_location_content(
        world_context=world,
        location_type=location_type,
        size=size,
        notable_features=notable_features,
        custom_details=custom_details,
        provider=provider,
        model=model
    )

    return location_data
```

### 4. Location Image Generation

**File:** `backend/routers/generation.py`

```python
@router.post("/location/generate-image/")
async def generate_location_image(
    location_name: str,
    location_type: str,
    description: str,
    time_of_day: str = "day",  # dawn, day, dusk, night
    weather: str = "clear",  # clear, rain, storm, fog, snow
    provider: str = "stable_diffusion",
    style_preset: str = "realistic",
):
    """
    Generate an image for a location (city, dungeon, etc.)
    """
    prompt = build_location_image_prompt(
        name=location_name,
        type=location_type,
        description=description,
        time_of_day=time_of_day,
        weather=weather,
        style_preset=style_preset
    )

    image_data = await generate_location_image(
        prompt=prompt,
        provider=provider,
        aspect_ratio="16:9"
    )

    return {
        "image_base64": image_data["image"],
        "prompt": image_data["prompt"]
    }
```

## Frontend Implementation

### 1. Create World Page

**File:** `frontend/src/pages/CreateWorld.jsx`

```javascript
export default function CreateWorldPage() {
  // Step 1: World Type & Settings
  const [worldType, setWorldType] = useState("fantasy");
  const [worldSize, setWorldSize] = useState("medium");
  const [climate, setClimate] = useState("temperate");
  const [magicLevel, setMagicLevel] = useState("medium");
  const [techLevel, setTechLevel] = useState("medieval");
  const [culturalInspiration, setCulturalInspiration] = useState("");
  const [customDetails, setCustomDetails] = useState("");

  // Step 2: Generation Results
  const [generatedWorld, setGeneratedWorld] = useState(null);
  const [worldName, setWorldName] = useState("");

  // Step 3: Landscape Generation
  const [landscapeImage, setLandscapeImage] = useState(null);
  const [generatingLandscape, setGeneratingLandscape] = useState(false);

  // Step 4: Save
  const [saving, setSaving] = useState(false);

  // UI steps
  const [activeStep, setActiveStep] = useState(0);
  const steps = ["World Settings", "Generate", "Landscape", "Review & Save"];

  const handleGenerate = async () => {
    const response = await axios.post(
      `${API_URL}/api/generate/world/`,
      {
        name: worldName,
        world_type: worldType,
        size: worldSize,
        climate: climate,
        magic_level: magicLevel,
        tech_level: techLevel,
        cultural_inspiration: culturalInspiration,
        custom_details: customDetails,
        provider: "groq"
      }
    );
    setGeneratedWorld(response.data);
    setActiveStep(2);
  };

  const handleGenerateLandscape = async () => {
    setGeneratingLandscape(true);
    const response = await axios.post(
      `${API_URL}/api/generate/world/generate-landscape/`,
      {
        world_name: worldName,
        description: generatedWorld.description,
        landscape_type: "overview",
        provider: "stable_diffusion",
        style_preset: "fantasy-art"
      }
    );
    setLandscapeImage(response.data.image_base64);
    setGeneratingLandscape(false);
    setActiveStep(3);
  };

  const handleSave = async () => {
    setSaving(true);
    await axios.post(`${API_URL}/api/worlds/`, {
      name: worldName,
      description: generatedWorld.description,
      history: generatedWorld.history,
      geography: generatedWorld.geography,
      culture: generatedWorld.culture,
      magic_system: generatedWorld.magic_system,
      technology_level: generatedWorld.technology_level,
      world_image: landscapeImage,
      structured_data: JSON.stringify(generatedWorld.structured_data)
    });
    setSaving(false);
    navigate("/worlds");
  };

  return (
    <Container>
      <Stepper activeStep={activeStep}>
        {steps.map((label) => (
          <Step key={label}><StepLabel>{label}</StepLabel></Step>
        ))}
      </Stepper>

      {/* Step 1: Settings */}
      {activeStep === 0 && (
        <Box>
          <TextField label="World Name" value={worldName} onChange={...} />
          <FormControl><Select label="World Type">
            <MenuItem value="fantasy">Fantasy</MenuItem>
            <MenuItem value="sci-fi">Sci-Fi</MenuItem>
            <MenuItem value="modern">Modern</MenuItem>
            <MenuItem value="post-apocalyptic">Post-Apocalyptic</MenuItem>
          </Select></FormControl>
          {/* More settings... */}
        </Box>
      )}

      {/* Step 2: Generate */}
      {activeStep === 1 && (
        <Button onClick={handleGenerate}>Generate World</Button>
      )}

      {/* Step 3: Landscape */}
      {activeStep === 2 && (
        <Box>
          {generatedWorld && (
            <>
              <Typography variant="h4">{worldName}</Typography>
              <Typography>{generatedWorld.description}</Typography>
              <Button onClick={handleGenerateLandscape}>
                Generate Landscape
              </Button>
            </>
          )}
        </Box>
      )}

      {/* Step 4: Review & Save */}
      {activeStep === 3 && (
        <Box>
          {landscapeImage && (
            <img src={`data:image/png;base64,${landscapeImage}`} />
          )}
          <Button onClick={handleSave}>Save World</Button>
        </Box>
      )}
    </Container>
  );
}
```

### 2. World Detail Page with Location Management

**File:** `frontend/src/pages/WorldDetail.jsx`

```javascript
export default function WorldDetailPage() {
  const { worldId } = useParams();
  const [world, setWorld] = useState(null);
  const [locations, setLocations] = useState([]);
  const [creating Location, setCreatingLocation] = useState(false);

  useEffect(() => {
    loadWorld();
    loadLocations();
  }, [worldId]);

  const loadWorld = async () => {
    const response = await axios.get(`${API_URL}/api/worlds/${worldId}`);
    setWorld(response.data);
  };

  const loadLocations = async () => {
    const response = await axios.get(
      `${API_URL}/api/locations/?world_id=${worldId}`
    );
    setLocations(response.data);
  };

  return (
    <Box>
      {/* World Overview with Landscape */}
      <Box>
        {world?.world_image && (
          <img src={`data:image/png;base64,${world.world_image}`} />
        )}
        <Typography variant="h3">{world?.name}</Typography>
        <Typography>{world?.description}</Typography>
      </Box>

      {/* World Details Tabs */}
      <Tabs>
        <Tab label="History" />
        <Tab label="Geography" />
        <Tab label="Culture" />
        <Tab label="Magic System" />
        <Tab label="Locations" />
      </Tabs>

      {/* Locations Grid */}
      <Grid container spacing={2}>
        {locations.map((location) => (
          <Grid item xs={12} sm={6} md={4} key={location.id}>
            <Card>
              {location.location_image && (
                <CardMedia image={`data:image/png;base64,${location.location_image}`} />
              )}
              <CardContent>
                <Typography variant="h6">{location.name}</Typography>
                <Chip label={location.location_type} />
              </CardContent>
            </Card>
          </Grid>
        ))}

        {/* Add Location Button */}
        <Grid item xs={12}>
          <Button onClick={() => setCreatingLocation(true)}>
            <AddLocationIcon /> Add Location
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}
```

### 3. Create Location Dialog

**File:** `frontend/src/components/CreateLocationDialog.jsx`

```javascript
export default function CreateLocationDialog({ open, onClose, worldId }) {
  const [locationType, setLocationType] = useState("city");
  const [locationSize, setLocationSize] = useState("medium");
  const [generating, setGenerating] = useState(false);
  const [generatedLocation, setGeneratedLocation] = useState(null);

  const locationTypes = [
    "City", "Town", "Village", "Castle", "Dungeon",
    "Forest", "Mountain", "Desert", "Ocean", "Ruins"
  ];

  const handleGenerate = async () => {
    setGenerating(true);
    const response = await axios.post(
      `${API_URL}/api/generate/location/`,
      {
        world_id: worldId,
        location_type: locationType,
        size: locationSize,
        provider: "groq"
      }
    );
    setGeneratedLocation(response.data);
    setGenerating(false);
  };

  const handleGenerateImage = async () => {
    const response = await axios.post(
      `${API_URL}/api/generate/location/generate-image/`,
      {
        location_name: generatedLocation.name,
        location_type: locationType,
        description: generatedLocation.description,
        provider: "stable_diffusion"
      }
    );
    setGeneratedLocation({
      ...generatedLocation,
      location_image: response.data.image_base64
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Location</DialogTitle>
      <DialogContent>
        <Select value={locationType} onChange={...}>
          {locationTypes.map((type) => (
            <MenuItem value={type.toLowerCase()}>{type}</MenuItem>
          ))}
        </Select>

        {generatedLocation && (
          <Box>
            <Typography variant="h6">{generatedLocation.name}</Typography>
            <Typography>{generatedLocation.description}</Typography>
            <Button onClick={handleGenerateImage}>Generate Image</Button>
            {generatedLocation.location_image && (
              <img src={`data:image/png;base64,${generatedLocation.location_image}`} />
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleGenerate}>Generate</Button>
        <Button onClick={handleSave}>Save Location</Button>
      </DialogActions>
    </Dialog>
  );
}
```

## Prompt Engineering

### World Generation Prompt Template

```python
def build_world_generation_prompt(
    name, world_type, size, climate, magic_level, tech_level,
    cultural_inspiration, custom_details
):
    prompt = f"""Create a detailed {world_type} world with the following characteristics:

Name: {name or "Generate an evocative name"}
Size: {size} ({get_size_description(size)})
Climate: {climate}
Magic Level: {magic_level}
Technology Level: {tech_level}
Cultural Inspiration: {cultural_inspiration or "Original/Mixed"}

Additional Details: {custom_details}

Generate a comprehensive world description including:

1. **Name**: An evocative name for this world
2. **Description**: A compelling overview (2-3 paragraphs)
3. **History**: Major historical events and eras (3-5 key periods)
4. **Geography**: Terrain, continents, major landmarks
5. **Culture**: Dominant cultures, customs, traditions
6. **Magic System**: How magic works (if applicable)
7. **Technology Level**: Available technology and its integration
8. **Notable Locations**: 3-5 major cities/regions to explore later
9. **Conflicts**: Current tensions or ongoing struggles
10. **Unique Features**: What makes this world special

Format as structured JSON."""
    return prompt
```

### Landscape Image Prompt Template

```python
def build_landscape_prompt(world_name, description, landscape_type, style_preset):
    style_tags = {
        "fantasy-art": "epic fantasy art, dramatic lighting, vibrant colors",
        "realistic": "photorealistic, natural lighting, detailed terrain",
        "painterly": "oil painting style, artistic, impressionist",
        "dark-fantasy": "dark fantasy, moody atmosphere, gothic"
    }

    prompt = f"""A breathtaking {landscape_type} view of {world_name}.
{description}
{style_tags[style_preset]}
High quality, detailed, cinematic composition, 8K resolution.
"""
    negative_prompt = "blurry, low quality, distorted, text, watermark"
    return prompt, negative_prompt
```

## Implementation Phases

### Phase 1: Basic World Generation (Week 1)

- ✅ Database schema verified
- 🚧 Backend world generation endpoint
- 🚧 Frontend CreateWorld page (basic form)
- 🚧 World list and detail pages

### Phase 2: Landscape Generation (Week 2)

- 🚧 Stable Diffusion integration for landscapes
- 🚧 World landscape generation UI
- 🚧 Image storage and display

### Phase 3: Location System (Week 3)

- 🚧 Location generation endpoint
- 🚧 Location management UI
- 🚧 Location image generation
- 🚧 Hierarchical location structure

### Phase 4: Advanced Features (Week 4)

- 🚧 Interactive world maps
- 🚧 Location relationships
- 🚧 Integration with characters (hometown, current location)
- 🚧 Integration with stories (setting)

## Testing Checklist

- [ ] Generate fantasy world with default settings
- [ ] Generate sci-fi world with custom details
- [ ] Create landscape image for world
- [ ] Add multiple locations to world
- [ ] Generate images for each location type
- [ ] Edit world details
- [ ] Delete world (cascade to locations)
- [ ] Link character to world location
- [ ] Use world as story setting

## Related Files

- `backend/routers/worlds.py` - World CRUD endpoints
- `backend/routers/generation.py` - Generation endpoints
- `backend/models.py` - World and Location models
- `frontend/src/pages/Worlds.jsx` - World list
- `frontend/src/pages/WorldDetail.jsx` - World detail
- `frontend/src/pages/CreateWorld.jsx` - World creation

## Next Actions

1. ✅ Verify database schema
2. 🔜 Create world generation prompts
3. 🔜 Implement backend generation endpoints
4. 🔜 Build CreateWorld frontend
5. 🔜 Test full workflow
