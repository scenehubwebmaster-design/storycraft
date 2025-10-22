"""Generate pseudo-embeddings for all references using the ORM ReferenceEmbedding model.

Usage:
  python scripts\generate_reference_embeddings.py --db e:\\storycraft\\storycraft.db
"""
from __future__ import annotations
from datetime import datetime
import os
import json
import argparse
import hashlib
import struct
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure repository root is on sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


def pseudo_embed(text: str, dim: int = 128):
    """Generate a pseudo-embedding vector from text using SHA256 hashing."""
    h = hashlib.sha256(text.encode('utf-8')).digest()
    vec = []
    i = 0
    while len(vec) < dim:
        chunk = h[i % len(h): (i % len(h)) + 8]
        if len(chunk) < 8:
            chunk = chunk.ljust(8, b'\0')
        val = struct.unpack('>Q', chunk)[0]
        f = ((val % 1000003) / 1000003.0) * 2 - 1
        vec.append(f)
        i += 8
    return vec


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=False, default=None)
    args = p.parse_args()

    from backend.database import DEFAULT_DB_FILE
    from backend.models import Reference, ReferenceEmbedding, Base

    db_path = args.db or DEFAULT_DB_FILE
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    
    # Ensure tables exist
    Base.metadata.create_all(engine)

    session = Session()
    
    # Get all references
    refs = session.query(Reference).all()
    print(f'Generating embeddings for {len(refs)} references...')
    
    for ref in refs:
        # Create embedding text from title + content
        text_blob = (ref.title or '') + '\n' + (ref.content or '')
        vec = pseudo_embed(text_blob, dim=128)
        vec_json = json.dumps(vec)
        
        # Upsert embedding
        emb = session.query(ReferenceEmbedding).filter(ReferenceEmbedding.reference_id == ref.id).first()
        if emb:
            emb.vector = vec_json
            emb.updated_at = datetime.utcnow()
        else:
            emb = ReferenceEmbedding(reference_id=ref.id, vector=vec_json)
            session.add(emb)
        
        session.commit()
    
    session.close()
    print(f'Done generating embeddings for {len(refs)} references.')


if __name__ == '__main__':
    main()
