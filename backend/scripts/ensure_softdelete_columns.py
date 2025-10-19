"""
Ensure the characters table has soft-delete columns (is_deleted, deleted_at).
Run once in development to migrate the on-disk SQLite DB used by the dev server.

Usage:
    python backend/scripts/ensure_softdelete_columns.py

This script is intentionally simple (no alembic). It inspects sqlite pragma and
adds columns via ALTER TABLE if they are missing. Safe to re-run.
"""
import sys
import os
from sqlalchemy import text


def ensure_columns(engine):
    missing = []
    with engine.connect() as conn:
        # Detect dialect
        dialect = conn.dialect.name
        if dialect != 'sqlite':
            print(f"This script only supports sqlite databases. Detected: {dialect}")
            return False

        # Check existing columns
        res = conn.execute(text("PRAGMA table_info('characters');")).fetchall()
        cols = {r[1] for r in res}  # second column is name
        print("Existing columns:", cols)

        if 'is_deleted' not in cols:
            print("Adding column is_deleted (BOOLEAN DEFAULT 0 NOT NULL)")
            try:
                conn.execute(text("ALTER TABLE characters ADD COLUMN is_deleted BOOLEAN DEFAULT 0 NOT NULL;"))
            except Exception as e:
                print("Failed to add is_deleted:", e)
                missing.append('is_deleted')
        else:
            print("is_deleted already present")

        if 'deleted_at' not in cols:
            print("Adding column deleted_at (DATETIME NULL)")
            try:
                conn.execute(text("ALTER TABLE characters ADD COLUMN deleted_at DATETIME NULL;"))
            except Exception as e:
                print("Failed to add deleted_at:", e)
                missing.append('deleted_at')
        else:
            print("deleted_at already present")

    if missing:
        print("Some columns failed to be added:", missing)
        return False

    print("Done. Soft-delete columns ensured.")
    return True


def main():
    # Import engine path from package
    try:
        from backend.database import engine
    except Exception:
        # allow running from repo root when backend isn't a package
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from backend.database import engine

    ok = ensure_columns(engine)
    if not ok:
        sys.exit(2)


if __name__ == '__main__':
    main()
