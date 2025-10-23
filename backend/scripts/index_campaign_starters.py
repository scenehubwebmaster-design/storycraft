"""
Index campaign starters and adventure templates into the RAG system
This makes them available for retrieval during campaign creation
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir.parent))

from backend.database import SessionLocal
from backend.models import Reference
from datetime import datetime
import re

def extract_campaign_templates():
    """Extract campaign templates from the markdown file"""
    
    # Read the campaign starters file
    starters_file = Path(__file__).parent.parent.parent / "data" / "phb" / "campaign_starters.md"
    
    with open(starters_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    templates = []
    
    # Extract Classic Opening Scenes
    opening_scenes = [
        {
            "key": "opening_tavern_meeting",
            "title": "Opening Scene: The Tavern Meeting",
            "ref_type": "campaign_starter",
            "category": "opening_scene",
            "tags": ["tavern", "classic", "meeting", "strangers"],
            "content": extract_section(content, "The Tavern Meeting")
        },
        {
            "key": "opening_caravan_guards",
            "title": "Opening Scene: The Caravan Guards",
            "ref_type": "campaign_starter",
            "category": "opening_scene",
            "tags": ["caravan", "travel", "guards", "bandits"],
            "content": extract_section(content, "The Caravan Guards")
        },
        {
            "key": "opening_prison_break",
            "title": "Opening Scene: Prison Break",
            "ref_type": "campaign_starter",
            "category": "opening_scene",
            "tags": ["prison", "escape", "wrongful", "dramatic"],
            "content": extract_section(content, "Prison Break")
        },
        {
            "key": "opening_festival_disaster",
            "title": "Opening Scene: The Festival Disaster",
            "ref_type": "campaign_starter",
            "category": "opening_scene",
            "tags": ["festival", "disaster", "chaos", "celebration"],
            "content": extract_section(content, "The Festival Disaster")
        },
        {
            "key": "opening_summons",
            "title": "Opening Scene: The Summons",
            "ref_type": "campaign_starter",
            "category": "opening_scene",
            "tags": ["mystery", "summons", "letter", "intrigue"],
            "content": extract_section(content, "The Summons")
        }
    ]
    
    # Extract One-Shot Adventures
    one_shots = [
        {
            "key": "oneshot_haunted_manor",
            "title": "One-Shot: The Haunted Manor",
            "ref_type": "campaign_template",
            "category": "one_shot",
            "level": 2,
            "tags": ["horror", "undead", "mystery", "manor"],
            "content": extract_section(content, "The Haunted Manor")
        },
        {
            "key": "oneshot_goblin_raiders",
            "title": "One-Shot: The Goblin Raiders",
            "ref_type": "campaign_template",
            "category": "one_shot",
            "level": 1,
            "tags": ["combat", "goblins", "rescue", "classic"],
            "content": extract_section(content, "The Goblin Raiders")
        }
    ]
    
    # Extract Short Adventures
    short_adventures = [
        {
            "key": "short_cult_crimson_eye",
            "title": "Short Adventure: The Cult of the Crimson Eye",
            "ref_type": "campaign_template",
            "category": "short_adventure",
            "level": 4,
            "tags": ["investigation", "cult", "urban", "mystery"],
            "content": extract_section(content, "The Cult of the Crimson Eye")
        },
        {
            "key": "short_lost_mine",
            "title": "Short Adventure: The Lost Mine of Phandelver",
            "ref_type": "campaign_template",
            "category": "short_adventure",
            "level": 3,
            "tags": ["classic", "dungeon", "mining", "dwarves"],
            "content": extract_section(content, "The Lost Mine of Phandelver")
        }
    ]
    
    # Extract Epic Campaigns
    epic_campaigns = [
        {
            "key": "epic_tyranny_dragons",
            "title": "Epic Campaign: Tyranny of Dragons",
            "ref_type": "campaign_template",
            "category": "epic_campaign",
            "level": 8,
            "tags": ["dragons", "epic", "tiamat", "world_threat"],
            "content": extract_section(content, "Tyranny of Dragons")
        }
    ]
    
    # Extract Campaign Tones
    tones = [
        {
            "key": "tone_heroic_fantasy",
            "title": "Campaign Tone: Heroic High Fantasy",
            "ref_type": "campaign_tone",
            "category": "tone",
            "tags": ["heroic", "high_fantasy", "good_vs_evil", "epic"],
            "content": extract_section(content, "Heroic High Fantasy")
        },
        {
            "key": "tone_dark_fantasy",
            "title": "Campaign Tone: Gritty Dark Fantasy",
            "ref_type": "campaign_tone",
            "category": "tone",
            "tags": ["dark", "gritty", "survival", "grey_morality"],
            "content": extract_section(content, "Gritty Dark Fantasy")
        },
        {
            "key": "tone_political",
            "title": "Campaign Tone: Political Intrigue",
            "ref_type": "campaign_tone",
            "category": "tone",
            "tags": ["political", "intrigue", "social", "diplomacy"],
            "content": extract_section(content, "Political Intrigue")
        }
    ]
    
    # Extract Settings
    settings = [
        {
            "key": "setting_forgotten_realms",
            "title": "Setting: Forgotten Realms",
            "ref_type": "campaign_setting",
            "category": "setting",
            "tags": ["forgotten_realms", "classic_dnd", "faerun", "waterdeep"],
            "content": extract_section(content, "Forgotten Realms")
        },
        {
            "key": "setting_eberron",
            "title": "Setting: Eberron",
            "ref_type": "campaign_setting",
            "category": "setting",
            "tags": ["eberron", "pulp", "magitech", "warforged"],
            "content": extract_section(content, "Eberron")
        }
    ]
    
    return opening_scenes + one_shots + short_adventures + epic_campaigns + tones + settings

def extract_section(content: str, heading: str) -> str:
    """Extract a section from markdown by heading"""
    # Find the heading
    pattern = rf"###.*{re.escape(heading)}.*?\n(.*?)(?=\n###|\n##|$)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return f"Content for {heading} not found"

def index_campaign_starters():
    """Index campaign templates into the database"""
    print("=" * 70)
    print("Campaign Starters Indexing")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    
    try:
        templates = extract_campaign_templates()
        
        print(f"📚 Found {len(templates)} campaign templates to index\n")
        
        indexed = 0
        updated = 0
        
        for template in templates:
            # Check if already exists
            existing = db.query(Reference).filter(Reference.key == template['key']).first()
            
            if existing:
                # Update existing
                existing.title = template['title']
                existing.ref_type = template['ref_type']
                existing.category = template['category']
                existing.content = template['content']
                existing.tags = template.get('tags', [])
                existing.level = template.get('level')
                existing.updated_at = datetime.utcnow()
                updated += 1
                print(f"  ✏️  Updated: {template['title']}")
            else:
                # Create new
                new_ref = Reference(
                    ref_type=template['ref_type'],
                    key=template['key'],
                    title=template['title'],
                    content=template['content'],
                    category=template['category'],
                    tags=template.get('tags', []),
                    level=template.get('level'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_ref)
                indexed += 1
                print(f"  ✅ Indexed: {template['title']}")
        
        db.commit()
        
        print()
        print("=" * 70)
        print("✨ Indexing Complete!")
        print("=" * 70)
        print(f"\n✅ Indexed: {indexed} new templates")
        print(f"✏️  Updated: {updated} existing templates")
        print(f"📖 Total: {indexed + updated} campaign templates in RAG system")
        print()
        print("🎯 Campaign templates are now available for AI DM retrieval!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during indexing: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    index_campaign_starters()
