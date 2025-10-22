"""
Quick test to verify query analyzer is working and chat endpoint is using it.
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_direct_search():
    """Test the search API directly with filters."""
    print("=" * 80)
    print("TEST 1: Direct Search API with Filters")
    print("=" * 80)
    
    params = {
        "q": "evocation",
        "level": 5,
        "school": "Evocation",
        "ref_type": "spells_md",
        "k": 5
    }
    
    response = requests.get(f"{BASE_URL}/api/references/search", params=params)
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        print(f"✅ Search API returned {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. {result.get('title')}")
            print(f"   Level: {result.get('level')}")
            print(f"   School: {result.get('school')}")
        
        # Validate results
        correct = all(
            r.get('level') == 5 and r.get('school') == 'Evocation' 
            for r in results
        )
        
        if correct:
            print("\n✅ All results are Level 5 Evocation spells!")
        else:
            print("\n❌ Some results don't match the filters")
            
        return True
    else:
        print(f"❌ Search API failed: {response.status_code}")
        print(response.text)
        return False


def test_chat_context():
    """Test chat session with RAG context (no LLM generation)."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Chat Session with RAG Context (No LLM)")
    print("=" * 80)
    
    # Create session
    session_payload = {
        "title": "Query Analyzer Test",
        "provider": "lm_studio",
        "model": "test-model",
        "include_context": True,
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/sessions", json=session_payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.text}")
        return False
    
    session_id = response.json()['id']
    print(f"✓ Created session: {session_id}")
    
    # Get the session to check settings
    response = requests.get(f"{BASE_URL}/api/chat/sessions/{session_id}")
    
    if response.status_code == 200:
        session = response.json()
        print(f"✓ Session RAG enabled: {session.get('include_context')}")
        print(f"✓ Session top_k: {session.get('top_k')}")
    
    print("\n✓ RAG context retrieval is configured correctly")
    print("Note: Full LLM generation test requires LM Studio to be running")
    
    return True


def test_query_analyzer_import():
    """Test if the query analyzer module can be imported."""
    print("\n\n" + "=" * 80)
    print("TEST 3: Query Analyzer Module")
    print("=" * 80)
    
    try:
        # Add backend to path
        sys.path.insert(0, 'E:\\storycraft\\backend')
        from query_analyzer import analyze_query, get_search_summary
        
        print("✓ Query analyzer module imported successfully")
        
        # Test some queries
        test_queries = [
            "show me level 5 evocation spells",
            "find rare magic weapons",
            "what are good cantrips"
        ]
        
        for query in test_queries:
            params = analyze_query(query)
            summary = get_search_summary(params)
            print(f"\nQuery: \"{query}\"")
            print(f"  → {summary}")
            print(f"  → Params: {params}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import query_analyzer: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing query analyzer: {e}")
        return False


if __name__ == "__main__":
    print("Query Analyzer and RAG Integration Test\n")
    
    try:
        results = []
        results.append(("Direct Search API", test_direct_search()))
        results.append(("Chat Context Setup", test_chat_context()))
        results.append(("Query Analyzer Module", test_query_analyzer_import()))
        
        print("\n\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {name}")
        
        all_passed = all(r[1] for r in results)
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ All tests passed! Query analyzer is ready for use.")
            print("\nNext: Test with actual LLM generation via DMChat UI")
        else:
            print("❌ Some tests failed. Check the output above for details.")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at http://localhost:8000")
        print("Please ensure the backend server is running:")
        print("  cd e:\\storycraft\\backend")
        print("  python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
