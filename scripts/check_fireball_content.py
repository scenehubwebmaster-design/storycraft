import sqlite3

conn = sqlite3.connect('storycraft.db')
cur = conn.cursor()
cur.execute('SELECT id, title, ref_type, substr(content, 1, 200) FROM "references" WHERE lower(title) = "fireball"')
rows = cur.fetchall()

if rows:
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Title: {row[1]}")
        print(f"Type: {row[2]}")
        print(f"Content preview: {row[3]}")
        print()
else:
    print("No exact 'Fireball' match found. Searching for partial...")
    cur.execute('SELECT id, title, ref_type FROM "references" WHERE lower(title) LIKE "%fireball%"')
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Title: {row[1]}, Type: {row[2]}")

conn.close()
