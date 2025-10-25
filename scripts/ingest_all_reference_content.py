"""
Ingest ALL reference content from documents/reference/ into RAG system.

This comprehensive importer handles:
1. Adventure modules (guild, generated, homebrew)
2. Classes (Barbarian, Bard, Cleric, etc.)
3. Species/Races (Elf, Dwarf, Dragonborn, etc.)
4. Spells (organized by school and level)
5. Magic Items (by rarity)
6. Equipment, Weapons, Tools
7. DM Mechanics (combat rules, treasure tables, etc.)
8. Core dungeon generation rules
9. NPC templates (already in database)

Usage:
    python scripts/ingest_all_reference_content.py [--clear] [--content-type TYPE]
    
Options:
    --clear           Clear existing data before import
    --content-type    Import only specific type (adventures, classes, spells, etc.)
"""

import sys
import os
import pathlib
import argparse
from datetime import datetime
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference
from tqdm import tqdm


def strip_frontmatter(text: str) -> tuple[str, dict]:
    """Strip YAML frontmatter and return (content, metadata)."""
    metadata = {}
    content = text
    
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    metadata[key] = value
            content = parts[2].lstrip('\n')
    
    return content, metadata


def extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from markdown heading or filename."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filename.replace('_', ' ').replace('-', ' ').title()


