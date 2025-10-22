# 🎲 D&D MCP Integration Implementation Plan

**Date:** January 2025  
**Goal:** Integrate D&D 5e API (via MCP) with AI Dungeon Master system  
**Status:** Planning Phase  
**Estimated Time:** 4-6 hours

---

## 📋 Overview

Integrate the D&D MCP server to provide real-time access to official D&D 5e content:

- **Spells**: All official spells with full details
- **Monsters**: Complete monster stat blocks
- **Equipment**: Weapons, armor, adventuring gear
- **Magic Items**: All magic items with properties
- **Classes/Races**: Character options
- **Features**: Class features and abilities

**Key Innovation:** Bridge MCP server (Node.js) with FastAPI backend (Python) for seamless integration.

---

## 🎯 Phase 1: DnD MCP Wrapper Service (2 hours)

### 1.1 Create Python MCP Client

**File:** `backend/services/dnd_mcp_client.py`

```python
"""
D&D MCP Client - Python wrapper for Node.js MCP server

This service communicates with the D&D MCP server to fetch official
D&D 5e content and format it for use in our AI DM system.

Architecture:
- Node.js MCP server runs as separate process
- Python client sends HTTP requests to proxy endpoint
- Results cached in Redis/memory for performance
- Fallback to existing RAG system if MCP unavailable
"""

class DndMcpClient:
    def __init__(self, mcp_endpoint="http://localhost:3001"):
        """Initialize MCP client with endpoint"""

    async def search_all(self, query: str) -> dict:
        """Search across all D&D categories"""

    async def get_spell(self, spell_name: str) -> dict:
        """Get detailed spell information"""

    async def get_monster(self, monster_name: str) -> dict:
        """Get monster stat block"""

    async def get_equipment(self, item_name: str) -> dict:
        """Get equipment details"""

    async def get_magic_item(self, item_name: str) -> dict:
        """Get magic item properties"""

    async def filter_spells_by_level(self, min_level: int, max_level: int) -> list:
        """Get spells within level range"""

    async def find_monsters_by_cr(self, min_cr: float, max_cr: float) -> list:
        """Get monsters within CR range"""
```

**Key Features:**

- Async HTTP client (aiohttp)
- Response caching (TTL: 1 hour)
- Error handling with fallback
- Type validation (Pydantic models)
- Retry logic for transient failures

### 1.2 Create MCP Proxy Server

**File:** `scripts/mcp_proxy_server.js`

```javascript
/**
 * MCP Proxy Server
 *
 * Bridges Node.js MCP server with Python FastAPI backend.
 * Accepts HTTP requests and forwards to MCP stdio server.
 */

const express = require("express");
const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const {
  StdioClientTransport,
} = require("@modelcontextprotocol/sdk/client/stdio.js");

const app = express();
const PORT = 3001;

// Initialize MCP client
let mcpClient = null;

async function initializeMCP() {
  const transport = new StdioClientTransport({
    command: "uv",
    args: ["--directory", "E:\\dnd-mcp", "run", "dnd_mcp_server.py"],
  });

  mcpClient = new Client(
    {
      name: "dnd-proxy",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await mcpClient.connect(transport);
  console.log("MCP client connected");
}

// Endpoint: Search all categories
app.post("/api/search", async (req, res) => {
  try {
    const { query } = req.body;
    const result = await mcpClient.callTool("search_all_categories", { query });
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint: Get spell details
app.get("/api/spell/:name", async (req, res) => {
  // Implementation
});

// Additional endpoints...

initializeMCP().then(() => {
  app.listen(PORT, () => {
    console.log(`MCP Proxy listening on port ${PORT}`);
  });
});
```

### 1.3 Pydantic Models for D&D Content

**File:** `backend/models/dnd_models.py`

