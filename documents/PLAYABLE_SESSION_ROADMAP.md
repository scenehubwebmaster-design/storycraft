# Roadmap to Playable AI DM Session

**Goal:** Enable a full end-to-end D&D game session with AI DM  
**Current Date:** October 22, 2025  
**Target:** MVP playable session in 3-4 days of focused work

---

## Current Status

### ✅ What We Have

1. **Database & Models** - Game sessions, party, combat, quests, NPCs, inventory, events
2. **Session Manager** - Full CRUD for game state, party management, HP tracking
3. **REST API** - 9 endpoints for session operations (`/api/game/*`)
4. **RAG System** - 1,916 documents including:
   - D&D rules (classes, spells, monsters, items)
   - DM tools (chamber design, hazards, traps)
   - Adventure creation guides (DMG Chapter 3)
   - Consolidated reference lists

### ❌ What We Need

1. **Dice Roller** - Roll d20, damage dice, ability checks
2. **Narrative Engine** - Generate scenes using RAG + LLM
3. **Chat Integration** - Link game sessions to DM chat
4. **Basic Combat** - Track initiative, turns, HP damage
5. **Frontend UI** - Display game state, make choices

---

## Implementation Phases

## Phase 1: Core Game Loop (2 days) 🎯 **CRITICAL**

### Day 1 Morning: Dice Roller + Combat Foundation

**Files:** `backend/game/dice_roller.py`, `backend/routers/game.py`

**Dice Roller Requirements:**

```python
# backend/game/dice_roller.py
class DiceRoller:
    def roll(notation: str) -> DiceResult
        # "1d20+5" → roll 1d20, add 5
        # "2d6" → roll 2d6
        # "4d8+3" → roll 4d8, add 3

    def roll_with_advantage() -> DiceResult
        # Roll 2d20, take higher

    def roll_with_disadvantage() -> DiceResult
        # Roll 2d20, take lower

    def roll_ability_check(modifier: int, dc: int) -> bool
        # Roll d20 + modifier vs DC
```

**API Endpoints:**

```
POST /api/game/sessions/{id}/roll
  Body: {"notation": "2d6+3", "advantage": null}
  Returns: {"total": 11, "rolls": [4, 5], "modifier": 3}

POST /api/game/sessions/{id}/combat/start
  Body: {"participants": [...]}
  Returns: Combat encounter with initiative order

POST /api/game/sessions/{id}/combat/{combat_id}/action
  Body: {"action": "attack", "target_id": 2}
  Returns: Updated combat state
```

**Combat Basics:**

- Roll initiative for all participants
- Track turn order
- Process attack rolls (d20 + modifier vs AC)
- Roll damage and apply to HP
- Update party_members table

### Day 1 Afternoon: Narrative Engine Core

**Files:** `backend/game/narrative_engine.py`

**Narrative Engine Requirements:**

```python
# backend/game/narrative_engine.py
class NarrativeEngine:
    def __init__(self, session_manager, rag_client, llm_client):
        self.session_manager = session_manager
        self.rag = rag_client
        self.llm = llm_client

    def generate_opening_scene(game_session) -> Scene
        """
        1. Query RAG for adventure hooks, starting areas
        2. Get party composition
        3. Generate opening description with LLM
        4. Present 3-4 choices to players
        """

    def process_player_choice(game_session, choice) -> Scene
        """
        1. Update game state based on choice
        2. Query RAG for relevant content
        3. Generate next scene with LLM
        4. Determine if combat/skill check needed
        5. Present new choices
        """

    def generate_combat_narration(combat_state) -> str
        """
        Narrate combat results in engaging way
        """
```

**RAG Integration:**

```python
# Pull from multiple document types
def get_scene_context(query, game_state):
    # Get adventure structure guidance
    adventure_docs = do_chunk_search(
        q=query,
        ref_type='adventures_md',
        k=2
    )

    # Get environmental details
    dm_tools = do_chunk_search(
        q=query,
        ref_type='core',  # chamber design, hazards
        k=2
    )

    # Get relevant monsters/NPCs if needed
    monsters = do_chunk_search(
        q=f"CR {party_level} {theme}",
        ref_type='monsters_md',
        k=3
    )

    return combined_context
```

### Day 2 Morning: DM Chat Integration

**Files:** `backend/routers/chat.py`, `backend/game/dm_chat_handler.py`

**Chat → Game Session Bridge:**

```python
# backend/game/dm_chat_handler.py
class DMChatHandler:
    def handle_message(chat_session, message, game_session):
        """
        1. Parse player input
        2. Determine intent (combat action, exploration, dialogue)
        3. Call appropriate game system
        4. Generate DM response
        5. Update game state
        6. Log event
        """

    def parse_player_intent(message) -> Intent
        # "I attack the goblin" → CombatAction
        # "I search the room" → SkillCheck
        # "I talk to the merchant" → Dialogue
```

