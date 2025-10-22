# AI DM: Full D&D Game System Implementation Plan

## Executive Summary

Transform the current AI DM chat system into a complete, end-to-end Dungeons & Dragons game master that can run full campaigns, manage character progression, track game state, and provide immersive storytelling.

## Current System Capabilities (Foundation)

### ✅ Already Implemented

- **RAG System**: Intelligent query analysis with filter extraction
- **Reference Database**: 1909 documents (spells, items, monsters, classes, species)
- **Chunk-based Search**: 6201 semantic chunks for precise retrieval
- **DM Tools**: 22 dungeon generation documents (chambers, hazards, traps, themes)
- **DMChat Interface**: Real-time chat with source citations
- **Character Management**: Character creation, storage, and retrieval
- **Multi-Provider LLM**: Support for OpenAI, Groq, Google, Anthropic

### 🎯 What We Need to Add

1. **Game State Management**: Track campaign progress, party status, locations
2. **Combat System**: Initiative, HP tracking, attack rolls, damage calculation
3. **Session Management**: Save/load game sessions, turn tracking
4. **Dice Rolling**: Virtual dice with visualization and history
5. **Inventory System**: Track items, equipment, currency
6. **Quest/Objective Tracking**: Campaign goals and progress
7. **NPC Management**: Generate, track, and manage NPCs
8. **Map/Location System**: Visual dungeon/world maps with fog of war
9. **Encounter Builder**: Balanced combat encounters based on party level
10. **Narrative Engine**: Story progression, branching paths, consequences

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  DMChat UI  │  Game Board  │  Character Sheet  │  DM Controls   │
│  (React)    │  (Canvas/3D) │  (Material-UI)    │  (Admin Panel) │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                     Game Engine (Backend)                        │
├─────────────────────────────────────────────────────────────────┤
│  Session     │  Combat      │  Narrative    │  Rule            │
│  Manager     │  Engine      │  Director     │  Validator       │
├─────────────────────────────────────────────────────────────────┤
│  State Store │  Event Log   │  Decision     │  Dice            │
│  (SQLite)    │  (Journal)   │  Tree         │  System          │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      AI/RAG Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Query       │  Reference    │  Monster      │  Encounter       │
│  Analyzer    │  Search       │  Search       │  Builder         │
│  (Existing)  │  (Existing)   │  (Existing)   │  (NEW)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Core Game State & Session Management (Week 1-2)

### 1.1 Database Schema Expansion

**New Tables:**

```sql
-- Game sessions (extends ChatSession)
CREATE TABLE game_sessions (
    id INTEGER PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chat_sessions(id),
    campaign_name TEXT,
    current_location TEXT,
    current_scene TEXT,
    game_state TEXT,  -- JSON: {turn_number, phase, active_combat, etc.}
    party_level INTEGER DEFAULT 1,
    session_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Party members (links characters to game sessions)
CREATE TABLE party_members (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    character_id INTEGER REFERENCES characters(id),
    current_hp INTEGER,
    max_hp INTEGER,
    temp_hp INTEGER DEFAULT 0,
    conditions TEXT,  -- JSON: ["poisoned", "blessed", etc.]
    position TEXT,  -- JSON: {x, y} or room_id
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP
);

-- Combat encounters
CREATE TABLE combat_encounters (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    name TEXT,
    description TEXT,
    difficulty TEXT,  -- easy, medium, hard, deadly
    is_active BOOLEAN DEFAULT FALSE,
    turn_order TEXT,  -- JSON: [{entity_id, initiative, type: 'pc'|'npc'}, ...]
    current_turn INTEGER DEFAULT 0,
    round_number INTEGER DEFAULT 1,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Combat participants (PCs and NPCs/Monsters)
CREATE TABLE combat_participants (
    id INTEGER PRIMARY KEY,
    encounter_id INTEGER REFERENCES combat_encounters(id),
    entity_type TEXT,  -- 'pc' or 'monster'
    entity_id INTEGER,  -- character_id or monster instance
    name TEXT,
    initiative INTEGER,
    current_hp INTEGER,
    max_hp INTEGER,
    ac INTEGER,
    conditions TEXT,  -- JSON array
    position TEXT,  -- JSON: {x, y}
    is_alive BOOLEAN DEFAULT TRUE
);

-- Quest/Objective tracking
CREATE TABLE quests (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    title TEXT,
    description TEXT,
    quest_giver TEXT,
    objectives TEXT,  -- JSON: [{description, completed, optional}, ...]
    status TEXT,  -- active, completed, failed, abandoned
    reward TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- NPCs (distinct from monsters - story characters)
CREATE TABLE npcs (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    name TEXT,
    description TEXT,
    role TEXT,  -- quest_giver, merchant, ally, enemy, neutral
    location TEXT,
    personality TEXT,
    relationship_to_party INTEGER,  -- -100 to 100
    dialogue_history TEXT,  -- JSON: [{message, timestamp}, ...]
    is_alive BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);

-- Inventory items (party-wide or individual)
CREATE TABLE inventory_items (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    character_id INTEGER REFERENCES characters(id) NULL,  -- NULL = party inventory
    item_reference_id INTEGER REFERENCES references(id) NULL,  -- link to magic_items_md
    item_name TEXT,
    quantity INTEGER DEFAULT 1,
    is_equipped BOOLEAN DEFAULT FALSE,
    description TEXT,
    acquired_at TIMESTAMP
);

-- Game event log (audit trail + story journal)
CREATE TABLE game_events (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    event_type TEXT,  -- combat, dialogue, skill_check, item_acquired, level_up, etc.
    description TEXT,
    game_state_snapshot TEXT,  -- JSON snapshot of relevant state
    turn_number INTEGER,
    created_at TIMESTAMP
);

-- Locations/Rooms (for dungeon crawling)
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    game_session_id INTEGER REFERENCES game_sessions(id),
    name TEXT,
    description TEXT,
    location_type TEXT,  -- dungeon, town, wilderness, etc.
    parent_location_id INTEGER REFERENCES locations(id) NULL,  -- for nested locations
    features TEXT,  -- JSON: [traps, hazards, treasure, etc.]
    connections TEXT,  -- JSON: {north: location_id, south: location_id, etc.}
    is_explored BOOLEAN DEFAULT FALSE,
    discovered_at TIMESTAMP
);
```

