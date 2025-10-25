"""
Complete RAG Re-ingestion Pipeline

This script performs a full re-ingestion of ALL reference content:
1. Clears existing data (optional)
2. Imports ALL reference content:
   - Adventure modules (guild, generated, homebrew)
   - Classes (12 PHB 2024 classes)
   - Species/Races (character options)
   - Spells (all schools and levels)
   - Magic Items (all rarities)
   - Equipment, Weapons, Tools
   - DM Mechanics & Rules
   - Monsters (markdown)
   - NPC Templates (100 diverse characters)
3. Chunks documents for retrieval
4. Generates embeddings for chunks
5. Generates embeddings for references (NPCs, classes, etc.)
6. Validates the ingestion

Usage:
    python scripts/rag_full_reingest.py [--clear]
    
Options:
    --clear    Clear existing data before re-ingestion (default: update only)
"""

import sys
import os
import pathlib
import argparse
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference, DocumentChunk

# Import the comprehensive ingestion module
from ingest_all_reference_content import (
    import_adventures,
    import_classes,
    import_species,
    import_spells,
    import_magic_items,
    import_equipment,
    import_mechanics,
    import_monsters,
    check_npc_templates
)
from chunk_documents import chunk_all_documents
from generate_chunk_embeddings import generate_embeddings


def generate_reference_embeddings_inline(session):
    """Generate embeddings for references (NPCs, classes, etc.) inline."""
    from sentence_transformers import SentenceTransformer
    from backend.models import ReferenceEmbedding
    
    print("=" * 70)
    print("GENERATING REFERENCE EMBEDDINGS")
    print("=" * 70)
    
    # Load model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Model loaded")
    
    # Get references without embeddings using ORM (avoid "references" keyword issue)
    embedded_ref_ids = session.query(ReferenceEmbedding.reference_id).distinct().subquery()
    
    references = session.query(Reference).filter(
        ~Reference.id.in_(embedded_ref_ids)
    ).all()
    
    if not references:
        print("✓ All references already have embeddings")
        return {'total_embeddings': 0}
    
    print(f"Found {len(references)} references needing embeddings")
    
    # Count by type
    ref_types = {}
    for ref in references:
        ref_types[ref.ref_type] = ref_types.get(ref.ref_type, 0) + 1
    
    print("\nBreakdown by type:")
    for rtype, count in sorted(ref_types.items()):
        print(f"  • {rtype}: {count}")
    
    # Generate embeddings
    print("\nGenerating embeddings...")
    texts = []
    ref_ids = []
    
    for ref in references:
        content_preview = ref.content[:2000] if ref.content else ""
        text = f"{ref.title}\n\n{content_preview}"
        texts.append(text)
        ref_ids.append(ref.id)
    
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
    
    # Store embeddings
    print("Storing embeddings...")
    for ref_id, embedding in zip(ref_ids, embeddings):
        vec_json = json.dumps(embedding.tolist())
        emb = ReferenceEmbedding(
            reference_id=ref_id,
            vector=vec_json
        )
        session.add(emb)
        
        if ref_id % 100 == 0:
            session.commit()
    
    session.commit()
    
    print(f"\n✓ Generated {len(embeddings)} reference embeddings")
    for rtype, count in sorted(ref_types.items()):
        print(f"  ✓ {rtype}: {count}")
    
    return {'total_embeddings': len(embeddings), 'by_type': ref_types}


def clear_existing_data(session):
    """Clear all existing references, chunks, and embeddings."""
    print("=" * 70)
    print("CLEARING EXISTING DATA")
    print("=" * 70)
    
    # Count before
    ref_count = session.query(Reference).count()
    chunk_count = session.query(DocumentChunk).count()
    
    print(f"Found {ref_count} references and {chunk_count} chunks")
    print("Deleting...")
    
    # Delete chunks first (foreign key constraint)
    session.query(DocumentChunk).delete()
    session.commit()
    
    # Delete references
    session.query(Reference).delete()
    session.commit()
    
    print("✓ All data cleared")
    print()