**Enhanced Chat Endpoint:**

```python
# backend/routers/chat.py
@router.post("/sessions/{session_id}/message")
def post_message_with_game(session_id, message, game_session_id=None):
    """
    If game_session_id provided:
    1. Process message through game system
    2. Roll dice if needed
    3. Update combat/exploration state
    4. Generate contextual response

    Otherwise: Normal chat behavior
    """
```

### Day 2 Afternoon: Session Lifecycle Testing

**Files:** `scripts/test_game_session_e2e.py`

**End-to-End Test:**

```python
# Test complete game loop
1. Create chat session
2. Create game session linked to chat
3. Add 2-3 D&D characters to party
4. Generate opening scene
5. Make player choice
6. Trigger combat encounter
7. Roll initiative
8. Execute combat actions (attack, damage)
9. End combat
10. Continue exploration
11. Save game state
12. Load game state
13. End session

# Verify:
- All state transitions work
- Events logged correctly
- HP updates persist
- Combat math correct
- RAG retrieval provides good context
```

---

## Phase 2: Frontend Game Board (1 day) 🎨

### Day 3: Basic Game UI

**Files:**

- `frontend/src/pages/GameSession.jsx`
- `frontend/src/components/game/GameBoard.jsx`
- `frontend/src/components/game/PartyPanel.jsx`
- `frontend/src/components/game/SceneDisplay.jsx`
- `frontend/src/hooks/useGameSession.js`

**Component Structure:**

```jsx
// GameSession.jsx - Main page
<GameBoard>
  <PartyPanel>
    - Character portraits - Current HP bars - Conditions/status effects - Quick
    stats
  </PartyPanel>

  <SceneDisplay>
    - Current scene description - DM narration - Available choices - Chat-style
    message history
  </SceneDisplay>

  <ActionPanel>
    - Choice buttons - Dice roller UI - Combat actions (if in combat) - Input
    for custom actions
  </ActionPanel>

  <CombatTracker>
    {" "}
    (if active) - Initiative order - Current turn indicator - Enemy HP - Action buttons
  </CombatTracker>
</GameBoard>
```

**useGameSession Hook:**

```javascript
function useGameSession(sessionId) {
  const [gameState, setGameState] = useState(null);
  const [party, setParty] = useState([]);
  const [currentScene, setCurrentScene] = useState(null);
  const [combatActive, setCombatActive] = useState(false);

  const makeChoice = async (choice) => {
    /* ... */
  };
  const rollDice = async (notation) => {
    /* ... */
  };
  const takeCombatAction = async (action, target) => {
    /* ... */
  };

  return {
    gameState,
    party,
    currentScene,
    combatActive,
    makeChoice,
    rollDice,
    takeCombatAction,
  };
}
```

---

## Phase 3: Polish & Playtest (0.5 days) ✨

### Features to Add

1. **Auto-save** - Save game state every turn
2. **Event log** - Show recent actions/rolls
3. **Dice roll animations** - Fun visual feedback
4. **Character portraits** - Use existing portrait system
5. **Sound effects** - Optional dice rolls, combat hits
6. **Mobile responsive** - Ensure playable on phones

### Playtesting Checklist

- [ ] Create new game session
- [ ] Add characters successfully
- [ ] Opening scene generates properly
- [ ] Choices lead to new scenes
- [ ] Combat initiates correctly
- [ ] Attack rolls work (d20 + mod vs AC)
- [ ] Damage applies to HP
- [ ] Death/unconsciousness handled
- [ ] Session saves and loads
- [ ] Multiple sessions don't interfere
- [ ] RAG context is relevant
- [ ] LLM responses are coherent

---

## Minimum Viable Session Flow

**Player Experience:**

1. **Start Session**

   ```
   Click "New Game Session"
   → Enter campaign name
   → Select characters from character list
   → Click "Begin Adventure"
   ```

2. **Opening Scene**

   ```
   AI DM: "You find yourselves in the village of Greenest as
           a massive blue dragon circles overhead. Panicked
           villagers run past. You see:

           1. Run to the keep for safety
           2. Help villagers fight approaching kobolds
           3. Investigate the dragon's lair
           4. Free action (describe what you do)"
   ```

3. **Make Choice**

   ```
   Player clicks "2. Help villagers fight kobolds"
   ```

4. **Combat Begins**

   ```
   AI DM: "You charge toward the kobolds menacing a family.
           Roll initiative!"

   [System rolls initiative for all participants]

   Initiative Order:
   1. Torrin (Dwarf Fighter) - 18
   2. Kobold Leader - 15
   3. Kobold 1 - 12
   4. Kobold 2 - 12
   5. Elara (Elf Wizard) - 10

   [Torrin's Turn]
   Your turn, Torrin! What do you do?

   [Action buttons appear]
   - Attack Kobold Leader
   - Attack Kobold 1
   - Attack Kobold 2
   - Cast Spell
   - Use Item
   - Custom Action
   ```

