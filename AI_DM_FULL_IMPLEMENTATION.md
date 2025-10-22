# AI Dungeon Master - Full Implementation Plan

## Executive Summary

This document outlines the complete implementation of an AI Dungeon Master system for StoryCraft, enabling users to play full D&D 5e sessions with an intelligent, context-aware DM powered by LLMs and RAG (Retrieval-Augmented Generation).

**Timeline**: 3-4 days
**Status**: Ready to implement (backend foundation complete)
**Goal**: Playable AI DM session from character creation through combat encounters

---

## Current System State

### ✅ Completed Foundation

1. **Database Schema** (9 game tables)

   - `game_sessions`: Campaign state and chat integration
   - `party_members`: Character HP, conditions, position
   - `combat_encounters`: Initiative, turn order, rounds
   - `combat_participants`: Monster/NPC combat tracking
   - `quests`: Objectives and progress
   - `npcs`: NPC dialogue history and relationships
   - `inventory_items`: Loot and equipment tracking
   - `game_events`: Complete audit log
   - `game_locations`: Map and exploration state

2. **Backend Infrastructure**

   - SessionManager class with full CRUD operations
   - 9 REST API endpoints at `/api/game/*`
   - SQLAlchemy ORM models with relationships
   - State save/load architecture
   - Event logging system

3. **RAG System Enhancement**
   - 1,916 reference documents
   - 6,228 embedded chunks (384 dimensions)
   - 7 DMG adventure creation documents ingested
   - Semantic search validated (0.4-0.7 relevance scores)
   - Ready for narrative engine integration

### 🎯 Implementation Phases

---

## Phase 1: Core Game Mechanics (Day 1)

### 1.1 Dice Rolling System

**File**: `backend/game/dice_roller.py`
**Time**: 1 hour
**Priority**: CRITICAL (foundation for all mechanics)

#### Requirements

```python
class DiceRoller:
    """D&D 5e compliant dice rolling with advantage/disadvantage"""

    def roll(self, notation: str) -> DiceResult:
        """
        Parse and roll D&D dice notation
        Examples: "2d6+3", "1d20", "4d8-2", "1d100"
        Supports: d4, d6, d8, d10, d12, d20, d100
        """
        pass

    def roll_with_advantage(self, notation: str = "1d20") -> DiceResult:
        """Roll twice, take higher result"""
        pass

    def roll_with_disadvantage(self, notation: str = "1d20") -> DiceResult:
        """Roll twice, take lower result"""
        pass

    def roll_ability_check(self, modifier: int, dc: int, advantage: bool = False) -> CheckResult:
        """
        Roll d20 + modifier vs DC
        Returns success/failure with detailed breakdown
        """
        pass

    def roll_attack(self, attack_bonus: int, target_ac: int, advantage: bool = False) -> AttackResult:
        """
        Roll to hit vs AC
        Includes critical hit/miss detection (natural 1/20)
        """
        pass

    def roll_damage(self, notation: str, critical: bool = False) -> DamageResult:
        """
        Roll damage dice
        Doubles dice on critical hits
        """
        pass
```

#### API Endpoint

```python
@router.post("/api/game/sessions/{session_id}/roll")
async def roll_dice(
    session_id: int,
    roll_request: RollRequest,
    db: Session = Depends(get_db)
):
    """
    Roll dice and log to game events

    Request:
    {
        "notation": "2d6+3",
        "advantage": false,
        "disadvantage": false,
        "purpose": "Attack roll",
        "character_id": 123
    }

    Response:
    {
        "total": 11,
        "rolls": [4, 4],
        "modifier": 3,
        "notation": "2d6+3",
        "breakdown": "4 + 4 + 3 = 11"
    }
    """
```

#### Testing

- Unit tests for all dice types (d4, d6, d8, d10, d12, d20, d100)
- Advantage/disadvantage logic
- Modifier parsing (+3, -2, etc.)
- Critical hit detection
- Invalid notation handling

