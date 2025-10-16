"""
Database Migration: Add D&D 5E Fields to Character Model
==========================================================
This migration adds comprehensive D&D 5th Edition character stats to the characters table.

New fields support:
- D&D mode flag (is_dnd)
- Core D&D stats (class, level, species, background, alignment)
- Ability scores (6 core abilities)
- Combat stats (HP, AC, Initiative, Speed)
- Proficiencies (skills, saves, armor, weapons, tools)
- Features (racial traits, class features, background features)
- Equipment (weapons, armor, gear, tools)
- Spellcasting (for caster classes)
- Languages

Run this script to migrate the database:
    python backend/migrate_add_dnd_stats.py
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "storycraft.db"

def migrate_database():
    """Add D&D 5E fields to the characters table."""
    
    print("=" * 70)
    print("D&D 5E Character Stats Migration")
    print("=" * 70)
    print()
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"❌ Error: Database not found at {DB_PATH}")
        print("   Please ensure the database exists before running migration.")
        return False
    
    print(f"📁 Database: {DB_PATH}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🔍 Checking existing columns...")
        cursor.execute("PRAGMA table_info(characters)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"   Found {len(existing_columns)} existing columns")
        print()
        
        # List of new columns to add
        new_columns = [
            ("is_dnd", "BOOLEAN DEFAULT 0"),
            ("dnd_class", "VARCHAR(100)"),
            ("dnd_level", "INTEGER DEFAULT 1"),
            ("dnd_species", "VARCHAR(100)"),
            ("dnd_background", "VARCHAR(100)"),
            ("dnd_alignment", "VARCHAR(50)"),
            ("dnd_ability_scores", "JSON"),
            ("dnd_hit_points", "INTEGER"),
            ("dnd_armor_class", "INTEGER"),
            ("dnd_initiative", "VARCHAR(10)"),
            ("dnd_speed", "INTEGER"),
            ("dnd_proficiency_bonus", "VARCHAR(10)"),
            ("dnd_skills", "JSON"),
            ("dnd_proficiencies", "JSON"),
            ("dnd_features", "JSON"),
            ("dnd_equipment", "JSON"),
            ("dnd_spellcasting", "JSON"),
            ("dnd_languages", "JSON")
        ]
        
        print("📝 Adding new D&D columns:")
        added_count = 0
        skipped_count = 0
        
        for column_name, column_type in new_columns:
            if column_name in existing_columns:
                print(f"   ⏭️  {column_name:<25} (already exists)")
                skipped_count += 1
            else:
                try:
                    sql = f"ALTER TABLE characters ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"   ✅ {column_name:<25} {column_type}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"   ❌ {column_name:<25} Error: {e}")
                    return False
        
        print()
        print("💾 Committing changes...")
        conn.commit()
        
        print()
        print("=" * 70)
        print("✨ Migration Complete!")
        print("=" * 70)
        print(f"   ✅ Added:   {added_count} new columns")
        print(f"   ⏭️  Skipped: {skipped_count} existing columns")
        print(f"   📊 Total:   {added_count + skipped_count} D&D columns")
        print()
        
        # Verify the migration
        print("🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(characters)")
        all_columns = cursor.fetchall()
        dnd_columns = [col for col in all_columns if col[1].startswith('dnd_') or col[1] == 'is_dnd']
        
        print(f"   ✅ Found {len(dnd_columns)} D&D-related columns in database")
        print()
        
        # Show sample of new columns
        print("📋 New D&D columns available:")
        for col in dnd_columns[:5]:
            print(f"   • {col[1]} ({col[2]})")
        if len(dnd_columns) > 5:
            print(f"   ... and {len(dnd_columns) - 5} more")
        print()
        
        conn.close()
        
        print("🎉 Database is now ready for D&D character creation!")
        print()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def rollback_migration():
    """Remove D&D 5E fields from the characters table (rollback)."""
    
    print("=" * 70)
    print("⚠️  D&D Migration Rollback")
    print("=" * 70)
    print()
    print("Note: SQLite does not support DROP COLUMN directly.")
    print("To rollback, you would need to:")
    print("  1. Create a backup of the database")
    print("  2. Create a new table without D&D columns")
    print("  3. Copy data from old table to new table")
    print("  4. Drop old table and rename new table")
    print()
    print("Or simply delete the database and run migrations from scratch.")
    print()


def check_migration_status():
    """Check if the D&D migration has been applied."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(characters)")
        columns = {row[1] for row in cursor.fetchall()}
        
        dnd_columns = [col for col in columns if col.startswith('dnd_') or col == 'is_dnd']
        
        print("=" * 70)
        print("D&D Migration Status")
        print("=" * 70)
        print()
        
        if dnd_columns:
            print(f"✅ Migration Applied: {len(dnd_columns)} D&D columns found")
            print()
            print("D&D columns:")
            for col in sorted(dnd_columns):
                print(f"   • {col}")
        else:
            print("❌ Migration Not Applied: No D&D columns found")
            print()
            print("Run: python backend/migrate_add_dnd_stats.py")
        
        print()
        conn.close()
        return bool(dnd_columns)
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            check_migration_status()
        elif command == "rollback":
            rollback_migration()
        elif command == "migrate":
            migrate_database()
        else:
            print(f"Unknown command: {command}")
            print()
            print("Usage:")
            print("  python migrate_add_dnd_stats.py          # Run migration")
            print("  python migrate_add_dnd_stats.py migrate  # Run migration")
            print("  python migrate_add_dnd_stats.py check    # Check status")
            print("  python migrate_add_dnd_stats.py rollback # Show rollback info")
    else:
        # Default: Run migration
        success = migrate_database()
        sys.exit(0 if success else 1)
