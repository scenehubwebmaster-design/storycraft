# D&D Campaign System - Complete Design Document

**Date:** October 22, 2025  
**Status:** Phase 2 Implementation  
**Goal:** Create a full-featured AI-powered D&D campaign experience

---

## Vision

Transform DMChat into a complete tabletop D&D experience with:

- Campaign creation and management
- Character selection and ability tracking
- Context-aware action chips (spells, abilities, items)
- Dynamic scene types (roleplay, combat, exploration)
- RAG-powered lore and rules integration
- Solo or multiplayer support

---

## Core Components

### 1. Campaign Management

**New Features:**

- **Campaign Creation Wizard**

  - Select campaign type (one-shot, short adventure, epic campaign)
  - Choose setting (Forgotten Realms, Eberron, Homebrew)
  - Set difficulty (Easy, Normal, Hard, Deadly)
  - Generate initial hook and setting description

- **Campaign State Tracking**
  - Current scene type (roleplay, combat, exploration, rest)
  - Active quest log
  - NPC tracker with relationships
  - Location/map tracking
  - Session notes and highlights

**Database Schema:**

```sql
campaigns
  id, title, description, setting, difficulty
  dm_session_id (FK to dm_sessions)
  current_scene_type, current_location
  quest_log (JSON), npc_tracker (JSON)
  created_at, updated_at

campaign_characters
  id, campaign_id (FK), character_id (FK)
  current_hp, current_resources (JSON)
  status (active, unconscious, dead)
```

---

### 2. Character Selection & Party Management

**Character Panel (Left Sidebar)**

- Display all available D&D characters
- Multi-select for party composition
- Show current HP, resources, conditions
- Quick stat reference (AC, saves, skills)

**Features:**

- Add characters to active campaign
- Real-time HP/resource tracking
- Death save tracker
- Condition indicators (poisoned, stunned, etc.)

---

### 3. Dynamic Action Chips System

**Context-Aware Chips:**

The AI DM analyzes the current scene and player character abilities to generate relevant action chips:

#### Combat Scene Chips

```javascript
// Wizard example
<Chip>🔥 Cast Fireball (3rd level)</Chip>
<Chip>⚡ Cast Lightning Bolt (3rd level)</Chip>
<Chip>🛡️ Cast Shield (Reaction)</Chip>
<Chip>⚔️ Attack with Quarterstaff (+3)</Chip>
<Chip>🎲 Roll Initiative</Chip>
```

#### Roleplay Scene Chips

```javascript
<Chip>💬 Persuade (CHA +5)</Chip>
<Chip>🤥 Deception (CHA +5)</Chip>
<Chip>🔍 Insight (WIS +2)</Chip>
<Chip>📖 Investigate (INT +3)</Chip>
```

#### Exploration Scene Chips

```javascript
<Chip>🔍 Perception (WIS +2)</Chip>
<Chip>🧭 Survival (WIS +2)</Chip>
<Chip>🔓 Thieves' Tools (DEX +5)</Chip>
<Chip>🧗 Athletics (STR +3)</Chip>
```

**Chip Data Structure:**

```javascript
{
  type: 'spell' | 'ability' | 'skill' | 'item' | 'action',
  name: 'Fireball',
  icon: '🔥',
  description: 'Each creature in a 20-foot-radius sphere...',
  cost: { type: 'spell_slot', level: 3 },
  prompt: 'I cast Fireball at [target], dealing [damage] fire damage...',
  metadata: {
    damage: '8d6',
    save: 'DEX',
    dc: 15,
    range: 150,
    aoe: '20-ft radius'
  }
}
```

---

### 4. Scene Type System

**Scene Types:**

- **Roleplay** - NPC interactions, story moments, decisions
- **Combat** - Initiative, turns, attacks, damage
- **Exploration** - Investigation, travel, puzzles
- **Rest** - Short/long rest, resource recovery
- **Shop** - Buy/sell equipment, services

**AI Context Injection:**

```python
# Backend: Add scene context to AI prompt
scene_context = {
    "type": "combat",
    "initiative_order": [...],
    "active_combatants": [...],
    "round": 3,
    "available_actions": ["attack", "cast_spell", "dodge", "help", "dash"]
}
```

**UI Indicators:**

```javascript
// Visual scene indicators
const SceneIndicator = ({ type }) => {
  const configs = {
    roleplay: { icon: "💬", color: "#667eea", label: "Roleplay" },
    combat: { icon: "⚔️", color: "#f03e3e", label: "Combat" },
    exploration: { icon: "🗺️", color: "#37b24d", label: "Exploration" },
    rest: { icon: "🔥", color: "#fd7e14", label: "Rest" },
    shop: { icon: "💰", color: "#f59f00", label: "Shop" },
  };
  // Render badge with icon and color
};
```

