# DMChat UI Testing Guide for RAG Improvements

## Setup Complete! ✅

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3001
- ✅ 1909 documents imported
- ✅ 6201 chunks created and embedded
- ✅ Query analyzer integrated into chat endpoint
- ✅ LM Studio available at http://100.120.44.114:1234

## Testing the Improved RAG System

### Step 1: Open DMChat

Navigate to: **http://localhost:3001/dm-chat**

### Step 2: Create a New Session

1. Click "New Chat" or the + button
2. Configure session settings:
   - **Title**: "RAG Test - Level 5 Spells"
   - **Provider**: Select **Groq** (or whichever provider you prefer)
   - **Model**: Select any available model
   - **Include Reference Context (RAG)**: ✅ **ENABLED** (very important!)
   - **Top-K**: 5 (default is fine)
3. Click "Create"

### Step 3: Test Problematic Queries

#### Test 1: Level 5 Evocation Spells

**Query:** "Show me level 5 evocation spells for my wizard"

**Expected Behavior:**

- Backend logs should show:
  ```
  [DEBUG] Query analysis: Searching: Level 5 | Evocation | Spells
  [DEBUG] Extracted params: {'level': 5, 'school': 'Evocation', 'ref_type': 'spells_md'}
  ```
- Retrieved sources should include:
  ✅ **Cone of Cold** (Level 5, Evocation)
  ✅ **Wall of Force** (Level 5, Evocation)
  ✅ **Flame Strike** (Level 5, Evocation)
  ✅ **Arcane Hand** (Level 5, Evocation)
  ✅ **Wall of Stone** (Level 5, Evocation)
- Should NOT include:
  ❌ Fireball (Level 3)
  ❌ Telekinesis (Transmutation)
  ❌ Prayer of Healing (Level 2)

#### Test 2: Rare Magic Weapons

**Query:** "Find some rare magic weapons for my fighter"

**Expected Behavior:**

- Query analysis: `Searching: Rare | Weapon | Weapons`
- All retrieved items should be:
  - Rarity: **Rare**
  - Category: **Weapon**

#### Test 3: Cantrips

**Query:** "What are good cantrips for a sorcerer?"

**Expected Behavior:**

- Query analysis: `Searching: Cantrip | Spells`
- All retrieved spells should be:
  - Level: **0** (Cantrip)

#### Test 4: DM Tools (NEW!)

**Query:** "What are some interesting dungeon hazards I can use?"

**Expected Behavior:**

- Query analysis should detect DM tool reference type
- Should retrieve from `documents/reference/core/hazards.md`
- Response should include dungeon hazards from D&D tables

#### Test 5: Dungeon Themes (NEW!)

**Query:** "Help me design a tomb dungeon with interesting chambers"

**Expected Behavior:**

- Should retrieve from `documents/reference/themes/purpose-tomb.md`
- Should also get `documents/reference/core/general-chambers.md`
- Response should reference d20/d100 tables for tomb purposes

### Step 4: Verify in Backend Logs

**How to view backend logs:**
The backend terminal window should show real-time debug output. Look for:

```
[DEBUG] Query analysis: Searching: Level 5 | Evocation | Spells
[DEBUG] Extracted params: {'original_query': 'show me level 5 evocation spells...', 'level': 5, 'school': 'Evocation', 'ref_type': 'spells_md'}
[DEBUG] Reference search returned 5 results
```

### Step 5: Check Source Citations

In the DMChat UI, below each AI response, you should see **source chips** showing which documents were retrieved:

- Click on the chips to see the full document
- Verify that the sources match your query filters
- For spell queries, check that level and school match

## What's New Under the Hood

### Query Analyzer in Action

The chat endpoint now:

1. Takes your natural language query
2. Extracts structured parameters:
   - Spell level (0-9, cantrips)
   - Spell school (Evocation, etc.)
   - Item rarity (Common, Rare, Legendary, etc.)
   - Item category (Weapon, Armor, etc.)
   - Reference type (spells, items, monsters, etc.)
3. Passes these filters to the search API
4. Returns only matching documents

### Before vs After

**Before (No Filter Extraction):**

```python
# Old code - no filters
reference_docs = do_reference_search(
    q=retrieval_query,
    ref_type=None,  # ❌ No type filtering
    k=5,
    db=db
)
# Result: Generic keyword matching, wrong spell levels
```

**After (With Query Analyzer):**

```python
# New code - intelligent filter extraction
query_params = analyze_query(retrieval_query)
reference_docs = do_reference_search(
    q=retrieval_query,
    ref_type=query_params.get('ref_type'),  # ✅ Filtered to spells_md
    k=5,
    db=db,
    level=query_params.get('level'),  # ✅ Filtered to level 5
    school=query_params.get('school'),  # ✅ Filtered to Evocation
    rarity=query_params.get('rarity'),
    category=query_params.get('category')
)
# Result: Only Level 5 Evocation spells!
```

## Troubleshooting

### Issue: No sources retrieved

**Check:**

- Is "Include Reference Context (RAG)" enabled in session settings?
- Check backend logs for errors
- Verify documents are in database: http://localhost:8000/docs → /api/references

### Issue: Wrong results still appearing

**Check:**

- Backend logs to see if query analyzer is extracting correct params
- If params are empty, the query might need pattern updates
- Try more specific queries: "level 5 evocation damage spells"

### Issue: LLM not generating responses

**Check:**

- Is the provider (Groq/OpenAI/etc.) configured with API keys?
- Check backend logs for LLM errors
- Try a different provider or model

## Success Criteria

After testing, you should observe:

✅ **Query Analysis**: Backend logs show extracted parameters  
✅ **Correct Filtering**: Retrieved sources match query constraints  
✅ **No Wrong Results**: Fireball not in Level 5 results, etc.  
✅ **Fast Response**: Results return in <5 seconds  
✅ **DM Tools Work**: Dungeon generation tables are accessible  
✅ **Source Citations**: UI shows chips with retrieved document names

## Next Steps After Testing

1. **Document Results**: Note any queries that still return wrong results
2. **Expand Patterns**: Add more query patterns to `query_analyzer.py` if needed
3. **Build Encounter UI**: Now that DM tools are imported, we can add encounter builder features
4. **LLM Fallback**: Consider adding LLM-based filter extraction for complex queries

## Quick Reference

**Frontend URL**: http://localhost:3001/dm-chat  
**Backend Docs**: http://localhost:8000/docs  
**Test Queries**:

- "show me level 5 evocation spells"
- "find rare magic weapons"
- "what are good cantrips"
- "dungeon hazards and traps"
- "help me design a tomb dungeon"
