"""
Database Migration: Add Combat Fields to Character Model
==========================================================
Phase A: Combat System Enhancement

This migration adds fields required for D&D 5e combat system:
- Attack bonuses (melee, ranged) - pre-calculated for efficiency
- Ability modifiers - pre-calculated to avoid redundant computation
- HP tracking - separate max and current HP
- Temporary HP - for spell effects
- Conditions - track combat conditions (poisoned, stunned, etc.)
- Death saves - track successes/failures
- Resources - track limited-use features (Rage, Action Surge, spell slots)

Run this script to migrate the database:
    python backend/migrations/add_combat_fields.py
"""

import sqlite3
import json
from pathlib import Path

# Database path - use the same logic as database.py (root level)
DB_PATH = Path(__file__).parent.parent.parent / "storycraft.db"  # Project root


def calculate_ability_modifier(score):
    """Calculate D&D 5e ability modifier from score."""
    return (score - 10) // 2


def get_class_resources(dnd_class, dnd_level):
    """Get initial resources for a D&D class."""
    resources = {
        "hit_dice": {"max": dnd_level, "current": dnd_level},
    }
    
    if not dnd_class:
        return resources
    
    class_lower = dnd_class.lower()
    
    if class_lower == "barbarian":
        resources["rage"] = {"max": 2, "current": 2}
    elif class_lower == "fighter":
        resources["action_surge"] = {"max": 1, "current": 1}
        resources["second_wind"] = {"max": 1, "current": 1}
    elif class_lower == "monk":
        resources["ki"] = {"max": dnd_level, "current": dnd_level}
    elif class_lower in ["cleric", "paladin"]:
        resources["channel_divinity"] = {"max": 1, "current": 1}
    elif class_lower == "druid":
        resources["wild_shape"] = {"max": 2, "current": 2}
    elif class_lower == "rogue" and dnd_level >= 3:
        dice_count = (dnd_level + 1) // 2
        resources["sneak_attack_dice"] = f"{dice_count}d6"
    elif class_lower == "sorcerer":
        resources["sorcery_points"] = {"max": dnd_level, "current": dnd_level}
    elif class_lower == "warlock":
        resources["pact_magic_slots"] = {"max": 1, "current": 1}
    elif class_lower == "bard":
        resources["bardic_inspiration"] = {"max": max(1, calculate_ability_modifier(10)), "current": max(1, calculate_ability_modifier(10))}  # Will be updated with CHA
    
    return resources


