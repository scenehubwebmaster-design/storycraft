DB migrations helper

This repository uses SQLAlchemy ORM models declared in `backend/models.py`.

Development helper

A small helper script exists to create any missing tables in the configured
SQLAlchemy engine. This is only suitable for local development and quick
manual fixes:

    python -m backend.scripts.create_chat_tables

Production migrations

For production deployments, you should use Alembic to generate deterministic
schema migration scripts and apply them under CI/ops. The helper above is not a
substitute for schema migration discipline.
