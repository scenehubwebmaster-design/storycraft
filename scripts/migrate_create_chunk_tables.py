"""Create document_chunks and chunk_embeddings tables.

This enables chunked RAG retrieval for better granularity on long documents.

Usage:
  python scripts\\migrate_create_chunk_tables.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from backend.database import DEFAULT_DB_FILE
from backend.models import Base, DocumentChunk, ChunkEmbedding

def main():
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    
    print("Creating chunk tables...")
    
    # Create tables if they don't exist
    DocumentChunk.__table__.create(engine, checkfirst=True)
    print("  ✓ document_chunks table created")
    
    ChunkEmbedding.__table__.create(engine, checkfirst=True)
    print("  ✓ chunk_embeddings table created")
    
    print("\n✅ Migration complete!")
    print("\nNext steps:")
    print("  1. Run chunk_documents.py to split references into chunks")
    print("  2. Run generate_chunk_embeddings.py to create embeddings for chunks")

if __name__ == '__main__':
    main()