5. **Combat Action**

   ```
   Player clicks "Attack Kobold Leader"

   [System rolls d20 + attack modifier]
   Roll: 15 + 5 = 20 vs AC 13 → HIT!

   [System rolls damage]
   Damage: 1d8+3 = 7 damage

   AI DM: "Your axe slams into the kobold leader's shield,
           dealing 7 damage! It staggers back, wounded."

   Kobold Leader HP: 20 → 13
   ```

6. **Combat Continues**

   ```
   [Enemy turns auto-resolve]
   [Player characters take turns]
   [Repeat until combat ends]
   ```

7. **Victory**

   ```
   AI DM: "The last kobold falls! The family thanks you
           profusely. You gained 150 XP.

           What do you do next?

           1. Continue to the keep
           2. Search the kobolds
           3. Rest and heal
           4. Free action"
   ```

8. **Session Save**

   ```
   [Auto-saves after each scene]

   Player can click "End Session" anytime
   → Saves current state
   → Can resume later
   ```

---

## Technical Architecture

### Request Flow

```
Frontend                Backend                    RAG           LLM
   │                       │                        │             │
   ├─ POST /game/sessions  │                        │             │
   │  ├─ create_session()  │                        │             │
   │  └─ add_party_member()│                        │             │
   │                       │                        │             │
   ├─ POST /chat/message   │                        │             │
   │  (with game_session_id)                        │             │
   │  ├─ parse_intent()    │                        │             │
   │  ├─ get_scene_context()───────► search()       │             │
   │  │                    │         (adventures_md,│             │
   │  │                    │          dm_tools,     │             │
   │  │                    │          monsters)     │             │
   │  ├─ generate_scene()  │                        │             │
   │  │                    ├────────────────────────┼──► prompt   │
   │  │                    │    RAG context         │   + context │
   │  │                    │                        │             │
   │  ├─ update_state()    │                        │             │
   │  └─ log_event()       │                        │             │
   │                       │                        │             │
   ├─ POST /game/.../combat/action                  │             │
   │  ├─ roll_dice()       │                        │             │
   │  ├─ resolve_attack()  │                        │             │
   │  ├─ apply_damage()    │                        │             │
   │  └─ update_combat()   │                        │             │
   │                       │                        │             │
   └─ GET /game/sessions/{id}                       │             │
      └─ get_session()     │                        │             │
         (with party, state, events)                │             │
```

---

## Critical Dependencies

### Must Have Before MVP

1. ✅ **Session Manager** - COMPLETE
2. ✅ **RAG System** - COMPLETE
3. ❌ **Dice Roller** - Need to implement
4. ❌ **Narrative Engine** - Need to implement
5. ❌ **Combat System** - Basic version needed
6. ❌ **Frontend UI** - Need to implement

### Can Add Later

- Advanced combat (conditions, spells, AoE)
- Inventory management UI
- Quest tracking UI
- NPC relationship system
- World map / location tracking
- Character leveling
- Loot generation
- Skill checks (perception, stealth, etc.)

---

## Development Priority Order

### Week 1 (MVP)

**Day 1:**

- Morning: Dice roller + basic combat
- Afternoon: Narrative engine core

**Day 2:**

- Morning: DM chat integration
- Afternoon: E2E testing

**Day 3:**

- All day: Frontend game board

**Day 4:**

- Morning: Polish and bug fixes
- Afternoon: First playtest session!

### Week 2 (Polish)

- Advanced combat features
- Better narration
- UI improvements
- Mobile optimization
- Sound effects
- More playtest sessions

---

## Success Criteria for MVP

A successful MVP session means:

1. ✅ **Can start a game** - Create session, add characters
2. ✅ **Can get opening scene** - RAG + LLM generates coherent start
3. ✅ **Can make choices** - Player choices lead to new scenes
4. ✅ **Can enter combat** - Combat encounter triggers properly
5. ✅ **Can fight** - Initiative, attacks, damage all work
6. ✅ **Can end combat** - Victory/defeat handled correctly
7. ✅ **Can continue** - Session continues after combat
8. ✅ **Can save/load** - Game state persists correctly
9. ✅ **RAG is helpful** - Retrieved documents improve narration
10. ✅ **Fun to play** - Session feels like D&D!

---

## Next Immediate Steps

**To start implementing RIGHT NOW:**

1. **Create dice roller** (`backend/game/dice_roller.py`)
2. **Add dice API endpoint** (`/api/game/sessions/{id}/roll`)
3. **Test dice rolling** (unit tests)
4. **Start narrative engine** (basic scene generation)
5. **Integrate with chat** (game-aware responses)

Want me to start implementing the dice roller? That's the foundation for everything else!
