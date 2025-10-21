#!/usr/bin/env python3
"""
Safe normalization script for references table.

What it does:
- Creates a timestamped backup of storycraft.db in tools/backups/
- Connects to the SQLite DB and updates ref_type to 'class' for known class keys
- Optionally deduplicates rows by (key, ref_type) keeping the newest updated_at

Usage:
  python tools/normalize_references.py --db e:/storycraft/storycraft.db --apply

Run without --apply for a dry-run report.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import datetime
from typing import Iterable


COMMON_CLASSES = {
    'barbarian','bard','cleric','druid','fighter','monk','paladin','ranger','rogue','sorcerer','warlock','wizard'
}


def backup_db(db_path: str) -> str:
    os.makedirs('tools/backups', exist_ok=True)
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dest = os.path.join('tools', 'backups', f'storycraft.db.backup.{ts}')
    shutil.copy2(db_path, dest)
    return dest


def find_class_keys(conn: sqlite3.Connection) -> Iterable[str]:
    cur = conn.cursor()
    cur.execute('SELECT key, ref_type FROM "references"')
    for key, ref_type in cur.fetchall():
        # key format like 'druid_phb2024' — check prefix
        prefix = key.split('_', 1)[0].lower()
        if prefix in COMMON_CLASSES:
            yield key
        elif ref_type and ref_type.lower() in COMMON_CLASSES:
            yield key


def dry_run_report(conn: sqlite3.Connection):
    keys = sorted(set(find_class_keys(conn)))
    print(f"Found {len(keys)} candidate keys that should be ref_type='class':")
    for k in keys:
        print(' -', k)


def apply_normalization(conn: sqlite3.Connection):
    cur = conn.cursor()
    # Update rows where key prefix is in COMMON_CLASSES OR ref_type in COMMON_CLASSES
    placeholders = ','.join('?' for _ in COMMON_CLASSES)
    prefixes = tuple(COMMON_CLASSES)

    # Update by key prefix
    for cls in COMMON_CLASSES:
        cur.execute(
            "UPDATE \"references\" SET ref_type = 'class' WHERE lower(substr(key,1,instr(key,'_')-1)) = ?",
            (cls,)
        )

    # Update rows where ref_type is a class name
    cur.execute(
        f"UPDATE \"references\" SET ref_type = 'class' WHERE lower(ref_type) IN ({placeholders})",
        prefixes,
    )

    conn.commit()

    # Deduplicate: for same (key, ref_type) keep the newest updated_at, delete others
    cur.execute(
        'SELECT key, ref_type, COUNT(*) as cnt FROM "references" GROUP BY key, ref_type HAVING cnt > 1'
    )
    dup_groups = cur.fetchall()
    removed = 0
    for key, ref_type, cnt in dup_groups:
        cur.execute(
            'SELECT id FROM "references" WHERE key = ? AND ref_type = ? ORDER BY datetime(updated_at) DESC',
            (key, ref_type),
        )
        ids = [r[0] for r in cur.fetchall()]
        to_delete = ids[1:]
        if to_delete:
            cur.execute(
                f'DELETE FROM "references" WHERE id IN ({','.join('?' for _ in to_delete)})',
                tuple(to_delete),
            )
            removed += len(to_delete)

    conn.commit()
    print(f"Normalization applied. Removed {removed} duplicate rows.")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--db', default='storycraft.db', help='Path to SQLite DB')
    p.add_argument('--apply', action='store_true', help='Actually apply changes (otherwise dry-run)')
    args = p.parse_args(argv)

    db_path = os.path.abspath(args.db)
    if not os.path.exists(db_path):
        print('DB not found:', db_path)
        return 2

    if args.apply:
        print('Creating DB backup...')
        bk = backup_db(db_path)
        print('Backup created at', bk)

    conn = sqlite3.connect(db_path)
    try:
        if args.apply:
            apply_normalization(conn)
        else:
            dry_run_report(conn)
    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
