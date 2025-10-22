import sqlite3
c=sqlite3.connect('storycraft.db')
r=list(c.execute('SELECT id, name, cr FROM monster_stats WHERE lower(name) LIKE "%goblin%"'))
print('Monsters:', r if r else 'No goblins found')
r2=list(c.execute('SELECT id, ref_type, title FROM "references" WHERE lower(title) LIKE "%goblin%"'))
print('References:', r2 if r2 else 'No goblin references found')
c.close()
