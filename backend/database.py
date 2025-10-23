from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
try:
    # SQLAlchemy 2.0
    from sqlalchemy.orm import declarative_base
except Exception:
    # Fallback for older SQLAlchemy versions
    from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration - prefer an absolute path so all processes use the same file
# Database is stored in PROJECT ROOT to consolidate all data including RAG embeddings
# This 490MB file contains: campaigns, characters, chat history, and 52K+ RAG embeddings
DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storycraft.db'))
# Allow tests to run against an isolated in-memory database to avoid stale
# on-disk schemas (pytest sets PYTEST_CURRENT_TEST in the environment).
pytest_env = any(k.startswith('PYTEST') for k in os.environ.keys())
if pytest_env:
    # Running under pytest - use an in-memory DB for isolation
    SQLALCHEMY_DATABASE_URL = os.environ.get('STORYCRAFT_DATABASE_URL', "sqlite:///:memory:")
else:
    SQLALCHEMY_DATABASE_URL = os.environ.get('STORYCRAFT_DATABASE_URL', f"sqlite:///{DEFAULT_DB_FILE}")

# Create engine
if SQLALCHEMY_DATABASE_URL.startswith('sqlite') and (':memory:' in SQLALCHEMY_DATABASE_URL):
    # Use StaticPool so the in-memory DB is shared across connections during tests
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
        future=True,
    )
else:
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
