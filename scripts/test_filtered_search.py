"""Test filtered searches with metadata."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.routers.references import do_reference_search

engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

def test_search(description, **kwargs):
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    
    session = Session()
    results = do_reference_search(db=session, **kwargs)
    session.close()
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results[:5], 1):  # Show top 5
        print(f"\n{i}. {result['title']}")
        print(f"   Type: {result['ref_type']}")
        if result.get('level') is not None:
            print(f"   Level: {result['level']}")
        if result.get('school'):
            print(f"   School: {result['school']}")
        if result.get('rarity'):
            print(f"   Rarity: {result['rarity']}")
        if result.get('category'):
            print(f"   Category: {result['category']}")
        if result.get('tags'):
            print(f"   Tags: {', '.join(result['tags'][:5])}")  # Show first 5 tags
        if 'score' in result:
            print(f"   Score: {result['score']:.4f}")
    
    if len(results) > 5:
        print(f"\n   ... and {len(results) - 5} more results")


# Test 1: 3rd-level spells
test_search(
    "3rd-level spells",
    q=None,
    ref_type='spells_md',
    level=3,
    k=10
)

# Test 2: 3rd-level fire spells (with semantic search)
test_search(
    "3rd-level fire spells with 'fire' in query",
    q="fire damage spell",
    ref_type='spells_md',
    level=3,
    k=10
)

# Test 3: Uncommon magic items
test_search(
    "Uncommon magic items",
    q=None,
    ref_type='magic_items_md',
    rarity='Uncommon',
    k=10
)

# Test 4: Rare weapons
test_search(
    "Rare magic weapons",
    q=None,
    ref_type='magic_items_md',
    rarity='Rare',
    category='Weapon',
    k=10
)

# Test 5: Evocation spells
test_search(
    "Evocation school spells",
    q=None,
    ref_type='spells_md',
    school='Evocation',
    k=10
)

# Test 6: Healing spells (by tag)
test_search(
    "Spells with 'healing' tag (not working yet - needs tag extraction improvement)",
    q="healing",
    ref_type='spells_md',
    k=10
)

# Test 7: Fire damage spells
test_search(
    "Fire damage spells (tag + semantic)",
    q="fire",
    ref_type='spells_md',
    tags=['fire'],
    k=10
)

# Test 8: Cantrips (level 0)
test_search(
    "Cantrips (level 0 spells)",
    q=None,
    ref_type='spells_md',
    level=0,
    k=10
)

# Test 9: Legendary items
test_search(
    "Legendary magic items",
    q=None,
    ref_type='magic_items_md',
    rarity='Legendary',
    k=10
)

# Test 10: Combined filters - 1st level evocation spells with fire damage
test_search(
    "1st-level Evocation spells with fire tag",
    q=None,
    ref_type='spells_md',
    level=1,
    school='Evocation',
    tags=['fire'],
    k=10
)

print(f"\n{'='*70}")
print("All tests complete!")
print(f"{'='*70}\n")
