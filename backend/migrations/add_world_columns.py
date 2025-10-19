#!/usr/bin/env python3
"""
Simple SQLite migration script to add missing columns to the worlds table.
Run from the backend directory where storycraft.db is accessible.
"""
import sqlite3

import os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'storycraft.db')

NEW_COLUMNS = [
    ("world_image", "TEXT"),
    ("world_map", "TEXT"),
    ("image_prompt", "TEXT"),
    ("structured_data", "TEXT"),
    ("climate", "TEXT"),
    ("population_level", "TEXT"),
    ("danger_level", "TEXT"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Get existing columns
cur.execute("PRAGMA table_info(worlds);")
cols = [r[1] for r in cur.fetchall()]

for name, ctype in NEW_COLUMNS:
    if name in cols:
        print(f"Column {name} already exists, skipping")
    else:
        sql = f"ALTER TABLE worlds ADD COLUMN {name} {ctype};"
        print(f"Adding column: {name} {ctype}")
        cur.execute(sql)

conn.commit()
conn.close()
print("Migration complete")
