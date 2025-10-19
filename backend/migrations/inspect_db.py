import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'storycraft.db')

if not os.path.exists(DB_PATH):
    print('DB missing', DB_PATH)
else:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print('Tables:')
    rows = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for row in rows:
        print(' ', row[0])

    print('\nPRAGMA table_info(worlds):')
    try:
        cols = cur.execute("PRAGMA table_info(worlds)").fetchall()
        for r in cols:
            print(' ', r)
    except Exception as e:
        print('  error', e)
    conn.close()