### 1.2 Backend API Endpoints

**Session Management:**

```python
POST   /api/game/sessions                    # Create new game session
GET    /api/game/sessions                    # List all game sessions
GET    /api/game/sessions/{id}               # Get session details + state
PUT    /api/game/sessions/{id}               # Update session state
DELETE /api/game/sessions/{id}               # End session
POST   /api/game/sessions/{id}/save          # Manual save checkpoint
POST   /api/game/sessions/{id}/load          # Load from checkpoint
```

**Party Management:**

```python
POST   /api/game/sessions/{id}/party         # Add character to party
DELETE /api/game/sessions/{id}/party/{char}  # Remove character
GET    /api/game/sessions/{id}/party         # List party members + status
PUT    /api/game/sessions/{id}/party/{char}  # Update HP, conditions, etc.
```

**Game Actions:**

```python
POST   /api/game/sessions/{id}/action        # Player action (attack, skill check, etc.)
POST   /api/game/sessions/{id}/dice          # Roll dice (with validation)
POST   /api/game/sessions/{id}/turn          # End turn / advance game
```

### 1.3 Frontend Components

**New React Components:**

```
frontend/src/components/game/
├── GameBoard.jsx              # Main game view (combines all panels)
├── PartyPanel.jsx             # Party HP, conditions, quick stats
├── CombatTracker.jsx          # Initiative order, turn tracker
├── DiceRoller.jsx             # Virtual dice with animations
├── InventoryPanel.jsx         # Party inventory management
├── QuestLog.jsx               # Active quests and objectives
├── LocationMap.jsx            # Visual map/dungeon layout
└── GameControls.jsx           # DM controls (if player is DM)
```

---

## Phase 2: Combat System (Week 3-4)

### 2.1 Combat Engine

**Core Combat Logic:**

```python
# backend/game/combat_engine.py

class CombatEngine:
    """Manages D&D 5e combat encounters"""

    def start_encounter(session_id, monsters, terrain=None):
        """Initialize combat, roll initiative, establish turn order"""
        pass

    def roll_initiative(participants):
        """Roll initiative for all participants (d20 + DEX mod)"""
        pass

    def process_attack(attacker, target, attack_type, weapon=None):
        """
        1. Roll attack (d20 + modifiers)
        2. Check advantage/disadvantage
        3. Compare to target AC
        4. On hit: roll damage
        5. Apply resistances/vulnerabilities
        6. Update HP
        """
        pass

    def apply_damage(target, damage, damage_type):
        """Apply damage considering resistances/immunities"""
        pass

    def check_saving_throw(target, dc, ability, advantage=None):
        """Roll saving throw (d20 + ability mod)"""
        pass

    def apply_condition(target, condition, duration):
        """Apply status condition (poisoned, stunned, etc.)"""
        pass

    def end_turn(encounter_id):
        """Advance to next turn, process ongoing effects"""
        pass

    def check_combat_end(encounter_id):
        """Check if combat should end (all enemies dead, party fled, etc.)"""
        pass
```

