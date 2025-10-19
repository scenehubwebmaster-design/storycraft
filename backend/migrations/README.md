This folder holds Alembic-style migration scripts. The repository may not be configured for Alembic by default.

If you use Alembic, these are the steps to apply the migration added here:

1. Install alembic (if not installed):
   pip install alembic

2. Ensure your alembic.ini is configured to use the same SQLALCHEMY_DATABASE_URL as your application (e.g., sqlite:///./storycraft.db or your production DB URL).

3. Place the migration script from `backend/migrations/versions/20251018_add_world_location_image_fields.py` into your Alembic versions directory.

4. Run the migration:

   alembic upgrade head

Notes:

- The migration attempts to add a self-referential FK for `locations.parent_location_id` -> `locations.id`. Some DB backends (SQLite) require special handling for altering constraints; if the FK creation fails, the script continues and you can create the FK in a follow-up migration or manage it manually.
- For production, always backup your DB before running migrations.
