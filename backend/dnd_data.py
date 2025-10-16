"""
D&D 5E Data Module
==================
Comprehensive reference data for D&D 5th Edition character creation.
Data sourced from D&D Beyond (October 2025) - Player's Handbook 2024 & supplemental sources.

This module provides:
- 13 character classes with hit dice, abilities, and proficiencies
- 10+ core species with traits and ability bonuses
- Backgrounds with skills, tools, and features
- Equipment lists and starting gear
- Ability score generation methods
- Skills and proficiencies reference
"""

# ============================================================================
# D&D CLASSES
# ============================================================================

DND_CLASSES = {
    "barbarian": {
        "name": "Barbarian",
        "description": "A fierce warrior powered by primal rage",
        "hit_die": 12,
        "primary_ability": ["Strength"],
        "saving_throws": ["Strength", "Constitution"],
        "armor_proficiencies": ["Light armor", "Medium armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons", "Martial weapons"],
        "skill_choices": 2,
        "skill_list": ["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"],
        "starting_equipment": [
            "Greataxe or any martial melee weapon",
            "Two handaxes or any simple weapon",
            "Explorer's pack and four javelins"
        ],
        "level_1_features": ["Rage", "Unarmored Defense"],
        "spellcaster": False
    },
    
    "bard": {
        "name": "Bard",
        "description": "An inspiring performer of music, dance, and magic",
        "hit_die": 8,
        "primary_ability": ["Charisma"],
        "saving_throws": ["Dexterity", "Charisma"],
        "armor_proficiencies": ["Light armor"],
        "weapon_proficiencies": ["Simple weapons", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
        "tool_proficiencies": ["Three musical instruments of your choice"],
        "skill_choices": 3,
        "skill_list": ["Any three skills"],
        "starting_equipment": [
            "Rapier or longsword or any simple weapon",
            "Diplomat's pack or entertainer's pack",
            "Lute or any other musical instrument",
            "Leather armor and dagger"
        ],
        "level_1_features": ["Spellcasting", "Bardic Inspiration"],
        "spellcaster": True,
        "spellcasting_ability": "Charisma",
        "cantrips_known": 2,
        "spells_known": 4,
        "spell_slots_level_1": 2
    },
    
    "cleric": {
        "name": "Cleric",
        "description": "A miraculous priest wielding divine power",
        "hit_die": 8,
        "primary_ability": ["Wisdom"],
        "saving_throws": ["Wisdom", "Charisma"],
        "armor_proficiencies": ["Light armor", "Medium armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons"],
        "skill_choices": 2,
        "skill_list": ["History", "Insight", "Medicine", "Persuasion", "Religion"],
        "starting_equipment": [
            "Mace or warhammer (if proficient)",
            "Scale mail or leather armor or chain mail (if proficient)",
            "Light crossbow and 20 bolts or any simple weapon",
            "Priest's pack or explorer's pack",
            "Shield and holy symbol"
        ],
        "level_1_features": ["Spellcasting", "Divine Domain"],
        "spellcaster": True,
        "spellcasting_ability": "Wisdom",
        "cantrips_known": 3,
        "spells_prepared": "Wisdom modifier + Cleric level",
        "spell_slots_level_1": 2
    },
    
    "druid": {
        "name": "Druid",
        "description": "A nature priest harnessing primal power",
        "hit_die": 8,
        "primary_ability": ["Wisdom"],
        "saving_throws": ["Intelligence", "Wisdom"],
        "armor_proficiencies": ["Light armor", "Medium armor", "Shields (druids will not wear armor or use shields made of metal)"],
        "weapon_proficiencies": ["Clubs", "Daggers", "Darts", "Javelins", "Maces", "Quarterstaffs", "Scimitars", "Sickles", "Slings", "Spears"],
        "tool_proficiencies": ["Herbalism kit"],
        "skill_choices": 2,
        "skill_list": ["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"],
        "starting_equipment": [
            "Wooden shield or any simple weapon",
            "Scimitar or any simple melee weapon",
            "Leather armor, explorer's pack, and druidic focus"
        ],
        "level_1_features": ["Spellcasting", "Druidic"],
        "spellcaster": True,
        "spellcasting_ability": "Wisdom",
        "cantrips_known": 2,
        "spells_prepared": "Wisdom modifier + Druid level",
        "spell_slots_level_1": 2
    },
    
    "fighter": {
        "name": "Fighter",
        "description": "A master of all arms and armor",
        "hit_die": 10,
        "primary_ability": ["Strength", "Dexterity"],
        "saving_throws": ["Strength", "Constitution"],
        "armor_proficiencies": ["All armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons", "Martial weapons"],
        "skill_choices": 2,
        "skill_list": ["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"],
        "starting_equipment": [
            "Chain mail or leather armor, longbow, and 20 arrows",
            "Martial weapon and shield or two martial weapons",
            "Light crossbow and 20 bolts or two handaxes",
            "Dungeoneer's pack or explorer's pack"
        ],
        "level_1_features": ["Fighting Style", "Second Wind"],
        "spellcaster": False
    },
    
    "monk": {
        "name": "Monk",
        "description": "A martial artist of supernatural focus",
        "hit_die": 8,
        "primary_ability": ["Dexterity", "Wisdom"],
        "saving_throws": ["Strength", "Dexterity"],
        "armor_proficiencies": ["None"],
        "weapon_proficiencies": ["Simple weapons", "Shortswords"],
        "tool_proficiencies": ["One type of artisan's tools or one musical instrument"],
        "skill_choices": 2,
        "skill_list": ["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
        "starting_equipment": [
            "Shortsword or any simple weapon",
            "Dungeoneer's pack or explorer's pack",
            "10 darts"
        ],
        "level_1_features": ["Unarmored Defense", "Martial Arts"],
        "spellcaster": False
    },
    
    "paladin": {
        "name": "Paladin",
        "description": "A devout warrior of sacred oaths",
        "hit_die": 10,
        "primary_ability": ["Strength", "Charisma"],
        "saving_throws": ["Wisdom", "Charisma"],
        "armor_proficiencies": ["All armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons", "Martial weapons"],
        "skill_choices": 2,
        "skill_list": ["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
        "starting_equipment": [
            "Martial weapon and shield or two martial weapons",
            "Five javelins or any simple melee weapon",
            "Priest's pack or explorer's pack",
            "Chain mail and holy symbol"
        ],
        "level_1_features": ["Divine Sense", "Lay on Hands"],
        "spellcaster": True,  # Half-caster starting at level 2
        "spellcasting_ability": "Charisma",
        "spells_prepared": "Charisma modifier + half Paladin level (rounded down)",
        "spell_slots_level_1": 0  # Starts at level 2
    },
    
    "ranger": {
        "name": "Ranger",
        "description": "A wandering warrior imbued with primal magic",
        "hit_die": 10,
        "primary_ability": ["Dexterity", "Wisdom"],
        "saving_throws": ["Strength", "Dexterity"],
        "armor_proficiencies": ["Light armor", "Medium armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons", "Martial weapons"],
        "skill_choices": 3,
        "skill_list": ["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"],
        "starting_equipment": [
            "Scale mail or leather armor",
            "Two shortswords or two simple melee weapons",
            "Dungeoneer's pack or explorer's pack",
            "Longbow and quiver of 20 arrows"
        ],
        "level_1_features": ["Favored Enemy", "Natural Explorer"],
        "spellcaster": True,  # Half-caster starting at level 2
        "spellcasting_ability": "Wisdom",
        "spells_known": 2,  # At level 2
        "spell_slots_level_1": 0  # Starts at level 2
    },
    
    "rogue": {
        "name": "Rogue",
        "description": "A dexterous expert in stealth and subterfuge",
        "hit_die": 8,
        "primary_ability": ["Dexterity"],
        "saving_throws": ["Dexterity", "Intelligence"],
        "armor_proficiencies": ["Light armor"],
        "weapon_proficiencies": ["Simple weapons", "Hand crossbows", "Longswords", "Rapiers", "Shortswords"],
        "tool_proficiencies": ["Thieves' tools"],
        "skill_choices": 4,
        "skill_list": ["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
        "starting_equipment": [
            "Rapier or shortsword",
            "Shortbow and quiver of 20 arrows or shortsword",
            "Burglar's pack or dungeoneer's pack or explorer's pack",
            "Leather armor, two daggers, and thieves' tools"
        ],
        "level_1_features": ["Expertise", "Sneak Attack", "Thieves' Cant"],
        "spellcaster": False
    },
    
    "sorcerer": {
        "name": "Sorcerer",
        "description": "A dazzling mage filled with innate magic",
        "hit_die": 6,
        "primary_ability": ["Charisma"],
        "saving_throws": ["Constitution", "Charisma"],
        "armor_proficiencies": ["None"],
        "weapon_proficiencies": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
        "skill_choices": 2,
        "skill_list": ["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
        "starting_equipment": [
            "Light crossbow and 20 bolts or any simple weapon",
            "Component pouch or arcane focus",
            "Dungeoneer's pack or explorer's pack",
            "Two daggers"
        ],
        "level_1_features": ["Spellcasting", "Sorcerous Origin"],
        "spellcaster": True,
        "spellcasting_ability": "Charisma",
        "cantrips_known": 4,
        "spells_known": 2,
        "spell_slots_level_1": 2
    },
    
    "warlock": {
        "name": "Warlock",
        "description": "An occultist empowered by otherworldly pacts",
        "hit_die": 8,
        "primary_ability": ["Charisma"],
        "saving_throws": ["Wisdom", "Charisma"],
        "armor_proficiencies": ["Light armor"],
        "weapon_proficiencies": ["Simple weapons"],
        "skill_choices": 2,
        "skill_list": ["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
        "starting_equipment": [
            "Light crossbow and 20 bolts or any simple weapon",
            "Component pouch or arcane focus",
            "Scholar's pack or dungeoneer's pack",
            "Leather armor, any simple weapon, and two daggers"
        ],
        "level_1_features": ["Otherworldly Patron", "Pact Magic"],
        "spellcaster": True,
        "spellcasting_ability": "Charisma",
        "cantrips_known": 2,
        "spells_known": 2,
        "spell_slots_level_1": 1  # Warlocks use Pact Magic slots
    },
    
    "wizard": {
        "name": "Wizard",
        "description": "A scholarly magic-user of arcane power",
        "hit_die": 6,
        "primary_ability": ["Intelligence"],
        "saving_throws": ["Intelligence", "Wisdom"],
        "armor_proficiencies": ["None"],
        "weapon_proficiencies": ["Daggers", "Darts", "Slings", "Quarterstaffs", "Light crossbows"],
        "skill_choices": 2,
        "skill_list": ["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"],
        "starting_equipment": [
            "Quarterstaff or dagger",
            "Component pouch or arcane focus",
            "Scholar's pack or explorer's pack",
            "Spellbook"
        ],
        "level_1_features": ["Spellcasting", "Arcane Recovery"],
        "spellcaster": True,
        "spellcasting_ability": "Intelligence",
        "cantrips_known": 3,
        "spells_in_spellbook": 6,
        "spells_prepared": "Intelligence modifier + Wizard level",
        "spell_slots_level_1": 2
    },
    
    "artificer": {
        "name": "Artificer",
        "description": "A master of invention and magical crafting",
        "hit_die": 8,
        "primary_ability": ["Intelligence"],
        "saving_throws": ["Constitution", "Intelligence"],
        "armor_proficiencies": ["Light armor", "Medium armor", "Shields"],
        "weapon_proficiencies": ["Simple weapons"],
        "tool_proficiencies": ["Thieves' tools", "Tinker's tools", "One type of artisan's tools of your choice"],
        "skill_choices": 2,
        "skill_list": ["Arcana", "History", "Investigation", "Medicine", "Nature", "Perception", "Sleight of Hand"],
        "starting_equipment": [
            "Any two simple weapons",
            "Light crossbow and 20 bolts",
            "Studded leather armor or scale mail",
            "Thieves' tools and dungeoneer's pack"
        ],
        "level_1_features": ["Magical Tinkering", "Spellcasting"],
        "spellcaster": True,  # Half-caster
        "spellcasting_ability": "Intelligence",
        "cantrips_known": 2,
        "spells_prepared": "Intelligence modifier + half Artificer level (rounded down)",
        "spell_slots_level_1": 2
    }
}

# ============================================================================
# D&D SPECIES (RACES)
# ============================================================================

DND_SPECIES = {
    # CORE 10 SPECIES (Player's Handbook 2024)
    
    "aasimar": {
        "name": "Aasimar",
        "description": "Mortals who carry a spark of the Upper Planes within their souls",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,  # Player chooses which abilities to increase
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Celestial Resistance (Resistance to necrotic and radiant damage)",
            "Darkvision (60 feet)",
            "Healing Hands (Heal HP equal to your level as an action, once per long rest)",
            "Light Bearer (You know the Light cantrip)",
            "Celestial Revelation (Transform as a bonus action, gain flight or radiant damage)"
        ],
        "languages": ["Common", "Celestial"]
    },
    
    "dragonborn": {
        "name": "Dragonborn",
        "description": "Descendants of dragons, hatched from chromatic and metallic dragon eggs",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Draconic Ancestry (Choose a dragon type for damage resistance and breath weapon)",
            "Breath Weapon (Exhale destructive energy, damage = level, Dex/Con save)",
            "Damage Resistance (Resist damage type based on Draconic Ancestry)",
            "Darkvision (60 feet)",
            "Draconic Flight (At 5th level, gain flying speed equal to walking speed)"
        ],
        "languages": ["Common", "Draconic"],
        "dragon_types": ["Black (Acid)", "Blue (Lightning)", "Brass (Fire)", "Bronze (Lightning)", 
                        "Copper (Acid)", "Gold (Fire)", "Green (Poison)", "Red (Fire)", 
                        "Silver (Cold)", "White (Cold)"]
    },
    
    "dwarf": {
        "name": "Dwarf",
        "description": "Bold and hardy folk, raised from the earth by a deity of the forge",
        "size": "Medium",
        "speed": 25,  # Not reduced by heavy armor
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Darkvision (120 feet)",
            "Dwarven Resilience (Advantage on saves vs. poison, resistance to poison damage)",
            "Dwarven Toughness (HP maximum increases by 1 per level)",
            "Stonecunning (Double proficiency for History checks about stonework)"
        ],
        "languages": ["Common", "Dwarvish"],
        "tool_proficiencies": ["Choose one: Smith's tools, Brewer's supplies, or Mason's tools"]
    },
    
    "elf": {
        "name": "Elf",
        "description": "Magical folk whose curiosity led them to explore the planes of existence",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Darkvision (60 feet)",
            "Elven Lineage (Choose High Elf, Wood Elf, or Drow heritage for bonus traits)",
            "Fey Ancestry (Advantage on saves vs. being charmed, magic can't put you to sleep)",
            "Keen Senses (Proficiency in Perception)",
            "Trance (Meditate 4 hours instead of sleeping 8 hours)"
        ],
        "languages": ["Common", "Elvish"],
        "lineages": {
            "high_elf": ["Cantrip from Wizard spell list", "Extra language"],
            "wood_elf": ["Speed increases to 35 feet", "Hide in light natural cover"],
            "drow": ["Darkvision extends to 120 feet", "Dancing Lights cantrip", "Sunlight Sensitivity"]
        }
    },
    
    "gnome": {
        "name": "Gnome",
        "description": "Magical folk created by gods of invention, illusions, and life underground",
        "size": "Small",
        "speed": 25,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Darkvision (60 feet)",
            "Gnomish Cunning (Advantage on Int, Wis, Cha saves vs. magic)",
            "Gnomish Lineage (Choose Forest Gnome or Rock Gnome for bonus traits)"
        ],
        "languages": ["Common", "Gnomish"],
        "lineages": {
            "forest_gnome": ["Minor Illusion cantrip", "Speak with small beasts"],
            "rock_gnome": ["Tinker feature", "History checks for magic items, tech, alchemical objects"]
        }
    },
    
    "goliath": {
        "name": "Goliath",
        "description": "Distant descendants of giants, seeking heights above their ancestors",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Giant Ancestry (Advantage on saves vs. being knocked prone)",
            "Large Form (Once per long rest, grow one size larger for 10 minutes, advantage on Str checks/saves)",
            "Powerful Build (Count as one size larger for carrying capacity and push/drag/lift)"
        ],
        "languages": ["Common", "Giant"]
    },
    
    "halfling": {
        "name": "Halfling",
        "description": "Small folk with a brave and adventurous spirit",
        "size": "Small",
        "speed": 25,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Brave (Advantage on saves vs. being frightened)",
            "Halfling Nimbleness (Move through space of Medium or larger creatures)",
            "Luck (Reroll 1 on attack roll, ability check, or save)",
            "Naturally Stealthy (Hide when obscured by Medium or larger creature)"
        ],
        "languages": ["Common", "Halfling"]
    },
    
    "human": {
        "name": "Human",
        "description": "Versatile and numerous folk found throughout the multiverse",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Resourceful (Gain Heroic Inspiration whenever you finish a long rest)",
            "Skillful (Proficiency in one skill of your choice)",
            "Versatile (Gain Origin feat of your choice)"
        ],
        "languages": ["Common", "One extra language of your choice"]
    },
    
    "orc": {
        "name": "Orc",
        "description": "Folk equipped with gifts to wander great plains, caverns, and seas",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Adrenaline Rush (Bonus action, move extra distance + temp HP, PB times per long rest)",
            "Darkvision (120 feet)",
            "Relentless Endurance (Drop to 1 HP instead of 0, once per long rest)"
        ],
        "languages": ["Common", "Orc"]
    },
    
    "tiefling": {
        "name": "Tiefling",
        "description": "Born in the Lower Planes or with fiendish ancestors",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "choice": 2,
            "options": "Any two abilities +2, +1 or +1, +1, +1"
        },
        "traits": [
            "Darkvision (60 feet)",
            "Fiendish Legacy (Choose Abyssal, Chthonic, or Infernal for spells)",
            "Otherworldly Presence (Proficiency in Intimidation or Persuasion)"
        ],
        "languages": ["Common", "Infernal or Abyssal"],
        "legacies": {
            "abyssal": ["Poison Spray cantrip", "Ray of Sickness at 3rd", "Hold Person at 5th"],
            "chthonic": ["Chill Touch cantrip", "False Life at 3rd", "Ray of Enfeeblement at 5th"],
            "infernal": ["Fire Bolt cantrip", "Hellish Rebuke at 3rd", "Darkness at 5th"]
        }
    },
    
    # POPULAR ADDITIONAL SPECIES
    
    "half-elf": {
        "name": "Half-Elf",
        "description": "Combining the best qualities of elves and humans",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "charisma": 2,
            "choice": "Two other abilities +1 each"
        },
        "traits": [
            "Darkvision (60 feet)",
            "Fey Ancestry (Advantage on saves vs. charmed, magic can't put you to sleep)",
            "Skill Versatility (Proficiency in two skills of your choice)"
        ],
        "languages": ["Common", "Elvish", "One extra language"]
    },
    
    "half-orc": {
        "name": "Half-Orc",
        "description": "Proud leaders and fierce warriors with orcish heritage",
        "size": "Medium",
        "speed": 30,
        "ability_bonuses": {
            "strength": 2,
            "constitution": 1
        },
        "traits": [
            "Darkvision (60 feet)",
            "Menacing (Proficiency in Intimidation)",
            "Relentless Endurance (Drop to 1 HP instead of 0, once per long rest)",
            "Savage Attacks (Roll one additional weapon damage die on critical hit)"
        ],
        "languages": ["Common", "Orc"]
    }
}