---

### 1.2 Combat System

**File**: `backend/game/combat_engine.py`
**Time**: 3-4 hours
**Priority**: CRITICAL

#### Requirements

```python
class CombatEngine:
    """D&D 5e combat encounter management"""

    def __init__(self, db: Session, dice_roller: DiceRoller):
        self.db = db
        self.dice = dice_roller

    def start_combat(
        self,
        game_session_id: int,
        participants: List[CombatantData]
    ) -> CombatEncounter:
        """
        1. Roll initiative for all participants
        2. Create combat_encounter record
        3. Create combat_participant records
        4. Sort by initiative (ties broken by DEX)
        5. Set turn to highest initiative
        6. Log combat start event
        """
        pass

    def process_attack(
        self,
        combat_id: int,
        attacker_id: int,
        target_id: int,
        weapon_damage: str,
        attack_bonus: int,
        target_ac: int,
        advantage: bool = False
    ) -> AttackResult:
        """
        1. Roll attack (d20 + bonus vs AC)
        2. On hit: roll damage
        3. On crit: double damage dice
        4. Apply damage to target HP
        5. Update combat_participant HP
        6. Update party_member HP if PC
        7. Check for death (HP <= 0)
        8. Log attack event
        9. Return detailed result
        """
        pass

    def next_turn(self, combat_id: int) -> CombatState:
        """
        1. Increment turn counter
        2. If end of initiative order, increment round
        3. Process conditions (duration tracking)
        4. Set current_turn to next participant
        5. Log turn change event
        """
        pass

    def end_combat(self, combat_id: int, outcome: str) -> None:
        """
        1. Mark combat as completed
        2. Award XP (if victory)
        3. Reset temp HP
        4. Clear combat conditions
        5. Log combat end event
        """
        pass

    def get_combat_state(self, combat_id: int) -> CombatState:
        """
        Return current combat state:
        - Turn order
        - Current turn
        - Round number
        - All participant HP/conditions
        - Combat log
        """
        pass
```

#### API Endpoints

```python
@router.post("/api/game/sessions/{session_id}/combat/start")
async def start_combat(...)

@router.post("/api/game/sessions/{session_id}/combat/{combat_id}/attack")
async def process_attack(...)

@router.post("/api/game/sessions/{session_id}/combat/{combat_id}/next-turn")
async def next_turn(...)

@router.post("/api/game/sessions/{session_id}/combat/{combat_id}/end")
async def end_combat(...)

@router.get("/api/game/sessions/{session_id}/combat/{combat_id}")
async def get_combat_state(...)
```

#### Testing

- Initiative order (including ties)
- Attack resolution (hit/miss/crit)
- Damage calculation and HP updates
- Death detection (HP <= 0)
- Multi-round combat flow
- Condition tracking

---

### 1.3 Narrative Engine with RAG

**File**: `backend/game/narrative_engine.py`
**Time**: 4-5 hours
**Priority**: CRITICAL

#### Requirements