---

### 5. Campaign Prompt Templates

**Campaign Generation Prompts:**

```javascript
const CAMPAIGN_TEMPLATES = {
  one_shot: {
    name: "One-Shot Adventure",
    duration: "2-4 hours",
    prompt: `
      Create an exciting one-shot D&D adventure for level [LEVEL] characters.
      
      Setting: [SETTING]
      Theme: [THEME]
      
      Include:
      - Engaging hook that immediately draws players in
      - 2-3 encounters (mix of combat, roleplay, exploration)
      - Clear objective and satisfying conclusion
      - 1-2 memorable NPCs
      - Treasure appropriate for level
      
      Begin by describing the opening scene vividly...
    `,
  },

  short_adventure: {
    name: "Short Adventure (3-5 sessions)",
    duration: "3-5 sessions",
    prompt: `
      Create a short D&D adventure arc for level [LEVEL] characters.
      
      Setting: [SETTING]
      Main Villain: [VILLAIN_TYPE]
      
      Structure:
      - Session 1: Introduction, first clues
      - Session 2-3: Investigation and challenges
      - Session 4-5: Confrontation and resolution
      
      Include:
      - Overarching plot with twists
      - 4-6 memorable NPCs with motivations
      - Mix of combat, roleplay, and exploration
      - Side quests and character development opportunities
      - Satisfying conclusion with consequences
      
      Begin with the initial hook...
    `,
  },

  epic_campaign: {
    name: "Epic Campaign (10+ sessions)",
    duration: "10+ sessions",
    prompt: `
      Create an epic D&D campaign for characters starting at level [LEVEL].
      
      Setting: [SETTING]
      Theme: [THEME]
      
      Campaign Structure:
      - Act 1 (Levels 1-5): Introduction and rising action
      - Act 2 (Levels 6-10): Complications and revelations  
      - Act 3 (Levels 11+): Climax and resolution
      
      Include:
      - Complex plot with multiple storylines
      - 10+ NPCs with deep backgrounds
      - Recurring villains and allies
      - Political intrigue and moral choices
      - World-changing consequences
      - Character-specific story arcs
      
      Begin by describing the world state and initial hook...
    `,
  },
};
```

---

### 6. RAG Integration for Lore & Rules

**Enhanced RAG Queries:**

```python
# Query types
RAG_QUERY_TYPES = {
    'spell_details': 'Retrieve spell description, components, damage',
    'monster_stats': 'Retrieve monster stat block from SRD',
    'rule_clarification': 'Retrieve rule from PHB/DMG',
    'lore': 'Retrieve setting lore from campaign books',
    'item_info': 'Retrieve magic item details'
}

# Example: Player casts Fireball
def get_spell_context(spell_name: str, level: int):
    """Retrieve spell details from RAG for AI context."""
    return {
        'spell': spell_name,
        'level': level,
        'description': '...from PHB...',
        'damage': '8d6 fire',
        'save': 'DEX',
        'effects': '...'
    }
```

---

### 7. Combat System Integration

**Combat Flow:**

1. DM initiates combat → System switches to combat mode
2. Roll initiative for all combatants (players + monsters)
3. Display initiative tracker UI
4. On each turn:
   - Show available actions as chips
   - Player clicks action → System structures the command
   - AI DM narrates result with dice rolls
   - Update HP/conditions automatically

**Combat UI Components:**

```javascript
<InitiativeTracker
  combatants={[...]}
  currentTurn={activeCharacter}
/>

<CombatActionPanel
  character={activeCharacter}
  availableActions={[
    { type: 'attack', weapon: 'Longsword', bonus: 5 },
    { type: 'spell', name: 'Cure Wounds', level: 1 },
    { type: 'ability', name: 'Second Wind' }
  ]}
/>

<CombatLog messages={combatHistory} />
```

---

### 8. Resource & HP Tracking

**Real-Time Tracking:**

- HP changes during combat
- Spell slot consumption
- Class resource usage (Rage, Ki, Channel Divinity)
- Condition application/removal
- Death saves

**Auto-Update Triggers:**

```javascript
// When AI DM says "take 15 damage"
extractDamage(dmResponse) → updateCharacterHP(charId, -15)

// When player uses spell
useSpellSlot(charId, level) → updateResources(charId, 'spell_slots', level, -1)

// When long rest
longRest(charId) → restoreHP() + restoreSpellSlots() + restoreAbilities()
```

---

## Implementation Phases

### Phase 2A: Core Campaign Infrastructure ✅ (Current)

- [x] Campaign creation endpoint
- [x] Character selection UI
- [x] Scene type tracking
- [ ] Campaign state management

### Phase 2B: Action Chips System

