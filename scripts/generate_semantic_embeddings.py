"""Generate real semantic embeddings for all references using sentence-transformers.

This replaces the pseudo-embeddings (SHA256-based) with actual semantic embeddings
that understand meaning and context.

Usage:
  python scripts\generate_semantic_embeddings.py --db e:\\storycraft\\storycraft.db
  
Model: all-MiniLM-L6-v2 (384 dimensions)
- Fast: ~1000 texts/second on CPU
- Small: 80MB model size
- Good quality: 0.68 on semantic search benchmarks
- Local: no API calls required
"""
from __future__ import annotations
from datetime import datetime
import os
import json
import argparse
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Ensure repository root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=False, default=None)
    p.add_argument('--model', default='all-MiniLM-L6-v2', help='Sentence transformer model name')
    p.add_argument('--batch-size', type=int, default=32, help='Batch size for encoding')
    args = p.parse_args()

    from backend.database import DEFAULT_DB_FILE
    from backend.models import Reference, ReferenceEmbedding, Base

    db_path = args.db or DEFAULT_DB_FILE
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    
    # Ensure tables exist
    Base.metadata.create_all(engine)

    print(f'Loading sentence transformer model: {args.model}...')
    model = SentenceTransformer(args.model)
    print(f'Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}')

    session = Session()
    
    # Get all references
    refs = session.query(Reference).all()
    print(f'Generating semantic embeddings for {len(refs)} references...')
    
    # Prepare texts for batch encoding
    texts = []
    for ref in refs:
        # Create embedding text: title is most important, then first 1000 chars of content
        text_blob = f"{ref.title or ''}\n{(ref.content or '')[:1000]}"
        texts.append(text_blob)
    
    # Encode in batches with progress bar
    embeddings = model.encode(
        texts, 
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print('Storing embeddings in database...')
    for ref, embedding in tqdm(zip(refs, embeddings), total=len(refs)):
        vec_json = json.dumps(embedding.tolist())
        
        # Upsert embedding
        emb = session.query(ReferenceEmbedding).filter(ReferenceEmbedding.reference_id == ref.id).first()
        if emb:
            emb.vector = vec_json
            emb.updated_at = datetime.utcnow()
        else:
            emb = ReferenceEmbedding(reference_id=ref.id, vector=vec_json)
            session.add(emb)
        
        # Commit in batches of 100 to improve performance
        if ref.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    print(f'✅ Done! Generated semantic embeddings for {len(refs)} references.')
    print(f'   Model: {args.model}')
    print(f'   Dimensions: {model.get_sentence_embedding_dimension()}')


if __name__ == '__main__':
    main()
