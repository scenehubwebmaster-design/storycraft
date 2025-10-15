"""
Database migration script to add portrait image fields to characters table.

Run this script to add the new columns:
    python migrate_add_portrait.py
"""
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'storycraft.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(characters)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'portrait_image' not in columns:
            print("Adding portrait_image column...")
            cursor.execute("ALTER TABLE characters ADD COLUMN portrait_image TEXT")
            print("✓ portrait_image column added")
        else:
            print("portrait_image column already exists")
        
        if 'image_prompt' not in columns:
            print("Adding image_prompt column...")
            cursor.execute("ALTER TABLE characters ADD COLUMN image_prompt TEXT")
            print("✓ image_prompt column added")
        else:
            print("image_prompt column already exists")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    print("Adding portrait image support to characters table\n")
    migrate()
