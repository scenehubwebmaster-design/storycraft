"""
Test chunk-based search functionality.
Compares full-document search vs chunk-based search.
"""

import sys
import os

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# Change to backend directory for relative imports
os.chdir(backend_path)

from database import SessionLocal
from routers.references import do_reference_search, do_chunk_search

def print_separator():
    print("\n" + "="*80 + "\n")

def test_search_comparison(query: str, k: int = 5):
    """Compare full-document search vs chunk-based search."""
    print(f"Query: '{query}'")
    print_separator()
    
    db = SessionLocal()
    
    try:
        # Full document search
        print("📄 FULL DOCUMENT SEARCH:")
        full_results = do_reference_search(q=query, ref_type=None, k=k, db=db)
        
        if not full_results:
            print("  No results found")
        else:
            for i, result in enumerate(full_results, 1):
                print(f"\n  {i}. {result['title']}")
                print(f"     Score: {result['score']:.4f}")
                print(f"     Type: {result['ref_type']}")
                content_preview = result['content'][:200].replace('\n', ' ')
                print(f"     Content: {content_preview}...")
        
        print_separator()
        
        # Chunk-based search
        print("🔍 CHUNK-BASED SEARCH:")
        chunk_results = do_chunk_search(
            q=query, 
            ref_type=None, 
            k=k, 
            db=db,
            chunks_per_doc=2
        )
        
        if not chunk_results:
            print("  No results found")
        else:
            for i, result in enumerate(chunk_results, 1):
                print(f"\n  {i}. {result['title']}")
                print(f"     Score: {result['score']:.4f}")
                print(f"     Type: {result['ref_type']}")
                
                if 'chunks' in result:
                    print(f"     Chunks: {len(result['chunks'])}")
                    for j, chunk in enumerate(result['chunks'], 1):
                        print(f"\n     Chunk {j} (index {chunk['chunk_index']}):")
                        if chunk['heading']:
                            print(f"       Heading: {chunk['heading']}")
                        print(f"       Score: {chunk['chunk_score']:.4f}")
                        print(f"       Text: {chunk['text'][:150]}...")
        
        print_separator()
        
    finally:
        db.close()

# Test cases
if __name__ == "__main__":
    print("CHUNK-BASED SEARCH TESTS")
    print("="*80)
    
    # Test 1: Specific spell section
    print("\n\nTest 1: Specific spell section query")
    test_search_comparison("What are the consequences of using the Wish spell?", k=3)
    
    # Test 2: Magic item ability
    print("\n\nTest 2: Magic item ability query")
    test_search_comparison("How does the vorpal sword decapitate enemies?", k=3)
    
    # Test 3: Class feature
    print("\n\nTest 3: Class feature query")
    test_search_comparison("How does a barbarian's rage work?", k=3)
    
    # Test 4: Spell component
    print("\n\nTest 4: Spell component query")
    test_search_comparison("spells that require a diamond worth at least 300 gp", k=3)
    
    # Test 5: Combat rule
    print("\n\nTest 5: Combat rule query")
    test_search_comparison("How do opportunity attacks work in combat?", k=3)
    
    print("\n\n✅ All chunk search tests completed!")
