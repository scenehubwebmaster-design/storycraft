import sqlite3

conn = sqlite3.connect('storycraft.db')
cur = conn.cursor()

# Check distinct rarities
print("Distinct rarity values:")
cur.execute('SELECT DISTINCT rarity FROM "references" WHERE rarity IS NOT NULL ORDER BY rarity')
rarities = cur.fetchall()
for r in rarities:
    cur.execute('SELECT COUNT(*) FROM "references" WHERE rarity = ?', (r[0],))
    count = cur.fetchone()[0]
    print(f"  {r[0]}: {count}")

print("\n" + "="*50)

# Check cantrips (level 0)
print("\nCantrips (level = 0):")
cur.execute('SELECT COUNT(*) FROM "references" WHERE level = 0')
cantrip_count = cur.fetchone()[0]
print(f"  Count: {cantrip_count}")

if cantrip_count > 0:
    cur.execute('SELECT title FROM "references" WHERE level = 0 LIMIT 5')
    print("  Examples:")
    for row in cur.fetchall():
        print(f"    - {row[0]}")

print("\n" + "="*50)

# Check level distribution
print("\nSpell level distribution:")
cur.execute('SELECT level, COUNT(*) FROM "references" WHERE ref_type = "spells_md" AND level IS NOT NULL GROUP BY level ORDER BY level')
for row in cur.fetchall():
    print(f"  Level {row[0]}: {row[1]} spells")

print("\n" + "="*50)

# Check school distribution
print("\nSpell school distribution:")
cur.execute('SELECT school, COUNT(*) FROM "references" WHERE ref_type = "spells_md" AND school IS NOT NULL GROUP BY school ORDER BY school')
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} spells")

conn.close()
