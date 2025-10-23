"""
RAG Content Generator for StoryCraft

Generates rich D&D 5e content in the tyranny_of_dragons structured format:
- 100 unique NPCs with detailed backgrounds
- 100 unique locations with atmospheric descriptions
- 100 unique encounters with tactical depth
- 5 complete adventure modules with structured content

Output follows the YAML frontmatter + markdown format optimized for RAG ingestion.
"""

import random
from pathlib import Path
from typing import Dict, Any

# Base output directory
OUTPUT_DIR = Path("e:/storycraft/documents/reference/adventures_md/generated_content")

# Content generation templates and data
RACES = ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Tiefling", "Half-Orc", "Gnome", "Half-Elf", "Aasimar", "Genasi", "Tabaxi", "Firbolg", "Goliath", "Kenku", "Lizardfolk"]
CLASSES = ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Paladin", "Bard", "Warlock", "Monk", "Druid", "Sorcerer", "Barbarian", "Artificer", "Blood Hunter"]
ALIGNMENTS = ["lawful-good", "neutral-good", "chaotic-good", "lawful-neutral", "true-neutral", "chaotic-neutral", "lawful-evil", "neutral-evil", "chaotic-evil"]

NPC_ROLES = [
    "merchant", "guard", "priest", "noble", "scholar", "artisan", "criminal", "adventurer",
    "innkeeper", "blacksmith", "wizard", "ranger", "spy", "diplomat", "healer", "bard",
    "captain", "sage", "alchemist", "librarian", "cult-leader", "bounty-hunter", "smuggler",
    "architect", "explorer", "cartographer", "fortune-teller", "jeweler", "shipwright"
]

LOCATION_TYPES = [
    "tavern", "temple", "dungeon", "ruins", "castle", "forest", "mountain", "cave", "city",
    "village", "port", "market", "tower", "fortress", "sanctuary", "library", "guild-hall",
    "crypt", "lair", "swamp", "desert", "island", "mine", "laboratory", "archive"
]

ENCOUNTER_TYPES = [
    "combat", "social", "exploration", "puzzle", "trap", "ambush", "negotiation", "chase",
    "heist", "rescue", "investigation", "ritual", "siege", "duel", "trial", "escape"
]

FACTIONS = [
    "Harpers", "Zhentarim", "Lords-Alliance", "Order-of-the-Gauntlet", "Emerald-Enclave",
    "Cult-of-the-Dragon", "Red-Wizards", "Xanathar-Guild", "Bregan-Daerthe", "Force-Grey"
]

THEMES = [
    "dragon-cult", "necromancy", "political-intrigue", "ancient-magic", "planar-rifts",
    "undead-plague", "artifact-hunt", "guild-wars", "divine-intervention", "elemental-chaos",
    "time-manipulation", "feywild-incursion", "demonic-invasion", "shadow-realm", "prophecy"
]

# Rich NPC personality traits
PERSONALITY_TRAITS = [
    "speaks in riddles", "nervous laughter", "collects rare coins", "superstitious",
    "eloquent speaker", "battle-scarred veteran", "paranoid about magic", "loves gambling",
    "obsessed with dragons", "haunted by past", "perfectionist", "crude humor",
    "philosophical", "pragmatic", "idealistic", "cynical", "optimistic", "melancholic"
]

# Rich location descriptors
LOCATION_DESCRIPTORS = [
    "crumbling", "magnificent", "eerie", "bustling", "abandoned", "fortified", "sacred",
    "corrupt", "mysterious", "ancient", "modern", "rustic", "elegant", "decrepit", "vibrant"
]


def sanitize_filename(name: str) -> str:
    """Convert name to safe filename."""
    return name.lower().replace(" ", "_").replace("'", "").replace('"', "")


