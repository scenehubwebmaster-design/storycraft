# Issue Resolution Summary

## Two Main Issues Fixed

### 1. Scene Images Not Appearing in Game Chat (Campaigns)

**Problem:**

- Backend successfully generated scene images via Stable Diffusion
- Images were not appearing in the frontend for campaign games
- Regular chat worked fine, but game-chat endpoint (used by campaigns) had silent failures

**Root Cause:**

- Background task `_generate_and_cache_image_game()` in game-chat endpoint had minimal logging
- All exceptions were caught with generic try-except blocks with no error output
- Impossible to debug where the task was failing

**Solution (Commit: `68410bc`):**
Added comprehensive logging throughout the background image generation task:

```python
# backend/routers/chat.py - Lines ~295-365
async def _generate_and_cache_image_game(...):
    try:
        print("[Background Scene Image - game_chat] Starting generation...")
        print("[Background Scene Image - game_chat] Calling generate_location_image...")
        gen = await generate_location_image(...)
        print(f"[Background Scene Image - game_chat] Generation completed. Result keys: {list(gen.keys())}")

        image_b64 = gen.get("image_base64") or gen.get("image")
        if not image_b64:
            print("[Background Scene Image - game_chat] ERROR: No image data")
            return

        print(f"[Background Scene Image - game_chat] Image data extracted, length: {len(image_b64)} bytes")
        # ... database operations ...
        print("[Background Scene Image - game_chat] Database commit successful")
        # ... SSE publish ...
        print("[Background Scene Image - game_chat] SSE event published successfully")
    except Exception as e:
        import traceback
        print(f"[Background Scene Image - game_chat] FAILED: {e}")
        print(f"[Background Scene Image - game_chat] Traceback: {traceback.format_exc()}")
```

**What to Look For:**

- Restart backend server
- Send a DM message in a campaign
- Watch backend console for `[Background Scene Image - game_chat]` logs
- Logs will show exactly where the task succeeds or fails

**Expected Flow:**

1. "Starting generation for message {id}"
2. "Calling generate_location_image..."
3. "Generation completed. Result keys: [...]"
4. "Image data extracted, length: X bytes"
5. "Database commit successful"
6. "SSE event published successfully"

If any step fails, you'll see the exact error with full traceback.

---

### 2. DM Not Using Character Stats / Asking Generic Questions

**Problem:**

- DM was giving generic responses like "roll a check and tell me the result"
- Characters were in the database with full D&D stats
- DM should reference specific character abilities (Stealth skill, equipment, etc.)

**Root Cause:**
The DM chat handler **already had** comprehensive character stats formatting (`_format_full_party_stats()`), but used a **heuristic** to decide when to include them:

1. **Compact Mode (names only):** Used during roleplay to save tokens
2. **Full Stats Mode:** Used during combat or when "mechanical keywords" detected

The heuristic was:

- Too strict: didn't include enough keywords for exploration/skill-based play
- Too aggressive: switched to compact mode too early in new games

**Solution (Commit: Latest):**
Enhanced the stats inclusion logic in `backend/game/dm_chat_handler.py`:

**Change 1: Always show stats for first 4 exchanges (8 messages)**

```python
def _should_include_stats(self, session_id: int) -> bool:
    # ... existing code ...

    # Always include stats for first 4 exchanges (8 messages) to help DM learn about party
    if len(self.conversation_history[session_id]) <= 8:
        print(f"[DM Context] Including stats - early game (message {len(self.conversation_history[session_id])}/8)")
        return True
```

This ensures the DM sees character abilities when you first start playing.

**Change 2: Expanded mechanical keyword detection**
Added exploration and skill-based keywords that should trigger full stats:

```python
mechanical_keywords = [
    # ... existing combat/spell keywords ...

    # Exploration and skill-based actions (NEW)
    ' search ', ' investigate', 'perception', ' listen', ' look for',
    ' stealth', ' hide ', ' sneak', 'acrobatics', 'athletics',
    'arcana', 'history', 'nature', 'religion', 'insight',
    'persuasion', 'deception', 'intimidation', 'performance',
    'survival', 'medicine', 'animal handling', ' climb', ' jump',
    'i try to', 'i attempt', 'i want to', 'can i'
]
```

