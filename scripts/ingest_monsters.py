"""Ingest monsters from 5thsrd.org into storycraft.db

This script currently scrapes the Monster Index page for links, then fetches
each monster page and stores a compact set of fields in the `monster_stats`
table. It is idempotent and uses upsert behavior.

Usage: python scripts/ingest_monsters.py --db e:\storycraft\storycraft.db
"""
from __future__ import annotations
import argparse
import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin

MONSTER_INDEX = "https://5thsrd.org/gamemaster_rules/monster_indexes/monsters_by_name/"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", name.lower()).strip("_")


def parse_stat_block(soup: BeautifulSoup) -> dict:
    # Try to extract common quick fields: CR, AC, HP, Speed, ability scores, senses, languages
    out = {}
    # Many pages have a table or a header with lines like 'Armor Class 15 (natural armor)'
    text = soup.get_text(separator="\n")
    # crude extractions
    m_cr = re.search(r"Challenge\s*\n?\s*([\d\/\.]+)\s*", text, re.IGNORECASE)
    if m_cr:
        out["cr"] = m_cr.group(1).strip()
    m_ac = re.search(r"Armor Class\s*\n?\s*([0-9() a-zA-Z+-]+)", text, re.IGNORECASE)
    if m_ac:
        out["ac"] = m_ac.group(1).strip()
    m_hp = re.search(r"Hit Points\s*\n?\s*([0-9() +dtdr\-]+)", text, re.IGNORECASE)
    if m_hp:
        out["hp"] = m_hp.group(1).strip()
    m_speed = re.search(r"Speed\s*\n?\s*([0-9a-zA-Z ,()\-]+)", text, re.IGNORECASE)
    if m_speed:
        out["speed"] = m_speed.group(1).strip()

    # ability scores: look for lines like 'STR 18 (+4) DEX 12 (+1)'
    m_stats = re.search(r"STR\s*(\d+)\s*\([^)]+\)\s*DEX\s*(\d+)\s*\([^)]+\)\s*CON\s*(\d+)\s*\([^)]+\)\s*INT\s*(\d+)\s*\([^)]+\)\s*WIS\s*(\d+)\s*\([^)]+\)\s*CHA\s*(\d+)", text, re.IGNORECASE)
    if m_stats:
        out.update({
            "str": int(m_stats.group(1)),
            "dex": int(m_stats.group(2)),
            "con": int(m_stats.group(3)),
            "int": int(m_stats.group(4)),
            "wis": int(m_stats.group(5)),
            "cha": int(m_stats.group(6)),
        })

    # Senses & Languages
    m_senses = re.search(r"Senses\s*\n?\s*([^\n]+)", text, re.IGNORECASE)
    if m_senses:
        out["senses"] = m_senses.group(1).strip()
    m_lang = re.search(r"Languages\s*\n?\s*([^\n]+)", text, re.IGNORECASE)
    if m_lang:
        out["languages"] = m_lang.group(1).strip()

    return out


def extract_monster_links(index_html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(index_html, "html.parser")
    links = []
    for a in soup.select("a"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if href and "/monsters/" in href and text:
            full = urljoin(MONSTER_INDEX, href)
            links.append((text, full))
    # dedupe preserving order
    seen = set()
    dedup = []
    for name, url in links:
        if url in seen:
            continue
        seen.add(url)
        dedup.append((name, url))
    return dedup


def numeric_cr_value(cr_text: str | None) -> float | None:
    if not cr_text:
        return None
    cr_text = cr_text.strip()
    # handle fractions like 1/2 -> 0.5
    if "/" in cr_text:
        try:
            num, den = cr_text.split("/")
            return float(num) / float(den)
        except Exception:
            return None
    try:
        return float(cr_text)
    except Exception:
        # sometimes CRs are like '1/2 (100 XP)'
        m = re.search(r"(\d+\/\d+|\d+\.?\d*)", cr_text)
        if m:
            t = m.group(1)
            if "/" in t:
                n, d = t.split("/")
                return float(n) / float(d)
            return float(t)
    return None


def upsert_monster(conn: sqlite3.Connection, monster: dict):
    cur = conn.cursor()
    # columns list
    cols = [
        "name",
        "slug",
        "url",
        "cr",
        "numeric_cr",
        "ac",
        "hp",
        "speed",
        "str",
        "dex",
        "con",
        "int",
        "wis",
        "cha",
        "senses",
        "languages",
        "traits",
        "actions",
        "reactions",
        "legendary_actions",
        "source",
        "raw_html",
    ]
    placeholders = ",".join(["?" for _ in cols])
    update_assign = ",".join([f"{c}=excluded.{c}" for c in cols if c != "name"])

    sql = f"""
    INSERT INTO monster_stats ({','.join(cols)})
    VALUES ({placeholders})
    ON CONFLICT(name) DO UPDATE SET
      {update_assign}, updated_at=CURRENT_TIMESTAMP
    ;
    """
    values = [monster.get(c) for c in cols]
    cur.execute(sql, values)
    conn.commit()


def fetch_monster_page(url: str) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="Path to storycraft.db")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of monsters to ingest (0 = all)")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    # ensure table exists
    with open("scripts/create_monster_stats.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    print("Fetching monster index...")
    idx_html = requests.get(MONSTER_INDEX, timeout=20).text
    links = extract_monster_links(idx_html)
    print(f"Found {len(links)} monster links")
    if args.limit and args.limit > 0:
        links = links[: args.limit]

    for name, url in links:
        print(f"Processing {name} -> {url}")
        try:
            page = fetch_monster_page(url)
            soup = BeautifulSoup(page, "html.parser")
            parsed = parse_stat_block(soup)
            monster = {
                "name": name,
                "slug": slugify(name),
                "url": url,
                "cr": parsed.get("cr"),
                "numeric_cr": numeric_cr_value(parsed.get("cr")),
                "ac": parsed.get("ac"),
                "hp": parsed.get("hp"),
                "speed": parsed.get("speed"),
                "str": parsed.get("str"),
                "dex": parsed.get("dex"),
                "con": parsed.get("con"),
                "int": parsed.get("int"),
                "wis": parsed.get("wis"),
                "cha": parsed.get("cha"),
                "senses": parsed.get("senses"),
                "languages": parsed.get("languages"),
                "traits": json.dumps([], ensure_ascii=False),
                "actions": json.dumps([], ensure_ascii=False),
                "reactions": json.dumps([], ensure_ascii=False),
                "legendary_actions": json.dumps([], ensure_ascii=False),
                "source": "5thsrd",
                "raw_html": page,
            }
            upsert_monster(conn, monster)
        except Exception as e:
            print(f"Failed {name}: {e}")


if __name__ == "__main__":
    main()