# ============================================================================
# D&D BACKGROUNDS
# ============================================================================

DND_BACKGROUNDS = {
    "acolyte": {
        "name": "Acolyte",
        "description": "You have spent your life in service to a temple",
        "skill_proficiencies": ["Insight", "Religion"],
        "tool_proficiencies": [],
        "languages": 2,
        "equipment": [
            "Holy symbol",
            "Prayer book or prayer wheel",
            "5 sticks of incense",
            "Vestments",
            "Common clothes",
            "Belt pouch with 15 gp"
        ],
        "feature": "Shelter of the Faithful",
        "feature_description": "You can receive free healing and care at temples of your faith"
    },
    
    "charlatan": {
        "name": "Charlatan",
        "description": "You have always had a way with people",
        "skill_proficiencies": ["Deception", "Sleight of Hand"],
        "tool_proficiencies": ["Disguise kit", "Forgery kit"],
        "equipment": [
            "Fine clothes",
            "Disguise kit",
            "Tools of your con",
            "Belt pouch with 15 gp"
        ],
        "feature": "False Identity",
        "feature_description": "You have created a second identity with documentation and disguises"
    },
    
    "criminal": {
        "name": "Criminal",
        "description": "You are an experienced criminal with a history of breaking the law",
        "skill_proficiencies": ["Deception", "Stealth"],
        "tool_proficiencies": ["One type of gaming set", "Thieves' tools"],
        "equipment": [
            "Crowbar",
            "Dark common clothes with hood",
            "Belt pouch with 15 gp"
        ],
        "feature": "Criminal Contact",
        "feature_description": "You have a reliable contact in the criminal underworld"
    },
    
    "entertainer": {
        "name": "Entertainer",
        "description": "You thrive in front of an audience",
        "skill_proficiencies": ["Acrobatics", "Performance"],
        "tool_proficiencies": ["Disguise kit", "One type of musical instrument"],
        "equipment": [
            "Musical instrument",
            "Favor of an admirer",
            "Costume",
            "Belt pouch with 15 gp"
        ],
        "feature": "By Popular Demand",
        "feature_description": "You can find a place to perform and receive free lodging"
    },
    
    "folk_hero": {
        "name": "Folk Hero",
        "description": "You come from humble origins but are destined for greatness",
        "skill_proficiencies": ["Animal Handling", "Survival"],
        "tool_proficiencies": ["One type of artisan's tools", "Vehicles (land)"],
        "equipment": [
            "Set of artisan's tools",
            "Shovel",
            "Iron pot",
            "Common clothes",
            "Belt pouch with 10 gp"
        ],
        "feature": "Rustic Hospitality",
        "feature_description": "Common folk will shelter and hide you from the law"
    },
    
    "guild_artisan": {
        "name": "Guild Artisan",
        "description": "You are a member of an artisan's guild",
        "skill_proficiencies": ["Insight", "Persuasion"],
        "tool_proficiencies": ["One type of artisan's tools"],
        "languages": 1,
        "equipment": [
            "Set of artisan's tools",
            "Letter of introduction from guild",
            "Traveler's clothes",
            "Belt pouch with 15 gp"
        ],
        "feature": "Guild Membership",
        "feature_description": "Support from your guild, including lodging and assistance"
    },
    
    "hermit": {
        "name": "Hermit",
        "description": "You lived in seclusion seeking enlightenment or secret knowledge",
        "skill_proficiencies": ["Medicine", "Religion"],
        "tool_proficiencies": ["Herbalism kit"],
        "languages": 1,
        "equipment": [
            "Scroll case with notes",
            "Winter blanket",
            "Common clothes",
            "Herbalism kit",
            "5 gp"
        ],
        "feature": "Discovery",
        "feature_description": "You learned a unique and powerful secret during your seclusion"
    },
    
    "noble": {
        "name": "Noble",
        "description": "You understand wealth, power, and privilege",
        "skill_proficiencies": ["History", "Persuasion"],
        "tool_proficiencies": ["One type of gaming set"],
        "languages": 1,
        "equipment": [
            "Fine clothes",
            "Signet ring",
            "Scroll of pedigree",
            "Purse with 25 gp"
        ],
        "feature": "Position of Privilege",
        "feature_description": "People assume you have the right to be wherever you are"
    },
    
    "outlander": {
        "name": "Outlander",
        "description": "You grew up in the wilds, far from civilization",
        "skill_proficiencies": ["Athletics", "Survival"],
        "tool_proficiencies": ["One type of musical instrument"],
        "languages": 1,
        "equipment": [
            "Staff",
            "Hunting trap",
            "Trophy from an animal",
            "Traveler's clothes",
            "Belt pouch with 10 gp"
        ],
        "feature": "Wanderer",
        "feature_description": "Excellent memory for geography and can find food/water for yourself and 5 others"
    },
    
    "sage": {
        "name": "Sage",
        "description": "You spent years learning the lore of the multiverse",
        "skill_proficiencies": ["Arcana", "History"],
        "languages": 2,
        "equipment": [
            "Bottle of black ink",
            "Quill",
            "Small knife",
            "Letter from dead colleague with unanswered question",
            "Common clothes",
            "Belt pouch with 10 gp"
        ],
        "feature": "Researcher",
        "feature_description": "You know how to obtain information and where to find it"
    },
    
    "soldier": {
        "name": "Soldier",
        "description": "You have military training and experience in warfare",
        "skill_proficiencies": ["Athletics", "Intimidation"],
        "tool_proficiencies": ["One type of gaming set", "Vehicles (land)"],
        "equipment": [
            "Insignia of rank",
            "Trophy from fallen enemy",
            "Set of bone dice or playing cards",
            "Common clothes",
            "Belt pouch with 10 gp"
        ],
        "feature": "Military Rank",
        "feature_description": "Soldiers defer to you and you can get access to military facilities"
    },
    
    "urchin": {
        "name": "Urchin",
        "description": "You grew up on the streets, surviving through cunning",
        "skill_proficiencies": ["Sleight of Hand", "Stealth"],
        "tool_proficiencies": ["Disguise kit", "Thieves' tools"],
        "equipment": [
            "Small knife",
            "Map of your home city",
            "Pet mouse",
            "Token of your parents",
            "Common clothes",
            "Belt pouch with 10 gp"
        ],
        "feature": "City Secrets",
        "feature_description": "You know the secret patterns of cities and can move twice as fast"
    }
}

