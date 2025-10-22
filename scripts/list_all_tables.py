import sqlite3
c=sqlite3.connect('storycraft.db')
tables=[r[0] for r in c.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')]
for t in tables:
    print(t)
c.close()