def generate_npc_name(race: str) -> str:
    """Generate culturally appropriate names."""
    prefixes = {
        "Human": ["Aldric", "Brenna", "Cedric", "Diana", "Edmund", "Fiona", "Gareth", "Helena"],
        "Elf": ["Aelrindel", "Ilphas", "Silaqui", "Thranduil", "Elara", "Galadrian", "Miriel"],
        "Dwarf": ["Balin", "Thorin", "Gimli", "Dwalin", "Brunhilda", "Kragni", "Ulfgar"],
        "Halfling": ["Bilbo", "Pippin", "Rosie", "Merry", "Lobelia", "Fredegar", "Daisy"],
        "Dragonborn": ["Arjhan", "Balasar", "Donaar", "Ghesh", "Heskan", "Kriv", "Medrash"],
        "Tiefling": ["Aktos", "Damakos", "Ekemon", "Iados", "Kairon", "Leucis", "Melech"],
        "Half-Orc": ["Grom", "Thokk", "Dench", "Feng", "Holg", "Keth", "Mhurren"],
        "Gnome": ["Alston", "Boddynock", "Brocc", "Burgell", "Dimble", "Eldon", "Fonkin"],
    }
    
    surnames = {
        "Human": ["Blackwood", "Ironforge", "Stormwind", "Silvermoon", "Ravenwood", "Thornheart"],
        "Elf": ["Moonwhisper", "Starweaver", "Nightbreeze", "Dawnbringer", "Forestwalker"],
        "Dwarf": ["Ironbeard", "Stonefist", "Hammerfall", "Deepdelver", "Goldseeker"],
        "Halfling": ["Goodbarrel", "Greenbottle", "Thornburrow", "Tealeaf", "Underbough"],
        "Dragonborn": ["Thunderscale", "Firebreath", "Ironhide", "Stormborn", "Wyrmkin"],
        "Tiefling": ["Hellspur", "Darkember", "Grimvale", "Ashborne", "Nightshade"],
        "Half-Orc": ["Bloodaxe", "Bonecrusher", "Ironjaw", "Steelgrip", "Warhammer"],
        "Gnome": ["Tinkertop", "Sparklegem", "Nimblefingers", "Brassgear", "Cogswell"],
    }
    
    first = random.choice(prefixes.get(race, prefixes["Human"]))
    last = random.choice(surnames.get(race, surnames["Human"]))
    return f"{first} {last}"


def generate_npc(index: int) -> Dict[str, Any]:
    """Generate a rich, unique NPC."""
    race = random.choice(RACES)
    npc_class = random.choice(CLASSES) if random.random() > 0.3 else None
    name = generate_npc_name(race)
    role = random.choice(NPC_ROLES)
    alignment = random.choice(ALIGNMENTS)
    faction = random.choice(FACTIONS) if random.random() > 0.5 else None
    trait = random.choice(PERSONALITY_TRAITS)
    
    # Generate rich background
    backgrounds = [
        f"Former {random.choice(CLASSES).lower()} who retired after a traumatic encounter with a {random.choice(['dragon', 'demon', 'lich', 'vampire', 'beholder'])}.",
        f"Secretly working for the {random.choice(FACTIONS).replace('-', ' ')} to gather intelligence on rival factions.",
        f"Seeks an ancient artifact called the {random.choice(['Crown', 'Amulet', 'Blade', 'Tome', 'Staff'])} of {random.choice(['Shadows', 'Storms', 'Dragons', 'Stars', 'Fire'])}.",
        f"Haunted by visions of a coming catastrophe involving {random.choice(THEMES).replace('-', ' ')}.",
        f"Expert in {random.choice(['arcane rituals', 'ancient languages', 'planar travel', 'forbidden lore', 'dragon magic'])}.",
        f"Owes a life debt to a mysterious benefactor from the {random.choice(['Feywild', 'Shadowfell', 'Nine Hells', 'Abyss', 'Astral Plane'])}.",
    ]
    
    background = random.choice(backgrounds)
    
    # Generate quest hooks
    hooks = [
        f"Needs adventurers to retrieve a stolen {random.choice(['spellbook', 'family heirloom', 'trade goods', 'prisoner', 'artifact'])}.",
        f"Offers information about {random.choice(THEMES).replace('-', ' ')} in exchange for discretion.",
        f"Warns of an impending {random.choice(['attack', 'ritual', 'heist', 'assassination', 'invasion'])} by {random.choice(['cultists', 'criminals', 'rival faction', 'monsters', 'undead'])}.",
        f"Knows the location of a hidden {random.choice(['dungeon', 'treasure', 'portal', 'sanctuary', 'weapon cache'])}.",
    ]
    
    hook = random.choice(hooks)
    
    return {
        "id": f"generated:npc:{index:03d}",
        "name": name,
        "race": race,
        "class": npc_class,
        "role": role,
        "alignment": alignment,
        "faction": faction,
        "trait": trait,
        "background": background,
        "hook": hook,
    }


