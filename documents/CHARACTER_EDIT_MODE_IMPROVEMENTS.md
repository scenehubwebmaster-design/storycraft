# Character Edit Mode Improvements

**Date:** October 18, 2025  
**Status:** 🚧 IN PROGRESS

## Changes Completed

### ✅ 1. Fixed Portrait Loading in Edit Mode (D&D Characters)

**Problem:** D&D characters didn't load portraits when editing because `loadCharacterPortrait()` was only called for legacy characters.

**Solution:** Added portrait loading call for D&D characters:

```javascript
// In loadCharacterData() - around line 175
if (character.is_dnd) {
  console.log("Loading D&D character for editing:", character);
  setIsDnDMode(true);
  setDndCharacter(character);

  // Load portrait separately ✅ NEW
  loadCharacterPortrait(characterId);

  setActiveStep(2);
  setSuccess("D&D character data loaded for editing");
}
```

**Files Modified:**

- `frontend/src/pages/CreateCharacter.jsx` - Added `loadCharacterPortrait(characterId)` call in D&D character loading block

### ✅ 2. Changed Default Portrait Provider to Stable Diffusion

**Problem:** Default was OpenAI DALL-E which requires API credits.

**Solution:** Changed defaults to local Stable Diffusion:

```javascript
// Around line 104
const [imageProvider, setImageProvider] = useState("stable_diffusion"); // Changed from "openai"
const [imageModel, setImageModel] = useState("stable-diffusion-v1-6"); // Changed from "dall-e-3"
```

**Impact:**

- New users will default to free local image generation
- Can still switch to OpenAI/Google in settings
- Requires Stable Diffusion backend to be running

**Files Modified:**

- `frontend/src/pages/CreateCharacter.jsx` - Updated default state values

## Changes Needed

### 🚧 3. Enable Editing of Character Fields

**Current Issue:** When editing a character (`?edit=2`), fields are displayed but **not editable**. Users cannot:

- Modify character name
- Edit description, personality, background
- Update D&D stats (class, species, level, etc.)
- Change structured profile fields

**Why It's Not Editable:**

The review step (Step 3) displays character data using **read-only components**:

1. **StructuredCharacterDisplay** - Displays structured profiles (view-only)
2. **DnDStatBlock** - Shows D&D stats (view-only)
3. **Typography** components - Plain text display

**What Needs to Change:**

#### Option A: Add Edit Mode Toggle

```javascript
const [isEditingFields, setIsEditingFields] = useState(false);

// Add "Edit Fields" button in review step
<Button onClick={() => setIsEditingFields(!isEditingFields)}>
  {isEditingFields ? "View Mode" : "Edit Mode"}
</Button>

// Conditionally render edit vs view components
{isEditingFields ? (
  <TextField value={characterName} onChange={...} />
) : (
  <Typography>{characterName}</Typography>
)}
```

#### Option B: Always Allow Editing in Edit Mode

```javascript
// In activeStep === 2 section, check if isEditMode
{isEditMode ? (
  // Show editable TextFields
  <TextField label="Description" value={description} onChange={...} />
) : (
  // Show read-only display
  <StructuredCharacterDisplay data={generatedContent} />
)}
```

#### Recommended Approach: **Option B with State Management**

**Implementation Steps:**

1. **Add Editable State for All Fields:**

```javascript
// New state for editable fields (only in edit mode)
const [editableDescription, setEditableDescription] = useState("");
const [editablePersonality, setEditablePersonality] = useState("");
const [editableBackground, setEditableBackground] = useState("");
const [editableAppearance, setEditableAppearance] = useState("");
// ... etc for all fields
```

2. **Load Character Data into Editable State:**

```javascript
const loadCharacterData = async (characterId) => {
  const character = response.data;

  // Existing code...
  setCharacterName(character.name || "");

  // NEW: Load into editable state
  if (character.description) setEditableDescription(character.description);
  if (character.personality) setEditablePersonality(character.personality);
  if (character.background) setEditableBackground(character.background);
  // ... etc
};
```

3. **Create Editable Review Component:**

```javascript
// New component: EditableCharacterForm.jsx
function EditableCharacterForm({ character, onChange }) {
  return (
    <Box>
      <TextField
        fullWidth
        label="Description"
        multiline
        rows={4}
        value={character.description}
        onChange={(e) => onChange("description", e.target.value)}
      />
      <TextField
        fullWidth
        label="Personality"
        multiline
        rows={3}
        value={character.personality}
        onChange={(e) => onChange("personality", e.target.value)}
      />
      {/* ... more fields */}
    </Box>
  );
}
```

4. **Update Save Handler to Use Edited Data:**

```javascript
const handleSave = async (finalContent) => {
  // In edit mode, use editable state instead of generatedContent
  const dataToSave = isEditMode
    ? {
        name: characterName,
        description: editableDescription,
        personality: editablePersonality,
        background: editableBackground,
        // ... etc
      }
    : finalContent;

  // Send UPDATE request instead of CREATE
  if (isEditMode) {
    await axios.put(`${API_URL}/api/characters/${editId}`, dataToSave);
  } else {
    await axios.post(`${API_URL}/api/characters/`, dataToSave);
  }
};
```

