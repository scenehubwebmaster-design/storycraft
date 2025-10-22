"""
Ingest D&D Mechanics Markdown Files into ChromaDB

This script reads all markdown files from documents/reference/dnd_mechanics/
and ingests them into ChromaDB for RAG retrieval during gameplay.

Features:
- Chunks markdown content intelligently (by section headers)
- Preserves document structure and context
- Adds metadata for filtering (source file, section, type)
- Handles existing collections (adds to existing or creates new)
- Progress reporting and error handling

Usage:
    python scripts/ingest_dnd_mechanics.py
    
    Optional arguments:
    --clear-existing    Clear existing dnd_mechanics collection before ingesting
    --chunk-size 500    Maximum chunk size in characters (default: 1000)
"""

import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import chromadb  # type: ignore
from chromadb.config import Settings  # type: ignore
from typing import List, Dict
import hashlib


def chunk_markdown_by_sections(
    content: str, 
    filename: str, 
    max_chunk_size: int = 1000
) -> List[Dict[str, str]]:
    """
    Chunk markdown content by section headers while preserving context.
    
    Strategy:
    1. Split by ## headers (main sections)
    2. If section too large, split by ### headers (subsections)
    3. If still too large, split by paragraphs
    4. Include file and section context in each chunk
    
    Args:
        content: Raw markdown text
        filename: Source filename (without extension)
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of dicts with 'text', 'metadata' keys
    """
    chunks = []
    
    # Split by ## headers (main sections)
    sections = re.split(r'\n## ', content)
    
    # First section is file header (before first ##)
    if sections[0].strip():
        chunks.append({
            'text': sections[0].strip(),
            'metadata': {
                'source': filename,
                'section': 'header',
                'type': 'dnd_mechanics'
            }
        })
    
    # Process each main section
    for section in sections[1:]:
        # Extract section title (first line)
        lines = section.split('\n', 1)
        section_title = lines[0].strip()
        section_content = lines[1] if len(lines) > 1 else ''
        
        # If section small enough, add as single chunk
        if len(section_content) <= max_chunk_size:
            chunks.append({
                'text': f"## {section_title}\n\n{section_content}",
                'metadata': {
                    'source': filename,
                    'section': section_title,
                    'type': 'dnd_mechanics'
                }
            })
        else:
            # Section too large, split by ### subsections
            subsections = re.split(r'\n### ', section_content)
            
            # First part (before first ###)
            if subsections[0].strip():
                chunks.append({
                    'text': f"## {section_title}\n\n{subsections[0].strip()}",
                    'metadata': {
                        'source': filename,
                        'section': section_title,
                        'type': 'dnd_mechanics'
                    }
                })
            
            # Process subsections
            for subsection in subsections[1:]:
                subsection_lines = subsection.split('\n', 1)
                subsection_title = subsection_lines[0].strip()
                subsection_content = subsection_lines[1] if len(subsection_lines) > 1 else ''
                
                # If subsection still too large, split by paragraphs
                if len(subsection_content) > max_chunk_size:
                    paragraphs = subsection_content.split('\n\n')
                    current_chunk = ''
                    
                    for para in paragraphs:
                        if len(current_chunk) + len(para) <= max_chunk_size:
                            current_chunk += para + '\n\n'
                        else:
                            # Save current chunk
                            if current_chunk.strip():
                                chunks.append({
                                    'text': f"## {section_title} - {subsection_title}\n\n{current_chunk.strip()}",
                                    'metadata': {
                                        'source': filename,
                                        'section': f"{section_title} - {subsection_title}",
                                        'type': 'dnd_mechanics'
                                    }
                                })
                            current_chunk = para + '\n\n'
                    
                    # Save remaining chunk
                    if current_chunk.strip():
                        chunks.append({
                            'text': f"## {section_title} - {subsection_title}\n\n{current_chunk.strip()}",
                            'metadata': {
                                'source': filename,
                                'section': f"{section_title} - {subsection_title}",
                                'type': 'dnd_mechanics'
                            }
                        })
                else:
                    # Subsection fits in one chunk
                    chunks.append({
                        'text': f"## {section_title}\n### {subsection_title}\n\n{subsection_content}",
                        'metadata': {
                            'source': filename,
                            'section': f"{section_title} - {subsection_title}",
                            'type': 'dnd_mechanics'
                        }
                    })
    
    return chunks


def generate_chunk_id(text: str, source: str, index: int) -> str:
    """
    Generate unique, deterministic ID for chunk.
    
    Uses MD5 hash of content + source + index to ensure:
    - Same content always gets same ID (idempotent ingestion)
    - Different chunks never collide
    
    Args:
        text: Chunk text
        source: Source filename
        index: Chunk index in document
        
    Returns:
        Unique chunk ID string
    """
    content = f"{source}_{index}_{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


