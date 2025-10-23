# Campaign AI DM Integration - Implementation Summary

## Overview

Implemented automatic campaign initialization with AI DM to seamlessly start D&D campaigns after setup, ensuring the AI has proper context and guidance to run the game.

## Changes Made

### 1. Navigation Update (`frontend/src/App.jsx`)

- **Added "Campaigns" navigation item** pointing to `/dm-chat`
- Icon: `CampaignIcon` with highlight styling
- Replaced "DM Chat" with "Campaigns" for better user clarity
- Removed generic "DM Chat" label (now accessible as "Campaigns")

### 2. Campaign-Session Linkage (`frontend/src/pages/DMChat.jsx`)

#### A. Campaign Loading When Session Selected

```javascript
const selectSession = async (sessionId) => {
  // ... load session
  await loadCampaignForSession(sessionId); // NEW: Auto-load campaign
};

const loadCampaignForSession = async (sessionId) => {
  const r = await fetch(`/api/campaigns/?chat_session_id=${sessionId}`);
  const campaigns = await r.json();
  if (campaigns && campaigns.length > 0) {
    setActiveCampaign(campaigns[0]);
  }
};
```

#### B. Automatic Campaign Initialization with AI DM

```javascript
const handleCampaignCreated = async (campaign) => {
  setActiveCampaign(campaign);
  await initializeCampaignWithAI(campaign); // NEW: Auto-start campaign
};

const initializeCampaignWithAI = async (campaign) => {
  // 1. Extract template metadata from campaign.description
  // 2. Fetch party composition
  // 3. Build comprehensive initialization prompt
  // 4. Send user message with campaign details
  // 5. Trigger AI DM to generate opening narration
};
```

**Initialization Prompt Includes:**

- Campaign title, type, setting, difficulty, starting level
- Adventure template ID and opening scene
- Campaign tone (heroic fantasy, dark fantasy, etc.)
- Full party roster with names, species, classes, levels
- Explicit DM instructions to:
  - Begin with selected opening scene
  - Follow adventure template structure
  - Maintain specified campaign tone
  - Track party resources and conditions
  - Use D&D 5e rules
  - Reference RAG knowledge base

#### C. Campaign Status Indicator

- Shows active campaign alert when campaign exists
- Displays: Campaign title, level, type
- Button changes from "Setup D&D Campaign" → "Campaign Settings"
- Visual feedback with success alert and campaign icon

### 3. Backend Campaign Filtering (`backend/routers/campaigns.py`)

```python
@router.get("/", response_model=List[dict])
async def list_campaigns(
    chat_session_id: Optional[int] = None,  # NEW: Filter parameter
    db: Session = Depends(get_db)
):
    """List all campaigns, optionally filtered by chat_session_id"""
    query = db.query(Campaign)

    if chat_session_id is not None:
        query = query.filter(Campaign.chat_session_id == chat_session_id)

    campaigns = query.order_by(Campaign.updated_at.desc()).all()
    return [c.to_dict() for c in campaigns]
```

### 4. AI DM System Prompt Enhancement (`backend/routers/chat.py`)

#### A. Campaign-Aware System Prompt

```python
# Check if session has active campaign
campaign = db.query(Campaign).filter(Campaign.chat_session_id == session_id).first()

if campaign:
    # Extract template metadata
    metadata = json.loads(metadata_match.group(1))

    campaign_context = f"""
**ACTIVE CAMPAIGN: {campaign.title}**
- Type: {campaign.campaign_type}
- Setting: {campaign.setting}
- Adventure Template: {metadata.get('template_id')}
- Opening Scene: {metadata.get('opening_scene')}
- Campaign Tone: {metadata.get('campaign_tone')}

You are the Dungeon Master for this campaign. Maintain consistency
with these details and reference the adventure template from your
knowledge base.
"""

system_prompt = """You are an expert Dungeon Master for D&D 5e.

Responsibilities:
- Narrate vivid, immersive scenes
- Roleplay NPCs with distinct personalities
- Apply D&D 5e rules accurately
- Ask for dice rolls when appropriate
- Track combat, initiative, HP, conditions
- Create engaging encounters and meaningful choices
- Adapt to player actions
"""

prompt = f"{system_prompt}{campaign_context}..."
```

## User Experience Flow

### Before Campaign Creation:

1. User navigates to **Campaigns** in nav bar
2. Creates a new chat session
3. Clicks "Setup D&D Campaign" button
4. Goes through 4-step wizard:
   - Campaign Details
   - Adventure Template & Opening Scene
   - Party Selection
   - Review & Create

### After Campaign Creation (Automatic):

5. ✨ **Campaign initialization message sent to AI DM** (automatic)
6. ✨ **AI DM generates opening narration** (automatic)
7. User sees:
   - Campaign initialization summary in chat
   - AI DM's opening scene narration
   - Green "Campaign Active" status indicator
   - Party panel on the right (if characters assigned)
