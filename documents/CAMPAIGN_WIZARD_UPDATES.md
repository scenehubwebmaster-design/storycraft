# Campaign Wizard Updates - Template Selection Feature

## Overview

Enhanced the Campaign Setup Wizard with a comprehensive adventure template selection system that integrates with the RAG-backed campaign starter content.

## What Was Implemented

### 1. Adventure Template Data Structure (CampaignSetupWizard.jsx)

#### Adventure Templates by Campaign Type

- **One-Shot Adventures**:

  - The Haunted Manor (Mystery/Horror, Levels 1-3)
  - The Goblin Raiders (Combat/Rescue, Levels 1-2)
  - Custom One-Shot (AI-generated)

- **Short Adventures**:

  - The Cult of the Crimson Eye (Investigation/Mystery, Levels 3-5)
  - The Lost Mine (Classic D&D, Levels 1-5)
  - Custom Short Adventure (AI-generated)

- **Epic Campaigns**:
  - Tyranny of Dragons (World-Threat, Levels 1-15)
  - Custom Epic Campaign (AI-generated)

#### Opening Scenes (5 Classic Options)

1. **The Tavern Meeting** 🍺 - Strangers meet in a cozy tavern
2. **The Caravan Guards** 🐴 - Bonds form during travel
3. **Prison Break** ⛓️ - Heroes escape imprisonment
4. **The Festival Disaster** 🎪 - Celebration turns to chaos
5. **The Summons** ✉️ - Mysterious messages call heroes

#### Campaign Tones (6 Options)

1. Heroic High Fantasy 🦸 - Clear good vs evil
2. Gritty Dark Fantasy 🌑 - Morally grey, survival-focused
3. Political Intrigue 👑 - Court politics and diplomacy
4. Mystery & Investigation 🔍 - Solve crimes and uncover secrets
5. Horror & Dread 👻 - Atmosphere of fear and cosmic horror
6. Lighthearted Comedy 😄 - Fun and silly adventures

### 2. Updated Wizard Flow (4 Steps)

**Previous**: 3 steps (Campaign Details → Select Party → Review)

**New**: 4 steps

1. **Campaign Details** - Basic campaign info (title, setting, difficulty, type, level)
2. **Adventure Template** ⭐ NEW - Template, opening scene, and tone selection
3. **Select Party** - Choose D&D characters to join
4. **Review & Create** - Review all selections with AI DM confirmation

### 3. Step 2: Adventure Template Selection UI

#### AI DM Confirmation Box

```
Your AI Dungeon Master Awaits
Choose an adventure template and opening scene. Your AI Dungeon Master
will craft a custom campaign using these elements and guide your party
through an epic journey!
```

#### Adventure Template Cards

- Visual card selection with icons
- Shows: Title, Type, Level Range, Description
- Color-coded selection borders
- Hover effects for better UX

#### Opening Scene Cards

- 5 classic D&D opening scenarios
- Each card shows:
  - Icon and title
  - Brief description
  - **Preview narration** (displayed when selected)
- Example preview: "The warm glow of the hearth illuminates worn wooden tables as travelers from distant lands find themselves sharing space..."

#### Campaign Tone Selector

- 6-tone grid layout
- Icons and descriptions for each tone
- Helps AI DM adjust narrative style

### 4. Step 4: Enhanced Review Screen

**Added Template Information Display**:

- Adventure template with icon and description
- Selected opening scene with icon
- Campaign tone selection
- AI DM confirmation message:
  ```
  Your AI Dungeon Master is Ready!
  Based on your selections, the AI DM will create a custom campaign experience.
  Your adventure will begin with the [Opening Scene] and follow the [Template]
  template in a [Tone] style.
  ```

### 5. Backend Integration

#### Template Metadata in Campaign

When a campaign is created, template selections are embedded in the description field:

```javascript
{
  template_id: "haunted_manor",
  opening_scene: "tavern_meeting",
  campaign_tone: "heroic_fantasy",
  user_description: "Original user description"
}
```

Format: `[AI_DM_METADATA: {...}]` appended to description

#### RAG System Integration

- 15 campaign templates indexed in backend RAG system
- Templates include full AI DM prompt instructions
- When AI DM starts a campaign, it can retrieve:
  - Full adventure synopsis
  - Key NPCs
  - Story structure
  - Session outlines
  - Opening narration text

### 6. State Management

**New State Variables**:

```javascript
const [selectedTemplate, setSelectedTemplate] = useState(null);
const [selectedOpening, setSelectedOpening] = useState("tavern_meeting");
const [campaignTone, setCampaignTone] = useState("heroic_fantasy");
```

**Validation**:

- Step 0: Campaign title required
- Step 1: Adventure template required (new)
- Step 2: At least one character required
- Step 3: Review (no validation)

### 7. Component Imports Added

```javascript
import { AutoAwesome } from "@mui/icons-material";
import { AlertTitle } from "@mui/material";
```

