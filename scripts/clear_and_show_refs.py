import sqlite3
conn=sqlite3.connect('storycraft.db')
cur=conn.cursor()
print('Existing counts before clear:')
for r in cur.execute('SELECT ref_type, COUNT(*) FROM "references" GROUP BY ref_type ORDER BY COUNT(*) DESC'):
    print(r)
cur.execute('DELETE FROM "references"')
conn.commit()
print('Cleared references table')
conn.close()