### 2.2 Combat AI for Monsters

```python
class MonsterAI:
    """AI decision-making for monsters in combat"""

    def choose_action(monster, party_members, battlefield):
        """
        Use LLM + rules to decide monster action:
        - Target selection (lowest HP, highest threat, random)
        - Action type (attack, spell, special ability)
        - Movement strategy
        - Consider monster intelligence and personality
        """
        pass

    def choose_target(monster, available_targets):
        """Smart target selection based on monster tactics"""
        pass
```

### 2.3 Combat UI

**Real-time Combat Display:**

- Initiative tracker (visual turn order)
- HP bars for all participants
- Condition icons
- Action buttons (Attack, Cast Spell, Dodge, etc.)
- Battlefield grid (optional - can be text-based initially)

---

## Phase 3: Narrative Engine & Decision Trees (Week 5-6)

### 3.1 Story Progression System

```python
# backend/game/narrative_engine.py

class NarrativeEngine:
    """Manages story progression and player choices"""

    def generate_scene(game_session, context):
        """
        Use RAG + LLM to generate next story beat:
        1. Retrieve relevant DM tools (dungeon themes, etc.)
        2. Consider party level, location, recent events
        3. Generate scene description
        4. Provide player choices
        """
        pass

    def process_player_choice(game_session, choice):
        """
        Update game state based on player decision:
        - Trigger events
        - Update quest progress
        - Modify NPC relationships
        - Generate consequences
        """
        pass

    def generate_branching_paths(current_state):
        """Create meaningful choices for players"""
        pass

    def check_quest_triggers(game_session):
        """Check if actions trigger quest updates"""
        pass
```

### 3.2 Dynamic Event System

**Event Types:**

- **Random Encounters**: Based on location, time, party level
- **Scripted Events**: Quest-related story moments
- **Environmental Hazards**: Traps, weather, terrain
- **NPC Interactions**: Dialogue, trade, persuasion

### 3.3 Consequence Tracking

```python
class ConsequenceEngine:
    """Track player decisions and apply long-term effects"""

    def record_decision(session_id, decision, context):
        """Store decision for future callback"""
        pass

    def apply_consequences(session_id):
        """
        Apply consequences of past decisions:
        - NPC attitudes change
        - World state shifts
        - New quest opportunities
        """
        pass
```

---

## Phase 4: Encounter Builder & Balance (Week 7-8)

### 4.1 Encounter Generation

```python
# backend/game/encounter_builder.py

class EncounterBuilder:
    """Generate balanced combat encounters"""

    def build_encounter(party_level, party_size, difficulty, theme=None):
        """
        1. Calculate XP budget based on difficulty
        2. Query monsters matching theme/CR
        3. Select monsters to fit budget
        4. Add terrain/environmental factors
        5. Suggest tactics for monsters
        """
        pass

    def calculate_xp_budget(party_level, party_size, difficulty):
        """Use D&D 5e encounter building rules"""
        pass

    def select_monsters(cr_range, theme, count):
        """Query monster database with filters"""
        pass

    def add_terrain_features(encounter, location_type):
        """
        Add interesting terrain:
        - Cover (half/three-quarter)
        - Difficult terrain
        - Hazards (lava, pits, etc.)
        - Interactive elements (levers, doors)
        """
        pass
```

### 4.2 Dynamic Difficulty Adjustment

```python
class DifficultyManager:
    """Adjust encounter difficulty based on party performance"""

    def analyze_party_performance(recent_combats):
        """Track win rate, average HP remaining, etc."""
        pass

    def suggest_difficulty_adjustment(analysis):
        """Recommend easier/harder encounters"""
        pass
```

---

## Phase 5: Enhanced UI/UX (Week 9-10)

### 5.1 Game Board Component

