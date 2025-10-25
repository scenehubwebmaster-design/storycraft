# Campaign Journal & Enhanced NPC System

## Overview

The Campaign Journal is a visual logging and reference system that enhances the D&D campaign experience by tracking NPCs, quests, decisions, and locations. It integrates with the checkpoint system to provide rich context for both players and the DM AI.

## Features

### 1. **NPC Codex with Portraits**

- Batch-generated portraits stored as static files (not base64)
- Importance ratings (1-5 stars)
- Relationship tracking (-100 to +100)
- First met location/session tracking
- Tags for categorization (quest_giver, merchant, villain, etc.)
- Quest associations

### 2. **Journal Timeline**

- Chronological event log with filtering
- Entry types: npc_met, location_visited, quest_update, decision, combat, loot, rest
- Importance-based filtering
- Tags and location tracking
- Links to specific NPCs/quests

### 3. **Quest Log**

- Active vs completed quest separation
- Progress tracking
- Reward display
- Visual status indicators

### 4. **Location Tracker**

- Visited locations registry
- Integration with journal entries
- Quick reference for world exploration

## Architecture

### Database Schema

**NPCs Table (Enhanced)**:

- `portrait_path`: File path (e.g., "npc_portraits/merchant_elara_123.png")
- `portrait_prompt`: SD prompt used for generation
- `first_met_location`: Where party first encountered NPC
- `first_met_session`: Chat session ID of first meeting
- `last_interaction`: Timestamp of last dialogue
- `importance`: 1-5 rating for journal filtering
- `tags`: JSON array ["quest_giver", "merchant", etc.]
- `quests_related`: JSON array of quest IDs

**JournalEntry Table (New)**:

```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL,
    chat_session_id INTEGER,
    chat_message_id INTEGER,
    entry_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    npc_id INTEGER,
    quest_id INTEGER,
    location_name VARCHAR(255),
    importance INTEGER DEFAULT 3,
    tags TEXT,  -- JSON
    involved_characters TEXT,  -- JSON
    game_session_number INTEGER,
    chroma_doc_id VARCHAR(255),  -- For RAG integration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Static File Storage

**Portrait Storage**:

- Location: `backend/static/npc_portraits/`
- Format: `{sanitized_name}_{npc_id}_{timestamp}.png`
- Size: 512x768 (portrait orientation)
- Served via: `http://localhost:8000/static/npc_portraits/{filename}`

**Benefits**:

- Fast loading (no base64 decoding)
- Browser caching
- Reduced database size
- Easy backup/management

## Usage

### 1. Database Migration

```bash
cd backend
python migrate_add_journal_and_npc_enhancements.py
```

This adds:

- New NPC columns
- JournalEntry table
- Performance indexes

### 2. Batch Portrait Generation

**Dry run** (see what will be generated):

```bash
python batch_generate_npc_portraits.py --dry-run
```

**Generate all missing portraits**:

```bash
python batch_generate_npc_portraits.py
```

**Generate for specific campaign**:

```bash
python batch_generate_npc_portraits.py --campaign-id 1
```

**Limit generation**:

```bash
python batch_generate_npc_portraits.py --limit 10
```

**Force regeneration** (even if portrait exists):

```bash
python batch_generate_npc_portraits.py --force
```

### 3. Frontend Integration

Add Journal button to DMChat:

```jsx
import CampaignJournal from '../components/CampaignJournal';

// In component state
const [journalOpen, setJournalOpen] = useState(false);

// In render
<IconButton onClick={() => setJournalOpen(true)}>
  <MenuBook />
</IconButton>

<CampaignJournal
  campaignId={activeCampaign?.id}
  open={journalOpen}
  onClose={() => setJournalOpen(false)}
/>
```

## Checkpoint Integration

### Enhanced Checkpoint Previews

Checkpoints now show rich metadata from journal:

```json
{
  "checkpoint_id": 123,
  "title": "Defended Emberfall Tavern",
  "summary": "AI-generated narrative summary",
  "journal_highlights": {
    "npcs_met": ["Elara the Merchant", "Captain Greaves"],
    "locations_visited": ["Emberfall Tavern", "Dark Forest"],
    "quests_updated": ["Save the Village"],
    "key_decisions": ["Chose to fight rather than flee"]
  }
}
```

### Visual Load Points

When selecting a checkpoint to restore:

