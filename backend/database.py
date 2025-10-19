from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration - prefer an absolute path so all processes use the same file
# Keep backward-compatible relative URL if an env var overrides it
DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))
SQLALCHEMY_DATABASE_URL = os.environ.get('STORYCRAFT_DATABASE_URL', f"sqlite:///{DEFAULT_DB_FILE}")

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