**Main Game View Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Campaign: The Lost Mines    Session #5    Level 3 Party   │
├──────────────────┬──────────────────────────────────────────┤
│                  │  Scene Description                       │
│   Party Panel    │  ────────────────────────────────────── │
│   ────────────   │  You enter a dimly lit chamber. Ancient │
│   [Avatar] HP    │  runes glow faintly on the walls. You   │
│   Theron  24/32  │  hear scraping sounds from the shadows.  │
│   Wizard         │                                          │
│                  │  What do you do?                         │
│   [Avatar] HP    │  ────────────────────────────────────── │
│   Kira    38/38  │                                          │
│   Fighter        │  [Roll Perception] [Search Room]        │
│                  │  [Attack] [Cast Spell] [Talk]           │
│   Gold: 250 gp   │                                          │
│                  │  DM Response:                            │
│   Active Quest:  │  Roll Perception (DC 12)...              │
│   Find the Gem   │  [Theron rolled: 15 (Success!)]         │
│   ⚙️ [Inventory]  │  You spot a trap mechanism...           │
│   📜 [Quest Log]  │                                          │
├──────────────────┼──────────────────────────────────────────┤
│   Combat (if active)          │   Map/Location             │
│   Turn: Goblin 2              │   [Mini-map or ASCII]      │
│   Initiative:                 │   ┌───┬───┬───┐            │
│   1. Kira (19)    ←           │   │ T │   │ G │            │
│   2. Theron (15)              │   ├───┼───┼───┤            │
│   3. Goblin 1 (12)            │   │   │ K │   │            │
│   4. Goblin 2 (8)  ← ACTIVE   │   ├───┼───┼───┤            │
│                               │   │ G │   │ D │            │
│   [End Turn] [Flee]           │   └───┴───┴───┘            │
└───────────────────────────────┴────────────────────────────┘
```

### 5.2 Dice Roller Component

**Features:**

- Visual 3D dice animation (or 2D sprite)
- Support for all D&D dice (d4, d6, d8, d10, d12, d20, d100)
- Modifiers (+5, advantage, disadvantage)
- Roll history
- Critical hit/fail highlighting

### 5.3 Character Sheet Integration

**Quick Stats Panel:**

- Current HP / Max HP
- AC, initiative bonus
- Spell slots remaining
- Conditions/buffs active
- Quick action buttons

---

## Phase 6: Advanced Features (Week 11-12)

### 6.1 Long Rest / Short Rest System

```python
def handle_rest(game_session, rest_type):
    """
    Short Rest:
    - Spend hit dice to recover HP
    - Recover some class features

    Long Rest:
    - Restore all HP
    - Restore all spell slots
    - Restore hit dice
    - Remove exhaustion levels
    """
    pass
```

### 6.2 Level Up System

```python
def level_up_character(character_id):
    """
    1. Increase HP (roll hit die + CON mod)
    2. Grant new features from class
    3. Increase spell slots
    4. ASI at levels 4, 8, 12, etc.
    """
    pass
```

### 6.3 Magic Item Distribution

```python
def generate_treasure(encounter_cr, rarity_budget):
    """
    Generate appropriate treasure:
    - Gold coins
    - Magic items (using magic_items_md references)
    - Consumables (potions, scrolls)
    """
    pass
```

### 6.4 NPC Dialogue System

```python
class DialogueManager:
    """Manage NPC conversations with personality"""

    def generate_npc_response(npc, player_message, context):
        """
        Use LLM + NPC personality to generate response:
        - Consider relationship to party
        - Include quest hooks
        - Provide trade options if merchant
        """
        pass

    def update_relationship(npc, action, magnitude):
        """Modify NPC attitude based on player actions"""
        pass
