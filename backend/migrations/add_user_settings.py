"""
Migration: Add user_settings table

Creates user_settings table for persisting user preferences across sessions.
Replaces localStorage-based settings with database-backed settings.

Run with:
    python backend/migrations/add_user_settings.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
import logging

# Get database URL
DEFAULT_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'storycraft.db'))
DATABASE_URL = os.environ.get('STORYCRAFT_DATABASE_URL', f"sqlite:///{DEFAULT_DB_FILE}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add user_settings table to database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        logger.info("Adding user_settings table...")
        
        # Create user_settings table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                
                -- TTS Settings
                tts_provider VARCHAR(50) DEFAULT 'kitten',
                tts_voice VARCHAR(50) DEFAULT 'tara',
                tts_enabled BOOLEAN DEFAULT 1,
                tts_auto_play BOOLEAN DEFAULT 0,
                tts_speed REAL DEFAULT 1.0,
                tts_model VARCHAR(50) DEFAULT 'standard',
                
                -- UI Preferences
                theme VARCHAR(20) DEFAULT 'dark',
                compact_mode BOOLEAN DEFAULT 0,
                show_dice_rolls BOOLEAN DEFAULT 1,
                
                -- RAG Settings
                rag_enabled BOOLEAN DEFAULT 1,
                rag_top_k INTEGER DEFAULT 5,
                
                -- LLM Settings
                preferred_provider VARCHAR(50) DEFAULT 'groq',
                preferred_model VARCHAR(100),
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 2000,
                
                -- Accessibility Settings
                font_size VARCHAR(20) DEFAULT 'medium',
                high_contrast BOOLEAN DEFAULT 0,
                reduce_animations BOOLEAN DEFAULT 0,
                
                -- Notification Settings
                sound_enabled BOOLEAN DEFAULT 1,
                dice_sound_enabled BOOLEAN DEFAULT 1,
                combat_alerts BOOLEAN DEFAULT 1,
                
                -- Metadata
                settings_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create index on user_id for faster lookups
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_settings_user_id 
            ON user_settings(user_id)
        """))
        
        # Create default settings record for single-user mode
        result = conn.execute(text("SELECT COUNT(*) as count FROM user_settings"))
        count = result.fetchone()[0]
        
        if count == 0:
            logger.info("Creating default settings record...")
            conn.execute(text("""
                INSERT INTO user_settings (user_id) VALUES (NULL)
            """))
            logger.info("Default settings created")
        else:
            logger.info(f"Found {count} existing settings records")
        
        conn.commit()
        logger.info("✅ Migration completed successfully!")


def rollback():
    """Remove user_settings table (for testing)"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        logger.info("Rolling back user_settings table...")
        conn.execute(text("DROP TABLE IF EXISTS user_settings"))
        conn.commit()
        logger.info("✅ Rollback completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="User Settings Migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop table)"
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback()
    else:
        migrate()
