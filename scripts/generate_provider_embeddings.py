"""Generate embeddings using a provider (LM Studio or OpenAI) and store in SQLite.

Configuration:
 - EMBED_PROVIDER: 'lmstudio' or 'openai' (default: 'lmstudio')
 - LMSTUDIO_API_URL / LMSTUDIO_API_KEY for LM Studio client (if used)
 - OPENAI_API_KEY for OpenAI (if used)

This script is intentionally small and synchronous for simplicity. It upserts into
`monster_embeddings` as JSON text under `vector` column.
"""
import os
import json
import time
from typing import List

from sqlalchemy.orm import Session
from datetime import datetime
import sys

# Make sure repository root is on sys.path so `backend` package can be imported when running from /scripts
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.database import SessionLocal
from backend.models import MonsterStat, MonsterEmbedding

try:
    import requests
except Exception:
    requests = None


def call_lmstudio_embedding(texts: List[str]):
    api_url = os.getenv('LMSTUDIO_API_URL')
    api_key = os.getenv('LMSTUDIO_API_KEY')
    if not api_url or not api_key:
        raise RuntimeError('LM Studio API config missing: set LMSTUDIO_API_URL and LMSTUDIO_API_KEY')
    payload = {'inputs': texts}
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    r = requests.post(f'{api_url}/embeddings', json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()


def call_openai_embeddings(texts: List[str]):
    import openai
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise RuntimeError('OPENAI_API_KEY not set')
    openai.api_key = key
    embeddings = []
    for t in texts:
        resp = openai.Embedding.create(input=t, model='text-embedding-3-small')
        embeddings.append(resp['data'][0]['embedding'])
    return embeddings


def pseudo_embed(text: str, dim: int = 128):
    import hashlib
    import struct
    h = hashlib.sha256(text.encode('utf-8')).digest()
    vec = []
    i = 0
    while len(vec) < dim:
        chunk = h[i % len(h): (i % len(h)) + 8]
        if len(chunk) < 8:
            chunk = chunk.ljust(8, b"\0")
        val = struct.unpack(
            ">Q", chunk
        )[0]
        f = ((val % 1000003) / 1000003.0) * 2 - 1
        vec.append(f)
        i += 8
    return vec


def generate_with_orm(batch: int = 16, provider: str | None = None):
    session: Session = SessionLocal()
    try:
        # Use ORM column query for id, name, actions to stay ORM-based while selecting only needed fields
        res = session.query(MonsterStat.id, MonsterStat.name, MonsterStat.actions).order_by(MonsterStat.id).all()
        if not res:
            print('No monsters found in DB')
            return 0

        # rows are tuples: (id, name, actions)
        provider = (provider or os.getenv('EMBED_PROVIDER', 'pseudo')).lower()
        i = 0
        count = 0
        while i < len(res):
            chunk = res[i:i+batch]
            texts = [((r[1] or '') + '\n' + (r[2] or '')) for r in chunk]
            vectors = None
            if provider == 'lmstudio':
                if requests is None:
                    raise RuntimeError('requests package is required for LM Studio provider')
                resp = call_lmstudio_embedding(texts)
                # try common keys
                vectors = resp.get('embeddings') or resp.get('data') or resp
            elif provider == 'openai':
                vectors = call_openai_embeddings(texts)
            else:
                # pseudo fallback
                vectors = [pseudo_embed(t, dim=128) for t in texts]

            ts = datetime.utcnow()
            for row, vec in zip(chunk, vectors):
                mid = row[0]
                vj = json.dumps(vec)
                # Try an UPDATE first to avoid loading rows that may have incompatible stored types
                updated = session.query(MonsterEmbedding).filter_by(monster_id=mid).update(
                    {MonsterEmbedding.vector: vj, MonsterEmbedding.updated_at: ts},
                    synchronize_session=False,
                )
                if not updated:
                    emb = MonsterEmbedding(monster_id=mid, vector=vj, created_at=ts, updated_at=ts)
                    session.add(emb)
                count += 1
            session.commit()
            i += batch

        print(f'Wrote embeddings for {count} monsters (provider={provider})')
        return count
    finally:
        session.close()


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--batch', type=int, default=16)
    p.add_argument('--provider', default=None)
    args = p.parse_args()
    generate_with_orm(batch=args.batch, provider=args.provider)