```python
class NarrativeEngine:
    """AI-powered scene generation using RAG + LLM"""

    def __init__(self, db: Session, embedder, llm_client):
        self.db = db
        self.embedder = embedder
        self.llm = llm_client

    async def generate_opening_scene(
        self,
        game_session: GameSession
    ) -> Scene:
        """
        1. Get party composition from party_members
        2. Query RAG for adventure structure guidance
           - adventures_md: "adventure opening", "hooks"
           - dm_tools_core: chambers, atmospheres
        3. Construct LLM prompt with:
           - Party details (classes, levels, backgrounds)
           - Adventure creation guidance from RAG
           - Scene generation instructions
        4. Generate opening scene with LLM
        5. Extract 3-4 player choices
        6. Save to game_state
        7. Log scene generation event
        8. Return Scene object
        """
        pass

    async def process_player_choice(
        self,
        game_session: GameSession,
        choice: PlayerChoice
    ) -> Scene:
        """
        1. Update game_state with player decision
        2. Query RAG for relevant context:
           - If exploration: dm_tools_core, adventures_md
           - If social: npcs, dialogue patterns
           - If potential combat: monsters_md, encounters
        3. Construct LLM prompt with:
           - Current game state
           - Party status
           - Previous events (last 5 from game_events)
           - RAG context
        4. Generate next scene
        5. Detect scene type:
           - Combat: trigger combat_engine.start_combat()
           - Skill check: trigger dice_roller.roll_ability_check()
           - Exploration: present new choices
        6. Update game_state
        7. Log scene event
        8. Return Scene object
        """
        pass

    async def generate_npc_dialogue(
        self,
        npc: NPC,
        player_message: str,
        game_context: Dict
    ) -> str:
        """
        1. Get NPC personality from npc.dialogue_history
        2. Query RAG for similar dialogue patterns
        3. Generate contextual response
        4. Update npc.dialogue_history
        5. Return NPC response
        """
        pass

    async def describe_combat_round(
        self,
        combat_state: CombatState,
        last_action: AttackResult
    ) -> str:
        """
        1. Get combat participants
        2. Describe last action dramatically
        3. Describe current battlefield state
        4. Prompt for next action
        """
        pass
```

#### RAG Integration Strategy

**Document Categories to Query**:

1. **adventures_md** (7 docs):

   - Adventure structure and pacing
   - Encounter creation
   - Location/event-based design
   - Complications and twists

2. **dm_tools_core** (13 docs):

   - Chamber descriptions
   - Atmospheric details
   - Story beats
   - NPC generation

3. **dm_tools_themes** (9 docs):

   - Genre-specific flavor
   - Cultural elements
   - Thematic consistency

4. **monsters_md** (hundreds):

   - Monster stats and lore
   - Encounter difficulty
   - Tactical behavior

5. **spells_md** (hundreds):
   - Spell effects
   - Combat interactions
   - Environmental consequences

**Query Examples**:

```python
# Opening scene
query = "dramatic adventure opening hook tavern mysterious stranger"
docs = rag_search(query, top_k=5, filters=["adventures_md", "dm_tools_core"])

# Combat encounter
query = "balanced combat encounter level 3 party goblin ambush"
docs = rag_search(query, top_k=5, filters=["adventures_md", "monsters_md"])

# NPC dialogue
query = "noble suspicious guards city intrigue"
docs = rag_search(query, top_k=3, filters=["dm_tools_core", "dm_tools_themes"])
```

#### LLM Prompt Structure

```
You are an expert D&D Dungeon Master running a 5e campaign.

PARTY STATUS:
- Character 1: Level 3 Fighter (15/24 HP, AC 18)
- Character 2: Level 3 Wizard (18/18 HP, AC 12)

CURRENT LOCATION: Ancient ruins entrance

GAME STATE:
- Quest: Retrieve the lost amulet
- Recently: Defeated goblin scouts
- Inventory: Rusty key, healing potion

ADVENTURE GUIDANCE (from DMG):
{RAG context from adventures_md}

ATMOSPHERIC ELEMENTS (from DM Tools):
{RAG context from dm_tools_core}

TASK: Generate the next scene based on the party's choice to "investigate the locked door".

Requirements:
1. Describe the scene vividly (2-3 paragraphs)
2. Present 3-4 meaningful choices
3. Include potential for combat/skill checks where appropriate
4. Maintain narrative momentum

Format response as JSON:
{
  "description": "...",
  "choices": [
    {"id": 1, "text": "...", "type": "exploration"},
    {"id": 2, "text": "...", "type": "social"},
    {"id": 3, "text": "...", "type": "combat_trigger"}
  ],
  "detected_events": ["skill_check:perception:DC15"]
}
```

#### API Endpoints

