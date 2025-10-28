# Database Path Audit - October 27, 2025

## Summary

Fixed all backend migration scripts to correctly reference the **root** `storycraft.db` instead of creating separate databases in subdirectories.

## Root Database Location

**Correct Path**: `E:\storycraft\storycraft.db` (project root)

## Files Fixed ✅

### Migration Scripts (backend/)

1. **migrate_add_dnd_stats.py**

   - **Before**: `Path(__file__).parent / "storycraft.db"` → `backend/storycraft.db` ❌
   - **After**: `Path(__file__).parent.parent / "storycraft.db"` → `storycraft.db` ✅

2. **migrate_add_generation_log.py**

   - **Before**: `Path(__file__).parent / "storycraft.db"` → `backend/storycraft.db` ❌
   - **After**: `Path(__file__).parent.parent / "storycraft.db"` → `storycraft.db` ✅

3. **migrate_add_structured_data.py**

   - **Before**: `os.path.join(os.path.dirname(__file__), "storycraft.db")` → `backend/storycraft.db` ❌
   - **After**: `os.path.join(os.path.dirname(__file__), "..", "storycraft.db")` → `storycraft.db` ✅

4. **migrate_add_portrait.py**

   - **Before**: `os.path.join(os.path.dirname(__file__), 'storycraft.db')` → `backend/storycraft.db` ❌
   - **After**: `os.path.join(os.path.dirname(__file__), '..', 'storycraft.db')` → `storycraft.db` ✅

5. **migrate_add_dm_roll_setting.py**
   - **Already Correct**: `os.path.join(os.path.dirname(__file__), "..", "storycraft.db")` ✅

### Utility Scripts (backend/)

6. **check_tables.py**

   - **Before**: `sqlite3.connect('storycraft.db')` → relative to CWD ❌
   - **After**: Uses absolute path to root `storycraft.db` ✅

7. **check_db_tables.py**

   - **Already Correct**: `os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))` ✅

8. **scripts/create_game_tables.py**
   - **Before**: `sqlite3.connect('storycraft.db')` → relative to CWD ❌
   - **After**: Uses absolute path to root `storycraft.db` ✅

## Files Already Correct ✅

### Core Database Module

- **backend/database.py**: Correctly uses `DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))`

### Migrations Folder (backend/migrations/)

All migration scripts in this folder already correctly reference the root database:

- add_campaign_system.py
- add_user_settings.py
- add_combat_fields.py
- add_world_columns.py
- inspect_db.py
- seed_sample_world.py
- update_campaign_session_reference.py

### API Routers

- **routers/monsters.py**: Uses `os.path.join(repo_root, 'storycraft.db')` ✅
- **routers/reference_search.py**: Uses `os.path.join(repo_root, "storycraft.db")` ✅

## Verification

Run this query to confirm the dm_roll_for_players column exists:

```bash
sqlite3 E:\storycraft\storycraft.db "PRAGMA table_info(user_settings);"
```

Expected output should include:

```
26|dm_roll_for_players|BOOLEAN|0|0|0
```

## Next Steps

1. ✅ All migration scripts fixed
2. ⏳ **Restart backend server** to clear SQLAlchemy cache
3. ⏳ Test DM generation with new settings
4. ⏳ Verify scene images render correctly

## Notes

- The root `storycraft.db` is ~490MB and contains all data: campaigns, characters, chat history, and 52K+ RAG embeddings
- Always use absolute paths or proper relative paths from the script location
- Never use bare `sqlite3.connect('storycraft.db')` without path resolution
