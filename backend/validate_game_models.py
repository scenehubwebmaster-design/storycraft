"""Validate game models match database schema"""
import sqlite3
import sys

def check_table_schema(db_path="storycraft.db"):
    """Check if game tables exist and match expected schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    expected_tables = [
        "game_sessions",
        "party_members", 
        "combat_encounters",
        "combat_participants",
        "quests",
        "npcs",
        "inventory_items",
        "game_events",
        "game_locations"
    ]
    
    print("Validating game system tables...")
    print("=" * 60)
    
    all_valid = True
    for table in expected_tables:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ {table:25} EXISTS")
        else:
            print(f"❌ {table:25} MISSING")
            all_valid = False
    
    print("=" * 60)
    
    # Check a few key columns in critical tables
    print("\nValidating key columns...")
    print("=" * 60)
    
    # GameSession
    cursor.execute("PRAGMA table_info(game_sessions)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    expected_columns = {
        "id": "INTEGER",
        "chat_session_id": "INTEGER",
        "campaign_name": "VARCHAR(255)",
        "game_state": "JSON",
        "party_level": "INTEGER"
    }
    
    for col, dtype in expected_columns.items():
        actual = columns.get(col)
        if actual:
            print(f"✅ game_sessions.{col:20} {dtype}")
        else:
            print(f"❌ game_sessions.{col:20} MISSING")
            all_valid = False
    
    print("=" * 60)
    
    conn.close()
    
    if all_valid:
        print("\n✅ All game system tables validated successfully!")
        print("   Models should match database schema.")
        return 0
    else:
        print("\n❌ Validation failed - schema mismatch detected")
        return 1

if __name__ == "__main__":
    sys.exit(check_table_schema())