```python
@router.post("/api/game/sessions/{session_id}/scene/start")
async def generate_opening_scene(...)

@router.post("/api/game/sessions/{session_id}/scene/choice")
async def process_player_choice(...)

@router.post("/api/game/sessions/{session_id}/npc/{npc_id}/dialogue")
async def generate_npc_dialogue(...)

@router.get("/api/game/sessions/{session_id}/scene/current")
async def get_current_scene(...)
```

#### Testing

- Opening scene generation quality
- RAG context relevance (manual review)
- Choice detection and parsing
- Combat trigger detection
- NPC personality consistency
- Scene continuity across multiple turns

---

## Phase 2: Chat Integration (Day 2)

### 2.1 DM Chat Handler

**File**: `backend/game/dm_chat_handler.py`
**Time**: 3-4 hours
**Priority**: HIGH

#### Requirements

```python
class DMChatHandler:
    """Integrate game systems with chat interface"""

    def __init__(
        self,
        db: Session,
        narrative_engine: NarrativeEngine,
        combat_engine: CombatEngine,
        dice_roller: DiceRoller
    ):
        self.db = db
        self.narrative = narrative_engine
        self.combat = combat_engine
        self.dice = dice_roller

    async def process_game_message(
        self,
        game_session: GameSession,
        user_message: str,
        chat_session: ChatSession
    ) -> DMResponse:
        """
        Main message processing pipeline

        1. Parse user intent:
           - Combat action: "I attack the goblin"
           - Skill check: "I search the room"
           - Exploration: "I open the door"
           - Dialogue: "I talk to the merchant"
           - OOC command: "/roll 2d6"

        2. Route to appropriate system:
           - Combat: combat_engine.process_attack()
           - Skill check: dice_roller.roll_ability_check()
           - Exploration: narrative_engine.process_player_choice()
           - Dialogue: narrative_engine.generate_npc_dialogue()
           - Command: execute_command()

        3. Generate DM response:
           - Combine system results
           - Add narrative flavor
           - Present next options

        4. Update game state
        5. Save to chat_messages
        6. Log to game_events
        """
        pass

    def parse_intent(self, message: str, game_context: Dict) -> Intent:
        """
        Use LLM to classify message intent

        Prompt: "Classify this D&D player action:
        Message: {message}
        Context: {in_combat, available_npcs, current_location}

        Return JSON: {
          'type': 'combat_action|skill_check|exploration|dialogue|command',
          'target': 'goblin|door|merchant|null',
          'action': 'attack|search|open|persuade|roll',
          'parameters': {...}
        }"
        """
        pass

    def execute_command(self, command: str, game_session: GameSession) -> str:
        """
        Handle OOC commands:
        /roll 2d6+3
        /hp 15
        /status
        /save
        /load
        /end
        """
        pass
```

#### Modified Chat Endpoint

```python
# backend/routers/chat.py

@router.post("/api/chat")
async def send_chat_message(
    message: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Enhanced to support game sessions

    If game_session_id provided:
        1. Route to DMChatHandler
        2. Process with game context
        3. Update game state
    Else:
        1. Use normal character chat
    """

    if message.game_session_id:
        game_session = db.query(GameSession).get(message.game_session_id)
        dm_handler = DMChatHandler(db, narrative, combat, dice)
        response = await dm_handler.process_game_message(
            game_session,
            message.content,
            chat_session
        )
    else:
        # Normal character chat (existing code)
        response = await character_chat(...)
```

#### Testing

- Intent classification accuracy
- Combat action routing
- Skill check parsing
- Command execution
- State persistence
- Error handling (invalid actions)

---

## Phase 3: Frontend Game Board (Day 3)

### 3.1 Game Session UI

**Files**:

- `frontend/src/pages/GameSession.jsx`
- `frontend/src/components/game/GameBoard.jsx`
- `frontend/src/components/game/PartyPanel.jsx`
- `frontend/src/components/game/SceneDisplay.jsx`
- `frontend/src/components/game/CombatTracker.jsx`
- `frontend/src/components/game/ActionPanel.jsx`
- `frontend/src/hooks/useGameSession.js`

