"""
Test chunk-based search functionality.
Direct test without importing routers.
"""

import sys
import os
import json
import math

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from database import SessionLocal
from models import Reference, ChunkEmbedding, DocumentChunk
from sentence_transformers import SentenceTransformer

def cosine(a, b):
    """Compute cosine similarity between two vectors."""
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)

def chunk_search_test(query: str, k: int = 5, chunks_per_doc: int = 2):
    """Test chunk-based search directly."""
    db = SessionLocal()
    
    try:
        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate query vector
        qv = model.encode(query).tolist()
        
        # Get all chunks (no filters for testing)
        chunks = db.query(DocumentChunk).all()
        print(f"Total chunks in database: {len(chunks)}")
        
        # Load chunk embeddings
        chunk_ids = [c.id for c in chunks]
        embeddings = db.query(ChunkEmbedding).filter(ChunkEmbedding.chunk_id.in_(chunk_ids)).all()
        vec_map = {e.chunk_id: json.loads(e.vector) for e in embeddings}
        print(f"Chunk embeddings loaded: {len(vec_map)}")
        
        # Score all chunks
        chunk_scores = []
        for chunk in chunks:
            if chunk.id in vec_map:
                score = cosine(qv, vec_map[chunk.id])
                chunk_scores.append((score, chunk))
        
        # Sort chunks by score
        chunk_scores.sort(key=lambda x: x[0], reverse=True)
        
        # Group chunks by parent document
        doc_chunks = {}  # source_id -> [(score, chunk), ...]
        for score, chunk in chunk_scores:
            if chunk.source_id not in doc_chunks:
                doc_chunks[chunk.source_id] = []
            if len(doc_chunks[chunk.source_id]) < chunks_per_doc:
                doc_chunks[chunk.source_id].append((score, chunk))
        
        # Calculate document scores
        doc_scores = []
        for source_id, chunks_list in doc_chunks.items():
            # Get parent reference
            ref = db.query(Reference).filter(Reference.id == source_id).first()
            if not ref:
                continue
            
            avg_score = sum(s for s, _ in chunks_list) / len(chunks_list)
            
            doc_scores.append({
                'title': ref.title,
                'ref_type': ref.ref_type,
                'score': avg_score,
                'chunks': [
                    {
                        'heading': chunk.heading,
                        'text': chunk.chunk_text[:300],
                        'chunk_index': chunk.chunk_index,
                        'chunk_score': score
                    }
                    for score, chunk in chunks_list
                ]
            })
        
        # Sort documents by score
        doc_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return doc_scores[:k]
        
    finally:
        db.close()

def print_results(query: str, results: list):
    """Print search results nicely."""
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}\n")
    
    if not results:
        print("  No results found\n")
        return
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Type: {result['ref_type']}")
        
        if 'chunks' in result:
            print(f"   Chunks: {len(result['chunks'])}")
            for j, chunk in enumerate(result['chunks'], 1):
                print(f"\n   Chunk {j} (index {chunk['chunk_index']}):")
                if chunk['heading']:
                    print(f"     Heading: {chunk['heading']}")
                print(f"     Score: {chunk['chunk_score']:.4f}")
                # Clean up text for display
                text = chunk['text'].replace('\n', ' ').strip()
                print(f"     Text: {text[:200]}...")
        
        print()

# Test cases
if __name__ == "__main__":
    print("CHUNK-BASED SEARCH TESTS")
    print("="*80)
    
    # Test 1: Specific spell section
    print("\n\nTest 1: Wish spell consequences")
    results = chunk_search_test("What are the consequences of using the Wish spell?", k=3)
    print_results("What are the consequences of using the Wish spell?", results)
    
    # Test 2: Barbarian rage
    print("\n\nTest 2: Barbarian rage mechanics")
    results = chunk_search_test("How does a barbarian's rage work?", k=3)
    print_results("How does a barbarian's rage work?", results)
    
    # Test 3: Fireball spell
    print("\n\nTest 3: Fireball spell")
    results = chunk_search_test("fireball", k=5)
    print_results("fireball", results)
    
    # Test 4: Opportunity attacks
    print("\n\nTest 4: Opportunity attacks")
    results = chunk_search_test("How do opportunity attacks work in combat?", k=3)
    print_results("How do opportunity attacks work in combat?", results)
    
    print("\n\n✅ All chunk search tests completed!")
