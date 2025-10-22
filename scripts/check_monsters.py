import sqlite3
import sys

db = 'e:/storycraft/storycraft.db'
if len(sys.argv) > 1:
    db = sys.argv[1]

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM sqlite_master WHERE name='monster_stats'")
exists = cur.fetchone()[0]
if not exists:
    print('monster_stats table not found')
    sys.exit(1)
cur.execute('SELECT count(*) FROM monster_stats')
count = cur.fetchone()[0]
print('monster_stats rows:', count)
cur.execute('SELECT name, cr, ac, hp FROM monster_stats LIMIT 5')
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