```python
from pydantic import BaseModel
from typing import List, Optional

class Spell(BaseModel):
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: List[str]
    duration: str
    description: str
    higher_levels: Optional[str] = None
    classes: List[str]

class Monster(BaseModel):
    name: str
    size: str
    type: str
    alignment: str
    armor_class: int
    hit_points: int
    hit_dice: str
    speed: dict
    abilities: dict  # STR, DEX, CON, INT, WIS, CHA
    challenge_rating: float
    actions: List[dict]
    special_abilities: List[dict]

class MagicItem(BaseModel):
    name: str
    rarity: str
    type: str
    requires_attunement: bool
    description: str
    properties: dict
```

---

## 🎯 Phase 2: RAG Enhancement with D&D Knowledge (1 hour)

### 2.1 Create D&D Knowledge Markdown Files

**Directory:** `documents/reference/dnd_mechanics/`

Create these files:

1. `combat_rules.md` - Action economy, attacks, conditions
2. `spellcasting_rules.md` - Spell slots, concentration, components
3. `rest_rules.md` - Short/long rest mechanics
4. `adventure_templates.md` - Five-room dungeon, quest hooks
5. `npc_archetypes.md` - Personality templates
6. `random_encounters.md` - Tables by environment
7. `environmental_hazards.md` - Traps, terrain effects
8. `treasure_tables.md` - Loot by CR
9. `condition_effects.md` - All D&D conditions
10. `scene_description_guide.md` - DM narration tips

### 2.2 Ingest Script

**File:** `scripts/ingest_dnd_mechanics.py`

```python
"""
Ingest D&D mechanics documents into RAG system.

This script:
1. Reads markdown files from documents/reference/dnd_mechanics/
2. Chunks content into semantic units
3. Generates embeddings
4. Stores in ChromaDB under 'dnd_mechanics' collection
"""

import chromadb
from pathlib import Path

def ingest_dnd_mechanics():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("dnd_mechanics")

    mechanics_dir = Path("documents/reference/dnd_mechanics")

    for md_file in mechanics_dir.glob("*.md"):
        content = md_file.read_text()
        # Chunk and ingest
        # ...
```

---

## 🎯 Phase 3: Narrative Engine Enhancement (1.5 hours)

### 3.1 Integrate MCP Client

**File:** `backend/game/narrative_engine.py` (modify)

```python
from backend.services.dnd_mcp_client import DndMcpClient

class NarrativeEngine:
    def __init__(self, db: Session):
        self.db = db
        self.dnd_mcp = DndMcpClient()  # NEW

    async def generate_opening_scene(self, game_session, adventure_type, location):
        # Query MCP for relevant monsters/items for this location
        monsters = await self.dnd_mcp.find_monsters_by_cr(
            min_cr=game_session.party_level - 2,
            max_cr=game_session.party_level + 2
        )

        # Get environment-appropriate spells
        spells = await self.dnd_mcp.filter_spells_by_level(
            min_level=0,
            max_level=3
        )

        # Build context with official D&D content
        context = f"""
        Location: {location}
        Appropriate monsters: {monsters}
        Available magic: {spells}
        """

        # Generate scene with LLM using official content
        # ...
```

### 3.2 Add Spell Lookup for Combat

```python
async def process_spell_cast(self, spell_name: str):
    """Look up spell details from MCP and apply effects"""
    spell = await self.dnd_mcp.get_spell(spell_name)

    if spell:
        # Apply spell effects based on official rules
        damage_dice = spell.get('damage', {}).get('damage_at_slot_level', {})
        save_dc = spell.get('dc', {}).get('dc_type', {}).get('index')
        # ...
```

### 3.3 Monster Stat Block Integration

```python
async def spawn_monster(self, monster_name: str, encounter_difficulty: str):
    """Spawn monster with official stat block"""
    monster = await self.dnd_mcp.get_monster(monster_name)

    combatant = {
        'name': monster['name'],
        'hp': monster['hit_points'],
        'max_hp': monster['hit_points'],
        'ac': monster['armor_class'],
        'initiative_bonus': self._calculate_dex_bonus(monster['dexterity']),
        'abilities': monster['abilities'],
        'actions': monster['actions'],
        'special_abilities': monster.get('special_abilities', [])
    }

    return combatant
```

