import sqlite3
import json
import hashlib
import struct
import math

def pseudo_embed(text: str, dim: int = 128):
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


def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def search(query, topk=5):
    conn = sqlite3.connect(r"e:/storycraft/storycraft.db")
    cur = conn.cursor()
    qv = pseudo_embed(query, dim=128)
    cur.execute('SELECT ref_id, vector FROM reference_vectors')
    rows = cur.fetchall()
    scored = []
    for rid, vj in rows:
        try:
            vec = json.loads(vj)
        except Exception:
            continue
        score = cosine(qv, vec)
        scored.append((score, rid))
    scored.sort(reverse=True)
    out = []
    for score, rid in scored[:topk]:
        cur.execute('SELECT title FROM "references" WHERE id=?', (rid,))
        row = cur.fetchone()
        out.append((score, rid, row[0] if row else None))
    conn.close()
    return out


if __name__ == '__main__':
    for item in search('fireball', topk=7):
        print(item)
