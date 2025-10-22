"""Ingest adventure creation documents into RAG system.

Imports DMG Chapter 3 documents from documents/reference/adventures_md/
into the references table with ref_type='adventures_md'.

Usage:
  python scripts\\ingest_adventures.py
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
                    
                    # Handle tags array
                    if key == 'tags' and value.startswith('['):
                        # Parse tags like [dnd, dmg, adventure-creation]
                        tags = re.findall(r'(\w+(?:-\w+)*)', value)
                        metadata[key] = tags
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


def import_adventures(db_session, adventures_dir: pathlib.Path) -> int:
    """
    Import all adventure .md files from adventures_dir into references table.
    
    Args:
        db_session: SQLAlchemy session
        adventures_dir: Path to adventures_md folder
        
    Returns:
        Number of files imported
    """
    if not adventures_dir.exists():
        print(f"❌ Adventures folder not found: {adventures_dir}")
        return 0
    
    files = sorted(adventures_dir.glob('*.md'))
    
    if not files:
        print(f"❌ No .md files found in {adventures_dir}")
        return 0
    
    print(f"📚 Importing {len(files)} adventure documents...")
    
    imported_count = 0
    updated_count = 0
    
    for file_path in tqdm(files, desc="Processing"):
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Strip frontmatter and get metadata
            clean_content, metadata = strip_frontmatter(content)
            
            # Extract title
            title = metadata.get('title') or extract_title_from_content(clean_content, file_path.stem)
            
            # Create machine key from filename
            key = file_path.stem
            
            # Extract tags from metadata
            tags = metadata.get('tags', [])
            if not isinstance(tags, list):
                tags = [tags] if tags else []
            
            # Add 'adventures' tag if not present
            if 'adventures' not in tags:
                tags.append('adventures')
            if 'dmg' not in tags:
                tags.append('dmg')
            
            # Check if reference already exists
            existing = db_session.query(Reference).filter(
                Reference.ref_type == 'adventures_md',
                Reference.key == key
            ).first()
            
            if existing:
                # Update existing reference
                existing.title = title
                existing.content = clean_content
                existing.tags = tags
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Create new reference
                ref = Reference(
                    ref_type='adventures_md',
                    key=key,
                    title=title,
                    content=clean_content,
                    source_url=None,
                    tags=tags,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db_session.add(ref)
                imported_count += 1
            
            # Commit in batches of 10
            if (imported_count + updated_count) % 10 == 0:
                db_session.commit()
        
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            continue
    
    # Final commit
    db_session.commit()
    
    print(f"\n✅ Import complete!")
    print(f"   New documents: {imported_count}")
    print(f"   Updated documents: {updated_count}")
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
    
    # Get adventures directory
    repo_root = pathlib.Path(__file__).parent.parent
    adventures_dir = repo_root / 'documents' / 'reference' / 'adventures_md'
    
    print(f"📂 Adventures directory: {adventures_dir}")
    
    # Import adventures
    count = import_adventures(session, adventures_dir)
    
    session.close()
    
    if count > 0:
        print(f"\n🎉 Successfully imported {count} adventure documents!")
        print(f"\n📝 Next steps:")
        print(f"   1. Run chunk_documents.py to split into retrievable chunks")
        print(f"   2. Run generate_chunk_embeddings.py to create embeddings")
        print(f"\n   Commands:")
        print(f"   python scripts\\chunk_documents.py")
        print(f"   python scripts\\generate_chunk_embeddings.py")
    else:
        print("\n⚠️  No documents were imported.")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
