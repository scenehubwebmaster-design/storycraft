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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='all-MiniLM-L6-v2', help='Sentence transformer model')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size for encoding')
    args = parser.parse_args()
    
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f'Loading sentence transformer model: {args.model}...')
    model = SentenceTransformer(args.model)
    print(f'Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}')
    
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
        batch_size=args.batch_size,
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
            emb.model = args.model
        else:
            emb = ChunkEmbedding(
                chunk_id=chunk.id,
                vector=vec_json,
                model=args.model
            )
            session.add(emb)
        
        # Commit in batches
        if chunk.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    print(f'\n✅ Done! Generated embeddings for {len(chunks)} chunks.')
    print(f'   Model: {args.model}')
    print(f'   Dimensions: {model.get_sentence_embedding_dimension()}')


if __name__ == '__main__':
    main()
