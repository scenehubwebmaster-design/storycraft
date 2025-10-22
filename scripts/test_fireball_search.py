"""Test search for just 'fireball'"""
import sys
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.routers.references import do_reference_search

db_path = DEFAULT_DB_FILE
engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

# Test query - just fireball
query = "fireball"
print(f"Query: {query}\n")

# Search spells only
results = do_reference_search(q=query, ref_type='spells_md', k=10, db=session)

print(f"Found {len(results)} spell results:\n")
for i, r in enumerate(results, 1):
    print(f"{i}. {r.get('title')} (score: {r.get('score', 'N/A'):.4f})")
    
session.close()
