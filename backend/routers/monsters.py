from fastapi import APIRouter, HTTPException
from typing import Optional
import os
import sqlite3
import json
import math

router = APIRouter(prefix="/api/monsters", tags=["monsters"])


def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


@router.get("/search")
def search_monsters(q: Optional[str] = None, k: int = 5, name: Optional[str] = None, cr: Optional[str] = None):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_path = os.path.join(repo_root, 'storycraft.db')
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail='DB not found')

    # Try FAISS index
    faiss_dir = os.path.join(repo_root, 'data', 'faiss')
    use_faiss = False
    try:
        import faiss
        use_faiss = os.path.exists(os.path.join(faiss_dir, 'faiss_index.bin'))
    except Exception:
        use_faiss = False

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Name or CR filters only
    filters = []
    params = []
    if name:
        filters.append('lower(name) LIKE ?')
        params.append(f'%{name.lower()}%')
    if cr:
        filters.append('cr = ?')
        params.append(cr)

    if q and use_faiss:
        # load index and id map
        idx = faiss.read_index(os.path.join(faiss_dir, 'faiss_index.bin'))
        with open(os.path.join(faiss_dir, 'faiss_id_map.json'), 'r', encoding='utf-8') as f:
            ids = json.load(f)
        
        # Use sentence-transformers for real semantic query encoding
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        vec = model.encode(q).tolist()
        
        import numpy as np
        v = np.array([vec]).astype('float32')
        faiss.normalize_L2(v)
        distances, indices = idx.search(v, k)
        result_ids = [ids[i] for i in indices[0] if i < len(ids)]
        # fetch results
        if not result_ids:
            conn.close()
            return {'results': []}
        placeholders = ','.join('?' for _ in result_ids)
        cur.execute(f'SELECT id, name, cr, ac, hp FROM monster_stats WHERE id IN ({placeholders})', tuple(result_ids))
        rows = cur.fetchall()
        conn.close()
        return {'results': [{'id': r[0], 'name': r[1], 'cr': r[2], 'ac': r[3], 'hp': r[4]} for r in rows]}

    # fallback: simple SQL + in-memory vector similarity if q provided
    where = ('WHERE ' + ' AND '.join(filters)) if filters else ''
    cur.execute(f'SELECT id, name, cr, ac, hp FROM monster_stats {where} ORDER BY name LIMIT 500', tuple(params))
    rows = cur.fetchall()
    results = [{'id': r[0], 'name': r[1], 'cr': r[2], 'ac': r[3], 'hp': r[4]} for r in rows]

    if q:
        # Use sentence-transformers for real semantic embeddings
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        qv = model.encode(q).tolist()
        
        # Load embeddings from database
        cur.execute('SELECT monster_id, vector FROM monster_embeddings')
        vecs = {r[0]: json.loads(r[1]) for r in cur.fetchall()}
        
        scored = []
        for r in results:
            vid = r['id']
            if vid in vecs:
                score = cosine(qv, vecs[vid])
            else:
                score = 0.0
            scored.append((score, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = [s[1] for s in scored[:k]]
        conn.close()
        return {'results': out}

    conn.close()
    return {'results': results[:k]}
