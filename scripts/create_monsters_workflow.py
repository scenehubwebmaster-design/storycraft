r"""Monsters RAG workflow helper

Actions:
 - generate pseudo embeddings for monsters (upsert into monster_embeddings)
 - build FAISS index (calls scripts/build_monster_faiss_index.build)
 - test backend /api/monsters/search endpoint

Usage examples:
 python scripts\create_monsters_workflow.py --db e:\\storycraft\\storycraft.db --generate-embeddings --rebuild-faiss --test-endpoint --query fireball

"""
from __future__ import annotations
import argparse
import sqlite3
import json
import hashlib
import struct
import os
import time
import sys
from typing import List


def pseudo_embed(text: str, dim: int = 128) -> List[float]:
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


def ensure_embeddings_table(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS monster_embeddings (
            monster_id INTEGER PRIMARY KEY,
            vector TEXT,
            updated_at REAL
        )
        """
    )
    conn.commit()


def generate_monster_embeddings(db_path: str, limit: int = 0) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    ensure_embeddings_table(conn)
    q = "SELECT id, name, actions FROM monster_stats ORDER BY id"
    if limit and limit > 0:
        q += f" LIMIT {limit}"
    cur.execute(q)
    rows = cur.fetchall()
    if not rows:
        print("No monsters found in monster_stats table.")
        conn.close()
        return 0
    count = 0
    for mid, name, actions in rows:
        text_blob = (name or '') + '\n' + (actions or '')
        vec = pseudo_embed(text_blob, dim=128)
        vecj = json.dumps(vec)
        ts = time.time()
        cur.execute('SELECT monster_id FROM monster_embeddings WHERE monster_id=?', (mid,))
        if cur.fetchone():
            cur.execute('UPDATE monster_embeddings SET vector=?, updated_at=? WHERE monster_id=?', (vecj, ts, mid))
        else:
            cur.execute('INSERT INTO monster_embeddings(monster_id, vector, updated_at) VALUES (?, ?, ?)', (mid, vecj, ts))
        count += 1
    conn.commit()
    conn.close()
    print(f'Generated embeddings for {count} monsters')
    return count


def build_faiss_index(db_path: str, out_dir: str):
    # Import the build function from the existing script
    try:
        from scripts.build_monster_faiss_index import build
    except Exception:
        # fallback to module import path
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from scripts.build_monster_faiss_index import build
    build(db_path, out_dir)


def test_backend_search(query: str, k: int = 5):
    import requests

    url = f'http://127.0.0.1:8000/api/monsters/search?q={requests.utils.quote(query)}&k={k}'
    try:
        r = requests.get(url, timeout=10)
        print('STATUS', r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
    except Exception as e:
        print('Error calling backend:', e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', default=r'e:\storycraft\storycraft.db')
    p.add_argument('--generate-embeddings', action='store_true')
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--rebuild-faiss', action='store_true')
    p.add_argument('--faiss-out', default=r'e:\storycraft\data\faiss')
    p.add_argument('--test-endpoint', action='store_true')
    p.add_argument('--query', default='fireball')
    args = p.parse_args()

    db_path = args.db
    if args.generate_embeddings:
        generate_monster_embeddings(db_path, limit=args.limit)

    if args.rebuild_faiss:
        print('Building FAISS index...')
        build_faiss_index(db_path, args.faiss_out)

    if args.test_endpoint:
        print('Testing backend endpoint...')
        test_backend_search(args.query)


if __name__ == '__main__':
    main()