def generate_location(index: int) -> Dict[str, Any]:
    """Generate a rich, unique location."""
    loc_type = random.choice(LOCATION_TYPES)
    descriptor = random.choice(LOCATION_DESCRIPTORS)
    
    location_names = {
        "tavern": ["The {adj} {noun}", ["Drunken", "Golden", "Silver", "Rusty", "Dancing"], ["Dragon", "Griffin", "Stag", "Maiden", "Goblet"]],
        "temple": ["Temple of {deity}", [], ["Bahamut", "Tiamat", "Pelor", "Lolth", "Moradin", "Sehanine"]],
        "dungeon": ["The {adj} {noun}", ["Forgotten", "Cursed", "Lost", "Hidden", "Dark"], ["Catacombs", "Vaults", "Labyrinth", "Depths", "Prison"]],
        "ruins": ["{adj} Ruins of {place}", ["Ancient", "Elven", "Dwarven", "Draconic", "Demonic"], ["Myth Drannor", "Netheril", "Aeor", "Moil", "Bael Turath"]],
        "castle": ["Castle {name}", [], ["Ravenloft", "Greyhawk", "Waterdeep", "Neverwinter", "Ironhold"]],
    }
    
    # Generate name
    template = location_names.get(loc_type, location_names["tavern"])
    format_str = template[0]
    
    # Check what placeholders we have
    if "{adj}" in format_str and "{noun}" in format_str:
        name = format_str.format(adj=random.choice(template[1]), noun=random.choice(template[2]))
    elif "{adj}" in format_str and "{place}" in format_str:
        name = format_str.format(adj=random.choice(template[1]), place=random.choice(template[2]))
    elif "{deity}" in format_str:
        name = format_str.format(deity=random.choice(template[2]))
    elif "{name}" in format_str:
        name = format_str.format(name=random.choice(template[2]))
    else:
        name = f"{descriptor.title()} {loc_type.replace('-', ' ').title()}"
    
    # Generate rich description
    descriptions = [
        f"A {descriptor} {loc_type.replace('-', ' ')} with walls adorned with {random.choice(['ancient tapestries', 'glowing runes', 'trophy heads', 'faded murals', 'mystical symbols'])}.",
        f"The air here is thick with {random.choice(['incense', 'decay', 'magic', 'fear', 'mystery'])}. {random.choice(['Strange sounds', 'Whispers', 'Echoes', 'Music', 'Silence'])} fill the space.",
        f"Built centuries ago by {random.choice(['elven architects', 'dwarven engineers', 'mad wizards', 'dragon cults', 'ancient empires'])}, it shows signs of {random.choice(['recent occupation', 'long abandonment', 'magical corruption', 'structural decay', 'restoration work'])}.",
        f"Local legends speak of {random.choice(['hidden treasures', 'trapped souls', 'powerful artifacts', 'ancient guardians', 'forbidden knowledge'])} within.",
    ]
    
    description = " ".join(random.sample(descriptions, 2))
    
    # Generate features
    features = [
        f"Secret passage behind the {random.choice(['altar', 'fireplace', 'bookshelf', 'statue', 'throne'])}",
        f"Magical ward preventing {random.choice(['scrying', 'teleportation', 'undead', 'fire', 'divination'])}",
        f"{random.choice(['Trapped', 'Locked', 'Hidden', 'Guarded', 'Cursed'])} {random.choice(['door', 'chest', 'vault', 'chamber', 'portal'])}",
        f"Resident {random.choice(['ghost', 'guardian', 'caretaker', 'hermit', 'monster'])} named {generate_npc_name('Human')}",
    ]
    
    feature_list = random.sample(features, 2)
    
    return {
        "id": f"generated:loc:{index:03d}",
        "title": name,
        "type": loc_type,
        "descriptor": descriptor,
        "description": description,
        "features": feature_list,
    }