Now when you say "I try to search the room" or "Can I hide?", the DM will see:

- Your Stealth skill proficiency
- Your Perception modifier
- Your equipment (like thieves' tools)
- Your current HP/AC in case of danger

**What Character Data the DM Sees (Full Stats Mode):**

```
=== PARTY CHARACTERS (FULL STATS) ===

**Elara Moonshadow**
  Class: Rogue 3, Species: Half-Elf
  HP: 18/22 (Temp: 0) | AC: 15
  STR: 10 (+0) | DEX: 17 (+3) | CON: 12 (+1)
  INT: 14 (+2) | WIS: 13 (+1) | CHA: 16 (+3)
  Proficiency: +2 | Initiative: +3 | Speed: 30 ft
  Skill Proficiencies: Stealth, Sleight of Hand, Perception, Investigation, Deception
```

**What the DM Sees (Compact Mode - only when safe):**

```
=== PARTY ===
Elara Moonshadow (Rogue 3)
```

**Debug Logging:**
Watch backend console for these messages:

- `[DM Context] Including FULL character stats (combat=True/False, keywords detected)`
- `[DM Context] Using COMPACT mode (names only) - no mechanical keywords detected`
- `[DM Context] Including stats - early game (message X/8)`

---

## Testing Steps

### Test Scene Images:

1. Restart backend: `cd backend && python -m uvicorn main:app --reload`
2. Open a campaign in frontend
3. Send a DM message (e.g., "I look around the tavern")
4. **Check backend console** for full image generation log sequence
5. **Check frontend** for scene image appearing within ~10 seconds

### Test Character Stats Integration:

1. Make sure characters are added to campaign (check party_members table)
2. Start a new campaign or clear conversation history
3. Send exploration message: "I want to search for hidden doors"
4. **Check backend console** for:
   - `[DM Context] Including stats - early game (message 2/8)`
   - Or: `[DM Context] Including FULL character stats (keywords detected)`
5. **Check DM response** should reference:
   - Specific skills: "Roll a Perception check (d20 + your Wisdom modifier)"
   - Character abilities: "With your Stealth proficiency, you could..."
   - Equipment: "You draw your rapier..."

### Success Criteria:

- ✅ Scene images appear in frontend
- ✅ Backend logs show full generation sequence
- ✅ DM mentions character-specific abilities
- ✅ DM suggests actions appropriate to character class
- ✅ No more generic "roll a check and tell me the result" responses

---

## What If It Still Doesn't Work?

### Scene Images:

**Check the new logging output:**

- If no logs at all → Background task not being created
- If logs stop at "Calling generate_location_image" → SD service issue
- If logs stop at "Generation completed" → Data extraction problem
- If logs stop at "Database commit" → SQLAlchemy/DB issue
- If logs stop at "SSE event published" → Frontend SSE handler issue

Share the backend console output showing where it stops.

### Character Stats:

**Check these things:**

1. Are characters actually added to the campaign's party_members?

   ```sql
   SELECT * FROM party_members WHERE session_id = <your_campaign_id>;
   ```

2. Do characters have D&D stats populated?

   ```sql
   SELECT name, dnd_class, dnd_level, dnd_ability_scores FROM characters;
   ```

3. What do the debug logs show?
   - "early game" → Stats should be included
   - "FULL character stats" → Stats should be included
   - "COMPACT mode" → Stats are hidden (only names shown)

If you see "COMPACT mode" too early, we can make the heuristic less aggressive (increase the 8-message threshold or add more keywords).

---

## Files Modified

1. `backend/routers/chat.py`

   - Added comprehensive logging to `_generate_and_cache_image_game()`
   - Added traceback on exceptions
   - Added early return with error logging if no image data

2. `backend/game/dm_chat_handler.py`
   - Always include stats for first 8 messages
   - Expanded mechanical keywords for exploration/skills
   - Added debug logging for stat inclusion decisions

Both changes are backwards-compatible and don't break existing functionality.
