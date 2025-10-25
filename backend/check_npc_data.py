"""Quick check of NPC-related data in the database."""

from .database import SessionLocal, engine
from sqlalchemy import inspect, text

db = SessionLocal()

# Check NPCs table
print("=" * 60)
print("NPCs TABLE")
print("=" * 60)
npcs_count = db.execute(text("SELECT COUNT(*) FROM npcs")).scalar()
print(f"Total NPCs in npcs table: {npcs_count}")

if npcs_count > 0:
    print("\nSample NPCs:")
    result = db.execute(text("SELECT id, name, role, game_session_id FROM npcs LIMIT 5"))
    for row in result:
        print(f"  - ID {row[0]}: {row[1]} ({row[2]}) - GameSession: {row[3]}")

# Check reference_embeddings schema
print("\n" + "=" * 60)
print("REFERENCE_EMBEDDINGS TABLE")
print("=" * 60)
inspector = inspect(engine)
columns = inspector.get_columns('reference_embeddings')
print("Columns:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")

# Count reference embeddings
ref_count = db.execute(text("SELECT COUNT(*) FROM reference_embeddings")).scalar()
print(f"\nTotal reference embeddings: {ref_count}")

# Sample some reference embeddings
print("\nSample reference embeddings:")
result = db.execute(text("SELECT id, reference_id FROM reference_embeddings LIMIT 5"))
for row in result:
    print(f"  - Embedding ID {row[0]}: Reference ID {row[1]}")

# Check if there's a references table (need to escape it)
print("\n" + "=" * 60)
print("Checking for NPC reference documents...")
print("=" * 60)

# Try to see if we have any monster_stats
monster_count = db.execute(text("SELECT COUNT(*) FROM monster_stats")).scalar()
print(f"Monster stats: {monster_count}")

# Sample monsters
if monster_count > 0:
    print("\nSample monsters:")
    result = db.execute(text("SELECT name, type, cr FROM monster_stats LIMIT 5"))
    for row in result:
        print(f"  - {row[0]} (Type: {row[1]}, CR: {row[2]})")

db.close()
