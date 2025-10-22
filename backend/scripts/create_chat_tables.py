"""Create missing chat tables (development helper).

Run this script from the repo root during development to ensure new tables
are created in the SQLite database used by the app. This is NOT a
replacement for proper Alembic migrations in production.

Usage:
    python -m backend.scripts.create_chat_tables
"""
from backend.database import engine, Base
import logging

logger = logging.getLogger("backend.scripts.create_chat_tables")

def main():
    logger.info("Creating tables via Base.metadata.create_all(bind=engine)")
    Base.metadata.create_all(bind=engine)
    logger.info("Create tables completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