- [ ] Character ability parser (extract spells, features from DB)
- [ ] Dynamic chip generator based on scene type
- [ ] Chip click → structured prompt system
- [ ] UI component library for chips

### Phase 2C: Combat Integration

- [ ] Initiative tracker UI
- [ ] Combat mode detection
- [ ] Automated HP/resource tracking
- [ ] Dice roll automation with visual feedback

### Phase 2D: RAG Enhancement

- [ ] Spell lookup integration
- [ ] Monster stat block retrieval
- [ ] Rule clarification system
- [ ] Lore injection for immersion

### Phase 2E: Polish & Features

- [ ] Quest log UI
- [ ] NPC relationship tracker
- [ ] Session summary generator
- [ ] Character progression (level up)
- [ ] Inventory management

---

## Technical Architecture

### Frontend Components

```
frontend/src/components/game/
  ├── campaign/
  │   ├── CampaignWizard.jsx (new)
  │   ├── CampaignSelector.jsx (new)
  │   ├── SceneIndicator.jsx (new)
  │   └── QuestLog.jsx (new)
  ├── character/
  │   ├── PartyPanel.jsx (new)
  │   ├── CharacterCard.jsx (new)
  │   └── ResourceTracker.jsx (new)
  ├── combat/
  │   ├── InitiativeTracker.jsx (new)
  │   ├── CombatActionPanel.jsx (new)
  │   └── DamageLogger.jsx (new)
  └── actions/
      ├── ActionChip.jsx (new)
      ├── ActionChipPanel.jsx (new)
      └── SpellCard.jsx (new)
```

### Backend Endpoints

```python
# Campaign management
POST   /api/campaigns/
GET    /api/campaigns/{id}
PATCH  /api/campaigns/{id}
POST   /api/campaigns/{id}/characters/add
DELETE /api/campaigns/{id}/characters/{char_id}

# Character abilities (for chip generation)
GET    /api/characters/{id}/abilities
GET    /api/characters/{id}/spells
GET    /api/characters/{id}/items

# Combat
POST   /api/combat/encounters/
POST   /api/combat/encounters/{id}/roll-initiative
POST   /api/combat/encounters/{id}/action
PATCH  /api/combat/encounters/{id}/update-hp

# RAG queries
POST   /api/rag/spell/{spell_name}
POST   /api/rag/monster/{monster_name}
POST   /api/rag/rule
```

---

## User Experience Flow

### Starting a Campaign

1. Player visits DMChat page
2. Clicks "New Campaign" button
3. Campaign Wizard opens:
   - Select campaign type (one-shot, short, epic)
   - Choose setting
   - Set difficulty
   - Pick starting level
4. AI generates campaign opening
5. Player selects party members from character list
6. Campaign begins with opening narration

### During Gameplay

1. **AI DM narrates scene** with rich description
2. **Scene indicator** shows current mode (roleplay/combat/exploration)
3. **Action chips appear** based on:
   - Character abilities
   - Scene context
   - Available resources
4. **Player clicks chip** or types custom action
5. **AI DM responds** with:
   - Dice rolls (if needed)
   - Outcome narration
   - Resource updates
   - Next prompt
6. Cycle repeats with dynamic scene transitions

### Combat Example

```
DM: "Three goblins ambush you from the brush! Roll initiative!"
[Scene switches to Combat mode]
[Initiative Tracker appears showing order]

[Your turn - Wizard]
Action Chips:
  🔥 Cast Fireball (3rd level) [Spell Slot: 3/4]
  ⚡ Cast Magic Missile (1st level) [Auto-hit]
  🛡️ Cast Shield (Reaction)
  ⚔️ Attack with Quarterstaff (+3)
  🏃 Dash (Move 60ft)

[Player clicks Fireball chip]
System generates: "I cast Fireball at the goblins, targeting the center one.
DC 15 DEX save. Rolling damage: [8d6]"

DM: "You unleash a massive ball of flame! [Rolls: 28 fire damage]
The goblins scramble but two fail their saves, taking full damage.
One is incinerated instantly! The others are badly burned.
[Goblin 1: Dead] [Goblin 2: 3/11 HP] [Goblin 3: 5/11 HP]
Goblin 2's turn..."
```

---

## Next Steps

1. **Immediate:** Create Campaign database models and API
2. **This Week:** Build PartyPanel and ActionChip components
3. **Next Week:** Integrate combat system with Initiative Tracker
4. **Following:** RAG integration for spell/monster lookups

This design creates a truly immersive D&D experience that combines:

- ✨ AI storytelling
- 📊 Automated mechanics
- 🎮 Intuitive UI
- 📚 Rules accuracy (via RAG)
- 🎭 Deep roleplay opportunities

The result: A solo or multiplayer D&D experience that rivals in-person tabletop gaming!
