"""Add metadata columns to references table.

This migration adds level, rarity, school, category, and tags columns
to enable filtered searches.

Usage:
  python scripts\\migrate_add_metadata_columns.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from backend.database import DEFAULT_DB_FILE

def main():
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    
    print("Adding metadata columns to references table...")
    
    with engine.connect() as conn:
        # Check if columns already exist
        result = conn.execute(text('PRAGMA table_info("references")'))
        columns = {row[1] for row in result}
        
        if 'level' not in columns:
            print("  Adding 'level' column...")
            conn.execute(text('ALTER TABLE "references" ADD COLUMN level INTEGER'))
            conn.commit()
        else:
            print("  'level' column already exists")
        
        if 'rarity' not in columns:
            print("  Adding 'rarity' column...")
            conn.execute(text('ALTER TABLE "references" ADD COLUMN rarity VARCHAR(50)'))
            conn.commit()
        else:
            print("  'rarity' column already exists")
        
        if 'school' not in columns:
            print("  Adding 'school' column...")
            conn.execute(text('ALTER TABLE "references" ADD COLUMN school VARCHAR(100)'))
            conn.commit()
        else:
            print("  'school' column already exists")
        
        if 'category' not in columns:
            print("  Adding 'category' column...")
            conn.execute(text('ALTER TABLE "references" ADD COLUMN category VARCHAR(100)'))
            conn.commit()
        else:
            print("  'category' column already exists")
        
        if 'tags' not in columns:
            print("  Adding 'tags' column...")
            conn.execute(text('ALTER TABLE "references" ADD COLUMN tags TEXT'))  # JSON stored as TEXT
            conn.commit()
        else:
            print("  'tags' column already exists")
    
    # Create indexes for better query performance
    print("\nCreating indexes...")
    with engine.connect() as conn:
        try:
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_references_level ON "references"(level)'))
            conn.commit()
            print("  Created index on level")
        except Exception as e:
            print(f"  Index on level: {e}")
        
        try:
            conn.execute(text('CREATE INDEX IF NOT EXISTS idx_references_rarity ON "references"(rarity)'))
            conn.commit()
            print("  Created index on rarity")
        except Exception as e:
            print(f"  Index on rarity: {e}")
    
    print("\n✅ Migration complete!")
    print("\nNext step: Run extract_reference_metadata.py to populate these fields")

if __name__ == '__main__':
    main()
