"""Split reference documents into chunks for better RAG retrieval.

Chunks are 512 tokens max with 50-token overlap to preserve context.
Headings are preserved to maintain document structure.

Usage:
  python scripts\\chunk_documents.py [--max-tokens 512] [--overlap 50]
"""
import sys
import os
import re
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference, DocumentChunk
from tqdm import tqdm


def count_tokens(text: str) -> int:
    """Approximate token count (rough estimate: 1 token ≈ 4 characters)."""
    return len(text) // 4


def extract_heading(text: str) -> str:
    """Extract markdown heading from text if present."""
    # Look for markdown heading at start: # Heading or ## Heading
    match = re.match(r'^#{1,6}\s+(.+?)$', text.strip(), re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def chunk_document(content: str, max_tokens: int = 512, overlap_tokens: int = 50):
    """
    Split document into chunks with overlap.
    
    Strategy:
    1. Split on double newlines (paragraphs)
    2. Respect markdown headings
    3. Keep chunks under max_tokens
    4. Add overlap_tokens from previous chunk for context
    
    Args:
        content: Document content to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Tokens of overlap between chunks
    
    Returns:
        List of (chunk_text, heading) tuples
    """
    if not content or not content.strip():
        return []
    
    # Split into sections by markdown headings
    # This keeps related content together
    heading_pattern = r'(^#{1,6}\s+.+?$)'
    parts = re.split(heading_pattern, content, flags=re.MULTILINE)
    
    chunks = []
    current_chunk = ""
    current_heading = None
    previous_overlap = ""
    
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        
        # Check if this is a heading
        if re.match(r'^#{1,6}\s+', part):
            # Save current chunk if it exists
            if current_chunk.strip():
                chunks.append((current_chunk.strip(), current_heading))
                # Keep some text for overlap
                chunk_tokens = current_chunk.split()
                if len(chunk_tokens) > overlap_tokens:
                    previous_overlap = ' '.join(chunk_tokens[-overlap_tokens:])
                else:
                    previous_overlap = current_chunk
            
            # Start new chunk with heading
            current_heading = extract_heading(part)
            current_chunk = previous_overlap + "\n\n" + part if previous_overlap else part
            previous_overlap = ""
        else:
            # Add content to current chunk
            potential_chunk = current_chunk + "\n\n" + part if current_chunk else part
            
            if count_tokens(potential_chunk) > max_tokens:
                # Chunk is too large, split it
                if current_chunk.strip():
                    # Save what we have
                    chunks.append((current_chunk.strip(), current_heading))
                    # Keep overlap
                    chunk_tokens = current_chunk.split()
                    if len(chunk_tokens) > overlap_tokens:
                        previous_overlap = ' '.join(chunk_tokens[-overlap_tokens:])
                    else:
                        previous_overlap = current_chunk
                
                # Start new chunk with overlap + new part
                current_chunk = (previous_overlap + "\n\n" + part) if previous_overlap else part
                
                # If even the new part alone is too large, split by paragraphs
                if count_tokens(current_chunk) > max_tokens:
                    paragraphs = part.split('\n\n')
                    temp_chunk = previous_overlap if previous_overlap else ""
                    
                    for para in paragraphs:
                        if count_tokens(temp_chunk + "\n\n" + para) > max_tokens:
                            if temp_chunk.strip():
                                chunks.append((temp_chunk.strip(), current_heading))
                                # Overlap
                                para_tokens = temp_chunk.split()
                                if len(para_tokens) > overlap_tokens:
                                    temp_chunk = ' '.join(para_tokens[-overlap_tokens:]) + "\n\n" + para
                                else:
                                    temp_chunk = para
                            else:
                                temp_chunk = para
                        else:
                            temp_chunk = temp_chunk + "\n\n" + para if temp_chunk else para
                    
                    current_chunk = temp_chunk
            else:
                current_chunk = potential_chunk
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append((current_chunk.strip(), current_heading))
    
    return chunks


def chunk_all_documents(max_tokens=512, overlap=50, limit=None):
    """
    Chunk all documents and return statistics.
    
    Returns:
        dict: Statistics about the chunking process
    """
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get all references
    query = session.query(Reference)
    if limit:
        query = query.limit(limit)
    refs = query.all()
    
    print(f'Chunking {len(refs)} documents...')
    print(f'  Max tokens per chunk: {max_tokens}')
    print(f'  Overlap: {overlap} tokens')
    
    total_chunks = 0
    refs_with_chunks = 0
    single_chunk_docs = 0
    multi_chunk_docs = 0
    
    for ref in tqdm(refs, desc="Processing"):
        content = ref.content or ''
        
        if not content.strip():
            continue
        
        # Delete existing chunks for this reference
        session.query(DocumentChunk).filter(DocumentChunk.source_id == ref.id).delete()
        
        # Create chunks
        chunks = chunk_document(content, max_tokens=max_tokens, overlap_tokens=overlap)
        
        if not chunks:
            continue
        
        refs_with_chunks += 1
        if len(chunks) == 1:
            single_chunk_docs += 1
        else:
            multi_chunk_docs += 1
        
        # Save chunks
        for idx, (chunk_text, heading) in enumerate(chunks):
            chunk = DocumentChunk(
                source_id=ref.id,
                chunk_index=idx,
                chunk_text=chunk_text,
                heading=heading,
                token_count=count_tokens(chunk_text)
            )
            session.add(chunk)
            total_chunks += 1
        
        # Commit in batches
        if ref.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    stats = {
        'documents_processed': len(refs),
        'documents_with_chunks': refs_with_chunks,
        'single_chunk_documents': single_chunk_docs,
        'multi_chunk_documents': multi_chunk_docs,
        'total_chunks': total_chunks,
        'avg_chunks_per_doc': total_chunks / refs_with_chunks if refs_with_chunks > 0 else 0
    }
    
    print('\n✅ Chunking complete!')
    print('\nStatistics:')
    print(f'  Documents processed: {stats["documents_processed"]}')
    print(f'  Documents with chunks: {stats["documents_with_chunks"]}')
    print(f'  Single-chunk documents: {stats["single_chunk_documents"]}')
    print(f'  Multi-chunk documents: {stats["multi_chunk_documents"]}')
    print(f'  Total chunks created: {stats["total_chunks"]}')
    print(f'  Average chunks per document: {stats["avg_chunks_per_doc"]:.2f}')
    
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-tokens', type=int, default=512, help='Maximum tokens per chunk')
    parser.add_argument('--overlap', type=int, default=50, help='Overlap tokens between chunks')
    parser.add_argument('--limit', type=int, help='Limit number of documents to process (for testing)')
    args = parser.parse_args()
    
    chunk_all_documents(max_tokens=args.max_tokens, overlap=args.overlap, limit=args.limit)
    print('\nNext step: Run generate_chunk_embeddings.py')


if __name__ == '__main__':
    main()