**Time**: 6-8 hours
**Priority**: HIGH

#### GameBoard Layout

```jsx
<GameBoard>
  <Grid container spacing={2}>
    {/* Left Column - Party Status */}
    <Grid item xs={12} md={3}>
      <PartyPanel
        partyMembers={gameSession.party}
        onHpUpdate={handleHpUpdate}
        onConditionAdd={handleConditionAdd}
      />
    </Grid>

    {/* Center Column - Scene & Chat */}
    <Grid item xs={12} md={6}>
      <SceneDisplay scene={currentScene} combatState={activeCombat} />

      <ChatInterface
        messages={chatHistory}
        onSendMessage={handlePlayerAction}
        gameMode={true}
      />

      <ActionPanel
        choices={currentScene.choices}
        inCombat={!!activeCombat}
        onChoiceSelect={handleChoice}
      />
    </Grid>

    {/* Right Column - DM Tools */}
    <Grid item xs={12} md={3}>
      {activeCombat ? (
        <CombatTracker
          combat={activeCombat}
          onAttack={handleAttack}
          onEndTurn={handleNextTurn}
          onEndCombat={handleEndCombat}
        />
      ) : (
        <DiceRoller onRoll={handleDiceRoll} />
      )}

      <GameControls
        onSave={handleSaveGame}
        onLoad={handleLoadGame}
        onEndSession={handleEndSession}
      />
    </Grid>
  </Grid>
</GameBoard>
```

#### PartyPanel Component

```jsx
function PartyPanel({ partyMembers, onHpUpdate, onConditionAdd }) {
  return (
    <Paper>
      <Typography variant="h6">Party Status</Typography>
      {partyMembers.map((member) => (
        <Card key={member.id}>
          <CardContent>
            <Typography variant="subtitle1">{member.character.name}</Typography>
            <Typography variant="body2">
              Level {member.character.level} {member.character.class}
            </Typography>

            {/* HP Bar */}
            <Box sx={{ mt: 1 }}>
              <LinearProgress
                variant="determinate"
                value={(member.current_hp / member.max_hp) * 100}
                color={getHpColor(member.current_hp, member.max_hp)}
              />
              <Typography variant="caption">
                HP: {member.current_hp}/{member.max_hp}
                {member.temp_hp > 0 && ` (+${member.temp_hp} temp)`}
              </Typography>
            </Box>

            {/* AC and Conditions */}
            <Typography variant="caption">
              AC: {member.character.armor_class}
            </Typography>
            {member.conditions?.length > 0 && (
              <Box sx={{ mt: 1 }}>
                {member.conditions.map((cond) => (
                  <Chip key={cond} label={cond} size="small" color="warning" />
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Paper>
  );
}
```

#### SceneDisplay Component

```jsx
function SceneDisplay({ scene, combatState }) {
  if (combatState) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" color="error">
          Combat - Round {combatState.round_number}
        </Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>
          {scene.combat_description}
        </Typography>
        <Typography variant="caption" sx={{ mt: 1 }}>
          Current Turn: {combatState.current_turn.name}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6">{scene.location}</Typography>
      <Typography variant="body1" sx={{ mt: 2, whiteSpace: "pre-wrap" }}>
        {scene.description}
      </Typography>
    </Paper>
  );
}
```

#### CombatTracker Component

