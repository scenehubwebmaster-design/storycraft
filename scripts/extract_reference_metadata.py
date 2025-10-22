"""Extract metadata from reference content and populate metadata fields.

This script parses the markdown content of each reference to extract:
- Spell level and school (for spells)
- Item rarity and category (for magic items)
- Tags (damage types, conditions, keywords)

Usage:
  python scripts\\extract_reference_metadata.py
"""
import sys
import os
import re
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import DEFAULT_DB_FILE
from backend.models import Reference
from tqdm import tqdm

# Spell schools
SPELL_SCHOOLS = [
    'Abjuration', 'Conjuration', 'Divination', 'Enchantment',
    'Evocation', 'Illusion', 'Necromancy', 'Transmutation'
]

# Magic item rarities
RARITIES = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary', 'Artifact']

# Magic item categories
ITEM_CATEGORIES = [
    'Weapon', 'Armor', 'Potion', 'Ring', 'Rod', 'Scroll', 'Staff', 'Wand',
    'Wondrous Item', 'Ammunition', 'Adventuring Gear'
]

# Damage types for tagging
DAMAGE_TYPES = [
    'acid', 'bludgeoning', 'cold', 'fire', 'force', 'lightning', 'necrotic',
    'piercing', 'poison', 'psychic', 'radiant', 'slashing', 'thunder'
]

# Conditions for tagging
CONDITIONS = [
    'blinded', 'charmed', 'deafened', 'exhaustion', 'frightened', 'grappled',
    'incapacitated', 'invisible', 'paralyzed', 'petrified', 'poisoned',
    'prone', 'restrained', 'stunned', 'unconscious'
]

# Common spell/item keywords
KEYWORDS = [
    'healing', 'damage', 'buff', 'debuff', 'control', 'utility', 'summoning',
    'teleportation', 'scrying', 'detection', 'protection', 'movement',
    'communication', 'creation', 'illusion', 'transformation', 'area'
]


def extract_spell_metadata(content: str):
    """Extract spell level and school from spell content."""
    level = None
    school = None
    tags = []
    
    # Look for "Xth-level school" or "Cantrip (school)" pattern
    # Example: "3rd-level evocation" or "Cantrip (evocation)"
    level_match = re.search(r'(\d)(?:st|nd|rd|th)-level\s+(\w+)', content, re.IGNORECASE)
    if level_match:
        level = int(level_match.group(1))
        school_candidate = level_match.group(2).capitalize()
        if school_candidate in SPELL_SCHOOLS:
            school = school_candidate
    
    # Check for cantrip - pattern: "cantrip (school)" OR "school cantrip"
    cantrip_match = re.search(r'cantrip\s*\((\w+)\)', content, re.IGNORECASE)
    if cantrip_match:
        level = 0
        school_candidate = cantrip_match.group(1).capitalize()
        if school_candidate in SPELL_SCHOOLS:
            school = school_candidate
    else:
        # Alternative cantrip pattern: "Evocation cantrip"
        cantrip_match2 = re.search(r'(\w+)\s+cantrip', content, re.IGNORECASE)
        if cantrip_match2:
            level = 0
            school_candidate = cantrip_match2.group(1).capitalize()
            if school_candidate in SPELL_SCHOOLS:
                school = school_candidate
    
    # Alternative pattern: "Level & School. 3rd-level evocation"
    alt_match = re.search(r'Level\s*&\s*School\.?\s+(\d)(?:st|nd|rd|th)-level\s+(\w+)', content, re.IGNORECASE)
    if alt_match and level is None:
        level = int(alt_match.group(1))
        school_candidate = alt_match.group(2).capitalize()
        if school_candidate in SPELL_SCHOOLS:
            school = school_candidate
    
    # Extract tags from content
    content_lower = content.lower()
    
    # Damage types
    for dtype in DAMAGE_TYPES:
        if dtype in content_lower:
            tags.append(dtype)
    
    # Conditions
    for condition in CONDITIONS:
        if condition in content_lower:
            tags.append(condition)
    
    # Check for area effects
    if any(word in content_lower for word in ['radius', 'cone', 'cube', 'cylinder', 'sphere', 'line']):
        tags.append('area')
    
    # Check for concentration
    if 'concentration' in content_lower:
        tags.append('concentration')
    
    return level, school, list(set(tags))


