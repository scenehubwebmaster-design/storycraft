from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..database import get_db
from sqlalchemy.orm import Session
import sqlite3
import json
import os
from pydantic import BaseModel
import hashlib
import struct
import math

router = APIRouter(prefix="/api/references", tags=["references_search"])


class SearchRequest(BaseModel):
    q: str
    k: Optional[int] = 5


def pseudo_embed(text: str, dim: int = 128):
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


def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


@router.post("/search", summary="Search references (vector search)")
def search_references(req: SearchRequest, db: Session = Depends(get_db)):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    db_path = os.path.join(repo_root, "storycraft.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="DB not found")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT ref_id, vector FROM reference_vectors')
    rows = cur.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No vectors found. Run embedding generation script.")

    # compute query embedding via pseudo_embed for now
    qvec = pseudo_embed(req.q, dim=128)
    candidates = []
    for ref_id, vec_json in rows:
        try:
            vec = json.loads(vec_json)
        except Exception:
            continue
        score = cosine(qvec, vec)
        candidates.append((score, ref_id))

    candidates.sort(reverse=True)
    topk = [ref_id for _, ref_id in candidates[: req.k]]
    if not topk:
        return {"results": []}

    # fetch full reference rows
    placeholders = ','.join('?' for _ in topk)
    cur.execute(f'SELECT id, ref_type, key, title, content FROM "references" WHERE id IN ({placeholders})', tuple(topk))
    docs = [
        {"id": r[0], "ref_type": r[1], "key": r[2], "title": r[3], "content": r[4]} for r in cur.fetchall()
    ]
    # preserve order of topk
    id2doc = {d['id']: d for d in docs}
    ordered = [id2doc[rid] for rid in topk if rid in id2doc]
    conn.close()
    return {"results": ordered}