```

---

## Implementation Priority & Roadmap

### Sprint 1 (Week 1-2): Foundation

- ✅ Database schema creation
- ✅ Session management endpoints
- ✅ Basic game state storage
- ✅ Party management UI

### Sprint 2 (Week 3-4): Combat Core

- ✅ Combat engine implementation
- ✅ Initiative & turn tracking
- ✅ Attack/damage resolution
- ✅ Combat UI components

### Sprint 3 (Week 5-6): Narrative

- ✅ Scene generation
- ✅ Player choice system
- ✅ Quest tracking
- ✅ Event logging

### Sprint 4 (Week 7-8): Encounters

- ✅ Encounter builder
- ✅ Monster AI
- ✅ Difficulty balancing
- ✅ Terrain generation

### Sprint 5 (Week 9-10): UX Polish

- ✅ Game board layout
- ✅ Dice roller
- ✅ Character panels
- ✅ Map visualization

### Sprint 6 (Week 11-12): Advanced

- ✅ Rest system
- ✅ Level up
- ✅ Treasure generation
- ✅ NPC dialogues

---

## Technical Considerations

### Performance

- **WebSocket Integration**: Real-time updates for multiplayer (future)
- **State Caching**: Redis for active game sessions
- **Lazy Loading**: Load game history on demand

### Data Integrity

- **Transaction Wrapper**: All game actions in DB transactions
- **State Validation**: Validate all state changes against D&D rules
- **Audit Trail**: Every action logged in game_events table

### AI/LLM Integration

- **Structured Prompts**: Use JSON schema for deterministic outputs
- **Fallback Rules**: Hard-coded D&D rules when LLM unavailable
- **Cost Management**: Cache common responses, use smaller models for simple tasks

### Extensibility

- **Plugin System**: Allow custom campaigns, homebrew rules
- **Modular Combat**: Easy to add new combat mechanics
- **API-First**: All game logic accessible via REST API

---

## Success Metrics

### MVP Success Criteria

1. ✅ Create game session with party of characters
2. ✅ DM generates opening scene
3. ✅ Players make choices that affect story
4. ✅ Combat encounter starts and resolves
5. ✅ HP tracking works correctly
6. ✅ Dice rolls are validated
7. ✅ Quest progress is tracked
8. ✅ Session can be saved and resumed

### Long-term Goals

- **Engagement**: Average session length > 30 minutes
- **Retention**: 50%+ of users return for second session
- **Accuracy**: 95%+ of D&D rules applied correctly
- **Performance**: < 3 second response time for actions
- **Storytelling**: 80%+ user satisfaction with narrative quality

---

## Next Immediate Actions

1. **Create database migration** for new tables
2. **Implement Session Manager** (backend/game/session_manager.py)
3. **Build GameBoard.jsx** (frontend component)
4. **Create game session endpoints** (/api/game/sessions/\*)
5. **Test basic flow**: Create session → Add party → Start game

---

## Questions to Address

### Game Design Decisions

1. **Solo or Party Play?**
   - Start with single player, design for multi-player later
2. **Campaign Length?**
   - Support both one-shots (2-3 hours) and long campaigns
3. **Automation Level?**
   - DM handles everything (full automation)
   - Player declares actions, DM narrates results
4. **Visual Fidelity?**
   - Start text-based with simple UI
   - Add visual maps/tokens later
5. **Homebrew Support?**
   - Phase 2 - focus on official 5e rules first

### Technical Decisions

1. **Real-time vs Turn-based?**
   - Turn-based with polling (simpler)
   - WebSocket for multiplayer later
2. **State Storage?**
   - SQLite for persistence
   - Redis for active session cache
3. **Dice RNG?**
   - Use cryptographically secure random (Python `secrets` module)
4. **Character Sheets?**
   - Leverage existing Character model
   - Extend with combat stats

---

## Files to Create (Initial Sprint)

### Backend

```
backend/
├── game/
│   ├── __init__.py
│   ├── session_manager.py       # Game session orchestration
│   ├── combat_engine.py         # Combat resolution
│   ├── narrative_engine.py      # Story generation
│   ├── encounter_builder.py     # Encounter creation
│   ├── dice_roller.py           # Validated dice rolling
│   ├── rules_validator.py       # D&D 5e rule enforcement
│   └── models.py                # Game-specific SQLAlchemy models
├── routers/
│   └── game.py                  # Game API endpoints
└── alembic/
    └── versions/
        └── xxx_add_game_tables.py
```

### Frontend

```
frontend/src/
├── pages/
│   └── GameSession.jsx          # Main game page
├── components/game/
│   ├── GameBoard.jsx            # Main layout
│   ├── PartyPanel.jsx           # Party status
│   ├── CombatTracker.jsx        # Combat UI
│   ├── DiceRoller.jsx           # Dice rolling
│   ├── QuestLog.jsx             # Quest tracking
│   └── GameControls.jsx         # Action buttons
└── hooks/
    └── useGameSession.js        # Game state management
```

---

## Summary

This plan transforms StoryCraft into a fully-functional AI Dungeon Master capable of running complete D&D 5e games. The phased approach allows for:

1. **Rapid MVP**: Core gameplay in 4 weeks
2. **Iterative Enhancement**: Add features based on user feedback
3. **Scalability**: Architecture supports multiplayer and advanced features
4. **Quality**: D&D rules enforced, narrative quality maintained

**Estimated Timeline**: 12 weeks for full feature set, 4 weeks for playable MVP.

**Next Step**: Review and approve this plan, then begin Sprint 1 with database schema creation.
