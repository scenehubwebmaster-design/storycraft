"""
Database migration to add generation_log column to characters table.
Run this script once to update the database schema.
"""
import sqlite3
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "storycraft.db"

if not db_path.exists():
    print(f"❌ Database not found at: {db_path}")
    exit(1)

print(f"📊 Connecting to database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(characters)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'generation_log' in columns:
        print("✅ Column 'generation_log' already exists in characters table")
    else:
        print("➕ Adding 'generation_log' column to characters table...")
        cursor.execute("""
            ALTER TABLE characters 
            ADD COLUMN generation_log TEXT
        """)
        conn.commit()
        print("✅ Successfully added 'generation_log' column")
    
    # Check current table structure
    print("\n📋 Current characters table structure:")
    cursor.execute("PRAGMA table_info(characters)")
    for row in cursor.fetchall():
        print(f"   - {row[1]} ({row[2]})")
    
    print("\n✅ Migration completed successfully!")
    
except sqlite3.Error as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
finally:
    conn.close()
