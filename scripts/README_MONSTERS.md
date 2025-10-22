Monster ingestion for StoryCraft

Files added:

- create_monster_stats.sql: SQL migration that creates the `monster_stats` table.
- ingest_monsters.py: Python script that scrapes 5thsrd.org and upserts monster records.

Quick start (Windows cmd.exe):

1. Install requirements (in repository root):
   python -m pip install -r requirements.txt

2. Run the script against your DB:
   python scripts\ingest_monsters.py --db e:\\storycraft\\storycraft.db

Notes:

- The parser is intentionally conservative: it extracts quick fields and stores full page HTML in `raw_html` for richer future parsing.
- This code is for ingesting SRD content. Verify licensing and attribution requirements before distributing.
