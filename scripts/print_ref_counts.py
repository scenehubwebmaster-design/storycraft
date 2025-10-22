import sqlite3
c=sqlite3.connect('storycraft.db')
rows=list(c.execute('SELECT ref_type, COUNT(*) FROM "references" GROUP BY ref_type ORDER BY COUNT(*) DESC'))
for r in rows:
    print(r[0], r[1])
c.close()
