"""
Manually create game system tables.
Run this instead of the problematic alembic migration.
"""
import sqlite3
import os

# Database path - use root storycraft.db
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'storycraft.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop any partial tables if they exist
tables_to_drop = [
    'game_locations', 'game_events', 'inventory_items', 'npcs', 'quests',
    'combat_participants', 'combat_encounters', 'party_members', 'game_sessions'
]

for table in tables_to_drop:
    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
        print(f"Dropped {table} (if existed)")
    except Exception as e:
        print(f"Error dropping {table}: {e}")

conn.commit()

# Now create all tables
print("\nCreating game system tables...")

# 1. Game sessions
cursor.execute('''
    CREATE TABLE game_sessions (
        id INTEGER PRIMARY KEY,
        chat_session_id INTEGER REFERENCES chat_sessions(id),
        campaign_name TEXT,
        current_location TEXT,
        current_scene TEXT,
        game_state TEXT,
        party_level INTEGER DEFAULT 1,
        session_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('CREATE INDEX ix_game_sessions_chat_session_id ON game_sessions(chat_session_id)')
print("✓ game_sessions")

# 2. Party members
cursor.execute('''
    CREATE TABLE party_members (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        character_id INTEGER NOT NULL REFERENCES characters(id),
        current_hp INTEGER,
        max_hp INTEGER,
        temp_hp INTEGER DEFAULT 0,
        conditions TEXT,
        position TEXT,
        is_active BOOLEAN DEFAULT 1,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('CREATE INDEX ix_party_members_game_session_id ON party_members(game_session_id)')
cursor.execute('CREATE INDEX ix_party_members_character_id ON party_members(character_id)')
print("✓ party_members")

# 3. Combat encounters
cursor.execute('''
    CREATE TABLE combat_encounters (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        name TEXT,
        description TEXT,
        difficulty TEXT,
        is_active BOOLEAN DEFAULT 0,
        turn_order TEXT,
        current_turn INTEGER DEFAULT 0,
        round_number INTEGER DEFAULT 1,
        started_at DATETIME,
        ended_at DATETIME
    )
''')
cursor.execute('CREATE INDEX ix_combat_encounters_game_session_id ON combat_encounters(game_session_id)')
cursor.execute('CREATE INDEX ix_combat_encounters_is_active ON combat_encounters(is_active)')
print("✓ combat_encounters")

# 4. Combat participants
cursor.execute('''
    CREATE TABLE combat_participants (
        id INTEGER PRIMARY KEY,
        encounter_id INTEGER NOT NULL REFERENCES combat_encounters(id) ON DELETE CASCADE,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        name TEXT NOT NULL,
        initiative INTEGER NOT NULL,
        current_hp INTEGER NOT NULL,
        max_hp INTEGER NOT NULL,
        ac INTEGER NOT NULL,
        conditions TEXT,
        position TEXT,
        is_alive BOOLEAN DEFAULT 1
    )
''')
cursor.execute('CREATE INDEX ix_combat_participants_encounter_id ON combat_participants(encounter_id)')
print("✓ combat_participants")

# 5. Quests
cursor.execute('''
    CREATE TABLE quests (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT,
        quest_giver TEXT,
        objectives TEXT,
        status TEXT DEFAULT 'active',
        reward TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    )
''')
cursor.execute('CREATE INDEX ix_quests_game_session_id ON quests(game_session_id)')
cursor.execute('CREATE INDEX ix_quests_status ON quests(status)')
print("✓ quests")

# 6. NPCs
cursor.execute('''
    CREATE TABLE npcs (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        role TEXT,
        location TEXT,
        personality TEXT,
        relationship_to_party INTEGER DEFAULT 0,
        dialogue_history TEXT,
        is_alive BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('CREATE INDEX ix_npcs_game_session_id ON npcs(game_session_id)')
print("✓ npcs")

# 7. Inventory items
cursor.execute('''
    CREATE TABLE inventory_items (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        character_id INTEGER REFERENCES characters(id),
        item_reference_id INTEGER REFERENCES "references"(id),
        item_name TEXT NOT NULL,
        quantity INTEGER DEFAULT 1,
        is_equipped BOOLEAN DEFAULT 0,
        description TEXT,
        acquired_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('CREATE INDEX ix_inventory_items_game_session_id ON inventory_items(game_session_id)')
cursor.execute('CREATE INDEX ix_inventory_items_character_id ON inventory_items(character_id)')
print("✓ inventory_items")

# 8. Game events
cursor.execute('''
    CREATE TABLE game_events (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        game_state_snapshot TEXT,
        turn_number INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
cursor.execute('CREATE INDEX ix_game_events_game_session_id ON game_events(game_session_id)')
cursor.execute('CREATE INDEX ix_game_events_event_type ON game_events(event_type)')
cursor.execute('CREATE INDEX ix_game_events_created_at ON game_events(created_at)')
print("✓ game_events")

# 9. Game locations
cursor.execute('''
    CREATE TABLE game_locations (
        id INTEGER PRIMARY KEY,
        game_session_id INTEGER NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        description TEXT,
        location_type TEXT,
        parent_location_id INTEGER REFERENCES game_locations(id),
        features TEXT,
        connections TEXT,
        is_explored BOOLEAN DEFAULT 0,
        discovered_at DATETIME
    )
''')
cursor.execute('CREATE INDEX ix_game_locations_game_session_id ON game_locations(game_session_id)')
cursor.execute('CREATE INDEX ix_game_locations_parent_location_id ON game_locations(parent_location_id)')
print("✓ game_locations")

conn.commit()
conn.close()

print("\n✅ All game system tables created successfully!")
print("\nNext steps:")
print("  1. Update models.py with SQLAlchemy models")
print("  2. Create backend/game/session_manager.py")
print("  3. Create backend/routers/game.py")
