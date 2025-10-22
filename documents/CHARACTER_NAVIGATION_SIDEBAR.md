# Character Details Navigation Sidebar

## Feature

Added a slim navigation sidebar for structured character details that provides quick jump links to each section, making it easier to browse long character profiles.

## Layout Changes

### Grid Structure

- **Portrait**: 3 columns (was 4) - Character portrait and image prompt
- **Navigation**: 2 columns (new) - Sticky section navigation sidebar
- **Details**: 7 columns (was 8) - Scrollable character details content

### Responsive Behavior

- **Desktop (md+)**: Shows all three columns with navigation
- **Mobile/Tablet**: Hides navigation sidebar, shows only portrait and details

## Navigation Features

### 1. Sticky Positioning

- Navigation stays visible as you scroll
- Positioned at `top: 16px`
- Maximum height matches details section: `calc(100vh - 250px)`

### 2. Section Links

The sidebar includes links to all 9 structured character sections:

1. Physical Appearance
2. Personality
3. Background
4. Motivations & Values
5. Fears & Weaknesses
6. Strengths & Abilities
7. Key Relationships
8. Character Arc Potential
9. Unique Qualities

### 3. Smooth Scrolling

- Click any section link to smoothly scroll to that section
- Uses `scrollIntoView({ behavior: "smooth", block: "start" })`
- `scrollMarginTop: "20px"` ensures proper spacing when scrolling

### 4. Visual Design

- Compact buttons with left-aligned text
- Small font size (0.8rem) to save space
- Subtle hover effects (background color and primary color text)
- "SECTIONS" label in uppercase for clarity

## Implementation Details

### Character Detail Page (`$characterId.jsx`)

```javascript
{
  /* Navigation Sidebar - Only for structured characters */
}
{
  character.structured_data && (
    <Grid
      size={{ xs: 12, md: 2 }}
      sx={{ display: { xs: "none", md: "block" } }}
    >
      <Card
        sx={{ position: "sticky", top: 16, maxHeight: "calc(100vh - 250px)" }}
      >
        <CardContent sx={{ py: 2, px: 1.5 }}>
          {/* Section buttons with smooth scroll */}
          <Button
            onClick={() => {
              const element = document.getElementById("physical");
              if (element) {
                element.scrollIntoView({ behavior: "smooth", block: "start" });
              }
            }}
          >
            Physical
          </Button>
          {/* ... more buttons ... */}
        </CardContent>
      </Card>
    </Grid>
  );
}
```

### Structured Character Display Component

Added `id` attributes and `scrollMarginTop` to each Card:

```javascript
<Card id="physical" sx={{ mb: 3, scrollMarginTop: "20px" }}>
  {/* Physical Appearance section */}
</Card>

<Card id="personality" sx={{ mb: 3, scrollMarginTop: "20px" }}>
  {/* Personality section */}
</Card>
// ... etc for all 9 sections
```

## User Experience

### Before

- Users had to manually scroll through long character profiles
- No quick way to jump to specific sections
- Hard to remember where sections were located

### After

- ✅ One-click navigation to any section
- ✅ Always visible navigation reference
- ✅ Smooth, animated scrolling transitions
- ✅ Clear visual indication of section structure
- ✅ Compact design doesn't take up much space

## Use Cases

1. **Quick Reference**: Jump directly to relationships or background without scrolling
2. **Comparison**: Quickly switch between sections to compare information
3. **Review**: Systematically go through each section in order
4. **Search**: Find specific information types faster

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Header: Character Name, Buttons                             │
├───────────┬──────────┬────────────────────────────────────┤
│           │          │                                      │
│ Portrait  │ Nav      │ Details (scrollable)                │
│           │ ───      │ ┌──────────────────────────────┐   │
│ ┌──────┐ │ Phys     │ │ Physical Appearance          │   │
│ │      │ │ Pers     │ │ • Height, Build, Hair, Eyes  │   │
│ │ IMG  │ │ Back     │ │ • Distinctive Features       │   │
│ │      │ │ Motiv    │ │ • Overall Description        │   │
│ └──────┘ │ Fears    │ └──────────────────────────────┘   │
│          │ Stren    │ ┌──────────────────────────────┐   │
│  Prompt  │ Rel      │ │ Personality                  │   │
│          │ Arc      │ │ • Core Traits                │   │
│          │ Unique   │ │ • Demeanor                   │   │
│          │          │ │ • Personality Overview       │   │
│          │          │ └──────────────────────────────┘   │
│          │          │ ┌──────────────────────────────┐   │
│          │          │ │ ...more sections...          │   │
│          │          │ └──────────────────────────────┘   │
└───────────┴──────────┴────────────────────────────────────┘
   3 cols     2 cols              7 cols
```

## Conditional Display

The navigation sidebar **only appears** for structured characters:

- Characters created with structured generation (has `structured_data`)
- Legacy characters (only description text) don't show navigation
- This prevents showing empty navigation for simple character profiles

## Browser Compatibility

- **All Modern Browsers**: Smooth scroll and sticky positioning work universally
- **Fallback**: If JavaScript is disabled, sections still work with manual scrolling

## Files Modified

1. **`frontend/src/routes/characters/$characterId.jsx`**
   - Adjusted grid layout (4-8 → 3-2-7 columns)
   - Added navigation sidebar component
   - Added conditional rendering based on `structured_data`
   - Implemented smooth scroll functionality

2. **`frontend/src/components/StructuredCharacterDisplay.jsx`**
   - Added `id` attributes to all 9 section Cards
   - Added `scrollMarginTop: "20px"` for proper scroll positioning
   - Sections: physical, personality, background, motivations, fears, strengths, relationships, arc, unique

## Future Enhancements

Consider adding:

- **Active section highlighting**: Change button style based on current scroll position
- **Collapse/expand navigation**: Minimize sidebar to save more space
- **Section progress indicator**: Show visual progress through the profile
- **Search within sections**: Filter sections based on keywords
- **Keyboard shortcuts**: Number keys to jump to sections
- **Section completion indicators**: Show which sections have content
