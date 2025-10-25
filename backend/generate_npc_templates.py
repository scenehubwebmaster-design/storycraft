"""
Generate 100 robust NPCs for RAG system with portraits.

This script creates diverse D&D NPCs with:
- Unique personalities and backgrounds
- Physical descriptions for portrait generation
- Traits, motivations, and quirks
- RAG-ready structure for semantic search
- Portrait path placeholders
"""

import json
import random
from .database import SessionLocal

# NPC Generation Templates
RACES = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"]
ROLES = ["Merchant", "Guard", "Innkeeper", "Blacksmith", "Priest", "Mage", "Bard", "Thief", "Noble", "Farmer",
         "Hunter", "Scholar", "Healer", "Spy", "Soldier", "Diplomat", "Artisan", "Cook", "Sailor", "Librarian"]
PERSONALITIES = ["Friendly", "Grumpy", "Mysterious", "Cheerful", "Suspicious", "Wise", "Eccentric", "Stern",
                 "Jovial", "Melancholic", "Ambitious", "Lazy", "Cautious", "Reckless", "Honest", "Deceptive"]
LOCATIONS = ["Town Square", "Tavern", "Market", "Temple", "Library", "Docks", "Palace", "Forge", "Guild Hall",
             "Inn", "Apothecary", "Barracks", "Arena", "Theater", "Cemetery", "Farm", "Workshop", "Tower"]

# Name generators
FIRST_NAMES = {
    "Human": ["Aric", "Elara", "Marcus", "Lydia", "Roland", "Sera", "Thomas", "Nina", "Victor", "Helena"],
    "Elf": ["Thranduil", "Arwen", "Legolas", "Galadriel", "Finrod", "Celebrian", "Elrond", "Lothíriel", "Glorfindel", "Nimrodel"],
    "Dwarf": ["Thorin", "Dagna", "Balin", "Helga", "Gimli", "Dis", "Dwalin", "Thora", "Oin", "Katri"],
    "Halfling": ["Bilbo", "Rosie", "Meriadoc", "Primrose", "Pippin", "Daisy", "Samwise", "Pearl", "Fredegar", "Marigold"],
    "Dragonborn": ["Rhogar", "Akra", "Balasar", "Mishann", "Ghesh", "Thava", "Heskan", "Surina", "Kriv", "Nala"],
    "Gnome": ["Glim", "Bimpnottin", "Boddynock", "Orryn", "Eldon", "Breena", "Fonkin", "Delebean", "Zook", "Caramip"],
    "Half-Elf": ["Taegen", "Faelynn", "Karth", "Liadon", "Immeral", "Shava", "Heian", "Silaqui", "Galinndan", "Xanaphia"],
    "Half-Orc": ["Grognak", "Ovak", "Dench", "Baggi", "Holg", "Ovarka", "Mhurren", "Neega", "Shump", "Volen"],
    "Tiefling": ["Zariel", "Damakos", "Akmenios", "Lerissa", "Morthos", "Orianna", "Therai", "Bryseis", "Ekemon", "Phelaia"]
}

LAST_NAMES = ["Brightwood", "Ironforge", "Stormwind", "Shadowmere", "Goldleaf", "Stoneheart", "Swiftfoot", "Firehand",
              "Moonwhisper", "Thornblade", "Silverstream", "Oakenshield", "Frostborn", "Ember heart", "Starweaver"]

def generate_npc_name(race):
    """Generate a random NPC name based on race"""
    first_names = FIRST_NAMES.get(race, FIRST_NAMES["Human"])
    first = random.choice(first_names)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def generate_physical_description(race):
    """Generate detailed physical description for portrait generation"""
    heights = {
        "Human": "average height",
        "Elf": "tall and slender",
        "Dwarf": "short and stocky",
        "Halfling": "diminutive stature",
        "Dragonborn": "imposing draconic build",
        "Gnome": "small with pointed features",
        "Half-Elf": "graceful medium build",
        "Half-Orc": "muscular and broad-shouldered",
        "Tiefling": "lithe with infernal features"
    }
    
    hair_colors = ["black", "brown", "blonde", "red", "silver", "white", "auburn", "chestnut", "platinum"]
    eye_colors = ["blue", "green", "brown", "hazel", "amber", "gray", "violet", "golden", "red"]
    ages = ["young", "middle-aged", "elderly", "youthful"]
    features = [
        "weathered face", "sharp features", "kind eyes", "stern expression",
        "scarred visage", "gentle smile", "piercing gaze", "warm demeanor",
        "rugged appearance", "elegant bearing", "mysterious aura", "battle-worn"
    ]
    
    height = heights.get(race, "average height")
    hair = random.choice(hair_colors)
    eyes = random.choice(eye_colors)
    age = random.choice(ages)
    feature = random.choice(features)
    
    # Add race-specific features
    race_features = {
        "Elf": " with pointed ears",
        "Dwarf": " with a braided beard",
        "Tiefling": " with horns and a tail",
        "Dragonborn": " with scaled skin",
        "Half-Orc": " with prominent tusks",
        "Gnome": " with a curious expression"
    }
    
    extra = race_features.get(race, "")
    
    return f"{age} {race} of {height}, {hair} hair, {eyes} eyes, {feature}{extra}"