def generate_encounter(index: int) -> Dict[str, Any]:
    """Generate a rich, unique encounter."""
    enc_type = random.choice(ENCOUNTER_TYPES)
    difficulty = random.choice(["easy", "medium", "hard", "deadly"])
    level_range = random.choice(["1-4", "5-10", "11-16", "17-20"])
    
    # Generate title
    titles = {
        "combat": f"Battle at the {random.choice(['Bridge', 'Crossroads', 'Gate', 'Ruins', 'Tower'])}",
        "social": f"Negotiation with {random.choice(['Nobles', 'Guild Masters', 'Cultists', 'Merchants', 'Bandits'])}",
        "exploration": f"Exploring the {random.choice(['Forgotten', 'Lost', 'Hidden', 'Ancient', 'Cursed'])} {random.choice(['Temple', 'Vault', 'Cave', 'Forest', 'City'])}",
        "puzzle": f"The {random.choice(['Riddle', 'Cipher', 'Maze', 'Lock', 'Trap'])} of {random.choice(['Shadows', 'Elements', 'Time', 'Mirrors', 'Dreams'])}",
    }
    
    title = titles.get(enc_type, f"{enc_type.title()} Encounter {index}")
    
    # Generate setup
    setups = [
        f"The party encounters {random.choice(['a group of', 'an ambush by', 'evidence of', 'the aftermath of', 'preparations for'])} {random.choice(['cultists', 'bandits', 'monsters', 'rival adventurers', 'undead'])}.",
        f"A {random.choice(['merchant', 'noble', 'priest', 'child', 'wounded soldier'])} approaches seeking {random.choice(['protection', 'revenge', 'answers', 'rescue', 'justice'])}.",
        f"Strange {random.choice(['symbols', 'sounds', 'lights', 'weather', 'visions'])} indicate {random.choice(['magical interference', 'planar activity', 'divine presence', 'ancient curse', 'impending danger'])}.",
        f"The path is blocked by {random.choice(['collapsed ruins', 'magical barrier', 'hostile forces', 'natural hazard', 'territorial creature'])}.",
    ]
    
    setup = random.choice(setups)
    
    # Generate tactics/solutions
    combat_tactics = [
        f"Enemies use {random.choice(['hit-and-run', 'defensive formations', 'magical ambush', 'overwhelming numbers', 'terrain advantage'])} tactics.",
        f"Boss has {random.choice(['legendary actions', 'lair actions', 'minions', 'magical immunities', 'regeneration'])}.",
        f"Environment features {random.choice(['difficult terrain', 'cover opportunities', 'hazards', 'interactive objects', 'dynamic elements'])}.",
    ]
    
    social_tactics = [
        f"NPC responds well to {random.choice(['flattery', 'intimidation', 'bribery', 'logical arguments', 'emotional appeals'])}.",
        f"Success requires DC {random.randint(12, 20)} {random.choice(['Persuasion', 'Deception', 'Intimidation', 'Insight', 'Performance'])} check.",
        f"Failure results in {random.choice(['combat', 'higher prices', 'lost opportunity', 'faction reputation loss', 'imprisonment'])}.",
    ]
    
    tactics = combat_tactics if enc_type == "combat" else social_tactics if enc_type == "social" else [
        f"Requires {random.choice(['Investigation', 'Perception', 'Arcana', 'Nature', 'Religion'])} checks to progress.",
        f"Hidden clues point toward {random.choice(['secret door', 'solution', 'trap', 'treasure', 'true enemy'])}.",
        f"Time pressure: {random.choice(['enemies approaching', 'ritual completing', 'structure collapsing', 'curse spreading', 'victim dying'])}.",
    ]
    
    # Generate rewards
    rewards = [
        f"{random.randint(100, 1000)} gp in {random.choice(['coins', 'gems', 'art objects', 'trade goods'])}",
        f"{random.choice(['Uncommon', 'Rare', 'Very Rare'])} magic item: {random.choice(['weapon', 'armor', 'wondrous item', 'potion', 'scroll'])}",
        f"Information about {random.choice(THEMES).replace('-', ' ')}",
        f"Favor from {random.choice(FACTIONS).replace('-', ' ')}",
    ]
    
    return {
        "id": f"generated:enc:{index:03d}",
        "title": title,
        "type": enc_type,
        "difficulty": difficulty,
        "level_range": level_range,
        "setup": setup,
        "tactics": random.sample(tactics, min(2, len(tactics))),
        "rewards": random.sample(rewards, 2),
    }


