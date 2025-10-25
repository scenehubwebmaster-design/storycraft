# Campaign Journal System - Scripts Usage

## Important: Module-Based Execution

All journal system scripts must be run as Python modules (using `-m` flag) from the **storycraft root directory**, not from within the backend folder. This is because `models.py` and other backend files use relative imports.

## Quick Setup

From the repository root (`e:\storycraft`):

```powershell
# Run the interactive setup script
python -m backend.setup_journal_system
```

## Individual Scripts

### 1. Database Migration

**Purpose**: Add journal_entries table and enhance NPC model

```powershell
# Run from repository root
cd e:\storycraft
python -m backend.migrate_add_journal_and_npc_enhancements
```

**What it does**:

- Adds NPC columns: portrait_path, portrait_prompt, first_met_location, etc.
- Creates journal_entries table
- Creates performance indexes
- Idempotent: safe to run multiple times

### 2. Batch Portrait Generation

**Purpose**: Generate portraits for NPCs in the database

```powershell
# Dry run - see what would be generated
python -m backend.batch_generate_npc_portraits --dry-run

# Generate all NPC portraits
python -m backend.batch_generate_npc_portraits

# Generate for specific campaign
python -m backend.batch_generate_npc_portraits --campaign-id 1

# Generate limited number
python -m backend.batch_generate_npc_portraits --limit 5

# Force regenerate existing
python -m backend.batch_generate_npc_portraits --force
```

**Output**: Saves to `backend/static/npc_portraits/`

### 3. Interactive Portrait Review

**Purpose**: Review generated portraits and selectively regenerate

```powershell
# Review all NPCs with portraits
python -m backend.review_npc_portraits

# Review specific campaign
python -m backend.review_npc_portraits --campaign-id 1
```

**Interactive options**:

- `[K]eep` - Accept current portrait
- `[R]egenerate` - Create new portrait (with optional prompt editing)
- `[D]elete` - Remove portrait file and DB reference
- `[S]kip` - Jump to end
- `[Q]uit` - Exit review

## Troubleshooting

### ImportError: attempted relative import with no known parent package

**Cause**: Running script directly from backend folder or without `-m` flag

**Solution**: Always run from repository root with module syntax:

```powershell
cd e:\storycraft
python -m backend.script_name
```

### Module not found errors

**Cause**: Not in repository root directory

**Solution**:

```powershell
cd e:\storycraft  # Go to repo root first
python -m backend.batch_generate_npc_portraits --dry-run
```

### Portrait directory not found

The scripts automatically create `backend/static/npc_portraits/` if it doesn't exist.

### Database locked

If you see "database is locked" errors:

1. Stop the backend server
2. Run the script
3. Restart backend server

## After Running Scripts

1. **Restart backend server** to mount static files:

   ```powershell
   cd e:\storycraft\backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test in DMChat**:

   - Open DMChat in browser
   - Click Journal icon (📖) in toolbar
   - Browse NPCs tab to see generated portraits

3. **Verify static files**:
   - Visit: http://localhost:8000/static/npc_portraits/
   - Should show directory listing of portraits

## File Locations

- **Portraits**: `backend/static/npc_portraits/`
- **Database**: `backend/storycraft.db`
- **API Docs**: http://localhost:8000/docs
- **Journal Endpoints**: `/api/campaigns/{id}/journal/*`

## Command Reference

All commands assume you're in `e:\storycraft` directory:

```powershell
# Migration
python -m backend.migrate_add_journal_and_npc_enhancements

# Portrait generation (dry run)
python -m backend.batch_generate_npc_portraits --dry-run

# Portrait generation (real)
python -m backend.batch_generate_npc_portraits --campaign-id 1

# Portrait review
python -m backend.review_npc_portraits --campaign-id 1

# Interactive setup (recommended)
python -m backend.setup_journal_system
```

## See Also

- `CAMPAIGN_JOURNAL_SYSTEM.md` - Complete architecture documentation
- `CAMPAIGN_JOURNAL_IMPLEMENTATION.md` - Feature details and troubleshooting
