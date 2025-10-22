"""Test reference search directly to debug scoring"""
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

# Test query
query = "Tell me about goblins and the fireball spell"
print(f"Query: {query}\n")

# Search all references
results = do_reference_search(q=query, ref_type=None, k=10, db=session)

print(f"Found {len(results)} results:\n")
for i, r in enumerate(results, 1):
    print(f"{i}. {r.get('title')} (ref_type: {r.get('ref_type')}, score: {r.get('score', 'N/A'):.4f})")
    
session.close()
