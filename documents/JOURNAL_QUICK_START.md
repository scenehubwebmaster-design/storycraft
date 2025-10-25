# 🚀 Campaign Journal System - Quick Start

## ✅ Status: Ready to Use

The migration has already been run successfully. The journal system is ready to use!

## 🎯 Quick Test (3 Steps)

### 1. Restart Backend

```powershell
cd e:\storycraft\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open DMChat

- Go to your browser
- Start or select a campaign

### 3. Test the Journal

- Click the **📖 Journal icon** in the toolbar
- Browse the 4 tabs:
  - **Timeline** - All campaign events
  - **NPC Codex** - Characters you've met
  - **Quest Log** - Active and completed quests
  - **Locations** - Places you've visited

## 🎨 Generate NPC Portraits (Optional)

If you have existing NPCs in your database:

```powershell
# See what NPCs need portraits
cd e:\storycraft
python -m backend.batch_generate_npc_portraits --dry-run

# Generate portraits for a campaign
python -m backend.batch_generate_npc_portraits --campaign-id 1

# Review and regenerate any poor portraits
python -m backend.review_npc_portraits --campaign-id 1
```

## 🧪 Test Auto-Logging

1. In DMChat, send a message that introduces NPCs or locations
2. Wait for DM response
3. Open the Journal
4. Check Timeline tab - you should see auto-created entries!

Example test message:

> "I enter the tavern and meet the bartender"

The system will automatically detect the NPC meeting and create a journal entry.

## 📁 What You Get

### Automatic Features:

- ✅ Journal entries auto-created from DM messages
- ✅ NPCs and quests tracked automatically
- ✅ Importance ratings (1-5 stars)
- ✅ Checkpoint previews show journal data
- ✅ Portrait display in NPC codex

### Manual Features:

- 🎨 Batch portrait generation
- 🔍 Interactive portrait review/regeneration
- ✏️ Manual journal entry creation (via API)

## 📚 Documentation

- **JOURNAL_SCRIPTS_README.md** - Complete script usage guide
- **CAMPAIGN_JOURNAL_SYSTEM.md** - Architecture documentation
- **CAMPAIGN_JOURNAL_IMPLEMENTATION.md** - Implementation details

## ⚠️ Important Note

All backend scripts must be run as **modules from the repository root**:

```powershell
# ✅ CORRECT (from e:\storycraft)
python -m backend.script_name

# ❌ WRONG (from e:\storycraft\backend)
python script_name.py
```

This is because backend files use relative imports.

## 🆘 Troubleshooting

### "ImportError: attempted relative import"

→ Make sure you're in `e:\storycraft` (repo root) and using `-m` flag

### "No NPCs to process"

→ This is normal if you haven't created NPCs yet. Play through DMChat first!

### Journal not showing

→ Make sure you restarted the backend server after running migration

### Portraits not loading

→ Check backend logs for "Mounted static files" message

## 🎉 Enjoy!

The journal system is now part of your DMChat experience. It will automatically track your campaign's story as you play!
