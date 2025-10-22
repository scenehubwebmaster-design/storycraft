# D&D Character Display Implementation

## Overview

Updated the character display system to properly show D&D 5th Edition characters using the DnDCharacterSheet component, with visual indicators throughout the UI.

## Changes Made

### 1. CharacterDetail Page (`frontend/src/pages/CharacterDetail.jsx`)

#### Added D&D Character Sheet Import

```javascript
import DnDCharacterSheet from "../components/DnDCharacterSheet";
```

#### Updated Display Logic

The page now checks for D&D characters **first**, before checking for structured characters:

```javascript
{
  character.is_dnd ? (
    // Display D&D character sheet
    <DnDCharacterSheet character={character} />
  ) : character.structured_data ? (
    // Display structured character profile
    <StructuredCharacterDisplay characterProfile={character.structured_data} />
  ) : (
    // Display legacy character format
    <Card>...</Card>
  );
}
```

**Display Priority:**

1. **D&D Characters** (`is_dnd = true`) → DnDCharacterSheet
2. **Structured Characters** (`structured_data` exists) → StructuredCharacterDisplay
3. **Legacy Characters** → Basic card layout

#### Added Visual Indicators in Header

**D&D Character Header:**

```javascript
<Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
  <Typography variant="h3">{character.name}</Typography>
  <Chip label="D&D 5E Character" color="error" />
</Box>
<Box>
  <Chip label={`Level ${character.dnd_level}`} size="small" />
  <Chip label={character.dnd_class} size="small" />
  <Chip label={character.dnd_species} size="small" />
</Box>
```

**Features:**

- Red "D&D 5E Character" badge
- Level, Class, and Species chips below name
- Distinct from structured character badges (purple)

#### Updated Navigation Sidebar

- Sidebar now hidden for D&D characters (DnDCharacterSheet has its own navigation)
- Only shows for structured non-D&D characters

#### Updated Grid Layout

```javascript
<Grid size={{ xs: 12, md: character.is_dnd ? 9 : (character.structured_data ? 7 : 9) }}>
```

- D&D characters: 9 columns (no sidebar)
- Structured characters: 7 columns (with sidebar)
- Legacy characters: 9 columns (no sidebar)

#### Added Info Banner

When viewing a D&D character, a red info banner appears:

```javascript
<Box sx={{ bgcolor: "error.main", color: "white" }}>
  <Chip label="D&D 5E Character" />
  <Typography>
    This is a D&D 5th Edition character with full stats and abilities
  </Typography>
</Box>
```

### 2. Characters List Page (`frontend/src/pages/Characters.jsx`)

#### Added D&D Chip to Card Title

```javascript
<Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
  <Typography variant="h6">{character.name}</Typography>
  {character.is_dnd && <Chip label="D&D" size="small" color="error" />}
</Box>
```

#### Updated Card Description for D&D Characters

D&D characters now show their class, level, and species instead of the generic description:

```javascript
if (character.is_dnd) {
  const parts = [];
  if (character.dnd_level) parts.push(`Level ${character.dnd_level}`);
  if (character.dnd_class) parts.push(character.dnd_class);
  if (character.dnd_species) parts.push(character.dnd_species);
  return parts.join(" • ") || "D&D Character";
}
```

**Example Output:**

- "Level 5 • Wizard • Elf"
- "Level 3 • Fighter • Human"

#### Added Multiple Character Type Chips

At the bottom of each card:

```javascript
<Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
  {character.is_dnd && (
    <Chip label="D&D 5E" size="small" color="error" variant="filled" />
  )}
  {character.structured_data && !character.is_dnd && (
    <Chip label="Structured" size="small" color="primary" variant="outlined" />
  )}
  <Chip
    label={formatDate(character.created_at)}
    size="small"
    variant="outlined"
  />
</Box>
```

**Chip Types:**

- **D&D 5E** - Red filled chip (for D&D characters)
- **Structured** - Purple outlined chip (for structured non-D&D characters)
- **Date** - Gray outlined chip (for all characters)

## Visual Design

### Color Scheme

**D&D Characters:**

