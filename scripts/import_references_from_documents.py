"""Import reference markdown files from documents/reference into the SQLite references table.

Maps folders to ref_type:
 - monsters_md -> species
 - magic_items_md -> equipment
 - spells_md -> other

Usage:
  python scripts\import_references_from_documents.py --db e:\\storycraft\\storycraft.db
"""
from __future__ import annotations
import argparse
import sqlite3
import pathlib
import os
from datetime import datetime

FOLDER_MAPPING = {
    'classes_md': 'classes_md',
    'equipment_md': 'equipment_md',
    'magic_items_md': 'magic_items_md',
    'monsters_md': 'monsters_md',
    'species_md': 'species_md',
    'spells_md': 'spells_md',
    'tools_md': 'tools_md',
    'weapons_md': 'weapons_md',
}


def strip_frontmatter(text: str) -> str:
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            return parts[2].lstrip('\n')
    return text


def human_title(stem: str) -> str:
    # replace underscores with spaces and capitalize
    return stem.replace('_', ' ').replace('-', ' ').title()


def import_folder(conn: sqlite3.Connection, folder: pathlib.Path, ref_type: str) -> int:
    imported = 0
    cur = conn.cursor()
    for p in folder.rglob('*.md'):
        try:
            content = p.read_text(encoding='utf-8')
        except Exception:
            continue
        body = strip_frontmatter(content)
        stem = p.stem
        key = stem.lower()
        title = human_title(stem)
        now = datetime.utcnow().isoformat()

        # check existing
        cur.execute('SELECT id FROM "references" WHERE key = ? AND ref_type = ?', (key, ref_type))
        row = cur.fetchone()
        if row:
            cur.execute(
                'UPDATE "references" SET title = ?, content = ?, updated_at = ? WHERE id = ?',
                (title, body, now, row[0]),
            )
        else:
            cur.execute(
                'INSERT INTO "references" (ref_type, key, title, content, source_url, created_at, updated_at) VALUES (?,?,?,?,?,?,?)',
                (ref_type, key, title, body, None, now, now),
            )
        imported += 1
    conn.commit()
    return imported


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True, help='Path to storycraft.db')
    p.add_argument('--docs-root', default=None, help='Path to documents folder (default repo documents)')
    args = p.parse_args()

    db_path = os.path.abspath(args.db)
    if not os.path.exists(db_path):
        print('DB not found:', db_path)
        return 2

    # find repo root from this script location
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    docs_root = args.docs_root or os.path.join(repo_root, 'documents')
    docs_root = os.path.abspath(docs_root)
    if not os.path.isdir(docs_root):
        print('Documents folder not found at', docs_root)
        return 2

    conn = sqlite3.connect(db_path)
    total = 0
    for folder_name, ref_type in FOLDER_MAPPING.items():
        folder = pathlib.Path(docs_root) / 'reference' / folder_name
        if not folder.exists():
            print('Skipping missing folder:', folder)
            continue
        print('Importing', folder_name, 'as', ref_type)
        count = import_folder(conn, folder, ref_type)
        print(f'  Imported {count} files from {folder_name}')
        total += count

    conn.close()
    print('Done. Total imported:', total)


if __name__ == '__main__':
    raise SystemExit(main())
