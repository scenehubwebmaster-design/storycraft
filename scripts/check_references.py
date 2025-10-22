import sqlite3
import sys

db = 'e:/storycraft/storycraft.db'
if len(sys.argv) > 1:
    db = sys.argv[1]

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM sqlite_master WHERE name='references'")
if cur.fetchone()[0]==0:
    print('references table not found')
    sys.exit(1)
cur.execute('SELECT ref_type, COUNT(*) FROM "references" GROUP BY ref_type')
for r in cur.fetchall():
    print(r)
print('\nSample entries:')
cur.execute('SELECT id, ref_type, key, title FROM "references" ORDER BY ref_type, title LIMIT 10')
for r in cur.fetchall():
    print(r)
conn.close()