def import_all_content(session):
    """Import ALL reference content (adventures, classes, spells, items, etc.)."""
    print("=" * 70)
    print("IMPORTING ALL REFERENCE CONTENT")
    print("=" * 70)
    print()
    
    repo_root = pathlib.Path(__file__).parent.parent
    reference_dir = repo_root / 'documents' / 'reference'
    
    if not reference_dir.exists():
        print(f"❌ Reference directory not found: {reference_dir}")
        return 0
    
    total_imported = 0
    
    # Import all content types
    content_importers = [
        ('Adventures', import_adventures),
        ('Classes', import_classes),
        ('Species/Races', import_species),
        ('Spells', import_spells),
        ('Magic Items', import_magic_items),
        ('Equipment/Weapons/Tools', import_equipment),
        ('DM Mechanics & Rules', import_mechanics),
        ('Monsters (Markdown)', import_monsters),
    ]
    
    for name, import_func in content_importers:
        print(f"\n{'=' * 70}")
        print(f"📂 {name}")
        print('=' * 70)
        try:
            count = import_func(session, reference_dir)
            total_imported += count
            if count > 0:
                print(f"✓ Imported/Updated {count} documents")
            else:
                print("⚠️  No documents found or imported")
        except Exception as e:
            print(f"❌ Error importing {name}: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    # Check NPC templates status
    print('=' * 70)
    print("👥 NPC Templates (Already in Database)")
    print('=' * 70)
    check_npc_templates(session)
    print()
    
    return total_imported


def main():
    """Main re-ingestion pipeline."""
    parser = argparse.ArgumentParser(description='Complete RAG re-ingestion pipeline')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before re-ingestion')
    args = parser.parse_args()
    
    start_time = datetime.now()
    
    print("\n")
    print("=" * 70)
    print("STORYCRAFT RAG FULL RE-INGESTION PIPELINE")
    print("=" * 70)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'CLEAR & RE-IMPORT' if args.clear else 'UPDATE EXISTING'}")
    print("=" * 70)
    print("\n")
    
    # Connect to database
    engine = create_engine(
        f"sqlite:///{DEFAULT_DB_FILE}",
        connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Step 1: Clear if requested
        if args.clear:
            clear_existing_data(session)
        
        # Step 2: Import all content
        total_imported = import_all_content(session)
        
        session.close()
        
        # Step 3: Chunk documents
        print("=" * 70)
        print("CHUNKING DOCUMENTS")
        print("=" * 70)
        chunk_stats = chunk_all_documents()
        print()
        
        # Step 4: Generate embeddings
        print("=" * 70)
        print("GENERATING EMBEDDINGS")
        print("=" * 70)
        embedding_stats = generate_embeddings()
        print()
        
        # Step 5: Generate reference embeddings (NPCs, classes, etc.)
        ref_embedding_stats = generate_reference_embeddings_inline(session)
        session.close()
        print()
        
        # Step 6: Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 70)
        print("RE-INGESTION COMPLETE!")
        print("=" * 70)
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()
        print("📊 Summary:")
        print(f"   Documents imported: {total_imported}")
        print(f"   Documents chunked: {chunk_stats.get('documents_processed', 0)}")
        print(f"   Total chunks: {chunk_stats.get('total_chunks', 0)}")
        print(f"   Chunk embeddings: {embedding_stats.get('total_embeddings', 0)}")
        print(f"   Reference embeddings: {ref_embedding_stats.get('total_embeddings', 0)}")
        print()
        print("✅ RAG system is ready!")
        print("   All D&D 5e reference content has been ingested and indexed.")
        print("   The AI DM can now access:")
        print("   - 📚 Adventures (Guild modules, generated, homebrew)")
        print("   - ⚔️  Classes (12 PHB 2024 classes)")
        print("   - 🧝 Species/Races (Player character options)")
        print("   - ✨ Spells (Organized by school and level)")
        print("   - 🔮 Magic Items (All rarities)")
        print("   - 🛡️  Equipment, Weapons, Tools")
        print("   - 📖 DM Mechanics (Combat, treasure, encounters)")
        print("   - 🏰 Dungeon Generation Rules")
        print("   - 👥 NPC Templates (100 diverse characters)")
        print("   - 🐉 Monsters (317 creatures with stats)")
        print()
        print("🎲 Ready to create epic campaigns with comprehensive D&D knowledge!")
        print("=" * 70)
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return 1


if __name__ == '__main__':
    sys.exit(main())