def ingest_dnd_mechanics(
    mechanics_dir: Path = Path("documents/reference/dnd_mechanics"),
    chroma_db_path: Path = Path("backend/chroma_db"),
    collection_name: str = "dnd_mechanics",
    clear_existing: bool = False,
    chunk_size: int = 1000
) -> Dict[str, int]:
    """
    Ingest all D&D mechanics markdown files into ChromaDB.
    
    Args:
        mechanics_dir: Directory containing markdown files
        chroma_db_path: Path to ChromaDB storage
        collection_name: Name of ChromaDB collection
        clear_existing: If True, clear existing collection before ingesting
        chunk_size: Maximum characters per chunk
        
    Returns:
        Dictionary with ingestion statistics
    """
    print("🎲 D&D Mechanics Ingestion")
    print(f"📁 Source: {mechanics_dir}")
    print(f"💾 ChromaDB: {chroma_db_path}")
    print(f"📦 Collection: {collection_name}")
    print(f"🧩 Chunk size: {chunk_size} chars")
    print("-" * 60)
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=str(chroma_db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    if clear_existing:
        try:
            client.delete_collection(collection_name)
            print(f"🗑️  Cleared existing collection: {collection_name}")
        except Exception:
            pass  # Collection didn't exist
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "D&D 5e mechanics reference for AI DM"}
    )
    
    # Find all markdown files
    md_files = list(mechanics_dir.glob("*.md"))
    
    if not md_files:
        print(f"❌ No markdown files found in {mechanics_dir}")
        return {"files": 0, "chunks": 0}
    
    print(f"📚 Found {len(md_files)} markdown files")
    print()
    
    # Track statistics
    stats = {
        "files": 0,
        "chunks": 0,
        "total_chars": 0
    }
    
    # Process each file
    for md_file in sorted(md_files):
        print(f"📖 Processing: {md_file.name}")
        
        # Read file content
        content = md_file.read_text(encoding='utf-8')
        filename_stem = md_file.stem  # filename without extension
        
        # Chunk content
        chunks = chunk_markdown_by_sections(content, filename_stem, chunk_size)
        
        if not chunks:
            print("  ⚠️  No chunks generated (empty file?)")
            continue
        
        # Prepare batch data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = generate_chunk_id(chunk['text'], filename_stem, i)
            documents.append(chunk['text'])
            metadatas.append(chunk['metadata'])
            ids.append(chunk_id)
        
        # Add to collection
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            stats['files'] += 1
            stats['chunks'] += len(chunks)
            stats['total_chars'] += sum(len(c['text']) for c in chunks)
            
            print(f"  ✅ Added {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Final summary
    print()
    print("=" * 60)
    print("📊 INGESTION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {stats['files']}")
    print(f"Chunks created: {stats['chunks']}")
    print(f"Total characters: {stats['total_chars']:,}")
    print(f"Average chunk size: {stats['total_chars'] // stats['chunks'] if stats['chunks'] > 0 else 0} chars")
    print()
    print("✅ D&D mechanics ingestion complete!")
    
    return stats


def test_retrieval(
    chroma_db_path: Path = Path("backend/chroma_db"),
    collection_name: str = "dnd_mechanics"
):
    """
    Test ChromaDB retrieval with sample queries.
    
    Verifies that ingestion worked by querying for common D&D terms.
    """
    print()
    print("🔍 Testing retrieval...")
    print("-" * 60)
    
    client = chromadb.PersistentClient(path=str(chroma_db_path))
    collection = client.get_collection(collection_name)
    
    # Test queries
    test_queries = [
        "What are the conditions in D&D?",
        "How do death saves work?",
        "Explain spell concentration mechanics",
        "How to build a five-room dungeon?",
        "What encounters are common in forests?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"\n  📄 Result {i+1} (from {metadata['source']}.md, section: {metadata['section']})")
                print(f"     {doc[:150]}..." if len(doc) > 150 else f"     {doc}")
        else:
            print("  ❌ No results found")
    
    print()
    print("✅ Retrieval test complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ingest D&D mechanics markdown files into ChromaDB"
    )
    parser.add_argument(
        '--clear-existing',
        action='store_true',
        help='Clear existing dnd_mechanics collection before ingesting'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Maximum chunk size in characters (default: 1000)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run retrieval tests after ingestion'
    )
    
    args = parser.parse_args()
    
    # Run ingestion
    stats = ingest_dnd_mechanics(
        clear_existing=args.clear_existing,
        chunk_size=args.chunk_size
    )
    
    # Run tests if requested
    if args.test and stats['chunks'] > 0:
        test_retrieval()
