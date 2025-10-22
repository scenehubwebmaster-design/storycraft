"""
Query analysis utilities for extracting structured search parameters from natural language.

This module provides intelligent parsing to convert queries like:
- "show me level 5 evocation spells" → level=5, school=Evocation, ref_type=spells_md
- "rare magic weapons" → rarity=Rare, category=Weapon, ref_type=magic_items_md
- "CR 5 undead monsters" → cr=5, type=undead, ref_type=monsters_md
"""

import re
from typing import Dict, List, Optional, Tuple

# Spell levels
SPELL_LEVEL_PATTERNS = [
    (r'\b(?:level\s+)?(\d)\s*(?:st|nd|rd|th)?(?:\s+level)?\s+(?:spell|spells|evocation|abjuration|conjuration|divination|enchantment|illusion|necromancy|transmutation)', 'level'),
    (r'\b(cantrip|cantrips)\b', 'level'),  # Special case for level 0
]

# Spell schools
SPELL_SCHOOLS = [
    'Abjuration', 'Conjuration', 'Divination', 'Enchantment',
    'Evocation', 'Illusion', 'Necromancy', 'Transmutation'
]

# Magic item rarities
RARITIES = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary', 'Artifact']

# Magic item categories
CATEGORIES = [
    'Weapon', 'Armor', 'Potion', 'Ring', 'Rod', 'Scroll',
    'Staff', 'Wand', 'Wondrous Item', 'Wondrous item'
]

# Reference types
REF_TYPE_KEYWORDS = {
    'spells_md': ['spell', 'spells', 'magic', 'cast', 'casting', 'cantrip', 'cantrips'],
    'magic_items_md': ['magic item', 'magic items', 'magical item', 'artifact', 'artifacts'],
    'classes_md': ['class', 'classes', 'fighter', 'wizard', 'cleric', 'rogue', 'barbarian', 'ranger', 'paladin', 'monk', 'druid', 'sorcerer', 'warlock', 'bard'],
    'species_md': ['race', 'races', 'species', 'elf', 'dwarf', 'human', 'halfling', 'dragonborn', 'gnome', 'half-elf', 'half-orc', 'tiefling'],
    'monsters_md': ['monster', 'monsters', 'creature', 'creatures', 'enemy', 'enemies'],
    'equipment_md': ['equipment', 'gear', 'items', 'tools'],
    'weapons_md': ['weapon', 'weapons', 'sword', 'axe', 'bow'],
    'core': ['dungeon', 'chamber', 'trap', 'hazard', 'passage'],
    'themes': ['lair', 'tomb', 'temple', 'stronghold', 'mine', 'vault'],
}


def extract_spell_level(query: str) -> Optional[int]:
    """Extract spell level from natural language query."""
    query_lower = query.lower()
    
    # Check for cantrip
    if re.search(r'\bcantrip', query_lower):
        return 0
    
    # Check for numeric level patterns
    for pattern, field_name in SPELL_LEVEL_PATTERNS:
        match = re.search(pattern, query_lower)
        if match and field_name == 'level':
            level = int(match.group(1))
            if 0 <= level <= 9:
                return level
    
    return None


def extract_spell_school(query: str) -> Optional[str]:
    """Extract spell school from query."""
    query_lower = query.lower()
    
    for school in SPELL_SCHOOLS:
        if school.lower() in query_lower:
            return school
    
    return None


def extract_rarity(query: str) -> Optional[str]:
    """Extract magic item rarity from query."""
    query_lower = query.lower()
    
    # Handle "very rare" as special case (must check before "rare")
    if 'very rare' in query_lower:
        return 'Very Rare'
    
    # Check rarities in order of specificity (longer/more specific first)
    for rarity in ['Legendary', 'Artifact', 'Uncommon', 'Rare', 'Common']:
        if rarity.lower() in query_lower:
            return rarity
    
    return None


def extract_category(query: str) -> Optional[str]:
    """Extract item category from query."""
    query_lower = query.lower()
    
    # Handle "wondrous item" variations
    if 'wondrous' in query_lower:
        return 'Wondrous item'
    
    for category in CATEGORIES:
        if category.lower() in query_lower:
            return category
    
    return None


def extract_ref_type(query: str) -> Optional[str]:
    """Infer reference type from query keywords."""
    query_lower = query.lower()
    
    # Score each ref_type based on keyword matches
    scores = {}
    for ref_type, keywords in REF_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            scores[ref_type] = score
    
    if not scores:
        return None
    
    # Return the ref_type with highest score
    return max(scores.items(), key=lambda x: x[1])[0]


def analyze_query(query: str) -> Dict[str, any]:
    """
    Analyze a natural language query and extract structured search parameters.
    
    Args:
        query: Natural language search query
        
    Returns:
        Dictionary with extracted parameters:
        - level: Spell level (0-9)
        - school: Spell school
        - rarity: Item rarity
        - category: Item category
        - ref_type: Reference type to search
        - original_query: Original query string
    """
    params = {
        'original_query': query,
    }
    
    # Extract structured parameters
    level = extract_spell_level(query)
    if level is not None:
        params['level'] = level
    
    school = extract_spell_school(query)
    if school:
        params['school'] = school
    
    rarity = extract_rarity(query)
    if rarity:
        params['rarity'] = rarity
    
    category = extract_category(query)
    if category:
        params['category'] = category
    
    ref_type = extract_ref_type(query)
    if ref_type:
        params['ref_type'] = ref_type
    
    return params


def get_search_summary(params: Dict[str, any]) -> str:
    """Generate a human-readable summary of extracted search parameters."""
    parts = []
    
    if 'level' in params:
        level = params['level']
        level_str = "Cantrip" if level == 0 else f"Level {level}"
        parts.append(level_str)
    
    if 'school' in params:
        parts.append(params['school'])
    
    if 'rarity' in params:
        parts.append(params['rarity'])
    
    if 'category' in params:
        parts.append(params['category'])
    
    if 'ref_type' in params:
        ref_type_name = params['ref_type'].replace('_md', '').replace('_', ' ').title()
        parts.append(ref_type_name)
    
    if parts:
        return f"Searching: {' | '.join(parts)}"
    else:
        return "Broad search (no specific filters detected)"


# Example usage and tests
if __name__ == "__main__":
    test_queries = [
        "show me level 5 evocation spells",
        "find rare magic weapons",
        "what are good cantrips for a wizard",
        "legendary armor items",
        "list all barbarian class features",
        "tell me about elves",
        "show me CR 5 monsters",
        "necromancy spells level 3",
        "uncommon wondrous items",
        "dungeon traps and hazards",
    ]
    
    print("Query Analysis Examples")
    print("=" * 70)
    
    for query in test_queries:
        params = analyze_query(query)
        summary = get_search_summary(params)
        
        print(f"\nQuery: \"{query}\"")
        print(f"  {summary}")
        print(f"  Params: {params}")
