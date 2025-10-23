"""Ingest Adventurer's Guild Modules into RAG system.

Imports DDEX/DDAL adventure modules from 
documents/reference/adventures_md/adventurers_guild_modules/
into the references table with ref_type='guild_modules'.

Each module folder (e.g., Defiance_in_Phlan/) is processed recursively,
including all markdown files in subdirectories (locations, npcs, missions, etc.).

Usage:
  python scripts\\ingest_guild_modules.py
"""
import sys
import os
import pathlib
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference
from datetime import datetime
from tqdm import tqdm


def strip_frontmatter(text: str) -> tuple[str, dict]:
    """
    Strip YAML frontmatter and return (content, metadata).
    
    Returns:
        (content_without_frontmatter, frontmatter_dict)
    """
    metadata = {}
    content = text
    
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            # Parse frontmatter
            frontmatter = parts[1].strip()
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Handle arrays
                    if value.startswith('[') or value.startswith('-'):
                        # Parse as list
                        if value.startswith('['):
                            # Inline array: [item1, item2, item3]
                            items = re.findall(r'[\w\s-]+', value)
                            metadata[key] = [item.strip() for item in items if item.strip()]
                        else:
                            # Multi-line array with dashes (will be parsed on subsequent lines)
                            if key not in metadata:
                                metadata[key] = []
                    elif line.strip().startswith('-'):
                        # This is a list item, add to last key
                        last_key = list(metadata.keys())[-1] if metadata else None
                        if last_key and isinstance(metadata[last_key], list):
                            metadata[last_key].append(line.strip()[1:].strip())
                    else:
                        metadata[key] = value
            
            content = parts[2].lstrip('\n')
    
    return content, metadata


def extract_title_from_content(content: str, filename: str) -> str:
    """Extract title from markdown heading or filename."""
    # Try to find first # heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Fall back to filename
    return filename.replace('_', ' ').replace('-', ' ').title().replace('.Md', '')


def get_module_name_from_path(file_path: pathlib.Path, modules_dir: pathlib.Path) -> str:
    """
    Extract the module name from the file path.
    e.g., .../Defiance_in_Phlan/locations/peat_bog.md -> Defiance_in_Phlan
    """
    try:
        relative = file_path.relative_to(modules_dir)
        return relative.parts[0]
    except (ValueError, IndexError):
        return "unknown_module"


def get_section_from_path(file_path: pathlib.Path, modules_dir: pathlib.Path) -> str:
    """
    Extract the section path from the file path, preserving subdirectory structure.
    e.g., .../Defiance_in_Phlan/locations/peat_bog.md -> locations
         .../Defiance_in_Phlan/index.md -> overview
         .../Bloodmoon_Epitaph/Epitaph_of_Thorns/items/index.md -> Epitaph_of_Thorns/items
    """
    try:
        relative = file_path.relative_to(modules_dir)
        parts = list(relative.parts)
        
        # Remove module name (first part) and filename (last part)
        if len(parts) > 2:
            # Build section path from everything between module and filename
            section_parts = parts[1:-1]
            return '/'.join(section_parts)
        elif file_path.stem in ('index', 'README'):
            return 'overview'
        else:
            return 'general'
    except (ValueError, IndexError):
        return 'general'


