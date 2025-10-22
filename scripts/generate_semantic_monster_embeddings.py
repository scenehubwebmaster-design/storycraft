"""Generate real semantic embeddings for all monsters using sentence-transformers.

This replaces the pseudo-embeddings with actual semantic embeddings.

Usage:
  python scripts\\generate_semantic_monster_embeddings.py --db e:\\storycraft\\storycraft.db
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
    from backend.models import MonsterStat, MonsterEmbedding, Base

    db_path = args.db or DEFAULT_DB_FILE
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    
    # Ensure tables exist
    Base.metadata.create_all(engine)

    print(f'Loading sentence transformer model: {args.model}...')
    model = SentenceTransformer(args.model)
    print(f'Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}')

    session = Session()
    
    # Get all monsters
    monsters = session.query(MonsterStat).all()
    print(f'Generating semantic embeddings for {len(monsters)} monsters...')
    
    # Prepare texts for batch encoding
    texts = []
    for mon in monsters:
        # Create embedding text from name, CR, and key attributes
        parts = [
            mon.name or '',
            f"CR {mon.cr or 0}",
            mon.traits or '',
            mon.actions or ''
        ]
        text_blob = '\n'.join(p for p in parts if p).strip()[:1000]
        texts.append(text_blob)
    
    # Encode in batches with progress bar
    embeddings = model.encode(
        texts, 
        batch_size=args.batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print('Storing embeddings in database...')
    for mon, embedding in tqdm(zip(monsters, embeddings), total=len(monsters)):
        vec_json = json.dumps(embedding.tolist())
        
        # Upsert embedding
        emb = session.query(MonsterEmbedding).filter(MonsterEmbedding.monster_id == mon.id).first()
        if emb:
            emb.vector = vec_json
            emb.updated_at = datetime.utcnow()
        else:
            emb = MonsterEmbedding(monster_id=mon.id, vector=vec_json)
            session.add(emb)
        
        # Commit in batches of 100
        if mon.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    print(f'✅ Done! Generated semantic embeddings for {len(monsters)} monsters.')
    print(f'   Model: {args.model}')
    print(f'   Dimensions: {model.get_sentence_embedding_dimension()}')


if __name__ == '__main__':
    main()
