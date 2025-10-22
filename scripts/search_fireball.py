import sqlite3
c=sqlite3.connect('storycraft.db')
r=list(c.execute('SELECT id, ref_type, title FROM "references" WHERE lower(title) LIKE "%fireball%" OR lower(key) LIKE "%fireball%"'))
print(r if r else 'No fireball found')
c.close()