**Files to Modify:**

- `frontend/src/pages/CreateCharacter.jsx` - Add editable state, conditional rendering
- `frontend/src/components/EditableCharacterForm.jsx` - NEW: Create editable form component
- `backend/routers/characters.py` - Ensure PUT endpoint exists and handles updates

**UI Mockup:**

```
┌─────────────────────────────────────────┐
│ Edit Character: Eiravyn Thorne          │
├─────────────────────────────────────────┤
│ [Character Name]                        │
│ ┌─────────────────────────────────┐     │
│ │ Eiravyn Thorne              [✓] │     │
│ └─────────────────────────────────┘     │
│                                         │
│ [Description]                           │
│ ┌─────────────────────────────────┐     │
│ │ Eiravyn wears a well-worn...    │     │
│ │ (editable multiline text)       │     │
│ └─────────────────────────────────┘     │
│                                         │
│ [Personality Traits]                    │
│ ┌─────────────────────────────────┐     │
│ │ • Strong sense of duty          │     │
│ │ • Witty sense of humor      [×] │     │
│ │ [+ Add trait]                   │     │
│ └─────────────────────────────────┘     │
│                                         │
│ [Background]                            │
│ ┌─────────────────────────────────┐     │
│ │ Born and raised in a small...   │     │
│ │ (editable multiline text)       │     │
│ └─────────────────────────────────┘     │
│                                         │
│ [D&D Stats] (for D&D characters)        │
│ ┌─────────────────────────────────┐     │
│ │ Class: [Wizard          ▾]      │     │
│ │ Species: [Tiefling       ▾]      │     │
│ │ Level: [1] Alignment: [CN▾]    │     │
│ └─────────────────────────────────┘     │
│                                         │
│          [Cancel]  [Save Changes]       │
└─────────────────────────────────────────┘
```

**Testing Plan:**

1. Go to http://localhost:3000/characters
2. Click "Edit" on any character
3. Should navigate to `/create/character?edit=2`
4. Should see editable form with pre-filled data
5. Modify any field
6. Click "Save Changes"
7. Should update character in database
8. Navigate back to character detail - changes should persist

## Additional Improvements

### 4. Better Edit Mode UI Indicators

Add visual indicators that user is in edit mode:

```javascript
{
  isEditMode && (
    <Alert severity="info" sx={{ mb: 2 }}>
      <strong>Edit Mode:</strong> Modify any fields below and click "Save
      Changes"
    </Alert>
  );
}
```

### 5. Dirty State Tracking

Track unsaved changes and warn before navigating away:

```javascript
const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

// Warn before leaving
useEffect(() => {
  const handleBeforeUnload = (e) => {
    if (hasUnsavedChanges) {
      e.preventDefault();
      e.returnValue = "";
    }
  };
  window.addEventListener("beforeunload", handleBeforeUnload);
  return () => window.removeEventListener("beforeunload", handleBeforeUnload);
}, [hasUnsavedChanges]);
```

### 6. Field Validation

Add validation for required fields:

```javascript
const [validationErrors, setValidationErrors] = useState({});

const validateFields = () => {
  const errors = {};
  if (!characterName.trim()) errors.name = "Name is required";
  if (!editableDescription.trim())
    errors.description = "Description is required";
  return errors;
};
```

## Backend API Verification

**Required Endpoints:**

- ✅ `GET /api/characters/{id}?exclude_portrait=true` - Load character
- ✅ `GET /api/characters/{id}/portrait/` - Load portrait separately
- ❓ `PUT /api/characters/{id}` - Update character (needs verification)
- ✅ `POST /api/characters/` - Create new character

**Check if PUT endpoint exists:**

```bash
# In backend/routers/characters.py
grep -n "put\|PUT" backend/routers/characters.py
```

If missing, need to add:

```python
@router.put("/{character_id}/", response_model=CharacterRead)
def update_character(
    character_id: int,
    character: CharacterUpdate,
    db: Session = Depends(get_db)
):
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Update fields
    for key, value in character.dict(exclude_unset=True).items():
        setattr(db_character, key, value)

    db_character.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_character)
    return db_character
```

## Next Steps

1. **Verify PUT endpoint exists** in backend
2. **Create EditableCharacterForm component**
3. **Add editable state management** to CreateCharacter.jsx
4. **Implement conditional rendering** for edit vs create mode
5. **Update save handler** to use PUT for updates
6. **Add unsaved changes warning**
7. **Test full edit flow**

## Related Files

- `frontend/src/pages/CreateCharacter.jsx` - Main component (2338 lines)
- `backend/routers/characters.py` - Character CRUD endpoints
- `frontend/src/components/StructuredCharacterDisplay.jsx` - Read-only display
- `frontend/src/components/DnDStatBlock.jsx` - D&D stats display