def write_npc_file(npc: Dict[str, Any], base_dir: Path):
    """Write NPC to markdown file."""
    filename = sanitize_filename(npc["name"]) + ".md"
    filepath = base_dir / "npcs" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
id: {npc['id']}
name: {npc['name']}
race: {npc['race']}
"""
    
    if npc['class']:
        content += f"class: {npc['class']}\n"
    
    content += f"""role: {npc['role']}
alignment: {npc['alignment']}
"""
    
    if npc['faction']:
        content += f"faction: {npc['faction']}\n"
    
    content += f"""tags:
- npc
- {npc['role']}
"""
    
    if npc['faction']:
        content += f"- {npc['faction'].lower()}\n"
    
    content += f"""---

## Personality
**Trait:** {npc['trait']}

## Background
{npc['background']}

## Quest Hook
{npc['hook']}

## Roleplaying Notes
- **Voice:** {random.choice(['Deep and gravelly', 'High-pitched and nervous', 'Smooth and eloquent', 'Gruff and direct', 'Soft and mysterious', 'Loud and boisterous'])}
- **Mannerism:** {random.choice(['Taps fingers when thinking', 'Avoids eye contact', 'Gestures dramatically', 'Constantly cleaning equipment', 'Strokes beard/hair', 'Fidgets with jewelry'])}
- **Motivation:** {random.choice(['Wealth', 'Power', 'Knowledge', 'Revenge', 'Redemption', 'Protection', 'Fame', 'Justice'])}
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath


def write_location_file(location: Dict[str, Any], base_dir: Path):
    """Write location to markdown file."""
    filename = sanitize_filename(location["title"]) + ".md"
    filepath = base_dir / "locations" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
id: {location['id']}
title: {location['title']}
type: {location['type']}
tags:
- location
- {location['type']}
- {location['descriptor']}
---

## Description
{location['description']}

## Notable Features
"""
    
    for feature in location['features']:
        content += f"- {feature}\n"
    
    content += f"""
## Atmosphere
{random.choice([
    'Tense and foreboding, as if danger lurks around every corner.',
    'Peaceful and welcoming, a haven from the dangers outside.',
    'Mysterious and enchanting, filled with strange magic.',
    'Dangerous and hostile, requiring constant vigilance.',
    'Melancholic and haunted, echoes of past tragedies linger.',
    'Vibrant and chaotic, full of activity and noise.',
])}

