# RAG Improvement Quick Start Guide

## What Changed?

The AI DM chat now intelligently extracts filters from your questions to find exactly what you're looking for. No more wrong spell levels or mixed item rarities!

## Before vs After

### Query: "Show me level 5 evocation spells"

**Before:** Fireball (Lvl 3), Telekinesis (wrong school), Prayer of Healing (Lvl 2) ❌  
**After:** Cone of Cold, Wall of Force, Flame Strike, Arcane Hand ✅

### Query: "Find rare magic weapons"

**Before:** Mixed rarities, mixed categories ❌  
**After:** Only Rare rarity, only Weapons ✅

## Quick Test (5 minutes)

### Step 1: Process New Documents

```powershell
cd e:\storycraft\scripts
python chunk_documents.py
python generate_chunk_embeddings.py
```

_(This takes 2-3 minutes - you only need to do this once)_

### Step 2: Restart Backend

```powershell
# Stop current backend (Ctrl+C if running)
cd e:\storycraft\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Run Automated Test

```powershell
cd e:\storycraft\scripts
python test_improved_rag.py
```

**Expected Output:**

```
✓ Created test session: 123
Query: "Show me level 5 evocation spells for my wizard"

Retrieved Sources:
1. Cone of Cold
   Level: 5
   School: Evocation

2. Wall of Force
   Level: 5
   School: Evocation

✓ Correct spells found: 5/7
✓ No incorrect spells found!

✅ TEST PASSED: RAG system now correctly filters Level 5 Evocation spells!
```

## Manual Testing (DMChat UI)

### Step 1: Start Frontend

```powershell
cd e:\storycraft\frontend
npm run dev
```

### Step 2: Open DMChat

Navigate to: http://localhost:3000/dm-chat

### Step 3: Create Session

- Click "New Chat"
- Enable "Include Reference Context (RAG)"
- Set Top-K: 5

### Step 4: Test Queries

**Try these queries:**

1. "Show me level 5 evocation spells for my wizard"
2. "Find rare magic weapons for my fighter"
3. "What are good cantrips for a sorcerer?"
4. "List legendary armor items"
5. "Tell me about dungeon traps and hazards"

**What to look for:**

- Spells should match the requested level
- Items should match the requested rarity
- Categories should be correct (weapons, armor, etc.)
- Response should include source citations

## Debugging

### Check Backend Logs

The backend prints query analysis:

```
[DEBUG] Query analysis: Searching: Level 5 | Evocation | Spells
[DEBUG] Extracted params: {'level': 5, 'school': 'Evocation', 'ref_type': 'spells_md'}
[DEBUG] Reference search returned 5 results
```

### Common Issues

**Issue:** Test script fails with connection error  
**Fix:** Ensure backend is running on http://localhost:8000

**Issue:** No results returned  
**Fix:** Make sure you ran `chunk_documents.py` and `generate_chunk_embeddings.py`

**Issue:** Wrong results still appearing  
**Fix:** Check backend logs for query analysis output. If params are empty, query analyzer may need pattern updates.

## What's New Under the Hood

### Query Analyzer (`backend/query_analyzer.py`)

Automatically detects:

- Spell levels (0-9, cantrips)
- Spell schools (Evocation, Abjuration, etc.)
- Item rarities (Common → Legendary → Artifact)
- Categories (Weapon, Armor, Wondrous Item)
- Reference types (spells, items, monsters, classes)

### Consolidated Lists (`documents/reference/generated_lists/`)

- 79 spell lists organized by school × level
- 6 magic item lists organized by rarity
- Classes overview
- DM tools index

### DM Tool Documents

- 13 core dungeon generation files (chambers, traps, hazards)
- 9 dungeon theme files (lair, tomb, temple, etc.)
- Enables encounter and session building

## Next Steps

After confirming tests pass:

1. Commit the chunked/embedded data (optional)
2. Test with real user queries
3. Gather feedback on accuracy improvements
4. Consider adding UI filter controls for power users

## Help & Support

**Test fails?** Check backend logs for error details  
**Wrong results?** Share the query and results for analysis  
**Feature request?** Document in GitHub issues

## Quick Reference

**Test Command:**

```powershell
cd e:\storycraft\scripts && python test_improved_rag.py
```

**Restart Backend:**

```powershell
cd e:\storycraft\backend && python -m uvicorn main:app --reload
```

**Start Full Dev:**

```powershell
cd e:\storycraft && npm run dev:all
```

**Check Backend Status:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/docs
```

## Success Criteria

✅ Test script passes (≥4 correct spells, 0 wrong spells)  
✅ DMChat returns correct spell levels  
✅ DMChat filters by rarity correctly  
✅ Backend logs show extracted parameters  
✅ Response time remains fast (<5 seconds)
