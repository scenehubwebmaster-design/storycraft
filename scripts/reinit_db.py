"""Create a fresh storycraft.db using backend.models.Base.metadata.create_all
Useful for reinitializing the local development DB.
"""
import os
import sys
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.models import Base
from sqlalchemy import create_engine

DB_PATH = os.path.abspath(os.path.join(os.getcwd(), 'storycraft.db'))
print('DB path:', DB_PATH)
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
print('Created schema on', DB_PATH)