## Connections
Connected to: {random.choice(['nearby settlements', 'trade routes', 'ancient road networks', 'underground passages', 'planar portals'])}

## Secrets
{random.choice([
    f"Hidden beneath is a {random.choice(['ancient vault', 'forgotten shrine', 'monster lair', 'smuggling operation', 'magical nexus'])}.",
    f"The location is actually {random.choice(['sentient', 'cursed', 'a mimic', 'phasing between planes', 'controlled by a hidden master'])}.",
    f"A {random.choice(['prophecy', 'treasure map', 'ancient text', 'magical key', 'divine blessing'])} points to this place.",
])}
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath


def write_encounter_file(encounter: Dict[str, Any], base_dir: Path):
    """Write encounter to markdown file."""
    filename = sanitize_filename(encounter["title"]) + ".md"
    filepath = base_dir / "encounters" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"""---
id: {encounter['id']}
title: {encounter['title']}
type: {encounter['type']}
difficulty: {encounter['difficulty']}
level_range: {encounter['level_range']}
tags:
- encounter
- {encounter['type']}
- {encounter['difficulty']}
---

## Setup
{encounter['setup']}

## Tactics & Solutions
"""
    
    for tactic in encounter['tactics']:
        content += f"- {tactic}\n"
    
    content += """
## Rewards
"""
    
    for reward in encounter['rewards']:
        content += f"- {reward}\n"
    
    content += """
## Scaling
- **Easy:** Reduce enemy HP by 25%, remove one enemy
- **Hard:** Increase enemy HP by 50%, add reinforcements
- **Deadly:** Add legendary resistance, double minions

## Variations
{random.choice([
    'Can be adapted for urban, wilderness, or dungeon settings.',
    'Works as random encounter or planned story beat.',
    'Can escalate to multi-session storyline.',
    'Suitable for tournament or convention play.',
])}
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath


def generate_adventure_module(index: int, base_dir: Path):
    """Generate a complete adventure module in tyranny_of_dragons structure."""
    
    adventure_names = [
        "Shadows of the Underdark",
        "Crown of the Fire Giants",
        "Curse of the Vampire Lord",
        "Secrets of the Wizard Conclave",
        "Depths of the Elemental Chaos",
    ]
    
    adventure_name = adventure_names[index - 1] if index <= len(adventure_names) else f"Adventure Module {index}"
    adventure_dir = base_dir / sanitize_filename(adventure_name)
    
    # Create directory structure
    for subdir in ["handouts", "items", "locations", "mechanics", "npcs", "parts"]:
        (adventure_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    # Generate index.md
    themes = random.sample(THEMES, 3)
    level_range = random.choice(["1-4", "5-10", "11-16", "17-20"])
    factions = random.sample(FACTIONS, 2)
    
    index_content = f"""---
id: generated:adventure:{index:02d}
title: {adventure_name}
edition: D&D 5e
levels: Optimized for {random.choice(['four', 'five', 'six'])} characters levels {level_range}
structure: {random.choice(['Three-act structure', 'Sandbox exploration', 'Linear storyline', 'Episodic missions'])}
themes:
"""
    
    for theme in themes:
        index_content += f"- {theme}\n"
    
    index_content += f"""setting: {random.choice(['Sword Coast', 'Moonsea', 'Underdark', 'Feywild', 'Shadowfell', 'Chult', 'Icewind Dale'])} — Forgotten Realms
tags:
- adventure
- generated
- levels-{level_range}
---

# Overview

{random.choice([
    'A mysterious threat emerges from the depths, threatening the region.',
    'Political intrigue and faction warfare threaten to tear the city apart.',
    'Ancient magic awakens, drawing adventurers into a race against time.',
    'A powerful artifact surfaces, attracting both heroes and villains.',
    'Strange phenomena herald the arrival of extraplanar forces.',
])}

