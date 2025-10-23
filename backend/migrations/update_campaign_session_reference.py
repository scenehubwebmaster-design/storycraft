"""
Migration: Update campaigns table to use chat_session_id instead of dm_session_id
Run this script to update the existing campaigns table schema
"""

import sqlite3
from pathlib import Path

# Database path (repo root)
DB_PATH = Path(__file__).parent.parent.parent / "storycraft.db"

def migrate():
    print("=" * 70)
    print("Campaign Session Reference Update Migration")
    print("=" * 70)
    print(f"\n📁 Database: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if chat_session_id column already exists
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'chat_session_id' in columns:
            print("✅ Column 'chat_session_id' already exists!")
            print("   No migration needed.")
            conn.close()
            return
        
        print("📝 Renaming dm_session_id to chat_session_id...")
        
        # SQLite doesn't support RENAME COLUMN in older versions
        # So we need to:
        # 1. Create a new table with the correct schema
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE campaigns_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                setting VARCHAR(100),
                difficulty VARCHAR(20),
                campaign_type VARCHAR(50),
                starting_level INTEGER DEFAULT 1,
                current_level INTEGER DEFAULT 1,
                chat_session_id INTEGER,
                current_scene_type VARCHAR(50) DEFAULT 'roleplay',
                current_location VARCHAR(200),
                quest_log TEXT,
                npc_tracker TEXT,
                session_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
            )
        """)
        print("   ✅ Created new table schema")
        
        # Copy data from old table (if it exists and has data)
        cursor.execute("""
            INSERT INTO campaigns_new 
            SELECT 
                id, title, description, setting, difficulty, campaign_type,
                starting_level, current_level, dm_session_id as chat_session_id,
                current_scene_type, current_location, quest_log, npc_tracker,
                session_notes, created_at, updated_at
            FROM campaigns
        """)
        
        rows_copied = cursor.rowcount
        print(f"   ✅ Copied {rows_copied} existing campaigns")
        
        # Drop old table
        cursor.execute("DROP TABLE campaigns")
        print("   ✅ Dropped old table")
        
        # Rename new table
        cursor.execute("ALTER TABLE campaigns_new RENAME TO campaigns")
        print("   ✅ Renamed new table to 'campaigns'")
        
        # Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_campaigns_chat_session_id ON campaigns (chat_session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_campaigns_created_at ON campaigns (created_at)")
        print("   ✅ Recreated indexes")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✨ Migration Complete!")
        print("=" * 70)
        print("\n✅ Updated column: dm_session_id → chat_session_id")
        print(f"✅ Migrated: {rows_copied} campaigns")
        print("\n🎉 campaigns table now references chat_sessions!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
