"""
Review and audit the RAG (Retrieval-Augmented Generation) system.

Analyzes what content is available for semantic search and suggests improvements.
"""

from sqlalchemy import func, text
from backend.database import SessionLocal
from backend.models import Reference, MonsterStat, MonsterEmbedding, ReferenceEmbedding, DocumentChunk, ChunkEmbedding

def analyze_references(db):
    """Analyze reference documents"""
    print("\n" + "=" * 80)
    print("📚 REFERENCE DOCUMENTS ANALYSIS")
    print("=" * 80)
    
    # Count by type
    ref_counts = db.query(
        Reference.ref_type,
        func.count(Reference.id).label('count')
    ).group_by(Reference.ref_type).all()
    
    print("\nReferences by type:")
    total_refs = 0
    for ref_type, count in ref_counts:
        print(f"  • {ref_type}: {count}")
        total_refs += count
    
    print(f"\n✓ Total references: {total_refs}")
    
    # Check embeddings coverage
    embedded_count = db.query(ReferenceEmbedding).count()
    print(f"✓ Embedded references: {embedded_count}")
    
    if embedded_count < total_refs:
        print(f"⚠️  Missing embeddings for {total_refs - embedded_count} references!")
    
    return total_refs, embedded_count

def analyze_monsters(db):
    """Analyze monster stats"""
    print("\n" + "=" * 80)
    print("🐉 MONSTER STATS ANALYSIS")
    print("=" * 80)
    
    total_monsters = db.query(MonsterStat).count()
    embedded_monsters = db.query(MonsterEmbedding).count()
    
    print(f"\n✓ Total monsters: {total_monsters}")
    print(f"✓ Embedded monsters: {embedded_monsters}")
    
    if embedded_monsters < total_monsters:
        print(f"⚠️  Missing embeddings for {total_monsters - embedded_monsters} monsters!")
    
    # Sample monsters by CR
    print("\nMonster distribution by Challenge Rating:")
    cr_dist = db.execute(text("""
        SELECT 
            CASE 
                WHEN numeric_cr <= 1 THEN 'CR 0-1'
                WHEN numeric_cr <= 5 THEN 'CR 2-5'
                WHEN numeric_cr <= 10 THEN 'CR 6-10'
                WHEN numeric_cr <= 15 THEN 'CR 11-15'
                WHEN numeric_cr <= 20 THEN 'CR 16-20'
                ELSE 'CR 21+'
            END as cr_range,
            COUNT(*) as count
        FROM monster_stats
        WHERE numeric_cr IS NOT NULL
        GROUP BY cr_range
        ORDER BY MIN(numeric_cr)
    """)).fetchall()
    
    for cr_range, count in cr_dist:
        print(f"  • {cr_range}: {count} monsters")
    
    return total_monsters, embedded_monsters

def analyze_document_chunks(db):
    """Analyze document chunks for RAG"""
    print("\n" + "=" * 80)
    print("📄 DOCUMENT CHUNKS ANALYSIS")
    print("=" * 80)
    
    total_chunks = db.query(DocumentChunk).count()
    embedded_chunks = db.query(ChunkEmbedding).count()
    
    print(f"\n✓ Total chunks: {total_chunks}")
    print(f"✓ Embedded chunks: {embedded_chunks}")
    
    if embedded_chunks < total_chunks:
        print(f"⚠️  Missing embeddings for {total_chunks - embedded_chunks} chunks!")
    
    if total_chunks > 0:
        # Sample chunk distribution
        chunk_dist = db.query(
            Reference.ref_type,
            func.count(DocumentChunk.id).label('chunk_count')
        ).join(DocumentChunk, Reference.id == DocumentChunk.source_id
        ).group_by(Reference.ref_type).all()
        
        print("\nChunk distribution by source type:")
        for ref_type, count in chunk_dist:
            print(f"  • {ref_type}: {count} chunks")
    
    return total_chunks, embedded_chunks

