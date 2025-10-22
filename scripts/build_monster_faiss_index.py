"""Build a FAISS index from monster_embeddings stored in the SQLite DB.

Requires faiss-cpu installed (pip install faiss-cpu).

Output:
 - faiss_index.bin
 - faiss_id_map.json (list of monster ids in index order)
"""
import sqlite3
import json
import numpy as np
import os


try:
    import faiss
except Exception:
    faiss = None


def build(db_path: str, out_dir: str = 'data/faiss'):
    os.makedirs(out_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT monster_id, vector FROM monster_embeddings')
    rows = cur.fetchall()
    if not rows:
        print('No embeddings found')
        return
    ids = []
    vecs = []
    for mid, vj in rows:
        try:
            vec = json.loads(vj)
        except Exception:
            continue
        ids.append(mid)
        vecs.append(vec)
    if faiss is None:
        print('faiss is not installed in this Python environment.')
        print('\nTo install (pip - recommended for most users):')
        print('  pip install faiss-cpu')
        print('\nIf you use conda (conda-forge):')
        print('  conda install -c conda-forge faiss-cpu')
        print('\nOnce installed, re-run this script to build the index.')
        return
    arr = np.array(vecs).astype('float32')
    dim = arr.shape[1]
    index = faiss.IndexFlatIP(dim)
    # normalize vectors for IP cosine
    faiss.normalize_L2(arr)
    index.add(arr)
    faiss.write_index(index, os.path.join(out_dir, 'faiss_index.bin'))
    with open(os.path.join(out_dir, 'faiss_id_map.json'), 'w', encoding='utf-8') as f:
        json.dump(ids, f)
    print(f'Built index with {len(ids)} vectors')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=False, default='storycraft.db')
    p.add_argument('--out', default='data/faiss')
    args = p.parse_args()
    build(args.db, args.out)
