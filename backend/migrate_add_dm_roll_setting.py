"""
Migration: Add dm_roll_for_players column to user_settings table

This migration adds the dm_roll_for_players boolean column to support
the "Allow DM to roll for players" feature.

Run this script from the backend directory:
    python migrate_add_dm_roll_setting.py
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storycraft.db")

def migrate():
    """Add dm_roll_for_players column to user_settings table"""
    
    print(f"[Migration] Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user_settings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'dm_roll_for_players' in columns:
            print("[Migration] Column 'dm_roll_for_players' already exists. Skipping.")
            return
        
        # Add the column with default value False
        print("[Migration] Adding 'dm_roll_for_players' column to user_settings table...")
        cursor.execute("""
            ALTER TABLE user_settings 
            ADD COLUMN dm_roll_for_players BOOLEAN DEFAULT 0
        """)
        
        conn.commit()
        print("[Migration] ✓ Successfully added dm_roll_for_players column")
        print("[Migration] ✓ Default value set to False (0)")
        
    except sqlite3.Error as e:
        print(f"[Migration] ✗ Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        print("[Migration] Database connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add dm_roll_for_players Setting")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("Migration complete! Restart the backend server.")
    print("=" * 60)