# ============================================================================
# ABILITY SCORES
# ============================================================================

ABILITY_SCORES = {
    "strength": {
        "name": "Strength",
        "abbreviation": "STR",
        "description": "Measures physical power, athletic training, and brute force"
    },
    "dexterity": {
        "name": "Dexterity",
        "abbreviation": "DEX",
        "description": "Measures agility, reflexes, balance, and hand-eye coordination"
    },
    "constitution": {
        "name": "Constitution",
        "abbreviation": "CON",
        "description": "Measures health, stamina, and vital force"
    },
    "intelligence": {
        "name": "Intelligence",
        "abbreviation": "INT",
        "description": "Measures reasoning, memory, and analytical thinking"
    },
    "wisdom": {
        "name": "Wisdom",
        "abbreviation": "WIS",
        "description": "Measures awareness, intuition, and insight"
    },
    "charisma": {
        "name": "Charisma",
        "abbreviation": "CHA",
        "description": "Measures force of personality, persuasiveness, and leadership"
    }
}

# Standard Array for ability scores
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# Point Buy system
POINT_BUY_COSTS = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9
}
POINT_BUY_TOTAL = 27

# ============================================================================
# SKILLS
# ============================================================================

DND_SKILLS = {
    "acrobatics": {"ability": "Dexterity", "description": "Balance, tumbling, aerial maneuvers"},
    "animal_handling": {"ability": "Wisdom", "description": "Calm or train animals"},
    "arcana": {"ability": "Intelligence", "description": "Recall lore about spells, magic items, planes"},
    "athletics": {"ability": "Strength", "description": "Climb, jump, swim, or physical activities"},
    "deception": {"ability": "Charisma", "description": "Hide the truth with words or actions"},
    "history": {"ability": "Intelligence", "description": "Recall historical events, legends, and lore"},
    "insight": {"ability": "Wisdom", "description": "Determine true intentions of a creature"},
    "intimidation": {"ability": "Charisma", "description": "Influence through threats or hostility"},
    "investigation": {"ability": "Intelligence", "description": "Look for clues and make deductions"},
    "medicine": {"ability": "Wisdom", "description": "Stabilize dying companion or diagnose illness"},
    "nature": {"ability": "Intelligence", "description": "Recall lore about terrain, plants, animals"},
    "perception": {"ability": "Wisdom", "description": "Spot, hear, or detect presence of something"},
    "performance": {"ability": "Charisma", "description": "Delight an audience with music, dance, or acting"},
    "persuasion": {"ability": "Charisma", "description": "Influence with tact, social graces, or good nature"},
    "religion": {"ability": "Intelligence", "description": "Recall lore about deities, rites, prayers"},
    "sleight_of_hand": {"ability": "Dexterity", "description": "Pick pockets, conceal objects, perform tricks"},
    "stealth": {"ability": "Dexterity", "description": "Move silently and hide"},
    "survival": {"ability": "Wisdom", "description": "Track, hunt, navigate wilderness"}
}

# ============================================================================
# ALIGNMENT
# ============================================================================

DND_ALIGNMENTS = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil"
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_class_names():
    """Return list of all available class names."""
    return list(DND_CLASSES.keys())

def get_class_info(class_key):
    """Get detailed information about a specific class."""
    return DND_CLASSES.get(class_key.lower())

def get_all_species_names():
    """Return list of all available species names."""
    return list(DND_SPECIES.keys())

def get_species_info(species_key):
    """Get detailed information about a specific species."""
    return DND_SPECIES.get(species_key.lower())

def get_all_background_names():
    """Return list of all available background names."""
    return list(DND_BACKGROUNDS.keys())

def get_background_info(background_key):
    """Get detailed information about a specific background."""
    return DND_BACKGROUNDS.get(background_key.lower())

def calculate_ability_modifier(score):
    """Calculate ability score modifier: (score - 10) // 2"""
    return (score - 10) // 2

def get_proficiency_bonus(level):
    """Get proficiency bonus for a given character level."""
    return 2 + ((level - 1) // 4)

def format_modifier(modifier):
    """Format modifier as string with + or - sign."""
    return f"+{modifier}" if modifier >= 0 else str(modifier)
