"""Debug why Fireball spell isn't ranking high."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference, ReferenceEmbedding
from sentence_transformers import SentenceTransformer
import json
import math

def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)

engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
session = Session()

# Load the Fireball spell specifically
fireball = session.query(Reference).filter(Reference.id == 696).first()
fireball_emb = session.query(ReferenceEmbedding).filter(ReferenceEmbedding.reference_id == 696).first()

if not fireball or not fireball_emb:
    print("Fireball not found!")
    session.close()
    exit(1)

print(f"Found: {fireball.title} ({fireball.ref_type})")
print(f"Content preview: {fireball.content[:200] if fireball.content else 'None'}...")
print()

# Load model and encode query
model = SentenceTransformer('all-MiniLM-L6-v2')
queries = [
    "fireball",
    "Tell me about goblins and the fireball spell",
    "fire magic spell area damage",
    "3rd level evocation spell"
]

fireball_vec = json.loads(fireball_emb.vector)

for query in queries:
    qv = model.encode(query).tolist()
    similarity = cosine(qv, fireball_vec)
    
    # Calculate keyword score
    query_lower = query.lower()
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'about', 'tell', 'me'}
    query_tokens = [w for w in query_lower.split() if w not in stopwords]
    
    title_lower = (fireball.title or '').lower()
    content_lower = (fireball.content or '').lower()[:1000]
    
    keyword_score = 0.0
    if query_lower in title_lower:
        keyword_score += 0.5
    for token in query_tokens:
        if token in title_lower:
            keyword_score += 0.3
    for token in query_tokens:
        if token in content_lower:
            keyword_score += 0.1
    if query_tokens:
        matches = sum(1 for t in query_tokens if t in title_lower or t in content_lower)
        keyword_score += 0.05 * matches / len(query_tokens)
    
    final_score = 0.7 * similarity + 0.3 * keyword_score
    
    print(f"Query: '{query}'")
    print(f"  Embedding similarity: {similarity:.4f}")
    print(f"  Keyword score: {keyword_score:.4f}")
    print(f"  Final score: {final_score:.4f}")
    print()

session.close()