def import_markdown_directory(
    session,
    directory: pathlib.Path,
    ref_type: str,
    category: str = None,
    tags: list = None
) -> int:
    """
    Generic markdown directory importer.
    
    Args:
        session: Database session
        directory: Path to directory containing .md files
        ref_type: Reference type (e.g., 'class', 'spell', 'equipment')
        category: Optional category field
        tags: Base tags to add to all imports
        
    Returns:
        Number of documents imported/updated
    """
    if not directory.exists():
        print(f"⚠️  Directory not found: {directory}")
        return 0
    
    # Get all markdown files (including subdirectories)
    md_files = list(directory.rglob('*.md'))
    
    if not md_files:
        print(f"⚠️  No .md files found in {directory}")
        return 0
    
    imported = 0
    updated = 0
    base_tags = tags or []
    
    for file_path in tqdm(md_files, desc=f"  {ref_type}"):
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if not content.strip():
                continue
            
            # Strip frontmatter
            clean_content, metadata = strip_frontmatter(content)
            
            # Extract title
            title = metadata.get('title') or extract_title_from_content(clean_content, file_path.stem)
            
            # Create unique key
            relative_path = file_path.relative_to(directory)
            key = f"{ref_type}/{str(relative_path.with_suffix('')).replace(os.sep, '/')}"
            
            # Build tags
            doc_tags = base_tags.copy()
            doc_tags.append(ref_type)
            
            # Add metadata tags
            if metadata.get('tags'):
                doc_tags.extend(metadata['tags'].split(','))
            
            # Add level/rarity info if present
            level = metadata.get('level')
            rarity = metadata.get('rarity')
            school = metadata.get('school')
            
            # Check if exists
            existing = session.query(Reference).filter(
                Reference.ref_type == ref_type,
                Reference.key == key
            ).first()
            
            if existing:
                existing.title = title
                existing.content = clean_content
                existing.tags = doc_tags
                existing.level = level
                existing.rarity = rarity
                existing.school = school
                existing.category = category
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                ref = Reference(
                    ref_type=ref_type,
                    key=key,
                    title=title,
                    content=clean_content,
                    tags=doc_tags,
                    level=level,
                    rarity=rarity,
                    school=school,
                    category=category,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(ref)
                imported += 1
            
            # Commit in batches
            if (imported + updated) % 50 == 0:
                session.commit()
        
        except Exception as e:
            print(f"\n❌ Error processing {file_path}: {e}")
            continue
    
    session.commit()
    return imported + updated


def import_adventures(session, reference_dir: pathlib.Path) -> int:
    """Import adventure modules (guild, generated, homebrew)."""
    print("\n📚 ADVENTURES")
    print("=" * 70)
    
    from ingest_guild_modules import import_guild_modules
    
    total = 0
    adventures_dir = reference_dir / 'adventures_md'
    
    for subdir in ['adventurers_guild_modules', 'generated_content', 'homebrew_adventures']:
        path = adventures_dir / subdir
        if path.exists():
            count = import_guild_modules(session, path)
            total += count
            print(f"✓ {subdir}: {count} documents")
    
    return total


def import_classes(session, reference_dir: pathlib.Path) -> int:
    """Import D&D classes."""
    print("\n⚔️  CLASSES")
    print("=" * 70)
    
    classes_dir = reference_dir / 'classes_md'
    count = import_markdown_directory(
        session,
        classes_dir,
        ref_type='class',
        tags=['dnd5e', 'phb2024', 'character_creation']
    )
    print(f"✓ Imported {count} class documents")
    return count


def import_species(session, reference_dir: pathlib.Path) -> int:
    """Import D&D species/races."""
    print("\n🧝 SPECIES")
    print("=" * 70)
    
    species_dir = reference_dir / 'species_md'
    count = import_markdown_directory(
        session,
        species_dir,
        ref_type='species',
        tags=['dnd5e', 'phb2024', 'character_creation']
    )
    print(f"✓ Imported {count} species documents")
    return count


def import_spells(session, reference_dir: pathlib.Path) -> int:
    """Import D&D spells."""
    print("\n✨ SPELLS")
    print("=" * 70)
    
    spells_dir = reference_dir / 'spells_md'
    count = import_markdown_directory(
        session,
        spells_dir,
        ref_type='spell',
        tags=['dnd5e', 'magic', 'spellcasting']
    )
    print(f"✓ Imported {count} spell documents")
    return count


def import_magic_items(session, reference_dir: pathlib.Path) -> int:
    """Import magic items."""
    print("\n🔮 MAGIC ITEMS")
    print("=" * 70)
    
    items_dir = reference_dir / 'magic_items_md'
    count = import_markdown_directory(
        session,
        items_dir,
        ref_type='magic_item',
        tags=['dnd5e', 'treasure', 'magic']
    )
    print(f"✓ Imported {count} magic item documents")
    return count


def import_equipment(session, reference_dir: pathlib.Path) -> int:
    """Import equipment, weapons, and tools."""
    print("\n🛡️  EQUIPMENT")
    print("=" * 70)
    
    total = 0
    
    # Equipment
    equipment_dir = reference_dir / 'equipment_md'
    if equipment_dir.exists():
        count = import_markdown_directory(
            session,
            equipment_dir,
            ref_type='equipment',
            tags=['dnd5e', 'gear']
        )
        total += count
        print(f"✓ Equipment: {count} documents")
    
    # Weapons
    weapons_dir = reference_dir / 'weapons_md'
    if weapons_dir.exists():
        count = import_markdown_directory(
            session,
            weapons_dir,
            ref_type='weapon',
            tags=['dnd5e', 'equipment', 'combat']
        )
        total += count
        print(f"✓ Weapons: {count} documents")
    
    # Tools
    tools_dir = reference_dir / 'tools_md'
    if tools_dir.exists():
        count = import_markdown_directory(
            session,
            tools_dir,
            ref_type='tool',
            tags=['dnd5e', 'equipment']
        )
        total += count
        print(f"✓ Tools: {count} documents")
    
    return total


def import_mechanics(session, reference_dir: pathlib.Path) -> int:
    """Import DM mechanics and rules."""
    print("\n📖 DM MECHANICS")
    print("=" * 70)
    
    total = 0
    
    # DM Mechanics
    mechanics_dir = reference_dir / 'dnd_mechanics'
    if mechanics_dir.exists():
        count = import_markdown_directory(
            session,
            mechanics_dir,
            ref_type='dm_mechanics',
            tags=['dm_guide', 'rules', 'mechanics']
        )
        total += count
        print(f"✓ DM Mechanics: {count} documents")
    
    # Core dungeon generation
    core_dir = reference_dir / 'core'
    if core_dir.exists():
        count = import_markdown_directory(
            session,
            core_dir,
            ref_type='dungeon_generation',
            tags=['dm_guide', 'dungeon_generation', 'procedural']
        )
        total += count
        print(f"✓ Dungeon Generation: {count} documents")
    
    return total


def import_monsters(session, reference_dir: pathlib.Path) -> int:
    """Import monster markdown files (note: most monsters are in database already)."""
    print("\n🐉 MONSTERS (MARKDOWN)")
    print("=" * 70)
    
    monsters_dir = reference_dir / 'monsters_md'
    if not monsters_dir.exists():
        print("⚠️  No monsters_md directory found")
        print("   (Note: Monsters are likely already in monster_stats table)")
        return 0
    
    count = import_markdown_directory(
        session,
        monsters_dir,
        ref_type='monster',
        tags=['dnd5e', 'creature', 'combat']
    )
    print(f"✓ Imported {count} monster markdown documents")
    print("   (Check monster_stats table for main monster database)")
    return count


def check_npc_templates(session) -> int:
    """Check NPC templates status (already in database)."""
    from backend.models import ReferenceEmbedding
    
    print("\n👥 NPC TEMPLATES")
    print("=" * 70)
    
    count = session.query(Reference).filter(Reference.ref_type == 'npc_template').count()
    print(f"✓ Found {count} NPC templates already in database")
    
    if count > 0:
        # Get NPCs with embeddings using ORM (avoid "references" keyword issue)
        embedded_count = session.query(Reference).filter(
            Reference.ref_type == 'npc_template'
        ).join(
            ReferenceEmbedding, Reference.id == ReferenceEmbedding.reference_id
        ).count()
        
        print(f"   • Embedded: {embedded_count}/{count}")
        
        if embedded_count < count:
            print(f"   ⚠️  {count - embedded_count} NPCs need embeddings")
    
    return count


def main():
    """Main import pipeline."""
    parser = argparse.ArgumentParser(description='Import all reference content into RAG system')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before import')
    parser.add_argument('--content-type', choices=[
        'all', 'adventures', 'classes', 'species', 'spells',
        'magic_items', 'equipment', 'mechanics', 'monsters'
    ], default='all', help='Content type to import')
    args = parser.parse_args()
    
    start_time = datetime.now()
    
    print("\n" + "=" * 70)
    print("STORYCRAFT REFERENCE CONTENT IMPORTER")
    print("=" * 70)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'CLEAR & IMPORT' if args.clear else 'UPDATE/ADD'}")
    print(f"Content: {args.content_type}")
    print("=" * 70)
    
    # Database setup
    engine = create_engine(
        f"sqlite:///{DEFAULT_DB_FILE}",
        connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    
    reference_dir = pathlib.Path(__file__).parent.parent / 'documents' / 'reference'
    
    if not reference_dir.exists():
        print(f"\n❌ Reference directory not found: {reference_dir}")
        return 1
    
    try:
        # Clear if requested
        if args.clear:
            print("\n⚠️  CLEARING EXISTING REFERENCES...")
            session.query(Reference).delete()
            session.commit()
            print("✓ Cleared")
        
        total_imported = 0
        content_types = {
            'adventures': import_adventures,
            'classes': import_classes,
            'species': import_species,
            'spells': import_spells,
            'magic_items': import_magic_items,
            'equipment': import_equipment,
            'mechanics': import_mechanics,
            'monsters': import_monsters,
        }
        
        # Import selected content
        if args.content_type == 'all':
            for name, import_func in content_types.items():
                count = import_func(session, reference_dir)
                total_imported += count
            
            # Check NPCs
            check_npc_templates(session)
        else:
            if args.content_type in content_types:
                count = content_types[args.content_type](session, reference_dir)
                total_imported += count
            else:
                print(f"❌ Unknown content type: {args.content_type}")
                return 1
        
        session.close()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("✅ IMPORT COMPLETE!")
        print("=" * 70)
        print(f"Duration: {duration:.1f} seconds")
        print(f"Documents imported/updated: {total_imported}")
        print("\n📋 Next Steps:")
        print("   1. Run chunk_documents.py to split into chunks")
        print("   2. Run generate_chunk_embeddings.py to create embeddings")
        print("\n   Commands:")
        print("   python scripts\\chunk_documents.py")
        print("   python scripts\\generate_chunk_embeddings.py")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return 1


if __name__ == '__main__':
    sys.exit(main())
