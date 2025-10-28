"""
Database migration: Add structured_data columns to Character and World models

This migration adds the structured_data JSON column to both the characters and worlds
tables to store the full CharacterProfile and WorldProfile objects from structured generation.

Usage:
    python migrate_add_structured_data.py
"""
import sqlite3
import os
import sys

# Get the database path - use root storycraft.db
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storycraft.db")

def migrate():
    """Add structured_data column to characters and worlds tables"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Please make sure the database exists before running migration.")
        sys.exit(1)
    
    print(f"🔄 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if structured_data column already exists in characters table
        cursor.execute("PRAGMA table_info(characters)")
        characters_columns = [col[1] for col in cursor.fetchall()]
        
        if "structured_data" not in characters_columns:
            print("➕ Adding structured_data column to characters table...")
            cursor.execute("""
                ALTER TABLE characters 
                ADD COLUMN structured_data TEXT
            """)
            print("   ✅ Characters table updated successfully!")
        else:
            print("   ℹ️  structured_data column already exists in characters table")
        
        # Check if structured_data column already exists in worlds table
        cursor.execute("PRAGMA table_info(worlds)")
        worlds_columns = [col[1] for col in cursor.fetchall()]
        
        if "structured_data" not in worlds_columns:
            print("➕ Adding structured_data column to worlds table...")
            cursor.execute("""
                ALTER TABLE worlds 
                ADD COLUMN structured_data TEXT
            """)
            print("   ✅ Worlds table updated successfully!")
        else:
            print("   ℹ️  structured_data column already exists in worlds table")
        
        # Commit the changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\n📊 Database schema updated:")
        print("   - characters.structured_data (JSON): Stores full CharacterProfile")
        print("   - worlds.structured_data (JSON): Stores full WorldProfile")
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()
        print("\n🔒 Database connection closed")


def rollback():
    """Remove structured_data columns (rollback migration)"""
    print("⚠️  Rolling back migration...")
    print(f"🔄 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # SQLite doesn't support DROP COLUMN directly for older versions
        # We'll need to create a backup and recreate the tables
        print("⚠️  Note: SQLite requires table recreation to remove columns")
        print("   This is a destructive operation. Backing up structured_data...")
        
        # Check if columns exist before attempting rollback
        cursor.execute("PRAGMA table_info(characters)")
        characters_columns = [col[1] for col in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(worlds)")
        worlds_columns = [col[1] for col in cursor.fetchall()]
        
        if "structured_data" in characters_columns or "structured_data" in worlds_columns:
            print("\n❌ Manual rollback required:")
            print("   1. Backup your database: cp storycraft.db storycraft.db.backup")
            print("   2. Drop and recreate tables without structured_data column")
            print("   3. Or use: python -c 'from database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)'")
            print("   ⚠️  This will lose all data!")
        else:
            print("   ℹ️  No structured_data columns found to remove")
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"\n❌ Rollback failed: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
