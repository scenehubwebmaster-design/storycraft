# Local migrations and Alembic

This project includes two helpers for ensuring the `characters` table has the soft-delete columns (`is_deleted`, `deleted_at`). Use the approach that fits your workflow.

## Quick local helper (recommended for local dev)

Run the lightweight script once to update your on-disk sqlite DB:

```powershell
python backend/scripts/ensure_softdelete_columns.py
```

Alternatively, start your dev server with the helper auto-run:

```powershell
$env:RUN_LOCAL_MIGRATIONS = "true"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

> Warning: `RUN_LOCAL_MIGRATIONS` is intended for local development only. Do not enable in production.

## Alembic (recommended for controlled deployments)

We include a minimal Alembic scaffold in `backend/alembic/` and a migration file in `backend/alembic/versions/` to add the soft-delete columns.

To run the migration with Alembic:

1. Install alembic in your environment (dev deps):

```bash
pip install alembic
```

2. Update `backend/alembic.ini` `sqlalchemy.url` to point to your database or set `DATABASE_URL` env var as appropriate.

3. Run the migration:

```bash
alembic -c backend/alembic.ini upgrade head
```

Notes:

- The included migration uses raw `ALTER TABLE` statements for sqlite. For other DBs it uses `op.add_column`.
- Downgrading the sqlite migration is not implemented because dropping columns in sqlite is non-trivial. If you require reversible migrations, consider using PostgreSQL or implement a table-copy migration.

### Note about previously-applied helper

If you already ran the quick local helper (`ensure_softdelete_columns.py`) before running Alembic, the helper will have added the soft-delete columns and an Alembic `upgrade` may fail with `duplicate column` errors.

In that case either:

- Run `alembic -c backend/alembic.ini stamp head` to mark the migration as applied (no schema changes will be executed), or
- Re-run `alembic upgrade` after the migration file has been made idempotent (the migration in this repo now checks for existing columns and will skip adding them).

## Best practice

- Use the Alembic migration when deploying or on CI to keep schema history consistent across environments.
- Use the quick helper only for local developer convenience.
