-- Migration: create monster_stats table
-- Run this SQL against storycraft.db to create the table used by the monster ingestion script.

CREATE TABLE IF NOT EXISTS monster_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT UNIQUE,
    url TEXT,
    cr TEXT,
    numeric_cr REAL,
    ac TEXT,
    hp TEXT,
    speed TEXT,
    str INTEGER,
    dex INTEGER,
    con INTEGER,
    int INTEGER,
    wis INTEGER,
    cha INTEGER,
    senses TEXT,
    languages TEXT,
    traits TEXT, -- JSON string
    actions TEXT, -- JSON string
    reactions TEXT, -- JSON string
    legendary_actions TEXT, -- JSON string
    source TEXT,
    raw_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_monster_slug ON monster_stats(slug);
CREATE INDEX IF NOT EXISTS idx_monster_numeric_cr ON monster_stats(numeric_cr);
CREATE INDEX IF NOT EXISTS idx_monster_name ON monster_stats(name);
