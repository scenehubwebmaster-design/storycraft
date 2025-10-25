"""
Database migration: Add Journal System and Enhanced NPC Tracking

This migration adds:
1. New NPC fields for portrait storage and enhanced tracking
2. New JournalEntry table for campaign event logging
3. Indexes for efficient journal/NPC queries

Run with: python -m backend.migrate_add_journal_and_npc_enhancements
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
import logging

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .database import SQLALCHEMY_DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add new columns and table for journal system."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        logger.info("Starting journal system migration...")
        
        # Step 1: Add new NPC columns
        npc_columns = [
            ("portrait_path", "TEXT"),
            ("portrait_prompt", "TEXT"),
            ("first_met_location", "TEXT"),
            ("first_met_session", "INTEGER"),
            ("last_interaction", "TIMESTAMP"),
            ("importance", "INTEGER DEFAULT 1"),
            ("tags", "TEXT"),  # JSON
            ("quests_related", "TEXT"),  # JSON
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]
        
        for col_name, col_type in npc_columns:
            try:
                sql = f"ALTER TABLE npcs ADD COLUMN {col_name} {col_type}"
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"✅ Added column npcs.{col_name}")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    logger.info(f"⏭️  Column npcs.{col_name} already exists, skipping")
                else:
                    logger.error(f"❌ Error adding npcs.{col_name}: {e}")
        
        # Step 2: Create journal_entries table
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                chat_session_id INTEGER,
                chat_message_id INTEGER,
                entry_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                npc_id INTEGER,
                quest_id INTEGER,
                location_name VARCHAR(255),
                importance INTEGER DEFAULT 3,
                tags TEXT,
                involved_characters TEXT,
                game_session_number INTEGER,
                chroma_doc_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(id),
                FOREIGN KEY (chat_message_id) REFERENCES chat_messages(id),
                FOREIGN KEY (npc_id) REFERENCES npcs(id),
                FOREIGN KEY (quest_id) REFERENCES quests(id)
            )
            """
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("✅ Created table journal_entries")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info("⏭️  Table journal_entries already exists, skipping")
            else:
                logger.error(f"❌ Error creating journal_entries: {e}")
                raise
        
        # Step 3: Create indexes for efficient queries
        indexes = [
            ("idx_journal_campaign", "journal_entries", "campaign_id"),
            ("idx_journal_entry_type", "journal_entries", "entry_type"),
            ("idx_journal_created_at", "journal_entries", "created_at"),
            ("idx_journal_importance", "journal_entries", "importance"),
            ("idx_npc_game_session", "npcs", "game_session_id"),
            ("idx_npc_importance", "npcs", "importance"),
        ]
        
        for idx_name, table, column in indexes:
            try:
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})"
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"✅ Created index {idx_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"⏭️  Index {idx_name} already exists, skipping")
                else:
                    logger.warning(f"⚠️  Could not create index {idx_name}: {e}")
        
        logger.info("🎉 Migration complete!")
        logger.info("\nNext steps:")
        logger.info("1. Run: python backend/batch_generate_npc_portraits.py --dry-run")
        logger.info("2. Generate portraits: python backend/batch_generate_npc_portraits.py")
        logger.info("3. Restart backend server to mount static files")

if __name__ == "__main__":
    run_migration()
