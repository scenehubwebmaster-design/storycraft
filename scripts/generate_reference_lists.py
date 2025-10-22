#!/usr/bin/env python3
"""Generate consolidated reference list documents for improved RAG retrieval.

Creates overview documents like:
- Spells by Level and School
- Magic Items by Rarity
- Monster Lists by CR
- DM Tools (encounters, dungeons, etc.)
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = "storycraft.db"
OUTPUT_DIR = Path("documents/reference/generated_lists")

def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_spell_lists(conn):
    """Generate spell list documents organized by level and school."""
    cursor = conn.cursor()
    
    # Get all spell schools
    cursor.execute('SELECT DISTINCT school FROM "references" WHERE ref_type="spells_md" AND school IS NOT NULL ORDER BY school')
    schools = [row[0] for row in cursor.fetchall()]
    
    print(f"Generating spell lists for {len(schools)} schools...")
    
    for school in schools:
        for level in range(0, 10):  # Levels 0-9
            cursor.execute('''
                SELECT title, key, content 
                FROM "references" 
                WHERE ref_type="spells_md" AND school=? AND level=?
                ORDER BY title
            ''', (school, level))
            
            spells = cursor.fetchall()
            
            if not spells:
                continue
            
            level_name = "Cantrip" if level == 0 else f"Level {level}"
            filename = f"spells_{school.lower()}_{level}.md"
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {school} Spells - {level_name}\n\n")
                f.write(f"A comprehensive list of {len(spells)} {school.lower()} spells at {level_name.lower()}.\n\n")
                f.write("---\n\n")
                
                for title, key, content in spells:
                    # Extract first paragraph or first 300 chars as summary
                    lines = content.split('\n') if content else []
                    summary_lines = []
                    char_count = 0
                    
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            summary_lines.append(line.strip())
                            char_count += len(line)
                            if char_count > 300:
                                break
                    
                    summary = ' '.join(summary_lines)[:300]
                    if len(' '.join(summary_lines)) > 300:
                        summary += "..."
                    
                    f.write(f"## {title}\n\n")
                    f.write(f"*{level_name} {school}*\n\n")
                    f.write(f"{summary}\n\n")
                    f.write(f"[Full details: {key}]\n\n")
                    f.write("---\n\n")
            
            print(f"  Created: {filename} ({len(spells)} spells)")

def generate_magic_item_lists(conn):
    """Generate magic item lists by rarity."""
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT rarity FROM "references" WHERE ref_type="magic_items_md" AND rarity IS NOT NULL ORDER BY rarity')
    rarities = [row[0] for row in cursor.fetchall()]
    
    print(f"\nGenerating magic item lists for {len(rarities)} rarities...")
    
    for rarity in rarities:
        cursor.execute('''
            SELECT title, key, content, category
            FROM "references" 
            WHERE ref_type="magic_items_md" AND rarity=?
            ORDER BY category, title
        ''', (rarity,))
        
        items = cursor.fetchall()
        
        if not items:
            continue
        
        filename = f"magic_items_{rarity.lower().replace(' ', '_')}.md"
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {rarity} Magic Items\n\n")
            f.write(f"A comprehensive list of {len(items)} {rarity.lower()} magic items.\n\n")
            f.write("---\n\n")
            
            # Group by category
            current_category = None
            for title, key, content, category in items:
                if category and category != current_category:
                    current_category = category
                    f.write(f"### {category}\n\n")
                
                # Extract summary
                lines = content.split('\n') if content else []
                summary_lines = []
                char_count = 0
                
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        summary_lines.append(line.strip())
                        char_count += len(line)
                        if char_count > 200:
                            break
                
                summary = ' '.join(summary_lines)[:200]
                if len(' '.join(summary_lines)) > 200:
                    summary += "..."
                
                f.write(f"**{title}** ({rarity})")
                if category:
                    f.write(f" - *{category}*")
                f.write(f"\n\n{summary}\n\n")
                f.write(f"[Full details: {key}]\n\n")
        
        print(f"  Created: {filename} ({len(items)} items)")

def generate_class_list(conn):
    """Generate a comprehensive class overview document."""
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT title, key, content
        FROM "references"
        WHERE ref_type="classes_md"
        ORDER BY title
    ''')
    
    classes = cursor.fetchall()
    
    if not classes:
        return
    
    print(f"\nGenerating class overview ({len(classes)} classes)...")
    
    filepath = OUTPUT_DIR / "classes_overview.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# D&D 5E Classes Overview\n\n")
        f.write(f"A comprehensive overview of all {len(classes)} character classes.\n\n")
        f.write("---\n\n")
        
        for title, key, content in classes:
            # Extract key features from first few paragraphs
            lines = content.split('\n') if content else []
            summary_lines = []
            char_count = 0
            
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    summary_lines.append(line.strip())
                    char_count += len(line)
                    if char_count > 400:
                        break
            
            summary = ' '.join(summary_lines)[:400]
            if len(' '.join(summary_lines)) > 400:
                summary += "..."
            
            f.write(f"## {title}\n\n")
            f.write(f"{summary}\n\n")
            f.write(f"[Full details: {key}]\n\n")
            f.write("---\n\n")
    
    print(f"  Created: classes_overview.md")

def generate_dm_tools_index(conn):
    """Generate an index document for DM tools (encounters, dungeons, etc.)."""
    cursor = conn.cursor()
    
    # Get all DM-related reference types
    dm_ref_types = []
    cursor.execute('SELECT DISTINCT ref_type FROM "references" ORDER BY ref_type')
    all_types = [row[0] for row in cursor.fetchall()]
    
    print(f"\nGenerating DM Tools index...")
    
    filepath = OUTPUT_DIR / "dm_tools_index.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Dungeon Master Tools & Resources\n\n")
        f.write("A comprehensive index of tools and resources for Dungeon Masters.\n\n")
        f.write("---\n\n")
        
        # Add section for each ref_type
        for ref_type in all_types:
            cursor.execute('''
                SELECT COUNT(*), title
                FROM "references"
                WHERE ref_type=?
            ''', (ref_type,))
            
            count = cursor.fetchone()[0]
            
            if count == 0:
                continue
            
            # Get a few examples
            cursor.execute('''
                SELECT title, key
                FROM "references"
                WHERE ref_type=?
                ORDER BY title
                LIMIT 5
            ''', (ref_type,))
            
            examples = cursor.fetchall()
            
            type_name = ref_type.replace('_', ' ').title()
            f.write(f"## {type_name}\n\n")
            f.write(f"**{count} resources available**\n\n")
            
            if examples:
                f.write("Examples:\n")
                for title, key in examples:
                    f.write(f"- {title}\n")
                f.write("\n")
            
            f.write("---\n\n")
    
    print(f"  Created: dm_tools_index.md")

def main():
    """Main execution."""
    print("=" * 70)
    print("GENERATING CONSOLIDATED REFERENCE LISTS")
    print("=" * 70)
    
    ensure_output_dir()
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        generate_spell_lists(conn)
        generate_magic_item_lists(conn)
        generate_class_list(conn)
        generate_dm_tools_index(conn)
        
        print("\n" + "=" * 70)
        print(f"COMPLETE! Generated lists saved to: {OUTPUT_DIR}")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Run sync-from-disk to import these documents")
        print("2. Run chunking script to process them")
        print("3. Generate embeddings for the new chunks")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
