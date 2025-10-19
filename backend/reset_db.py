"""
Simple script to drop and recreate the SQLite database tables using SQLAlchemy models.
Use with caution: this will delete existing data.
"""
from backend.database import engine, Base
# import models to ensure metadata is registered
import backend.models  # noqa: F401

if __name__ == "__main__":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Database reinitialized.")