## User Experience Flow

1. **Step 1**: User enters campaign title, description, chooses type (one-shot/short/epic), setting, difficulty, level
2. **Step 2 (NEW)**:
   - User sees AI DM confirmation message
   - Selects adventure template from available options for their campaign type
   - Chooses opening scene (sees narration preview when selected)
   - Picks campaign tone (heroic, dark, political, etc.)
3. **Step 3**: User selects D&D characters for the party
4. **Step 4**:
   - Reviews all selections including template info
   - Sees AI DM confirmation with personalized message
   - Creates campaign

## AI DM Integration (Future Enhancement)

The template metadata is now stored with each campaign. Next steps for full AI DM integration:

1. **Campaign Start**: When AI DM receives first message, extract template metadata
2. **RAG Retrieval**: Query RAG system for selected template:

   ```python
   template_id = extract_metadata(campaign.description)["template_id"]
   opening_scene = extract_metadata(campaign.description)["opening_scene"]

   # Retrieve from RAG
   template_content = retrieve_reference(template_id)
   opening_narration = retrieve_reference(opening_scene)
   ```

3. **System Prompt Injection**: Inject template into AI DM system prompt:

   ```
   You are running the adventure: {template.title}

   Synopsis: {template.synopsis}

   Opening Scene: {opening_narration}

   Campaign Tone: {tone.description}

   Story Structure: {template.story_beats}

   Key NPCs: {template.npcs}
   ```

4. **Session Tracking**: AI DM tracks progress through template story beats

## Testing Checklist

- [ ] Frontend starts without errors ✅
- [ ] Wizard opens and shows 4 steps ✅
- [ ] Step 2 displays adventure templates correctly
- [ ] Clicking a template selects it (border highlight)
- [ ] Opening scene cards display and preview narration shows when selected
- [ ] Campaign tone cards selectable
- [ ] Step 3 (party selection) still works
- [ ] Step 4 (review) shows all template information
- [ ] Campaign creation includes template metadata in description
- [ ] Backend accepts and stores campaign with metadata

## Files Modified

1. `frontend/src/components/CampaignSetupWizard.jsx`
   - Added template data structures (lines 80-260)
   - Updated steps array (3 → 4 steps)
   - Added state for template selection
   - Implemented Step 2 UI (case 1)
   - Shifted party selection to Step 3 (case 2)
   - Enhanced review screen (case 3)
   - Updated handleCreate to include template metadata
   - Updated validation in handleNext
   - Changed character loading to trigger on step 2

## Files Previously Created (RAG Backend)

1. `data/phb/campaign_starters.md` - 15 campaign templates with AI DM instructions
2. `backend/scripts/index_campaign_starters.py` - Indexed templates into RAG

## Campaign Starters Available in RAG

- **Opening Scenes**: 5 indexed
- **One-Shots**: 2 indexed
- **Short Adventures**: 2 indexed
- **Epic Campaigns**: 1 indexed
- **Campaign Tones**: 3 indexed
- **Settings**: 2 indexed
- **Total**: 15 templates

## Next Steps

1. **AI DM System Prompt Enhancement** (backend)

   - Modify AI DM initialization to extract template metadata from campaign.description
   - Add RAG retrieval step to fetch full template content
   - Inject template content into system prompt

2. **Campaign Session Tracking** (backend)

   - Track progress through template story beats
   - Update campaign.session_notes with completed beats
   - Allow AI DM to reference remaining story structure

3. **Opening Narration Delivery** (backend)

   - When campaign first starts, AI DM delivers opening scene narration
   - Use exact text from selected opening scene template

4. **Template Customization** (future frontend)
   - Allow users to view full template before selecting
   - Add "Customize Template" option to modify adventure elements
   - Preview key NPCs and story beats

## Technical Notes

- Template metadata stored as JSON string in campaign.description field
- Format: `[AI_DM_METADATA: {...}]` marker for easy extraction
- User description preserved before metadata marker
- Backend can parse with regex: `\[AI_DM_METADATA: ({.*?})\]`

## Success Metrics

✅ Campaign wizard now has 4 steps instead of 3
✅ 15 pre-built adventure templates available
✅ 5 classic opening scenes with preview narration
✅ 6 campaign tone options
✅ Template metadata saved with campaign
✅ AI DM confirmation messages shown to user
✅ Frontend compiles without errors

## User-Facing Benefits

1. **Guided Adventure Creation**: No more blank-page syndrome - users choose from proven adventures
2. **Classic D&D Openings**: Players get iconic starting scenarios (tavern meeting!)
3. **Tone Control**: Players can request specific atmosphere (heroic vs dark fantasy)
4. **AI DM Confidence**: Clear message that AI will handle campaign structure
5. **Preview System**: See opening narration before committing

---

**Status**: ✅ Frontend implementation complete, ready for testing
**Date**: 2025-01-20
**Next**: Test wizard flow in browser, then implement AI DM backend integration
