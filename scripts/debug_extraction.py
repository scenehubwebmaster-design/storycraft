import sqlite3

conn = sqlite3.connect('storycraft.db')
cur = conn.cursor()

# Find a cantrip by name
print("Checking Fire Bolt (should be a cantrip):")
cur.execute('SELECT title, level, school, substr(content, 1, 300) FROM "references" WHERE title = "Fire Bolt"')
row = cur.fetchone()
if row:
    print(f"Title: {row[0]}")
    print(f"Level: {row[1]}")
    print(f"School: {row[2]}")
    print(f"Content: {row[3]}")
else:
    print("Not found!")

print("\n" + "="*70 + "\n")

# Find a magic item and check its rarity text
print("Checking a magic item for rarity format:")
cur.execute('SELECT title, rarity, substr(content, 1, 500) FROM "references" WHERE ref_type = "magic_items_md" LIMIT 1')
row = cur.fetchone()
if row:
    print(f"Title: {row[0]}")
    print(f"Extracted Rarity: {row[1]}")
    print(f"Content: {row[2]}")

print("\n" + "="*70 + "\n")

# Search for "uncommon" in content
print("Searching for items with 'uncommon' in content:")
cur.execute('SELECT title, rarity, substr(content, 1, 200) FROM "references" WHERE ref_type = "magic_items_md" AND lower(content) LIKE "%uncommon%" LIMIT 3')
for row in cur.fetchall():
    print(f"\nTitle: {row[0]}")
    print(f"Extracted Rarity: {row[1]}")
    print(f"Content snippet: {row[2][:150]}...")

conn.close()