def migrate_database():
    """Add combat-specific fields to the characters table."""
    
    print("=" * 70)
    print("Combat System Enhancement - Phase A")
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
            ("dnd_ability_modifiers", "JSON"),
            ("dnd_melee_attack_bonus", "INTEGER"),
            ("dnd_ranged_attack_bonus", "INTEGER"),
            ("dnd_hit_points_max", "INTEGER"),
            ("dnd_hit_points_current", "INTEGER"),
            ("dnd_temporary_hp", "INTEGER DEFAULT 0"),
            ("dnd_conditions", "JSON"),
            ("dnd_death_saves", "JSON"),
            ("dnd_resources", "JSON"),
        ]
        
        print("📝 Adding new combat columns:")
        added_count = 0
        skipped_count = 0
        
        for column_name, column_type in new_columns:
            if column_name in existing_columns:
                print(f"   ⏭️  {column_name:<30} (already exists)")
                skipped_count += 1
            else:
                try:
                    sql = f"ALTER TABLE characters ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"   ✅ {column_name:<30} {column_type}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"   ❌ {column_name:<30} Error: {e}")
                    return False
        
        print()
        
        # Migrate existing data
        if added_count > 0:
            print("🔄 Migrating existing D&D characters...")
            cursor.execute("""
                SELECT id, dnd_ability_scores, dnd_hit_points, dnd_proficiency_bonus, 
                       dnd_class, dnd_level
                FROM characters
                WHERE is_dnd = 1
            """)
            
            characters = cursor.fetchall()
            print(f"   Found {len(characters)} D&D characters to migrate")
            print()
            
            migrated_count = 0
            for char in characters:
                char_id, ability_scores_json, hp, prof_bonus_str, dnd_class, dnd_level = char
                
                # Parse ability scores
                try:
                    ability_scores = json.loads(ability_scores_json) if ability_scores_json else {}
                except (json.JSONDecodeError, TypeError):
                    ability_scores = {}
                
                # Calculate ability modifiers
                ability_modifiers = {}
                for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                    score = ability_scores.get(ability, 10)
                    modifier = calculate_ability_modifier(score)
                    ability_modifiers[ability] = modifier
                
                # Calculate attack bonuses
                try:
                    prof_bonus = int(prof_bonus_str.replace("+", "")) if prof_bonus_str else 2
                except (ValueError, AttributeError, TypeError):
                    prof_bonus = 2
                
                str_mod = ability_modifiers.get("strength", 0)
                dex_mod = ability_modifiers.get("dexterity", 0)
                
                melee_attack_bonus = str_mod + prof_bonus
                ranged_attack_bonus = dex_mod + prof_bonus
                
                # Initialize resources
                resources = get_class_resources(dnd_class, dnd_level or 1)
                
                # Update character
                cursor.execute("""
                    UPDATE characters
                    SET 
                        dnd_ability_modifiers = ?,
                        dnd_melee_attack_bonus = ?,
                        dnd_ranged_attack_bonus = ?,
                        dnd_hit_points_max = ?,
                        dnd_hit_points_current = ?,
                        dnd_temporary_hp = 0,
                        dnd_conditions = '[]',
                        dnd_death_saves = ?,
                        dnd_resources = ?
                    WHERE id = ?
                """, (
                    json.dumps(ability_modifiers),
                    melee_attack_bonus,
                    ranged_attack_bonus,
                    hp,
                    hp,  # Current HP starts at max
                    json.dumps({"successes": 0, "failures": 0}),
                    json.dumps(resources),
                    char_id
                ))
                
                migrated_count += 1
                if migrated_count % 10 == 0:
                    print(f"   Migrated {migrated_count}/{len(characters)} characters...")
            
            print(f"   ✅ Successfully migrated {migrated_count} characters")
            print()
        
        print("💾 Committing changes...")
        conn.commit()
        
        print()
        print("=" * 70)
        print("✨ Migration Complete!")
        print("=" * 70)
        print(f"   ✅ Added:    {added_count} new columns")
        print(f"   ⏭️  Skipped:  {skipped_count} existing columns")
        if added_count > 0:
            print(f"   🔄 Migrated: {migrated_count} existing D&D characters")
        print()
        
        # Verify the migration
        print("🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(characters)")
        all_columns = cursor.fetchall()
        combat_columns = [col for col in all_columns if any(x in col[1] for x in ['ability_modifiers', 'attack_bonus', 'hit_points_', 'temporary_hp', 'conditions', 'death_saves', 'resources'])]
        
        print(f"   ✅ Found {len(combat_columns)} combat-related columns in database")
        print()
        
        # Show new columns
        print("📋 New combat columns:")
        for col in combat_columns:
            print(f"   • {col[1]} ({col[2]})")
        print()
        
        conn.close()
        
        print("🎉 Database is now ready for D&D combat system!")
        print()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_migration_status():
    """Check if the combat fields migration has been applied."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(characters)")
        columns = {row[1] for row in cursor.fetchall()}
        
        combat_columns = [col for col in columns if any(x in col for x in ['ability_modifiers', 'attack_bonus', 'hit_points_', 'temporary_hp', 'conditions', 'death_saves', 'resources'])]
        
        print("=" * 70)
        print("Combat Fields Migration Status")
        print("=" * 70)
        print()
        
        if combat_columns:
            print(f"✅ Migration Applied: {len(combat_columns)} combat columns found")
            print()
            print("Combat columns:")
            for col in sorted(combat_columns):
                print(f"   • {col}")
        else:
            print("❌ Migration Not Applied: No combat columns found")
            print()
            print("Run: python backend/migrations/add_combat_fields.py")
        
        print()
        conn.close()
        return bool(combat_columns)
        
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
        elif command == "migrate":
            migrate_database()
        else:
            print(f"Unknown command: {command}")
            print()
            print("Usage:")
            print("  python migrations/add_combat_fields.py          # Run migration")
            print("  python migrations/add_combat_fields.py migrate  # Run migration")
            print("  python migrations/add_combat_fields.py check    # Check status")
    else:
        # Default: Run migration
        success = migrate_database()
        sys.exit(0 if success else 1)

