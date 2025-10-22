"""Parse markdown monster files and import structured stats into the ORM MonsterStat table.

Also generates pseudo-embeddings and stores them in MonsterEmbedding.

Usage:
  python scripts\import_monsters_md_to_stats.py --db e:\\storycraft\\storycraft.db --limit 50
"""
from __future__ import annotations
from datetime import datetime
import os
import re
import json
import argparse
import pathlib
import hashlib
import struct
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure repository root is on sys.path so 'backend' package imports work when running scripts directly
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from datetime import datetime


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


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", name.lower()).strip("_")


def parse_markdown_fields(text: str) -> dict:
    out = {}
    m_cr = re.search(r"Challenge\s*\n?\s*([\d\/\.]+)", text, re.IGNORECASE)
    if m_cr:
        out['cr'] = m_cr.group(1).strip()
    m_ac = re.search(r"Armor Class\s*\n?\s*([0-9() a-zA-Z+-]+)", text, re.IGNORECASE)
    if m_ac:
        out['ac'] = m_ac.group(1).strip()
    m_hp = re.search(r"Hit Points\s*\n?\s*([0-9() +dtdr\-]+)", text, re.IGNORECASE)
    if m_hp:
        out['hp'] = m_hp.group(1).strip()
    m_speed = re.search(r"Speed\s*\n?\s*([0-9a-zA-Z ,()\-]+)", text, re.IGNORECASE)
    if m_speed:
        out['speed'] = m_speed.group(1).strip()

    m_stats = re.search(r"STR\s*(\d+)\D+DEX\s*(\d+)\D+CON\s*(\d+)\D+INT\s*(\d+)\D+WIS\s*(\d+)\D+CHA\s*(\d+)", text, re.IGNORECASE)
    if m_stats:
        out.update({
            'str': int(m_stats.group(1)),
            'dex': int(m_stats.group(2)),
            'con': int(m_stats.group(3)),
            'int': int(m_stats.group(4)),
            'wis': int(m_stats.group(5)),
            'cha': int(m_stats.group(6)),
        })

    # Capture Traits / Actions / Reactions / Legendary sections.
    # We'll look for headings like 'Traits', 'Actions', 'Reactions', 'Legendary Actions'
    # fallback simple heading regex too
    sec_map = {'traits': [], 'actions': [], 'reactions': [], 'legendary_actions': []}
    # Try markdown-style headings (### Actions) or plain headings followed by newline
    for m in re.finditer(r"^(?:#{1,4}\s*)?(Traits|Actions|Reactions|Legendary Actions)[:\s]*\n([\s\S]*?)(?=\n#{1,4}\s*\w|\n[A-Z][a-z]+|$)", text, flags=re.IGNORECASE | re.MULTILINE):
        heading = m.group(1).strip().lower()
        body = m.group(2).strip()
        key = heading.replace(' ', '_')
        # split into named entries: lines that look like 'Berserk. ...' or 'Claw. Melee Weapon Attack...'
        parts = [p.strip() for p in re.split(r"\n\s*(?=[A-Z][a-z0-9'\- ]+\.)", body) if p.strip()]
        entries = []
        for p in parts:
            # name is up to the first period
            if '.' in p:
                name, desc = p.split('.', 1)
                entries.append({'name': name.strip(), 'desc': desc.strip()})
            else:
                entries.append({'name': '', 'desc': p})
        if key in sec_map:
            sec_map[key] = entries

    out['traits'] = json.dumps(sec_map['traits'], ensure_ascii=False)
    out['actions'] = json.dumps(sec_map['actions'], ensure_ascii=False)
    out['reactions'] = json.dumps(sec_map['reactions'], ensure_ascii=False)
    out['legendary_actions'] = json.dumps(sec_map['legendary_actions'], ensure_ascii=False)

    # Damage/resistances/immunities and saving throws extraction (heuristic)
    m_res = re.search(r"Damage Resistances\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if m_res:
        out['damage_resistances'] = m_res.group(1).strip()
    m_imm = re.search(r"Damage Immunities\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if m_imm:
        out['damage_immunities'] = m_imm.group(1).strip()
    m_cimm = re.search(r"Condition Immunities\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if m_cimm:
        out['condition_immunities'] = m_cimm.group(1).strip()
    m_saves = re.search(r"Saving Throws\s*:\s*([^\n]+)", text, re.IGNORECASE)
    if m_saves:
        out['saving_throws'] = m_saves.group(1).strip()
    # keep freeform damage line if present
    m_damage_line = re.search(r"(\b\w+ damage\b[\s\S]*?)\n", text, re.IGNORECASE)
    if m_damage_line:
        out['damage'] = m_damage_line.group(1).strip()

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=False, default=None)
    p.add_argument('--docs-root', default=None)
    p.add_argument('--limit', type=int, default=0)
    args = p.parse_args()

    # import backend models after ensuring repo_root is on sys.path
    from backend.database import DEFAULT_DB_FILE
    from backend.models import MonsterStat, MonsterEmbedding, Base

    db_path = args.db or DEFAULT_DB_FILE
    docs_root = args.docs_root or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'documents'))
    mons_folder = pathlib.Path(docs_root) / 'reference' / 'monsters_md'
    if not mons_folder.exists():
        print('Monsters folder not found at', mons_folder)
        return 2

    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    # Ensure tables exist
    Base.metadata.create_all(engine)

    session = Session()
    files = sorted(mons_folder.rglob('*.md'))
    if args.limit > 0:
        files = files[: args.limit]
    print(f'Importing {len(files)} monster files...')

    for pth in files:
        try:
            text = pth.read_text(encoding='utf-8')
        except Exception:
            continue
        stem = pth.stem
        name = stem.replace('_', ' ').title()
        slug = slugify(stem)
        fields = parse_markdown_fields(text)

        # Upsert MonsterStat
        mon = session.query(MonsterStat).filter(MonsterStat.name == name).first()
        if mon:
            mon.slug = slug
            mon.cr = fields.get('cr')
            mon.ac = fields.get('ac')
            mon.hp = fields.get('hp')
            mon.speed = fields.get('speed')
            mon.str = fields.get('str')
            mon.dex = fields.get('dex')
            mon.con = fields.get('con')
            mon.int = fields.get('int')
            mon.wis = fields.get('wis')
            mon.cha = fields.get('cha')
            mon.traits = fields.get('traits')
            mon.actions = fields.get('actions')
            mon.reactions = fields.get('reactions')
            mon.legendary_actions = fields.get('legendary_actions')
            mon.damage_resistances = fields.get('damage_resistances')
            mon.damage_immunities = fields.get('damage_immunities')
            mon.condition_immunities = fields.get('condition_immunities')
            mon.saving_throws = fields.get('saving_throws')
            mon.raw_html = None
            mon.source = 'local_md'
            mon.updated_at = datetime.utcnow()
        else:
            mon = MonsterStat(
                name=name,
                slug=slug,
                cr=fields.get('cr'),
                ac=fields.get('ac'),
                hp=fields.get('hp'),
                speed=fields.get('speed'),
                str=fields.get('str'),
                dex=fields.get('dex'),
                con=fields.get('con'),
                int=fields.get('int'),
                wis=fields.get('wis'),
                cha=fields.get('cha'),
                traits=fields.get('traits'),
                actions=fields.get('actions'),
                reactions=fields.get('reactions'),
                legendary_actions=fields.get('legendary_actions'),
                damage_resistances=fields.get('damage_resistances'),
                damage_immunities=fields.get('damage_immunities'),
                condition_immunities=fields.get('condition_immunities'),
                saving_throws=fields.get('saving_throws'),
                source='local_md',
            )
            session.add(mon)
        session.commit()

        # generate and upsert embedding
        text_blob = (name or '') + '\n' + (fields.get('actions') or '')
        vec = pseudo_embed(text_blob, dim=128)
        vec_json = json.dumps(vec)
        emb = session.query(MonsterEmbedding).filter(MonsterEmbedding.monster_id == mon.id).first()
        if emb:
            emb.vector = vec_json
            emb.updated_at = datetime.utcnow()
        else:
            emb = MonsterEmbedding(monster_id=mon.id, vector=vec_json)
            session.add(emb)
        session.commit()

    session.close()
    print('Done importing monsters.')


if __name__ == '__main__':
    main()