def extract_item_metadata(content: str, title: str):
    """Extract rarity and category from magic item content."""
    rarity = None
    category = None
    tags = []
    
    content_lower = content.lower()
    
    # Look for rarity - check multiple patterns
    # Pattern 1: "Armor (medium or heavy), uncommon"
    # Pattern 2: "uncommon magic item"
    rarity_match = re.search(r',\s*(common|uncommon|rare|very\s+rare|legendary|artifact)\b', content, re.IGNORECASE)
    if rarity_match:
        rarity_text = rarity_match.group(1)
        # Capitalize properly (handle "very rare")
        if 'very' in rarity_text.lower():
            rarity = 'Very Rare'
        else:
            rarity = rarity_text.capitalize()
    else:
        # Fallback: look for rarity word anywhere
        for r in RARITIES:
            if r.lower() in content_lower:
                rarity = r
                break
    
    # Look for category/type
    for cat in ITEM_CATEGORIES:
        if cat.lower() in content_lower or cat.lower() in title.lower():
            category = cat
            break
    
    # Infer category from title
    if not category:
        title_lower = title.lower()
        if 'potion' in title_lower:
            category = 'Potion'
        elif 'ring' in title_lower:
            category = 'Ring'
        elif 'staff' in title_lower:
            category = 'Staff'
        elif 'wand' in title_lower:
            category = 'Wand'
        elif 'rod' in title_lower:
            category = 'Rod'
        elif 'armor' in title_lower or 'mail' in title_lower or 'plate' in title_lower:
            category = 'Armor'
        elif any(w in title_lower for w in ['sword', 'bow', 'axe', 'mace', 'dagger', 'javelin']):
            category = 'Weapon'
    
    # Extract tags
    for dtype in DAMAGE_TYPES:
        if dtype in content_lower:
            tags.append(dtype)
    
    # Check for attunement
    if 'attunement' in content_lower:
        tags.append('attunement')
    
    # Check for cursed
    if 'cursed' in content_lower or 'curse' in content_lower:
        tags.append('cursed')
    
    return rarity, category, list(set(tags))


def main():
    engine = create_engine(f'sqlite:///{DEFAULT_DB_FILE}', connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get all references
    refs = session.query(Reference).all()
    print(f'Extracting metadata for {len(refs)} references...')
    
    stats = {
        'spells_processed': 0,
        'items_processed': 0,
        'others_processed': 0,
        'spells_with_level': 0,
        'spells_with_school': 0,
        'items_with_rarity': 0,
        'items_with_category': 0,
        'total_tags': 0
    }
    
    for ref in tqdm(refs, desc="Processing"):
        content = ref.content or ''
        title = ref.title or ''
        
        if ref.ref_type == 'spells_md':
            level, school, tags = extract_spell_metadata(content)
            ref.level = level
            ref.school = school
            ref.tags = tags if tags else None
            
            stats['spells_processed'] += 1
            if level is not None:
                stats['spells_with_level'] += 1
            if school:
                stats['spells_with_school'] += 1
            if tags:
                stats['total_tags'] += len(tags)
        
        elif ref.ref_type == 'magic_items_md':
            rarity, category, tags = extract_item_metadata(content, title)
            ref.rarity = rarity
            ref.category = category
            ref.tags = tags if tags else None
            
            stats['items_processed'] += 1
            if rarity:
                stats['items_with_rarity'] += 1
            if category:
                stats['items_with_category'] += 1
            if tags:
                stats['total_tags'] += len(tags)
        
        else:
            # For other types, just extract basic tags
            content_lower = content.lower()
            tags = []
            
            for dtype in DAMAGE_TYPES:
                if dtype in content_lower:
                    tags.append(dtype)
            
            if tags:
                ref.tags = tags
                stats['total_tags'] += len(tags)
            
            stats['others_processed'] += 1
        
        # Commit in batches
        if ref.id % 100 == 0:
            session.commit()
    
    # Final commit
    session.commit()
    session.close()
    
    print('\n✅ Metadata extraction complete!')
    print(f'\nStatistics:')
    print(f'  Spells processed: {stats["spells_processed"]}')
    print(f'    - With level: {stats["spells_with_level"]}')
    print(f'    - With school: {stats["spells_with_school"]}')
    print(f'  Magic items processed: {stats["items_processed"]}')
    print(f'    - With rarity: {stats["items_with_rarity"]}')
    print(f'    - With category: {stats["items_with_category"]}')
    print(f'  Other references: {stats["others_processed"]}')
    print(f'  Total tags extracted: {stats["total_tags"]}')


if __name__ == '__main__':
    main()
