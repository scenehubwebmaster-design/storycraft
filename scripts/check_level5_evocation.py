#!/usr/bin/env python3
"""Check Level 5 Evocation spells in the database."""

import sqlite3

conn = sqlite3.connect('storycraft.db')
cursor = conn.cursor()

# Get Level 5 Evocation spells
query = 'SELECT title, key FROM "references" WHERE ref_type="spells_md" AND level=5 AND school="Evocation" ORDER BY title'
cursor.execute(query)

spells = cursor.fetchall()

print(f"Level 5 Evocation Spells ({len(spells)} found):")
print("=" * 50)
for title, key in spells:
    print(f"  - {title} ({key})")

conn.close()