```jsx
function CombatTracker({ combat, onAttack, onEndTurn, onEndCombat }) {
  return (
    <Paper>
      <Typography variant="h6">Initiative Order</Typography>
      <List>
        {combat.turn_order.map((participant, index) => (
          <ListItem
            key={participant.id}
            selected={index === combat.current_turn}
          >
            <ListItemText
              primary={participant.name}
              secondary={`HP: ${participant.current_hp}/${participant.max_hp} | AC: ${participant.ac}`}
            />
            <Typography variant="body2">{participant.initiative}</Typography>
          </ListItem>
        ))}
      </List>

      <Box sx={{ mt: 2 }}>
        <Button variant="contained" onClick={onAttack} fullWidth>
          Attack
        </Button>
        <Button variant="outlined" onClick={onEndTurn} fullWidth sx={{ mt: 1 }}>
          End Turn
        </Button>
      </Box>
    </Paper>
  );
}
```

#### useGameSession Hook

```javascript
function useGameSession(sessionId) {
  const [gameSession, setGameSession] = useState(null);
  const [currentScene, setCurrentScene] = useState(null);
  const [activeCombat, setActiveCombat] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load game session
  useEffect(() => {
    async function loadSession() {
      const response = await fetch(`/api/game/sessions/${sessionId}`);
      const data = await response.json();
      setGameSession(data);
      setCurrentScene(data.game_state?.current_scene);
    }
    loadSession();
  }, [sessionId]);

  // Poll for combat updates
  useEffect(() => {
    if (!activeCombat) return;

    const interval = setInterval(async () => {
      const response = await fetch(
        `/api/game/sessions/${sessionId}/combat/${activeCombat.id}`
      );
      const data = await response.json();
      setActiveCombat(data);
    }, 2000);

    return () => clearInterval(interval);
  }, [activeCombat, sessionId]);

  const sendMessage = async (message) => {
    setLoading(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: message,
          chat_session_id: gameSession.chat_session_id,
          game_session_id: sessionId,
        }),
      });

      const data = await response.json();
      setChatHistory((prev) => [...prev, data]);

      // Update scene if changed
      if (data.scene) {
        setCurrentScene(data.scene);
      }

      // Update combat if started
      if (data.combat) {
        setActiveCombat(data.combat);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateHp = async (characterId, newHp) => {
    await fetch(`/api/game/sessions/${sessionId}/party/${characterId}/hp`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ current_hp: newHp }),
    });
    // Reload session
    loadSession();
  };

  return {
    gameSession,
    currentScene,
    activeCombat,
    chatHistory,
    loading,
    error,
    sendMessage,
    updateHp,
  };
}
```

#### Testing

- Component rendering (Vitest)
- State management
- Combat UI updates
- HP bar visualization
- Choice selection
- Mobile responsiveness

---

## Phase 4: End-to-End Testing & Polish (Day 4)

### 4.1 E2E Test Script

**File**: `scripts/test_game_session_e2e.py`
**Time**: 2-3 hours

#### Test Flow

