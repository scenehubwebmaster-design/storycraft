import sqlite3

conn = sqlite3.connect('storycraft.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Total tables: {len(tables)}")
print("\nAll tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if game_sessions exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='game_sessions'")
game_sess = cursor.fetchone()
print(f"\ngame_sessions exists: {game_sess is not None}")

conn.close()