- Badge Color: `error.main` (#f44336 - Red)
- Reasoning: Distinct from purple theme, represents action/adventure

**Structured Characters:**

- Badge Color: `primary.main` (#9c27b0 - Purple)
- Reasoning: Matches app's primary brand color

**Legacy Characters:**

- No special badge
- Standard card appearance

### Layout

#### Character List Cards

```
┌─────────────────────────────────┐
│     [Portrait Image]            │
├─────────────────────────────────┤
│ Name [D&D Badge]                │
│ Level 5 • Wizard • Elf          │
│                                 │
│ [D&D 5E] [Created: Date]       │
│ [View] [Edit] [Delete]         │
└─────────────────────────────────┘
```

#### Character Detail Header

```
Character Name [D&D 5E Character]
[Level 5] [Wizard] [Elf]

Created: January 15, 2025
Updated: January 16, 2025
```

## Database Fields Used

The following fields from the Character model are used to identify and display D&D characters:

```python
# Core D&D identifier
is_dnd = Column(Boolean, default=False)

# Basic info (displayed in cards and header)
dnd_class = Column(String(100))       # "Wizard", "Fighter", etc.
dnd_level = Column(Integer)           # 1-20
dnd_species = Column(String(100))     # "Elf", "Dwarf", etc.

# Additional D&D data (used by DnDCharacterSheet)
dnd_background = Column(String(100))
dnd_alignment = Column(String(50))
dnd_ability_scores = Column(JSON)
dnd_hit_points = Column(Integer)
dnd_armor_class = Column(Integer)
# ... (all other D&D fields)
```

## Component Flow

### Character List → Detail View

1. **User browses Characters page**

   - Sees D&D chip on card
   - Sees "Level X • Class • Species" description

2. **User clicks "View Details"**

   - Navigates to `/characters/:id`
   - CharacterDetail checks `character.is_dnd`

3. **If D&D character:**

   - Shows D&D badge in header
   - Shows level/class/species chips
   - Displays DnDCharacterSheet component
   - No sidebar navigation (sheet has its own)

4. **If Structured character:**

   - Shows Structured badge
   - Displays StructuredCharacterDisplay
   - Shows sidebar navigation

5. **If Legacy character:**
   - No special badge
   - Shows basic card layout

## Testing Checklist

- [x] D&D characters display DnDCharacterSheet component
- [x] D&D characters show red "D&D" badge on list cards
- [x] D&D characters show class/level/species in card description
- [x] D&D characters show "D&D 5E" chip at bottom of card
- [x] D&D character detail shows header badges (D&D 5E, Level, Class, Species)
- [x] D&D character detail shows red info banner
- [x] D&D character detail hides sidebar navigation
- [x] Structured non-D&D characters still work correctly
- [x] Legacy characters still work correctly
- [x] No console errors
- [x] Responsive on mobile devices

## Edge Cases Handled

### Character with both `is_dnd` and `structured_data`

- **Behavior:** Shows as D&D character (DnDCharacterSheet)
- **Reasoning:** D&D check comes first, D&D format is more specific

### Character with `is_dnd` but missing D&D fields

- **Card description:** Shows "D&D Character" (fallback)
- **Detail view:** DnDCharacterSheet handles missing data gracefully
- **Chips:** Only shows chips for fields that exist

### Character with neither flag

- **Behavior:** Falls back to legacy display
- **No errors thrown**

## Related Components

### DnDCharacterSheet (`frontend/src/components/DnDCharacterSheet.jsx`)

- **Purpose:** Display complete D&D 5E character sheet
- **Features:**
  - Full stat block (ability scores, AC, HP, etc.)
  - Skills and proficiencies
  - Equipment and inventory
  - Spellcasting (if applicable)
  - Narrative backstory
  - Export options (JSON, text, print)
- **Used by:** CharacterDetail for D&D characters

### StructuredCharacterDisplay (`frontend/src/components/StructuredCharacterDisplay.jsx`)

- **Purpose:** Display narrative character profiles
- **Features:**
  - Organized sections (Physical, Personality, Background, etc.)
  - Color-coded cards with left borders
  - Sidebar navigation
- **Used by:** CharacterDetail for structured non-D&D characters

## Future Enhancements

### Potential Improvements

1. **Quick Stats on Card**

   - Show AC, HP, Initiative on character card hover
   - Small stat badges below portrait

2. **D&D Edition Selector**

   - Support for different D&D editions (3.5, 4E, 5E)
   - Edition badge on cards

3. **Character Class Icon**

   - Visual icon for each class (sword for Fighter, book for Wizard)
   - Replace or supplement text chip

4. **Level Progress Bar**

   - Visual indicator of level progression
   - Show XP if applicable

5. **Party View**

   - Group D&D characters into parties
   - Show party composition

6. **Character Comparison**
   - Compare multiple D&D characters side-by-side
   - Useful for party balance

## Migration Notes

### Existing Characters

- All existing characters have `is_dnd = False` by default
- No data migration needed
- D&D characters are only created through new D&D creation flow

### Backward Compatibility

- Legacy character display unchanged
- Structured character display unchanged
- Only adds D&D display option, doesn't remove anything

## Commit Message

```
feat: Add D&D character display with visual indicators

- Add DnDCharacterSheet component to CharacterDetail page
- Check is_dnd flag before structured_data flag
- Add red "D&D" badge to character cards in list
- Show level/class/species in card description for D&D characters
- Add D&D 5E chip to card bottom indicators
- Add D&D header badges in detail view (Level, Class, Species)
- Add red info banner for D&D character details
- Hide sidebar navigation for D&D characters (use sheet's own nav)
- Update grid layout to accommodate D&D sheet width
- Add character type chips: D&D 5E (red), Structured (purple)
- Maintain backward compatibility with legacy characters
```

## Summary

Successfully implemented D&D character detection and display:

✅ **Character List:**

- D&D badge next to name
- Level/Class/Species description
- D&D 5E chip indicator

✅ **Character Detail:**

- DnDCharacterSheet component for D&D characters
- Header badges and info banner
- Proper grid layout (no sidebar for D&D)
- Priority: D&D > Structured > Legacy

✅ **Visual Consistency:**

- Red theme for D&D (action/adventure)
- Purple theme for Structured (brand color)
- Clear distinction between character types

✅ **User Experience:**

- Immediate visual feedback on character type
- Appropriate display component for each type
- No confusion between D&D and narrative characters

The system now correctly identifies and displays D&D characters with their full stat blocks, while maintaining support for structured and legacy character formats.