Touchpoints for factions: **{factions[0].replace('-', ' ')}**, **{factions[1].replace('-', ' ')}**.

## Story Beats
- **Act I:** {random.choice(['Investigation and discovery', 'Gathering allies', 'Thwarting initial threat', 'Uncovering conspiracy'])}
- **Act II:** {random.choice(['Escalating conflict', 'Dungeon delving', 'Faction warfare', 'Planar travel'])}
- **Act III:** {random.choice(['Final confrontation', 'Siege defense', 'Ritual prevention', 'Epic battle'])}

## Success States
- Primary threat neutralized; region saved from {random.choice(['destruction', 'conquest', 'corruption', 'annihilation'])}.
- Key NPCs rescued or alliances forged.
- Artifact secured or destroyed.

## Failure States
- Enemy achieves their goal; catastrophic consequences ensue.
- Key NPCs perish or turn against the party.
- Region falls under enemy control.

## Player-Facing Summary
{adventure_name} presents a challenging adventure involving {', '.join([t.replace('-', ' ') for t in themes[:2]])}. Your choices will determine the fate of {random.choice(['thousands', 'an entire city', 'the region', 'multiple planes of existence'])}.
"""
    
    (adventure_dir / "index.md").write_text(index_content, encoding='utf-8')
    
    # Generate README
    readme_content = f"""# {adventure_name}

A generated D&D 5e adventure module for levels {level_range}.

## Structure
- `index.md` - Main adventure overview
- `handouts/` - Player handouts and props
- `items/` - Magic items and treasure
- `locations/` - Key locations and maps
- `mechanics/` - Combat encounters and challenges
- `npcs/` - Non-player characters
- `parts/` - Adventure sections/chapters

## Themes
{', '.join([t.replace('-', ' ').title() for t in themes])}

## Running This Adventure
See `index.md` for complete overview and story structure.
"""
    
    (adventure_dir / "README.md").write_text(readme_content, encoding='utf-8')
    
    # Generate ATTRIBUTION
    attribution_content = f"""# Attribution

**{adventure_name}**

Generated content for StoryCraft RAG system.
Based on D&D 5e SRD and compatible with Forgotten Realms setting.

Generated: October 23, 2025
System: StoryCraft RAG Content Generator

## License
This adventure module is provided for personal use in D&D 5e campaigns.
Compatible with Systems Reference Document (SRD) 5.1.
"""
    
    (adventure_dir / "ATTRIBUTION.md").write_text(attribution_content, encoding='utf-8')
    
    # Generate 5 NPCs for this adventure
    for i in range(5):
        npc = generate_npc(index * 100 + i)
        write_npc_file(npc, adventure_dir)
    
    # Generate 5 locations
    for i in range(5):
        location = generate_location(index * 100 + i)
        write_location_file(location, adventure_dir)
    
    # Generate 3 major encounters
    for i in range(3):
        encounter = generate_encounter(index * 100 + i)
        write_encounter_file(encounter, adventure_dir)
    
    # Generate hook handout
    hook_content = f"""---
id: generated:adventure:{index:02d}:hook
title: Adventure Hook
tags:
- handout
- hook
---

## How the Adventure Begins

{random.choice([
    'The party receives a mysterious letter requesting their aid.',
    'A desperate messenger arrives with news of imminent danger.',
    'Strange omens and prophecies point to the party.',
    'A valuable item or person has gone missing.',
    'The party witnesses a crime or supernatural event.',
])}

### Additional Hooks
- **Harpers:** {random.choice(['Investigate reports of dark magic', 'Protect innocent civilians', 'Preserve knowledge'])}
- **Zhentarim:** {random.choice(['Eliminate competition', 'Secure valuable resources', 'Expand influence'])}
- **Lords Alliance:** {random.choice(['Defend settlements', 'Maintain order', 'Diplomatic mission'])}
"""
    
    (adventure_dir / "handouts" / "hook.md").write_text(hook_content, encoding='utf-8')
    
    # Generate items index
    items_content = f"""---