---

## 🎯 Phase 4: DM Chat Handler Enhancement (1 hour)

### 4.1 Add D&D Content Commands

**File:** `backend/game/dm_chat_handler.py` (modify)

```python
async def _handle_command(self, game_session, message):
    """Enhanced command handling with D&D lookups"""

    command = message.split()[0].lower()
    args = ' '.join(message.split()[1:])

    if command == '/spell':
        # Look up spell in MCP
        spell = await self.dnd_mcp.get_spell(args)
        return self._format_spell_info(spell)

    elif command == '/monster':
        # Look up monster in MCP
        monster = await self.dnd_mcp.get_monster(args)
        return self._format_monster_stat_block(monster)

    elif command == '/item':
        # Look up item in MCP
        item = await self.dnd_mcp.get_magic_item(args)
        return self._format_item_info(item)

    # ... existing commands
```

### 4.2 Context-Aware Entity Recognition

```python
async def _parse_intent(self, game_session, user_message):
    """Enhanced intent parsing with D&D entity recognition"""

    # Check if message mentions spell names
    spell_mentions = await self._find_spell_mentions(user_message)

    # Check if message mentions monsters
    monster_mentions = await self._find_monster_mentions(user_message)

    # Enhance LLM prompt with official content
    context = {
        'spells': spell_mentions,
        'monsters': monster_mentions,
        'available_actions': self._get_available_actions(game_session)
    }

    # Pass to LLM for intent classification with D&D context
    # ...
```

---

## 🎯 Phase 5: API Endpoints for D&D Content (0.5 hours)

### 5.1 New Router

**File:** `backend/routers/dnd_content.py`

```python
"""
D&D Content Router - Expose MCP content via REST API
"""

from fastapi import APIRouter, Depends
from backend.services.dnd_mcp_client import DndMcpClient

router = APIRouter(prefix="/api/dnd", tags=["dnd-content"])

@router.get("/spell/{spell_name}")
async def get_spell(spell_name: str):
    """Get spell details from D&D 5e API"""
    client = DndMcpClient()
    spell = await client.get_spell(spell_name)
    return spell

@router.get("/monster/{monster_name}")
async def get_monster(monster_name: str):
    """Get monster stat block"""
    client = DndMcpClient()
    monster = await client.get_monster(monster_name)
    return monster

@router.get("/spells")
async def list_spells(
    min_level: int = 0,
    max_level: int = 9,
    school: str = None
):
    """List spells with filters"""
    client = DndMcpClient()
    spells = await client.filter_spells_by_level(min_level, max_level)

    if school:
        spells = [s for s in spells if s['school'] == school]

    return spells

@router.get("/monsters")
async def list_monsters(min_cr: float = 0, max_cr: float = 30):
    """List monsters by CR"""
    client = DndMcpClient()
    monsters = await client.find_monsters_by_cr(min_cr, max_cr)
    return monsters

@router.post("/search")
async def search_dnd_content(query: str):
    """Search all D&D content"""
    client = DndMcpClient()
    results = await client.search_all(query)
    return results
```

### 5.2 Register Router

**File:** `backend/main.py` (modify)

```python
from backend.routers import dnd_content

app.include_router(dnd_content.router)
```

---

## 🎯 Phase 6: Frontend D&D Content Display (1 hour)

### 6.1 Create D&D Content Components

**Files:**

- `frontend/src/components/dnd/SpellCard.jsx` - Display spell details
- `frontend/src/components/dnd/MonsterStatBlock.jsx` - Display monster stats
- `frontend/src/components/dnd/ItemCard.jsx` - Display magic items
- `frontend/src/components/dnd/DndSearch.jsx` - Search D&D content

### 6.2 Integrate into GameSession

Add D&D content panel:

