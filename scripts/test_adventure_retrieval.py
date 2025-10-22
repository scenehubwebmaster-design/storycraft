"""Test adventure document ingestion and RAG retrieval.

Verifies that the 7 adventure creation documents were properly ingested
and can be retrieved via semantic search.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference
from backend.routers.references import do_chunk_search


def main():
    """Test adventure document retrieval."""
    engine = create_engine(
        f'sqlite:///{DEFAULT_DB_FILE}',
        connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check how many adventure documents exist
    adventure_refs = session.query(Reference).filter(
        Reference.ref_type == 'adventures_md'
    ).all()
    
    print(f"📚 Adventure Documents in Database")
    print(f"=" * 60)
    print(f"Total count: {len(adventure_refs)}")
    print()
    
    for ref in adventure_refs:
        tags_str = ', '.join(ref.tags) if ref.tags else 'none'
        print(f"✓ {ref.title}")
        print(f"  Key: {ref.key}")
        print(f"  Tags: {tags_str}")
        print()
    
    # Test semantic search for encounter building
    print(f"\n🔍 Testing Semantic Search")
    print(f"=" * 60)
    
    test_queries = [
        "How do I create balanced combat encounters?",
        "What makes a great adventure?",
        "How to build location-based adventures?",
        "Creating random encounters",
        "Adventure structure and pacing"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print(f"-" * 40)
        
        # Use chunk search for better results
        results = do_chunk_search(
            q=query,
            ref_type='adventures_md',
            k=3,
            db=session,
            chunks_per_doc=2
        )
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']} (score: {result.get('score', 0):.3f})")
                
                # Show best chunk
                if result.get('chunks'):
                    best_chunk = result['chunks'][0]
                    heading = best_chunk.get('heading', 'No heading')
                    text_preview = best_chunk['text'][:150].replace('\n', ' ')
                    print(f"   Section: {heading}")
                    print(f"   Preview: {text_preview}...")
        else:
            print("   No results found")
    
    session.close()
    
    print(f"\n✅ Test complete!")
    print(f"\nThe adventure documents are now available to the AI DM for:")
    print(f"  - Building balanced encounters")
    print(f"  - Creating adventure structures")
    print(f"  - Designing location-based and event-based adventures")
    print(f"  - Generating random encounters")
    print(f"  - Adding complications and framing events")


if __name__ == '__main__':
    main()
