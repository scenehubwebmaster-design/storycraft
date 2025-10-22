import sqlite3
conn = sqlite3.connect('storycraft.db')
cur = conn.cursor()
cur.execute('SELECT ref_type, COUNT(*) FROM "references" GROUP BY ref_type')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]}')
conn.close()
