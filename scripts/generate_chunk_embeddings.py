"""Generate semantic embeddings for document chunks.

Uses sentence-transformers (all-MiniLM-L6-v2) to create 384-dim embeddings.

Usage:
  python scripts\\generate_chunk_embeddings.py [--batch-size 32]
"""
import sys
import os
import json
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import DocumentChunk, ChunkEmbedding
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def generate_embeddings(model_name='all-MiniLM-L6-v2', batch_size=32):
    """
    Generate embeddings for all chunks and return statistics.
    
    Returns:
        dict: Statistics about the embedding generation
    """
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f'Loading sentence transformer model: {model_name}...')
    model = SentenceTransformer(model_name)
    embedding_dim = model.get_sentence_embedding_dimension()
    print(f'Model loaded. Embedding dimension: {embedding_dim}')
    
    # Get all chunks
    chunks = session.query(DocumentChunk).all()
    print(f'Generating embeddings for {len(chunks)} chunks...')
    
    # Prepare texts for batch encoding
    texts = []
    for chunk in chunks:
        # Use heading + chunk text for embedding
        text = f"{chunk.heading}\n{chunk.chunk_text}" if chunk.heading else chunk.chunk_text
        texts.append(text)
    
    # Encode in batches with progress bar
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print('Storing embeddings in database...')
    for chunk, embedding in tqdm(zip(chunks, embeddings), total=len(chunks)):
        vec_json = json.dumps(embedding.tolist())
        
        # Upsert embedding
        emb = session.query(ChunkEmbedding).filter(ChunkEmbedding.chunk_id == chunk.id).first()
        if emb:
            emb.vector = vec_json
            emb.model = model_name
        else:
            emb = ChunkEmbedding(
                chunk_id=chunk.id,
                vector=vec_json,
                model=model_name
            )
            session.add(emb)
        
        # Commit in batches
        if chunk.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    stats = {
        'total_embeddings': len(chunks),
        'model': model_name,
        'embedding_dimension': embedding_dim
    }
    
    print(f'\n✅ Done! Generated embeddings for {len(chunks)} chunks.')
    print(f'   Model: {model_name}')
    print(f'   Dimensions: {embedding_dim}')
    
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='all-MiniLM-L6-v2', help='Sentence transformer model')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for encoding')
    args = parser.parse_args()
    
    generate_embeddings(model_name=args.model, batch_size=args.batch_size)


if __name__ == '__main__':
    main()