1. Show NPC portraits grid
2. Display active quests with progress
3. Highlight key decisions made
4. Show location history

This creates a "save point" feel similar to video games.

## RAG Integration

### Journal Entries in Vector DB

Each journal entry can be stored in ChromaDB for DM AI context:

**Storage**:

```python
# In checkpoint creation
journal_summary = create_journal_summary(campaign_id)
chroma_doc_id = store_in_chroma(
    text=journal_summary,
    metadata={
        "campaign_id": campaign_id,
        "type": "journal",
        "importance": calculate_importance(entries)
    }
)
```

**Retrieval**:

```python
# When DM generates response
journal_context = retrieve_from_chroma(
    query=user_message,
    filter={"campaign_id": campaign_id, "type": "journal"},
    n_results=5
)
```

**Benefits**:

- DM remembers past NPCs, decisions, and events
- Context-aware responses ("Remember when you met Elara?")
- Consistent character portrayal
- Long-term campaign continuity

### Structured Metadata (Alternative)

Instead of RAG, journal data can be passed directly to DM AI as structured JSON:

```python
def get_campaign_context(campaign_id):
    return {
        "npcs": get_important_npcs(campaign_id, importance >= 3),
        "active_quests": get_active_quests(campaign_id),
        "recent_locations": get_recent_locations(campaign_id, limit=5),
        "key_decisions": get_recent_decisions(campaign_id, importance >= 4)
    }
```

**Recommendation**: Use RAG for large campaigns (>50 entries), structured metadata for smaller ones.

## API Endpoints (To Be Implemented)

```
GET  /api/campaigns/{campaign_id}/journal/entries
GET  /api/campaigns/{campaign_id}/journal/entries?type=npc_met
GET  /api/campaigns/{campaign_id}/journal/entries?importance>=4
POST /api/campaigns/{campaign_id}/journal/entries

GET  /api/campaigns/{campaign_id}/npcs
GET  /api/campaigns/{campaign_id}/npcs/{npc_id}
PUT  /api/campaigns/{campaign_id}/npcs/{npc_id}

GET  /api/campaigns/{campaign_id}/quests
POST /api/campaigns/{campaign_id}/quests
PUT  /api/campaigns/{campaign_id}/quests/{quest_id}

GET  /static/npc_portraits/{filename}  # Static file serving
```

## Auto-Logging from DM Messages

Future enhancement: Extract journal entries from DM responses automatically:

```python
def extract_journal_entries(dm_message_content):
    """
    Parse DM message for journal-worthy events using LLM.

    Returns: List of JournalEntry objects
    """
    prompt = f"""
    Analyze this D&D DM message and extract journal entries:

    Message: {dm_message_content}

    Extract:
    - NPCs introduced (name, description, role)
    - Locations visited
    - Quest updates
    - Important decisions made by players
    - Combat encounters
    - Loot acquired

    Return as JSON array with type, title, description for each.
    """

    entries = llm_parse(prompt)
    return entries
```

## Performance Considerations

**Portrait Files**:

- ~100KB per portrait (PNG, 512x768)
- 100 NPCs = ~10MB total
- Static file serving is fast with nginx/CDN

**Database**:

- Journal entries: ~500 bytes each
- 1000 entries = ~500KB
- Indexes on campaign_id, entry_type, importance, created_at

**RAG**:

- Embed journal summaries (not individual entries)
- Update embeddings on checkpoint creation
- Query top 5-10 relevant entries per DM response

## Future Enhancements

1. **Interactive NPC Portraits**: Click portrait to view full dialogue history
2. **Quest Trees**: Visual graph of quest dependencies
3. **Location Maps**: Integrate with world map generation
4. **Decision Impact Tracking**: Show consequences of past choices
5. **Export Journal**: PDF/Markdown export for offline reference
6. **Shared Journals**: Multi-player campaigns with shared journal view
7. **Voice Memos**: Audio annotations for journal entries
8. **Screenshot Integration**: Attach images to journal entries

## Testing Checklist

- [ ] Migration runs successfully
- [ ] Batch portrait generation works
- [ ] Static file serving accessible
- [ ] Journal UI loads correctly
- [ ] NPC portraits display in codex
- [ ] Timeline filtering works
- [ ] Quest log shows active/completed
- [ ] Checkpoint integration shows journal data
- [ ] RAG retrieval includes journal context
- [ ] Portrait generation handles unicode names
- [ ] File paths are cross-platform compatible
