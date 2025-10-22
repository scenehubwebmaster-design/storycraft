"""Test the improved semantic search with real embeddings."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.routers.references import do_reference_search

engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

# Test query
query = "Tell me about goblins and the fireball spell"

print(f"Testing search with real semantic embeddings...")
print(f"Query: {query}")
print()

results = do_reference_search(q=query, ref_type=None, k=10, db=session)

print(f"Top 10 results:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['title']}")
    print(f"   Type: {result['ref_type']}")
    print(f"   Score: {result['score']:.4f}")
    if '_debug_emb_score' in result:
        print(f"   Embedding: {result['_debug_emb_score']:.4f}, Keyword: {result['_debug_keyword_score']:.4f}")

session.close()