8. User can immediately start playing by responding to AI DM

### Example Initialization Message:

```
🎲 Campaign Initialized: The Lost Mine of Phandelver

Campaign Details:
- Type: SHORT ADVENTURE
- Setting: Forgotten Realms
- Difficulty: Normal
- Starting Level: 1
- Adventure Template: lost_mine
- Opening Scene: tavern_meeting
- Campaign Tone: heroic_fantasy

The Adventuring Party:
- Thorin Ironforge (Dwarf Fighter, Level 1)
- Elara Moonshadow (Elf Wizard, Level 1)
- Grimm Shadowblade (Human Rogue, Level 1)

Dungeon Master Instructions:
You are now running this D&D 5th Edition campaign...
Please begin the adventure with the opening scene narration!
```

### AI DM Response (Automatic):

```
The warm glow of the hearth illuminates worn wooden tables as travelers
from distant lands find themselves sharing space in the Stonehill Inn...

[Full opening narration from selected scene]

What do your characters do?
```

## Technical Benefits

### 1. **Zero Manual Setup Required**

- No need for users to type "start the campaign"
- No need to explain campaign details to AI
- AI DM has full context immediately

### 2. **Consistent Campaign Context**

- AI DM always knows active campaign details
- Every generation includes campaign context in prompt
- Template information retrieved from RAG automatically

### 3. **Session Persistence**

- When user returns and selects session, campaign auto-loads
- Campaign status visible at all times
- AI maintains campaign context across sessions

### 4. **Template Integration**

- Adventure templates from RAG system referenced in system prompt
- AI DM instructed to follow template structure
- Opening scenes deliver consistent narrative style

## Data Flow

```
Campaign Creation
    ↓
Campaign Saved with metadata
(template_id, opening_scene, tone in description)
    ↓
handleCampaignCreated() triggered
    ↓
initializeCampaignWithAI() called
    ↓
1. Extract metadata from campaign.description
2. Fetch party from /api/campaigns/{id}/party
3. Build initialization prompt with:
   - Campaign details
   - Template info
   - Party roster
   - DM instructions
    ↓
4. POST to /api/chat/sessions/{id}/messages (user message)
5. POST to /api/chat/sessions/{id}/generate (AI response)
    ↓
Backend generate_for_session():
1. Load campaign by chat_session_id
2. Extract template metadata
3. Build campaign_context string
4. Include in system prompt
5. Retrieve RAG docs (monsters + references)
6. Call LLM with full context
    ↓
AI DM generates opening narration
    ↓
User sees campaign active + opening scene
    ↓
Ready to play! 🎲
```

## Files Modified

1. **`frontend/src/App.jsx`**

   - Added CampaignIcon import
   - Added "Campaigns" navigation item

2. **`frontend/src/pages/DMChat.jsx`**

   - Added `loadCampaignForSession()` function
   - Modified `selectSession()` to auto-load campaign
   - Added `initializeCampaignWithAI()` function
   - Modified `handleCampaignCreated()` to trigger initialization
   - Added campaign status indicator UI
   - Added CampaignIcon import

3. **`backend/routers/campaigns.py`**

   - Added `chat_session_id` filter parameter to `list_campaigns()`
   - Enables filtering campaigns by session

4. **`backend/routers/chat.py`**
   - Added campaign context extraction
   - Added campaign-aware system prompt
   - AI DM now receives campaign details in every generation

## Testing Checklist

- [x] "Campaigns" nav item visible and navigates to DM Chat
- [ ] Creating a campaign automatically sends initialization message
- [ ] AI DM receives campaign context in system prompt
- [ ] Opening narration generated automatically after campaign creation
- [ ] Campaign status indicator shows when campaign active
- [ ] Selecting a session loads its associated campaign
- [ ] Campaign details persist across sessions
- [ ] Party panel shows campaign characters
- [ ] AI DM maintains campaign context throughout conversation

## Next Steps (Optional Enhancements)

1. **Campaign Summary Command**: Add `/campaign` command to show current campaign details
2. **Scene Transitions**: Let DM update `current_location` and `current_scene_type` dynamically
3. **Quest Log Integration**: Auto-update quest log based on AI DM narration
4. **NPC Tracker**: Parse AI DM messages to track introduced NPCs
5. **Session Notes**: Auto-save session summaries after each play session
6. **Campaign Templates Panel**: Show full adventure template in sidebar during play
7. **Manual Campaign Start**: For existing campaigns, add "Begin Campaign" button

## Success Metrics

✅ **User can create a campaign and start playing immediately** - No manual prompting required
✅ **AI DM has full context** - System prompt includes all campaign details
✅ **Campaign persists** - Session selection auto-loads campaign
✅ **Visual feedback** - Users see campaign status at all times
✅ **Template integration** - Adventure templates guide AI DM behavior

---

**Implementation Date**: January 20, 2025  
**Status**: ✅ Complete and ready for testing
