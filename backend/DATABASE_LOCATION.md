# Database Location Configuration

## 📍 Current Database Location

**The application database is located at:**
```
storycraft.db (PROJECT ROOT)
```

## ⚠️ Important Notes

### Single Source of Truth
- **ONLY** `storycraft.db` in the project root should be used
- This file contains ALL application data:
  - Campaign data (14+ campaigns)
  - Characters and chat history  
  - RAG embeddings (52K+ vectors from D&D books)
  - User settings

### Why Project Root?
1. **Historical Reasons**: Original database location, contains all production data
2. **RAG Integration**: Stores 52,248 embeddings (439 MB) alongside 6,001 document chunks
3. **Consolidated Data**: Single file for all SQLite data (campaigns, RAG, chat)
4. **Size**: ~490 MB is NORMAL and EXPECTED for a RAG system with this much data

### Database Size Breakdown
The 490 MB size is NOT bloat - it's justified:
- **Campaign & Character Data**: ~50 MB
- **RAG Document Chunks**: 6,001 text chunks from D&D Player's Handbook
- **RAG Embeddings**: 52,248 vectors × 8,415 bytes each = **~439 MB**
- **Chat History & Metadata**: ~1 MB

**The large size comes from storing embeddings for semantic search!** This is normal for RAG systems.

### Configuration
The database path is set in `backend/database.py`:
```python
DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))
# Resolves to: e:\storycraft\storycraft.db (PROJECT ROOT)
```

### Environment Override
You can override the database location with an environment variable:
```bash
set STORYCRAFT_DATABASE_URL=sqlite:///path/to/your/database.db
```

## 🔄 Migration History

**October 23, 2025 - FINAL DECISION**: Keep database in project root

- **Investigation**: Found backend/storycraft.db (11MB) vs root storycraft.db (490MB)
- **Initial Plan**: Consolidate to backend folder
- **Discovery**: The 490MB file contains ALL production data including 52K embeddings
- **Resolution**: Reverted to use root database - the size is justified by RAG embeddings
- **Lesson**: "Bloated" database was actually the correct, complete database

### Why the Size Difference?
- **Root DB** (490MB): Complete with all embeddings for RAG semantic search
- **Backend DB** (11MB): Older copy without embeddings - missing production data

## 🗄️ RAG Architecture

### Hybrid Storage System
StoryCraft uses BOTH SQLite and ChromaDB for RAG:

**SQLite** (`storycraft.db`):
- Stores actual text chunks from D&D books
- Stores embedding vectors for those chunks
- Primary source of truth for document data

**ChromaDB** (`backend/chroma_db/`):
- Additional vector index for fast semantic search
- Supplements SQLite embeddings
- Used for similarity queries

### Embedding Details
- **Count**: 52,248 embedding vectors
- **Size per vector**: ~8,415 bytes (stored as TEXT)
- **Total embedding storage**: 439 MB in SQLite
- **Source**: D&D 5e Player's Handbook chunks

## 🧪 Testing

When running tests, the application uses an in-memory database:
```python
if pytest_env:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
```

This ensures tests don't interfere with production data.

## 📝 Running Migrations

Always run migrations from backend directory, they will operate on root database:
```bash
cd backend
alembic upgrade head
```

Or use Python migration scripts from project root:
```bash
python backend/migrations/add_user_settings.py
```

## ❓ Troubleshooting

### "No such table" errors
- Verify `storycraft.db` exists in project root
- Check you're not accidentally creating a new DB
- Run migrations: `cd backend && alembic upgrade head`

### Database seems empty
- Make sure backend is using ROOT database (check database.py)
- Don't confuse with `backend/storycraft.db` (old/incomplete copy)
- Check `STORYCRAFT_DATABASE_URL` environment variable isn't overriding

### File size concerns
- 490 MB is NORMAL for 52K embeddings
- Each embedding is 8,415 bytes
- This is how RAG systems work - they store vectors for semantic search
- To reduce size, you'd have to remove embeddings (breaking RAG functionality)

## 🔧 Maintenance

### Vacuuming (NOT RECOMMENDED)
SQLite VACUUM would reduce file size but won't help much since the embeddings are actively used:
```bash
sqlite3 storycraft.db "VACUUM;"
```
**Note**: This won't significantly reduce size as embeddings are legitimate data, not fragmentation.

### Backup Strategy
Given the large size, use incremental backups:
```bash
# Full backup (490 MB)
copy storycraft.db storycraft.db.backup

# Or use SQLite backup API for hot backups while app is running
```

### Migration Safety
Always backup before running migrations:
```bash
copy storycraft.db storycraft.db.pre_migration
cd backend
alembic upgrade head
```
