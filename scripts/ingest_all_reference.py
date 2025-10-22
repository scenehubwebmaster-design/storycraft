"""
Ingest All D&D Reference Content into ChromaDB

This script ingests ALL markdown files from documents/reference/ into ChromaDB,
organizing content by folder type with appropriate metadata and chunking strategies.

Folders processed:
- dnd_mechanics/    : Core D&D rules and mechanics
- classes_md/       : PHB 2024 class guides
- spells_md/        : Individual spell descriptions
- monsters_md/      : Monster stat blocks
- magic_items_md/   : Magic item descriptions
- equipment_md/     : Equipment and gear
- species_md/       : Character races/species
- adventures_md/    : DMG adventure creation guides
- core/            : Dungeon generation rules
- generated_lists/ : Pre-organized reference lists
- weapons_md/      : Weapon details
- tools_md/        : Tool proficiencies
- themes/          : Campaign themes

Usage:
    python scripts/ingest_all_reference.py [--clear-existing] [--folders classes_md spells_md]
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import chromadb  # type: ignore
from chromadb.config import Settings  # type: ignore
from typing import List, Dict, Optional
import hashlib
import time


# Folder configurations with metadata
FOLDER_CONFIGS = {
    'dnd_mechanics': {
        'description': 'Core D&D 5e mechanics and rules',
        'chunk_size': 1000,
        'priority': 1
    },
    'classes_md': {
        'description': 'PHB 2024 class guides and features',
        'chunk_size': 1200,
        'priority': 1
    },
    'adventures_md': {
        'description': 'DMG adventure creation and structure guides',
        'chunk_size': 1000,
        'priority': 1
    },
    'core': {
        'description': 'Dungeon generation rules and tables',
        'chunk_size': 800,
        'priority': 1
    },
    'equipment_md': {
        'description': 'Equipment, gear, and adventuring supplies',
        'chunk_size': 600,
        'priority': 2
    },
    'species_md': {
        'description': 'Character races and species traits',
        'chunk_size': 1000,
        'priority': 2
    },
    'spells_md': {
        'description': 'Individual spell descriptions',
        'chunk_size': 800,
        'priority': 2
    },
    'monsters_md': {
        'description': 'Monster stat blocks and lore',
        'chunk_size': 1000,
        'priority': 2
    },
    'magic_items_md': {
        'description': 'Magic item descriptions and properties',
        'chunk_size': 800,
        'priority': 2
    },
    'generated_lists': {
        'description': 'Pre-organized reference lists',
        'chunk_size': 1200,
        'priority': 3
    },
    'weapons_md': {
        'description': 'Weapon statistics and properties',
        'chunk_size': 600,
        'priority': 3
    },
    'tools_md': {
        'description': 'Tool proficiencies and usage',
        'chunk_size': 600,
        'priority': 3
    },
    'themes': {
        'description': 'Campaign themes and settings',
        'chunk_size': 1000,
        'priority': 3
    }
}


def chunk_markdown_by_sections(
    content: str,
    filename: str,
    folder: str,
    max_chunk_size: int = 1000
) -> List[Dict[str, str]]:
    """
    Chunk markdown content by section headers with folder-specific strategies.
    """
    chunks = []
    
    # Special handling for different content types
    if folder == 'spells_md' or folder == 'monsters_md' or folder == 'magic_items_md':
        # These are typically single entities, chunk more conservatively
        if len(content) <= max_chunk_size * 2:
            # Small file, keep as single chunk with context
            chunks.append({
                'text': content.strip(),
                'metadata': {
                    'source': filename,
                    'folder': folder,
                    'section': 'full',
                    'type': 'reference'
                }
            })
            return chunks
    
    # Split by ## headers (main sections)
    sections = re.split(r'\n## ', content)
    
    # First section is file header
    if sections[0].strip():
        # Extract title from first line if it's a # header
        header_text = sections[0].strip()
        title_match = re.match(r'^#\s+(.+)$', header_text.split('\n')[0])
        section_name = title_match.group(1) if title_match else 'header'
        
        chunks.append({
            'text': header_text,
            'metadata': {
                'source': filename,
                'folder': folder,
                'section': section_name,
                'type': 'reference'
            }
        })
    
    # Process each main section
    for section in sections[1:]:
        lines = section.split('\n', 1)
        section_title = lines[0].strip()
        section_content = lines[1] if len(lines) > 1 else ''
        
        # If section fits in one chunk
        if len(section_content) <= max_chunk_size:
            chunks.append({
                'text': f"## {section_title}\n\n{section_content}",
                'metadata': {
                    'source': filename,
                    'folder': folder,
                    'section': section_title,
                    'type': 'reference'
                }
            })
        else:
            # Split by ### subsections
            subsections = re.split(r'\n### ', section_content)
            
            # First part before any subsection
            if subsections[0].strip():
                chunks.append({
                    'text': f"## {section_title}\n\n{subsections[0].strip()}",
                    'metadata': {
                        'source': filename,
                        'folder': folder,
                        'section': section_title,
                        'type': 'reference'
                    }
                })
            
            # Process subsections
            for subsection in subsections[1:]:
                subsection_lines = subsection.split('\n', 1)
                subsection_title = subsection_lines[0].strip()
                subsection_content = subsection_lines[1] if len(subsection_lines) > 1 else ''
                
                if len(subsection_content) > max_chunk_size:
                    # Split by paragraphs
                    paragraphs = subsection_content.split('\n\n')
                    current_chunk = ''
                    
                    for para in paragraphs:
                        if len(current_chunk) + len(para) <= max_chunk_size:
                            current_chunk += para + '\n\n'
                        else:
                            if current_chunk.strip():
                                chunks.append({
                                    'text': f"## {section_title} - {subsection_title}\n\n{current_chunk.strip()}",
                                    'metadata': {
                                        'source': filename,
                                        'folder': folder,
                                        'section': f"{section_title} - {subsection_title}",
                                        'type': 'reference'
                                    }
                                })
                            current_chunk = para + '\n\n'
                    
                    if current_chunk.strip():
                        chunks.append({
                            'text': f"## {section_title} - {subsection_title}\n\n{current_chunk.strip()}",
                            'metadata': {
                                'source': filename,
                                'folder': folder,
                                'section': f"{section_title} - {subsection_title}",
                                'type': 'reference'
                            }
                        })
                else:
                    chunks.append({
                        'text': f"## {section_title}\n### {subsection_title}\n\n{subsection_content}",
                        'metadata': {
                            'source': filename,
                            'folder': folder,
                            'section': f"{section_title} - {subsection_title}",
                            'type': 'reference'
                        }
                    })
    
    return chunks


def generate_chunk_id(text: str, source: str, folder: str, index: int) -> str:
    """Generate unique ID for chunk."""
    content = f"{folder}_{source}_{index}_{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


def ingest_reference_folder(
    folder_path: Path,
    folder_name: str,
    collection,
    config: Dict,
    stats: Dict
) -> None:
    """
    Ingest all markdown files from a single folder.
    """
    if not folder_path.exists():
        print(f"  ⚠️  Folder not found: {folder_path}")
        return
    
    md_files = list(folder_path.glob("*.md"))
    
    if not md_files:
        print(f"  ⚠️  No markdown files in {folder_name}/")
        return
    
    print(f"\n📁 {folder_name}/ ({len(md_files)} files)")
    print(f"   {config['description']}")
    
    folder_chunks = 0
    folder_chars = 0
    
    for md_file in sorted(md_files):
        filename_stem = md_file.stem
        
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Chunk content
            chunks = chunk_markdown_by_sections(
                content,
                filename_stem,
                folder_name,
                config['chunk_size']
            )
            
            if not chunks:
                continue
            
            # Prepare batch data
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = generate_chunk_id(
                    chunk['text'],
                    filename_stem,
                    folder_name,
                    i
                )
                documents.append(chunk['text'])
                metadatas.append(chunk['metadata'])
                ids.append(chunk_id)
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            folder_chunks += len(chunks)
            folder_chars += sum(len(c['text']) for c in chunks)
            
            # Progress indicator
            if len(md_files) > 20:
                print('.', end='', flush=True)
            else:
                print(f"   ✅ {filename_stem}.md ({len(chunks)} chunks)")
        
        except Exception as e:
            print(f"\n   ❌ Error processing {md_file.name}: {e}")
    
    if len(md_files) > 20:
        print()  # Newline after dots
    
    print(f"   📊 Total: {folder_chunks} chunks, {folder_chars:,} characters")
    
    stats['folders_processed'] += 1
    stats['total_files'] += len(md_files)
    stats['total_chunks'] += folder_chunks
    stats['total_chars'] += folder_chars


def ingest_all_reference(
    reference_dir: Path = Path("documents/reference"),
    chroma_db_path: Path = Path("backend/chroma_db"),
    collection_name: str = "dnd_reference",
    clear_existing: bool = False,
    folders_filter: Optional[List[str]] = None
) -> Dict:
    """
    Ingest all D&D reference content into ChromaDB.
    """
    print("=" * 70)
    print("🎲 D&D REFERENCE INGESTION - FULL CONTENT")
    print("=" * 70)
    print(f"📁 Source: {reference_dir}")
    print(f"💾 ChromaDB: {chroma_db_path}")
    print(f"📦 Collection: {collection_name}")
    
    if folders_filter:
        print(f"🎯 Folders: {', '.join(folders_filter)}")
    else:
        print(f"🎯 Folders: ALL ({len(FOLDER_CONFIGS)} configured)")
    
    print("=" * 70)
    
    start_time = time.time()
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(
        path=str(chroma_db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Handle existing collection
    if clear_existing:
        try:
            client.delete_collection(collection_name)
            print(f"🗑️  Cleared existing collection: {collection_name}\n")
        except Exception:
            pass
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Complete D&D 5e reference content"}
    )
    
    # Statistics
    stats = {
        'folders_processed': 0,
        'total_files': 0,
        'total_chunks': 0,
        'total_chars': 0
    }
    
    # Determine which folders to process
    folders_to_process = folders_filter if folders_filter else list(FOLDER_CONFIGS.keys())
    
    # Sort by priority
    folders_to_process.sort(key=lambda f: FOLDER_CONFIGS.get(f, {}).get('priority', 999))
    
    # Process each folder
    for folder_name in folders_to_process:
        if folder_name not in FOLDER_CONFIGS:
            print(f"⚠️  Unknown folder: {folder_name} (skipping)")
            continue
        
        folder_path = reference_dir / folder_name
        config = FOLDER_CONFIGS[folder_name]
        
        ingest_reference_folder(
            folder_path,
            folder_name,
            collection,
            config,
            stats
        )
    
    elapsed_time = time.time() - start_time
    
    # Final summary
    print()
    print("=" * 70)
    print("📊 INGESTION COMPLETE")
    print("=" * 70)
    print(f"Folders processed: {stats['folders_processed']}")
    print(f"Files processed: {stats['total_files']}")
    print(f"Chunks created: {stats['total_chunks']:,}")
    print(f"Total characters: {stats['total_chars']:,}")
    print(f"Average chunk size: {stats['total_chars'] // stats['total_chunks'] if stats['total_chunks'] > 0 else 0} chars")
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print()
    print("✅ D&D reference ingestion complete!")
    print()
    
    return stats


def list_available_folders(reference_dir: Path = Path("documents/reference")):
    """List all available folders and their configurations."""
    print("📚 Available Reference Folders:")
    print("=" * 70)
    
    for folder_name, config in sorted(FOLDER_CONFIGS.items(), key=lambda x: x[1]['priority']):
        folder_path = reference_dir / folder_name
        if folder_path.exists():
            md_files = list(folder_path.glob("*.md"))
            status = f"✅ {len(md_files)} files"
        else:
            status = "❌ Not found"
        
        print(f"[P{config['priority']}] {folder_name:20s} - {config['description'][:40]:40s} {status}")
    
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest D&D reference content into ChromaDB"
    )
    parser.add_argument(
        '--clear-existing',
        action='store_true',
        help='Clear existing collection before ingesting'
    )
    parser.add_argument(
        '--folders',
        nargs='+',
        help='Specific folders to ingest (default: all)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available folders and exit'
    )
    parser.add_argument(
        '--collection',
        default='dnd_reference',
        help='ChromaDB collection name (default: dnd_reference)'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_folders()
    else:
        ingest_all_reference(
            clear_existing=args.clear_existing,
            folders_filter=args.folders,
            collection_name=args.collection
        )