```python
async def test_full_game_session():
    """
    Complete AI DM session from start to finish
    """

    # 1. Create chat session
    chat_session = create_chat_session()

    # 2. Create game session
    game_session = await api.post('/api/game/sessions', {
        'campaign_name': 'Test Campaign',
        'chat_session_id': chat_session.id,
        'party_level': 3
    })

    # 3. Add 2 characters to party
    fighter = create_character(name='Garrick', class_='Fighter', level=3)
    wizard = create_character(name='Elara', class_='Wizard', level=3)

    await api.post(f'/api/game/sessions/{game_session.id}/party', {
        'character_id': fighter.id
    })
    await api.post(f'/api/game/sessions/{game_session.id}/party', {
        'character_id': wizard.id
    })

    # 4. Generate opening scene
    scene = await api.post(
        f'/api/game/sessions/{game_session.id}/scene/start'
    )
    assert len(scene['choices']) >= 3
    print(f"Opening: {scene['description']}")

    # 5. Make exploration choice
    choice_response = await api.post(
        f'/api/game/sessions/{game_session.id}/scene/choice',
        {'choice_id': scene['choices'][0]['id']}
    )
    print(f"Exploration: {choice_response['description']}")

    # 6. Trigger combat
    combat_choice = next(
        c for c in choice_response['choices']
        if c['type'] == 'combat_trigger'
    )
    combat_scene = await api.post(
        f'/api/game/sessions/{game_session.id}/scene/choice',
        {'choice_id': combat_choice['id']}
    )

    combat = combat_scene['combat']
    assert combat is not None
    assert len(combat['turn_order']) > 0
    print(f"Combat started! Initiative: {combat['turn_order']}")

    # 7. Execute attack
    attacker = combat['turn_order'][0]
    target = combat['turn_order'][1]

    attack_result = await api.post(
        f'/api/game/sessions/{game_session.id}/combat/{combat['id']}/attack',
        {
            'attacker_id': attacker['id'],
            'target_id': target['id'],
            'weapon_damage': '1d8+3',
            'attack_bonus': 5,
            'target_ac': target['ac']
        }
    )

    if attack_result['hit']:
        print(f"HIT! {attack_result['damage']} damage")
        assert target['current_hp'] < target['max_hp']
    else:
        print("MISS!")

    # 8. Complete combat round
    await api.post(
        f'/api/game/sessions/{game_session.id}/combat/{combat['id']}/next-turn'
    )

    # 9. End combat
    await api.post(
        f'/api/game/sessions/{game_session.id}/combat/{combat['id']}/end',
        {'outcome': 'victory'}
    )

    # 10. Continue exploration
    next_scene = await api.post(
        f'/api/game/sessions/{game_session.id}/scene/choice',
        {'choice_id': 1}
    )
    print(f"Post-combat: {next_scene['description']}")

    # 11. Save game state
    save_response = await api.put(
        f'/api/game/sessions/{game_session.id}',
        {'game_state': {'checkpoint': 'after_first_combat'}}
    )
    assert save_response['game_state']['checkpoint'] == 'after_first_combat'

    # 12. Verify event log
    events = await api.get(
        f'/api/game/sessions/{game_session.id}/events'
    )
    assert len(events) >= 5  # Start, choices, combat, attacks, end

    print("✅ Full session test PASSED!")
    print(f"Total events logged: {len(events)}")
    print(f"Final party HP:")

    party = await api.get(f'/api/game/sessions/{game_session.id}/party')
    for member in party:
        print(f"  {member['character']['name']}: {member['current_hp']}/{member['max_hp']} HP")
```

#### Test Coverage

- Session creation and lifecycle
- Party management
- Scene generation quality
- Combat mechanics
- Dice rolling
- State persistence
- Event logging
- HP tracking
- RAG integration (manual review of scenes)

---

### 4.2 Documentation

**Files to Create/Update**:

1. **AI_DM_USER_GUIDE.md**

   - How to start a game session
   - Party setup
   - Making choices
   - Combat actions
   - Commands reference
   - Saving/loading games

2. **AI_DM_TECHNICAL_REFERENCE.md**

   - API endpoints documentation
   - Database schema
   - RAG integration patterns
   - LLM prompt engineering
   - Extending the system

3. **AI_DM_TROUBLESHOOTING.md**
   - Common issues
   - Debug mode
   - Log analysis
   - Performance optimization

---

## Phase 5: Advanced Features (Future)

### 5.1 Character Progression

- XP tracking and level-up
- Skill improvements
- Feat selection
- Spell learning

### 5.2 Inventory Management

- Loot generation
- Equipment tracking
- Shop interfaces
- Crafting system

### 5.3 Quest System

- Quest creation and tracking
- Objectives and rewards
- Branching quest lines
- Quest journal UI

### 5.4 Map & Location System

- Interactive maps
- Fog of war
- Location discovery
- Fast travel

### 5.5 Multiplayer Support

- Multiple players in one session
- Turn coordination
- Player-to-player interaction
- DM controls for human DMs

---

## Success Criteria

### Minimum Viable Session (MVP)

A successful MVP session includes:

