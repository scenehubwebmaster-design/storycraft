"""Quick DB count checker for storycraft.db"""
import sqlite3
import os
DB='storycraft.db'
if not os.path.exists(DB):
    print('DB not found:', DB)
    raise SystemExit(2)

conn = sqlite3.connect(DB)
cur = conn.cursor()

tables = ['references','reference_embeddings','monster_stats','monster_embeddings','characters','stories','chat_sessions','chat_messages']
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM \"{t}\"")
        n = cur.fetchone()[0]
    except Exception as e:
        n = f'ERR: {e}'
    print(f'{t}: {n}')

cur.close()
conn.close()