def generate_personality_traits():
    """Generate personality traits and quirks"""
    traits = [
        "speaks in riddles", "constantly humming", "tells bad jokes", "very punctual",
        "overly dramatic", "whispers secrets", "loves animals", "fears magic",
        "collects trinkets", "quotes poetry", "superstitious", "optimistic",
        "pessimistic", "perfectionist", "impulsive", "methodical"
    ]
    
    motivations = [
        "seeking revenge", "protecting family", "accumulating wealth", "gaining knowledge",
        "finding adventure", "maintaining peace", "achieving fame", "serving deity",
        "uncovering truth", "helping others", "proving worth", "escaping past"
    ]
    
    return {
        "trait": random.choice(traits),
        "motivation": random.choice(motivations),
        "quirk": random.choice(["has a pet rat", "wears lucky charm", "never lies", "always hungry",
                                 "speaks third person", "counts everything", "avoids eye contact", "very loud"])
    }

def generate_backstory(name, race, role):
    """Generate a brief backstory"""
    backgrounds = [
        f"{name} grew up in a small village and learned the {role.lower()} trade from their parents.",
        f"Once an adventurer, {name} retired to pursue a quieter life as a {role.lower()}.",
        f"{name} came to this town seeking a fresh start after leaving their homeland.",
        f"Born into nobility, {name} rejected that life to become a {role.lower()}.",
        f"{name} is a refugee who rebuilt their life from nothing as a respected {role.lower()}.",
        f"After serving in the military, {name} settled down and became a {role.lower()}.",
        f"{name} inherited this {role.lower()} business from a mysterious benefactor.",
        f"A former criminal, {name} now lives honestly as a {role.lower()}.",
        f"{name} was once a scholar but found true purpose as a {role.lower()}.",
        f"Orphaned young, {name} was taken in by a master {role.lower()} and trained in the craft."
    ]
    
    return random.choice(backgrounds)

def generate_npc_data():
    """Generate a complete NPC data structure"""
    race = random.choice(RACES)
    role = random.choice(ROLES)
    name = generate_npc_name(race)
    personality = random.choice(PERSONALITIES)
    location = random.choice(LOCATIONS)
    
    physical_desc = generate_physical_description(race)
    personality_data = generate_personality_traits()
    backstory = generate_backstory(name, race, role)
    
    # Generate portrait prompt for SD
    portrait_prompt = f"portrait of {physical_desc}, {personality.lower()} expression, D&D character art, fantasy style, highly detailed"
    
    return {
        "name": name,
        "race": race,
        "role": role,
        "location": location,
        "description": f"{name} is a {personality.lower()} {race} {role.lower()}. {physical_desc}.",
        "personality": f"{personality}. {personality_data['trait'].capitalize()}. Motivated by {personality_data['motivation']}.",
        "backstory": backstory,
        "quirk": personality_data['quirk'],
        "physical_description": physical_desc,
        "portrait_prompt": portrait_prompt,
        "importance": random.randint(2, 4),  # 2-4 for template NPCs
        "relationship_to_party": 0,  # Neutral initially
        "tags": [role.lower(), race.lower(), personality.lower()],
        "is_alive": True
    }

def create_reference_npcs(db, count: int = 100):
    """Create NPC references that can be ingested into RAG system"""
    from .models import Reference
    
    print(f"🎭 Generating {count} NPC templates for RAG system...")
    
    created_count = 0
    
    for i in range(count):
        npc_data = generate_npc_data()
        
        # Create comprehensive content for RAG
        content = f"""# {npc_data['name']}
        
**Race**: {npc_data['race']}  
**Role**: {npc_data['role']}  
**Location**: {npc_data['location']}

## Description
{npc_data['description']}

## Personality
{npc_data['personality']}

## Backstory
{npc_data['backstory']}

## Quirk
{npc_data['quirk']}

## Physical Description
{npc_data['physical_description']}

## Portrait Prompt
{npc_data['portrait_prompt']}

## Usage in Campaigns
This NPC can be used as a {npc_data['role'].lower()} in any campaign. They work well in {npc_data['location'].lower()} settings.
"""
        
        # Store as Reference document
        ref = Reference(
            ref_type="npc_template",
            key=npc_data['name'].lower().replace(" ", "_"),
            title=npc_data['name'],
            content=content,
            category=npc_data['role'],
            tags=json.dumps(npc_data['tags'])
        )
        
        db.add(ref)
        created_count += 1
        
        if (i + 1) % 10 == 0:
            db.commit()
            print(f"  Created {i + 1}/{count} NPC templates...")
    
    db.commit()
    print(f"✅ Created {created_count} NPC templates successfully!")
    print("📁 They are stored in 'references' table with ref_type='npc_template'")
    print("🔍 Ready for RAG embedding and semantic search")
    
    return created_count

def main():
    """Main execution"""
    db = SessionLocal()
    
    try:
        # Check existing NPC templates
        from .models import Reference
        existing = db.query(Reference).filter(Reference.ref_type == "npc_template").count()
        
        if existing > 0:
            print(f"⚠️  Found {existing} existing NPC templates")
            response = input("Do you want to add more NPCs? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Generate NPCs
        count = int(input("How many NPCs to generate? (default 100): ") or "100")
        create_reference_npcs(db, count)
        
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Run embedding generation to add these to RAG system")
        print("2. Use batch_generate_npc_portraits.py to generate portraits")
        print("3. NPCs will be available for DM to insert into campaigns")
        print("\nTo use in campaigns:")
        print("  - DM can search for NPCs by role, race, or personality")
        print("  - When selected, copy to game-specific 'npcs' table")
        print("  - Generate portrait using stored portrait_prompt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