def import_guild_modules(db_session, modules_dir: pathlib.Path) -> int:
    """
    Import all guild module .md files from modules_dir into references table.
    
    Recursively processes all module folders and their subdirectories.
    
    Args:
        db_session: SQLAlchemy session
        modules_dir: Path to adventurers_guild_modules folder
        
    Returns:
        Number of files imported
    """
    if not modules_dir.exists():
        print(f"❌ Guild modules folder not found: {modules_dir}")
        return 0
    
    # Get all module directories
    module_dirs = [d for d in modules_dir.iterdir() if d.is_dir()]
    
    if not module_dirs:
        print(f"❌ No module directories found in {modules_dir}")
        return 0
    
    print(f"📚 Found {len(module_dirs)} module directories:")
    for d in module_dirs:
        print(f"   - {d.name}")
    
    # Collect all markdown files from all modules
    all_files = []
    for module_dir in module_dirs:
        files = list(module_dir.rglob('*.md'))
        all_files.extend(files)
    
    if not all_files:
        print("❌ No .md files found in any module directories")
        return 0
    
    print(f"\n📄 Processing {len(all_files)} markdown files...")
    
    imported_count = 0
    updated_count = 0
    skipped_count = 0
    
    for file_path in tqdm(all_files, desc="Processing"):
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Skip empty files
            if not content.strip():
                skipped_count += 1
                continue
            
            # Strip frontmatter and get metadata
            clean_content, metadata = strip_frontmatter(content)
            
            # Extract info from path
            module_name = get_module_name_from_path(file_path, modules_dir)
            section = get_section_from_path(file_path, modules_dir)
            
            # Extract title
            title = metadata.get('title') or extract_title_from_content(clean_content, file_path.stem)
            
            # Create unique key from module + section + filename
            key = f"{module_name}/{section}/{file_path.stem}"
            
            # Build comprehensive tags
            tags = metadata.get('tags', [])
            if not isinstance(tags, list):
                tags = [tags] if tags else []
            
            # Add standard tags
            standard_tags = ['guild_module', 'adventure', 'ddal', module_name.lower(), section]
            for tag in standard_tags:
                if tag and tag not in tags:
                    tags.append(tag)
            
            # Add theme tags from metadata
            themes = metadata.get('themes', [])
            if isinstance(themes, list):
                tags.extend(themes)
            
            # Add location/setting tags
            setting = metadata.get('setting')
            if setting:
                tags.append(setting.lower())
            
            # Build enhanced content with metadata context
            enhanced_content = f"# {title}\n\n"
            
            if module_name:
                enhanced_content += f"**Module:** {module_name.replace('_', ' ')}\n"
            if section and section != 'overview':
                enhanced_content += f"**Section:** {section.replace('_', ' ').title()}\n"
            if metadata.get('edition'):
                enhanced_content += f"**Edition:** {metadata['edition']}\n"
            if metadata.get('levels'):
                enhanced_content += f"**Levels:** {metadata['levels']}\n"
            if setting:
                enhanced_content += f"**Setting:** {setting}\n"
            
            enhanced_content += "\n---\n\n" + clean_content
            
            # Check if reference already exists
            existing = db_session.query(Reference).filter(
                Reference.ref_type == 'guild_modules',
                Reference.key == key
            ).first()
            
            if existing:
                # Update existing reference
                existing.title = title
                existing.content = enhanced_content
                existing.tags = tags
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new reference
                ref = Reference(
                    ref_type='guild_modules',
                    key=key,
                    title=title,
                    content=enhanced_content,
                    source_url=metadata.get('source_url'),
                    tags=tags,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db_session.add(ref)
                imported_count += 1
            
            # Commit in batches of 20
            if (imported_count + updated_count) % 20 == 0:
                db_session.commit()
        
        except Exception as e:
            print(f"\n❌ Error processing {file_path}: {e}")
            continue
    
    # Final commit
    db_session.commit()
    
    print("\n✅ Import complete!")
    print(f"   New documents: {imported_count}")
    print(f"   Updated documents: {updated_count}")
    print(f"   Skipped (empty): {skipped_count}")
    print(f"   Total processed: {imported_count + updated_count}")
    
    return imported_count + updated_count


def main():
    """Main entry point."""
    # Set up database connection
    engine = create_engine(
        f'sqlite:///{DEFAULT_DB_FILE}',
        connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get directories to import
    repo_root = pathlib.Path(__file__).parent.parent
    modules_dir = repo_root / 'documents' / 'reference' / 'adventures_md' / 'adventurers_guild_modules'
    generated_dir = repo_root / 'documents' / 'reference' / 'adventures_md' / 'generated_content'
    homebrew_dir = repo_root / 'documents' / 'reference' / 'adventures_md' / 'homebrew_adventures'
    
    print(f"📂 Guild modules directory: {modules_dir}")
    print(f"📂 Generated content directory: {generated_dir}")
    print(f"📂 Homebrew adventures directory: {homebrew_dir}")
    print("📂 Checking paths...")
    print(f"   Modules exists: {modules_dir.exists()}")
    print(f"   Generated exists: {generated_dir.exists()}")
    print(f"   Homebrew exists: {homebrew_dir.exists()}")
    print()
    
    # Import from both directories
    total_count = 0
    
    if modules_dir.exists():
        print("=" * 70)
        print("Importing Guild Modules...")
        print("=" * 70)
        count = import_guild_modules(session, modules_dir)
        total_count += count
        print(f"✓ Imported {count} guild module documents")
        print()
    
    if generated_dir.exists():
        print("=" * 70)
        print("Importing Generated Content...")
        print("=" * 70)
        count = import_guild_modules(session, generated_dir)
        total_count += count
        print(f"✓ Imported {count} generated content documents")
        print()
    
    if homebrew_dir.exists():
        print("=" * 70)
        print("Importing Homebrew Adventures...")
        print("=" * 70)
        count = import_guild_modules(session, homebrew_dir)
        total_count += count
        print(f"✓ Imported {count} homebrew adventure documents")
        print()
    
    session.close()
    
    if total_count > 0:
        print("=" * 70)
        print(f"🎉 Successfully imported {total_count} total documents!")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Run chunk_documents.py to split into retrievable chunks")
        print("   2. Run generate_chunk_embeddings.py to create embeddings")
        print("\n   Commands:")
        print("   python scripts\\chunk_documents.py")
        print("   python scripts\\generate_chunk_embeddings.py")
        print("\n💡 These modules will now be available in campaign creation!")
        print("   - Module-specific content for adventure hooks")
        print("   - Location and NPC details for rich encounters")
        print("   - Mission structures for organized play")
    else:
        print("\n⚠️  No documents were imported.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