```jsx
<Grid item xs={12} md={4}>
  <DndSearch onSelect={handleDndContentSelect} />

  {selectedSpell && <SpellCard spell={selectedSpell} />}
  {selectedMonster && <MonsterStatBlock monster={selectedMonster} />}
</Grid>
```

### 6.3 Add Quick Reference Buttons

```jsx
<Box sx={{ display: "flex", gap: 1 }}>
  <Button onClick={() => openSpellList()}>📚 Spells</Button>
  <Button onClick={() => openMonsterList()}>👹 Monsters</Button>
  <Button onClick={() => openItemList()}>✨ Items</Button>
</Box>
```

---

## 📊 Testing Plan

### Unit Tests

**File:** `backend/tests/test_dnd_mcp_client.py`

```python
import pytest
from backend.services.dnd_mcp_client import DndMcpClient

@pytest.mark.asyncio
async def test_search_spells():
    client = DndMcpClient()
    results = await client.search_all("fireball")
    assert 'spells' in results
    assert any(s['name'] == 'Fireball' for s in results['spells'])

@pytest.mark.asyncio
async def test_get_spell_details():
    client = DndMcpClient()
    spell = await client.get_spell("fireball")
    assert spell['name'] == 'Fireball'
    assert spell['level'] == 3
    assert spell['school'] == 'evocation'

@pytest.mark.asyncio
async def test_filter_spells_by_level():
    client = DndMcpClient()
    spells = await client.filter_spells_by_level(0, 2)
    assert all(s['level'] <= 2 for s in spells)
```

### Integration Tests

**File:** `backend/tests/test_narrative_with_mcp.py`

```python
@pytest.mark.asyncio
async def test_scene_generation_with_monsters():
    engine = NarrativeEngine(db)
    scene = await engine.generate_opening_scene(
        game_session,
        adventure_type="dungeon",
        location="Ancient Ruins"
    )

    # Should include appropriate monsters from MCP
    assert scene.description
    assert len(scene.choices) > 0
```

### E2E Tests

**File:** `scripts/test_mcp_integration_e2e.py`

```python
"""
E2E test: Full game session with D&D MCP integration

Test flow:
1. Start game session
2. Generate scene (should fetch monsters from MCP)
3. Player casts spell (should look up spell in MCP)
4. Enter combat with monster (should use official stat block)
5. Verify all D&D content is accurate
"""
```

---

## 🚀 Deployment Checklist

### Backend

- [ ] Install Node.js dependencies for MCP proxy
- [ ] Start MCP proxy server on port 3001
- [ ] Configure Python backend to use proxy endpoint
- [ ] Add error handling for MCP unavailability
- [ ] Set up response caching (Redis or in-memory)
- [ ] Test all MCP client methods
- [ ] Verify fallback to RAG when MCP down

### Frontend

- [ ] Create D&D content components
- [ ] Add search interface
- [ ] Test spell/monster/item displays
- [ ] Add loading states
- [ ] Add error handling

### Documentation

- [ ] Document MCP setup process
- [ ] Add examples of using D&D content
- [ ] Update API documentation
- [ ] Create user guide for D&D features

---

## 📝 Implementation Order

### Day 1 (Morning - 3 hours)

1. ✅ Fix DnD MCP server installation
2. ⏳ Create MCP proxy server (scripts/mcp_proxy_server.js)
3. ⏳ Create Python MCP client (backend/services/dnd_mcp_client.py)
4. ⏳ Test basic connectivity

### Day 1 (Afternoon - 3 hours)

5. ⏳ Create Pydantic models for D&D content
6. ⏳ Create D&D knowledge markdown files
7. ⏳ Ingest markdown files into RAG
8. ⏳ Test RAG queries with new content

### Day 2 (Morning - 3 hours)

9. ⏳ Integrate MCP client into narrative engine
10. ⏳ Add spell lookup for combat
11. ⏳ Add monster spawning with stat blocks
12. ⏳ Test scene generation with MCP content

### Day 2 (Afternoon - 2 hours)

