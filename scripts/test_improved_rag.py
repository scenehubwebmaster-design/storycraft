"""
Test script to verify improved RAG system with intelligent filter extraction.

This tests the problematic query "level 5 evocation spells" that previously
returned incorrect results (Fireball, Telekinesis, etc.)
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_session():
    """Create a new chat session for testing."""
    payload = {
        "title": "RAG Test Session",
        "provider": "lm_studio",
        "model": "local-model",
        "include_context": True,
        "top_k": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/chat/sessions", json=payload)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Error creating session: {response.text}")
        return None


def send_message(session_id, message):
    """Send a message to the chat session and get response."""
    payload = {
        "content": message
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat/sessions/{session_id}/generate",
        json=payload
    )
    
    return response.json()


def test_level5_evocation():
    """Test the problematic 'level 5 evocation spells' query."""
    print("=" * 80)
    print("TEST: Level 5 Evocation Spells Query")
    print("=" * 80)
    
    session_id = create_test_session()
    if not session_id:
        print("❌ Failed to create test session")
        return
    
    print(f"✓ Created test session: {session_id}\n")
    
    # The problematic query
    query = "Show me level 5 evocation spells for my wizard"
    print(f"Query: \"{query}\"\n")
    
    result = send_message(session_id, query)
    
    print("Response:")
    print("-" * 80)
    print(result.get('assistant_message', 'No response'))
    print("-" * 80)
    
    print("\nRetrieved Sources:")
    sources = result.get('retrievals', [])
    if sources:
        for i, source in enumerate(sources, 1):
            print(f"\n{i}. {source.get('title', 'Unknown')}")
            if 'level' in source:
                print(f"   Level: {source['level']}")
            if 'school' in source:
                print(f"   School: {source['school']}")
    else:
        print("  (No sources retrieved)")
    
    # Check if correct spells are included
    correct_spells = [
        "Arcane Hand",
        "Cone of Cold",
        "Flame Strike",
        "Hallow",
        "Mass Cure Wounds",
        "Wall of Force",
        "Wall of Stone"
    ]
    
    wrong_spells = [
        "Fireball",  # Level 3, not 5
        "Telekinesis",  # Transmutation, not Evocation
        "Prayer of Healing",  # Level 2
        "Eldritch Blast"  # Cantrip
    ]
    
    print("\n\nValidation:")
    print("-" * 80)
    
    source_titles = [s.get('title', '').lower() for s in sources]
    
    correct_found = [spell for spell in correct_spells if spell.lower() in ' '.join(source_titles)]
    wrong_found = [spell for spell in wrong_spells if spell.lower() in ' '.join(source_titles)]
    
    print(f"✓ Correct spells found: {len(correct_found)}/{len(correct_spells)}")
    for spell in correct_found:
        print(f"  ✓ {spell}")
    
    if wrong_found:
        print(f"\n❌ Wrong spells found: {len(wrong_found)}")
        for spell in wrong_found:
            print(f"  ❌ {spell}")
    else:
        print("\n✓ No incorrect spells found!")
    
    # Success criteria
    success = len(correct_found) >= 4 and len(wrong_found) == 0
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: RAG system now correctly filters Level 5 Evocation spells!")
    else:
        print("❌ TEST FAILED: RAG system still returning incorrect results")
    print("=" * 80)


def test_rare_magic_items():
    """Test 'rare magic weapons' query."""
    print("\n\n" + "=" * 80)
    print("TEST: Rare Magic Weapons Query")
    print("=" * 80)
    
    session_id = create_test_session()
    if not session_id:
        print("❌ Failed to create test session")
        return
    
    print(f"✓ Created test session: {session_id}\n")
    
    query = "Find some rare magic weapons for my fighter"
    print(f"Query: \"{query}\"\n")
    
    result = send_message(session_id, query)
    
    print("Retrieved Sources:")
    sources = result.get('retrievals', [])
    if sources:
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source.get('title', 'Unknown')}")
            if 'rarity' in source:
                print(f"   Rarity: {source['rarity']}")
            if 'category' in source:
                print(f"   Category: {source['category']}")
    
    # Check that all results are Rare rarity
    rarities = [s.get('rarity', '').lower() for s in sources if 'rarity' in s]
    all_rare = all(r == 'rare' for r in rarities)
    
    print("\nValidation:")
    print("-" * 80)
    if all_rare and rarities:
        print(f"✅ All {len(rarities)} items are Rare rarity")
    elif rarities:
        print(f"❌ Mixed rarities found: {set(rarities)}")
    else:
        print("⚠️ No rarity information in results")


if __name__ == "__main__":
    print("Testing Improved RAG System with Intelligent Filter Extraction\n")
    
    try:
        test_level5_evocation()
        test_rare_magic_items()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend at http://localhost:8000")
        print("Please ensure the backend server is running:")
        print("  cd e:\\storycraft\\backend")
        print("  python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
