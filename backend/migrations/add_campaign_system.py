"""
Database Migration: Add Campaign System
========================================

Adds tables for D&D campaign management:
- campaigns: Campaign metadata and state
- campaign_characters: Links characters to campaigns with current state
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "storycraft.db"


def migrate():
    """Add campaign system tables."""
    print("=" * 70)
    print("Campaign System Migration")
    print("=" * 70)
    print(f"\n📁 Database: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create campaigns table
        print("📝 Creating campaigns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                setting VARCHAR(100),
                difficulty VARCHAR(20),
                campaign_type VARCHAR(50),
                starting_level INTEGER DEFAULT 1,
                current_level INTEGER DEFAULT 1,
                dm_session_id INTEGER,
                current_scene_type VARCHAR(50) DEFAULT 'roleplay',
                current_location VARCHAR(200),
                quest_log TEXT,
                npc_tracker TEXT,
                session_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dm_session_id) REFERENCES dm_sessions(id) ON DELETE SET NULL
            )
        """)
        print("   ✅ campaigns table created")
        
        # Create campaign_characters junction table
        print("📝 Creating campaign_characters table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                character_id INTEGER NOT NULL,
                current_hp INTEGER,
                current_resources TEXT,
                status VARCHAR(20) DEFAULT 'active',
                conditions TEXT,
                position_in_initiative INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                UNIQUE(campaign_id, character_id)
            )
        """)
        print("   ✅ campaign_characters table created")
        
        # Create indexes for performance
        print("📝 Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_campaigns_dm_session 
            ON campaigns(dm_session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_campaign_chars_campaign 
            ON campaign_characters(campaign_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_campaign_chars_character 
            ON campaign_characters(character_id)
        """)
        print("   ✅ Indexes created")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✨ Migration Complete!")
        print("=" * 70)
        print("\nCampaign system tables created:")
        print("   • campaigns")
        print("   • campaign_characters")
        print("\n🎉 Ready for D&D campaign management!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