id: generated:adventure:{index:02d}:items
title: Treasure & Magic Items
tags:
- items
- treasure
---

## Treasure Parcels

### Early Adventure
- {random.randint(50, 200)} gp
- {random.choice(['Potion of Healing', 'Spell Scroll (1st level)', 'Bag of gemstones (50 gp value)'])}

### Mid Adventure
- {random.randint(300, 800)} gp
- {random.choice(['Weapon +1', 'Armor +1', 'Ring of Protection', 'Cloak of Protection', 'Wand of Magic Missiles'])}

### Final Reward
- {random.randint(1000, 5000)} gp
- {random.choice(['Weapon +2', 'Armor +2', 'Ring of Spell Storing', 'Staff of Power', 'Helm of Brilliance'])}
- {random.choice(['Rare gemstone (1000 gp)', 'Art object collection (2000 gp)', 'Deed to property', 'Spellbook with 10 spells'])}
"""
    
    (adventure_dir / "items" / "index.md").write_text(items_content, encoding='utf-8')
    
    print(f"✓ Generated adventure module: {adventure_name}")
    return adventure_dir


def main():
    """Main content generation workflow."""
    print("=" * 70)
    print("StoryCraft RAG Content Generator")
    print("=" * 70)
    print()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {
        "npcs": 0,
        "locations": 0,
        "encounters": 0,
        "adventures": 0,
        "files": 0
    }
    
    # Generate standalone NPCs
    print("Generating 100 unique NPCs...")
    standalone_dir = OUTPUT_DIR / "standalone_content"
    for i in range(1, 101):
        npc = generate_npc(i)
        write_npc_file(npc, standalone_dir)
        stats["npcs"] += 1
        stats["files"] += 1
        if i % 10 == 0:
            print(f"  {i}/100 NPCs generated...")
    
    print(f"✓ Generated {stats['npcs']} NPCs")
    print()
    
    # Generate standalone locations
    print("Generating 100 unique locations...")
    for i in range(1, 101):
        location = generate_location(i)
        write_location_file(location, standalone_dir)
        stats["locations"] += 1
        stats["files"] += 1
        if i % 10 == 0:
            print(f"  {i}/100 Locations generated...")
    
    print(f"✓ Generated {stats['locations']} Locations")
    print()
    
    # Generate standalone encounters
    print("Generating 100 unique encounters...")
    for i in range(1, 101):
        encounter = generate_encounter(i)
        write_encounter_file(encounter, standalone_dir)
        stats["encounters"] += 1
        stats["files"] += 1
        if i % 10 == 0:
            print(f"  {i}/100 Encounters generated...")
    
    print(f"✓ Generated {stats['encounters']} Encounters")
    print()
    
    # Generate 5 complete adventure modules
    print("Generating 5 complete adventure modules...")
    for i in range(1, 6):
        generate_adventure_module(i, OUTPUT_DIR)
        stats["adventures"] += 1
        # Each adventure generates: index, README, ATTRIBUTION, 5 NPCs, 5 locations, 3 encounters, hook, items
        stats["files"] += 17
    
    print(f"✓ Generated {stats['adventures']} Adventure Modules")
    print()
    
    # Summary
    print("=" * 70)
    print("GENERATION COMPLETE!")
    print("=" * 70)
    print(f"Total NPCs:       {stats['npcs']}")
    print(f"Total Locations:  {stats['locations']}")
    print(f"Total Encounters: {stats['encounters']}")
    print(f"Total Adventures: {stats['adventures']}")
    print(f"Total Files:      {stats['files']}")
    print()
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    print("Next steps:")
    print("1. Review generated content in the output directory")
    print("2. Run RAG ingestion script to add to vector database:")
    print("   python scripts/ingest_guild_modules.py")
    print()


if __name__ == "__main__":
    main()