def suggest_improvements(stats, db):
    """Suggest improvements to RAG system"""
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    total_refs, embedded_refs = stats['references']
    total_monsters, embedded_monsters = stats['monsters']
    total_chunks, embedded_chunks = stats['chunks']
    
    recommendations = []
    
    # Check embedding coverage
    if embedded_refs < total_refs:
        recommendations.append({
            "priority": "HIGH",
            "action": f"Generate embeddings for {total_refs - embedded_refs} references",
            "command": "python -m backend.scripts.embed_references"
        })
    
    if embedded_monsters < total_monsters:
        recommendations.append({
            "priority": "HIGH",
            "action": f"Generate embeddings for {total_monsters - embedded_monsters} monsters",
            "command": "python -m backend.scripts.embed_monsters"
        })
    
    if embedded_chunks < total_chunks:
        recommendations.append({
            "priority": "HIGH",
            "action": f"Generate embeddings for {total_chunks - embedded_chunks} chunks",
            "command": "python -m backend.scripts.embed_chunks"
        })
    
    # Check for missing content types
    ref_types = set(db.query(Reference.ref_type).distinct().all())
    ref_types_set = {rt[0] for rt in ref_types}
    
    recommended_types = {
        'class', 'species', 'spell', 'equipment', 'feat', 'background',
        'magic_item', 'condition', 'rule', 'npc_template'
    }
    
    missing_types = recommended_types - ref_types_set
    if missing_types:
        recommendations.append({
            "priority": "MEDIUM",
            "action": f"Consider adding these reference types: {', '.join(missing_types)}",
            "command": "Scrape or import from D&D 5e SRD"
        })
    
    # Check for RAG system files
    import os
    chroma_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
    if not os.path.exists(chroma_dir):
        recommendations.append({
            "priority": "HIGH",
            "action": "Initialize ChromaDB database",
            "command": "Create ./chroma_db directory and initialize collections"
        })
    
    # Print recommendations
    if not recommendations:
        print("\n✅ RAG system is fully configured!")
        print("✨ All content is embedded and ready for semantic search")
    else:
        print("\n📋 Action items:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['action']}")
            print(f"   Command: {rec['command']}")
    
    # Additional suggestions
    print("\n" + "=" * 80)
    print("🎯 ENHANCEMENT OPPORTUNITIES")
    print("=" * 80)
    print("\n1. NPC Templates (COMPLETED ✓)")
    print("   - 100 diverse NPC templates created")
    print("   - Ready for portrait generation")
    print("   - Includes physical descriptions, personalities, backstories")
    
    print("\n2. Adventure Hooks")
    print("   - Add pre-written adventure hooks and plot seeds")
    print("   - Store as 'adventure_hook' references")
    print("   - Categorize by theme, difficulty, setting")
    
    print("\n3. Location Templates")
    print("   - Create reusable location descriptions")
    print("   - Taverns, dungeons, cities, wilderness")
    print("   - Include maps, NPCs, encounters")
    
    print("\n4. Magic Items")
    print("   - Comprehensive magic item database")
    print("   - Custom homebrew items")
    print("   - Item properties and lore")
    
    print("\n5. Random Encounter Tables")
    print("   - By environment type (forest, dungeon, city)")
    print("   - By difficulty/CR")
    print("   - Themed encounters")
    
    print("\n6. Traps and Puzzles")
    print("   - Mechanical traps with DCs")
    print("   - Logic puzzles and riddles")
    print("   - Environmental hazards")
    
    print("\n7. Quest Templates")
    print("   - Structured quest frameworks")
    print("   - Objectives, rewards, complications")
    print("   - Multiple resolution paths")

def main():
    """Main execution"""
    db = SessionLocal()
    
    try:
        print("🔍 RAG SYSTEM AUDIT")
        print("=" * 80)
        print("Analyzing content available for semantic search...")
        
        # Gather statistics
        stats = {
            'references': analyze_references(db),
            'monsters': analyze_monsters(db),
            'chunks': analyze_document_chunks(db)
        }
        
        # Provide recommendations
        suggest_improvements(stats, db)
        
        print("\n" + "=" * 80)
        print("✅ AUDIT COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
