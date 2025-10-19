This project uses SQLAlchemy models defined in `backend/models.py`.

The recent world/location model changes added the following new columns:

Worlds table additions:

- world_image TEXT
- world_map TEXT
- image_prompt TEXT
- climate VARCHAR(100)
- population_level VARCHAR(50)
- danger_level VARCHAR(50)

Locations table additions:

- location_image TEXT
- image_prompt TEXT
- parent_location_id INTEGER (FK -> locations.id)
- coordinates VARCHAR(50)
- notable_features TEXT
- inhabitants TEXT

How to apply these changes (manual SQL example):

1. If you are using SQLite or a DB without automatic migrations, run SQL commands similar to:

ALTER TABLE worlds ADD COLUMN world_image TEXT;
ALTER TABLE worlds ADD COLUMN world_map TEXT;
ALTER TABLE worlds ADD COLUMN image_prompt TEXT;
ALTER TABLE worlds ADD COLUMN climate VARCHAR(100);
ALTER TABLE worlds ADD COLUMN population_level VARCHAR(50);
ALTER TABLE worlds ADD COLUMN danger_level VARCHAR(50);

ALTER TABLE locations ADD COLUMN location_image TEXT;
ALTER TABLE locations ADD COLUMN image_prompt TEXT;
ALTER TABLE locations ADD COLUMN parent_location_id INTEGER;
ALTER TABLE locations ADD COLUMN coordinates VARCHAR(50);
ALTER TABLE locations ADD COLUMN notable_features TEXT;
ALTER TABLE locations ADD COLUMN inhabitants TEXT;

2. If you use Alembic or another migration tool, create a new migration script that includes the above ALTER TABLE statements and run the migration.

3. After applying DB changes, restart the backend server.

Notes:

- parent_location_id should reference `locations.id`. If you enforce the FK, ensure circular dependencies are handled (some DBs need to add the column first and then create the FK constraint).
- For production deployments, back up your database before applying schema changes.
- If your DB backend requires different types or syntax (Postgres, MySQL), adapt the SQL types accordingly.

If you'd like, I can generate an Alembic migration script or a one-off Python script to apply these ALTER TABLE commands—tell me which DB backend you use and I'll prepare it.
