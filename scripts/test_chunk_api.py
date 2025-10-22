"""
Test chunk-based search via the API.
Requires backend to be running on http://localhost:8000
"""

import requests
import json

API_BASE = "http://localhost:8000/api/references"

def test_search(query: str, use_chunks: bool = False, k: int = 5):
    """Test search endpoint."""
    params = {
        "q": query,
        "k": k,
        "use_chunks": use_chunks,
        "chunks_per_doc": 2
    }
    
    response = requests.get(f"{API_BASE}/search", params=params)
    
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def print_results(title: str, results: list):
    """Print search results nicely."""
    print(f"\n{'='*80}")
    print(title)
    print(f"{'='*80}\n")
    
    if not results:
        print("  No results found\n")
        return
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Score: {result.get('score', 0):.4f}")
        print(f"   Type: {result.get('ref_type', 'unknown')}")
        
        if 'chunks' in result:
            print(f"   Chunks: {len(result['chunks'])}")
            for j, chunk in enumerate(result['chunks'], 1):
                print(f"\n   Chunk {j} (index {chunk['chunk_index']}):")
                if chunk.get('heading'):
                    print(f"     Heading: {chunk['heading']}")
                print(f"     Score: {chunk['chunk_score']:.4f}")
                text = chunk['text'].replace('\n', ' ').strip()
                print(f"     Text: {text[:200]}...")
        else:
            # Full document search
            content = result.get('content', '')[:300].replace('\n', ' ')
            print(f"   Content: {content}...")
        
        print()

def compare_search(query: str, k: int = 5):
    """Compare full document search vs chunk-based search."""
    print(f"\n\n{'#'*80}")
    print(f"Query: '{query}'")
    print(f"{'#'*80}")
    
    # Full document search
    full_results = test_search(query, use_chunks=False, k=k)
    if full_results is not None:
        print_results("📄 FULL DOCUMENT SEARCH", full_results)
    
    # Chunk-based search
    chunk_results = test_search(query, use_chunks=True, k=k)
    if chunk_results is not None:
        print_results("🔍 CHUNK-BASED SEARCH", chunk_results)

if __name__ == "__main__":
    print("CHUNK-BASED SEARCH API TESTS")
    print("="*80)
    print("NOTE: Backend must be running on http://localhost:8000")
    print("="*80)
    
    # Test if backend is running
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"\n✅ Backend is running (status: {response.status_code})\n")
    except Exception as e:
        print(f"\n❌ ERROR: Backend is not running!")
        print(f"   {e}")
        print(f"\n   Please start the backend first:")
        print(f"   cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Test 1: Wish spell consequences
    compare_search("What are the consequences of using the Wish spell?", k=3)
    
    # Test 2: Barbarian rage
    compare_search("How does a barbarian's rage work?", k=3)
    
    # Test 3: Fireball
    compare_search("fireball", k=5)
    
    # Test 4: Opportunity attacks
    compare_search("How do opportunity attacks work in combat?", k=3)
    
    # Test 5: Vorpal sword
    compare_search("vorpal sword decapitation", k=3)
    
    print("\n\n✅ All API tests completed!")