1. ✅ Party creation (2+ characters)
2. ✅ Opening scene generation (with RAG context)
3. ✅ 3+ exploration choices
4. ✅ Combat encounter:
   - Initiative rolling
   - 2+ rounds of combat
   - Attack resolution
   - HP tracking
   - Victory/defeat determination
5. ✅ Post-combat exploration
6. ✅ Save/load game state
7. ✅ Complete event log

### Quality Metrics

- **Scene Quality**: RAG relevance scores > 0.4
- **Response Time**: Scene generation < 5 seconds
- **Combat Accuracy**: 100% mechanical correctness
- **State Consistency**: No data loss on save/load
- **UI Responsiveness**: < 100ms for user actions

### User Experience

- Clear narrative descriptions
- Meaningful player choices
- Tactical combat decisions
- Seamless system integration
- Mobile-friendly interface

---

## Implementation Checklist

### Day 1: Core Mechanics

- [ ] Dice roller (1h)
  - [ ] DiceRoller class
  - [ ] API endpoint
  - [ ] Unit tests
- [ ] Combat system (4h)
  - [ ] CombatEngine class
  - [ ] API endpoints (5 endpoints)
  - [ ] Combat flow tests
- [ ] Narrative engine (4h)
  - [ ] NarrativeEngine class
  - [ ] RAG integration
  - [ ] Scene generation
  - [ ] API endpoints

### Day 2: Chat Integration

- [ ] DM chat handler (4h)
  - [ ] DMChatHandler class
  - [ ] Intent parsing
  - [ ] Command execution
  - [ ] Modified chat endpoint
  - [ ] Integration tests

### Day 3: Frontend

- [ ] Game board UI (8h)
  - [ ] GameSession page
  - [ ] PartyPanel component
  - [ ] SceneDisplay component
  - [ ] CombatTracker component
  - [ ] ActionPanel component
  - [ ] useGameSession hook
  - [ ] Component tests

### Day 4: Testing & Polish

- [ ] E2E testing (3h)
  - [ ] Full session test script
  - [ ] Coverage validation
  - [ ] Performance testing
- [ ] Documentation (2h)
  - [ ] User guide
  - [ ] Technical reference
  - [ ] Troubleshooting guide
- [ ] Bug fixes and polish (3h)

---

## Risk Mitigation

### Technical Risks

1. **LLM Response Quality**

   - Mitigation: Use temperature=0.7, provide strong RAG context
   - Fallback: Template-based scenes for common situations

2. **RAG Relevance**

   - Mitigation: Test queries manually, tune similarity thresholds
   - Fallback: Broader queries if no results above threshold

3. **Combat Complexity**

   - Mitigation: Start with basic attack/damage, add features incrementally
   - Fallback: Simplified combat for MVP

4. **State Management**
   - Mitigation: Comprehensive event logging, frequent saves
   - Fallback: State reconstruction from event log

### Performance Risks

1. **Scene Generation Latency**

   - Mitigation: Async processing, loading indicators
   - Target: < 5 seconds per scene

2. **RAG Query Speed**

   - Mitigation: Pre-computed embeddings, indexed searches
   - Target: < 500ms per query

3. **Frontend Responsiveness**
   - Mitigation: Optimistic UI updates, WebSocket for real-time
   - Target: < 100ms UI feedback

---

## Next Steps After Completion

1. **Playtesting**: Run 5+ full sessions with different party compositions
2. **Feedback Collection**: Gather user input on narrative quality and combat flow
3. **Iteration**: Refine prompts, RAG queries, and UI based on feedback
4. **Advanced Features**: Quest system, inventory, character progression
5. **Multiplayer**: Enable multiple players in one session
6. **AI Enhancements**: Fine-tune LLM on D&D transcripts, train custom models

---

## Conclusion

This implementation plan provides a clear path from the current backend foundation to a fully playable AI DM system in 3-4 days. The phased approach ensures each component is tested and validated before moving to the next, minimizing risk and maximizing quality.

**Ready to begin implementation!**