13. ⏳ Enhance DM chat handler with /spell, /monster, /item commands
14. ⏳ Add context-aware entity recognition
15. ⏳ Create D&D content API endpoints
16. ⏳ Test all endpoints

### Day 3 (All day - 4 hours)

17. ⏳ Create frontend D&D content components
18. ⏳ Integrate into GameSession page
19. ⏳ Add quick reference buttons
20. ⏳ Write E2E tests
21. ⏳ Update documentation
22. ⏳ Final testing and polish

**Total Estimated Time:** 12 hours over 3 days

---

## 🎯 Success Criteria

### Must Have (MVP)

- [x] DnD MCP server running and accessible
- [ ] Python MCP client working
- [ ] Spells searchable via API
- [ ] Monsters searchable via API
- [ ] Scene generation uses official monsters
- [ ] /spell command shows accurate spell info

### Nice to Have

- [ ] All 10 D&D mechanics markdown files in RAG
- [ ] Frontend spell/monster cards
- [ ] Quick reference buttons
- [ ] Auto-suggest spell/monster names
- [ ] Cache for frequently accessed content

### Stretch Goals

- [ ] Character sheet integration (use official race/class data)
- [ ] Automatic spell slot tracking
- [ ] Initiative tracker with official monster stats
- [ ] Loot generator using official treasure tables
- [ ] NPC generator using official races/classes

---

## 🔧 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ GameSession │  │ DndSearch    │  │ SpellCard    │       │
│  │  Page       │  │ Component    │  │ Component    │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routers                                              │   │
│  │  - game.py (game endpoints)                          │   │
│  │  - chat.py (chat + TTS)                              │   │
│  │  - dnd_content.py (NEW - D&D API)                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Game Systems                                         │   │
│  │  - narrative_engine.py (+ MCP integration)           │   │
│  │  - dm_chat_handler.py (+ D&D commands)               │   │
│  │  - combat_engine.py (+ official stat blocks)         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Services                                             │   │
│  │  - dnd_mcp_client.py (NEW - Python MCP wrapper)      │   │
│  │  - tts_service.py (OrpheusTTS)                       │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│               MCP Proxy Server (Node.js)                     │
│  - Express HTTP server on port 3001                          │
│  - Translates HTTP → MCP stdio calls                         │
│  - Handles request/response conversion                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ stdio
┌───────────────────────────▼─────────────────────────────────┐
│              DnD MCP Server (Python)                         │
│  - Connects to D&D 5e API (dnd5eapi.co)                     │
│  - Tools: search, get_spell, get_monster, filter, etc.      │
│  - Official D&D content with attribution                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Innovations

1. **Hybrid Knowledge System**

   - MCP provides real-time official content
   - RAG provides DM guidance and mechanics
   - Combined for accurate, rich responses

2. **Seamless Integration**

   - Python backend talks to Node.js MCP via HTTP proxy
   - No need to rewrite MCP server in Python
   - Maintains type safety with Pydantic models

3. **Smart Fallback**

   - If MCP unavailable, use RAG system
   - Graceful degradation
   - Error messages guide users

4. **Context-Aware DM**

   - Narrative engine uses appropriate monsters for party level
   - Combat uses official stat blocks
   - Spell effects follow official rules

5. **Player Tools**
   - Quick lookup of spells during game
   - Monster reference without DM
   - Item descriptions on demand

---

## 🎓 Learning Resources

### MCP Documentation

- https://modelcontextprotocol.io/docs
- https://github.com/modelcontextprotocol/servers

### D&D 5e API

- https://www.dnd5eapi.co/
- https://www.dnd5eapi.co/docs/

### Our Implementation

- `E:\dnd-mcp` - MCP server location
- `.vscode/mcp.json` - MCP configuration
- This file - Complete implementation plan

---

**Status:** Ready to implement! Let's build this! 🚀🎲

**Next Step:** Create MCP proxy server (scripts/mcp_proxy_server.js)
