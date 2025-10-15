"""
Prompt templates and configurations for AI-powered story generation.
"""

# Theme options for stories
THEMES = [
    "Fantasy",
    "Sci-Fi", 
    "Horror",
    "Mystery",
    "Romance",
    "Adventure",
    "Historical",
    "Contemporary",
    "Cyberpunk",
    "Steampunk",
    "Post-Apocalyptic",
    "Urban Fantasy",
    "Space Opera",
    "Western",
    "Noir",
    "Thriller",
    "Comedy",
    "Drama"
]

# Character personality traits
PERSONALITY_TRAITS = [
    "Brave",
    "Shy",
    "Witty",
    "Serious",
    "Energetic",
    "Calm",
    "Ambitious",
    "Humble",
    "Cunning",
    "Honest",
    "Loyal",
    "Rebellious",
    "Cautious",
    "Impulsive",
    "Charming",
    "Awkward",
    "Confident",
    "Insecure",
    "Optimistic",
    "Pessimistic",
    "Empathetic",
    "Cold",
    "Passionate",
    "Reserved",
    "Bold",
    "Nervous",
    "Charismatic",
    "Introverted",
    "Extroverted",
    "Analytical"
]

# Physical characteristics
PHYSICAL_TRAITS = [
    "Tall",
    "Short",
    "Athletic",
    "Frail",
    "Muscular",
    "Slender",
    "Scarred",
    "Elegant",
    "Rugged",
    "Youthful",
    "Weathered",
    "Striking",
    "Plain",
    "Intimidating",
    "Graceful",
    "Clumsy"
]

# Emotional traits
EMOTIONAL_TRAITS = [
    "Passionate",
    "Reserved",
    "Empathetic",
    "Cold",
    "Volatile",
    "Stable",
    "Anxious",
    "Confident",
    "Melancholic",
    "Cheerful",
    "Angry",
    "Serene",
    "Fearful",
    "Courageous"
]

# Story tones
TONES = [
    "Epic",
    "Dark",
    "Whimsical",
    "Gritty",
    "Lighthearted",
    "Mysterious",
    "Romantic",
    "Tense",
    "Comedic",
    "Tragic",
    "Hopeful",
    "Bleak",
    "Suspenseful",
    "Action-Packed",
    "Contemplative",
    "Satirical"
]

# Setting types
SETTINGS = [
    "Medieval",
    "Modern",
    "Futuristic",
    "Urban",
    "Rural",
    "Wilderness",
    "Underground",
    "Underwater",
    "Space",
    "Dimensional",
    "Desert",
    "Arctic",
    "Tropical",
    "Mountain",
    "Coastal",
    "Cityscape",
    "Village",
    "Castle",
    "Spaceship",
    "Space Station"
]

# Story lengths
STORY_LENGTHS = {
    "flash_fiction": "Flash Fiction (500-1000 words)",
    "short_story": "Short Story (3,000-7,500 words)",
    "novelette": "Novelette (7,500-20,000 words)",
    "novella": "Novella (20,000-50,000 words)",
    "novel": "Novel (50,000-110,000 words)",
    "campaign": "D&D Campaign (multiple sessions)",
    "one_shot": "One-Shot Adventure (single session)"
}

# Plot structures
PLOT_STRUCTURES = [
    "Hero's Journey",
    "Three-Act Structure",
    "Five-Act Structure",
    "Seven-Point Story",
    "Save the Cat",
    "Episodic",
    "Quest",
    "Coming of Age",
    "Redemption Arc",
    "Tragedy",
    "Rags to Riches",
    "Overcoming the Monster",
    "Rebirth"
]

# World-building elements
WORLD_ELEMENTS = [
    "Magic System",
    "Technology",
    "Politics",
    "Religion",
    "Economy",
    "Social Structure",
    "Geography",
    "Climate",
    "Flora and Fauna",
    "History",
    "Mythology",
    "Languages",
    "Culture",
    "Warfare",
    "Trade",
    "Architecture"
]

# Character archetypes
CHARACTER_ARCHETYPES = [
    "Hero",
    "Mentor",
    "Villain",
    "Anti-Hero",
    "Sidekick",
    "Trickster",
    "Guardian",
    "Herald",
    "Shapeshifter",
    "Shadow",
    "Everyman",
    "Innocent",
    "Explorer",
    "Sage",
    "Outlaw",
    "Magician",
    "Lover",
    "Jester",
    "Caregiver",
    "Ruler"
]

# Conflict types
CONFLICT_TYPES = [
    "Person vs. Person",
    "Person vs. Self",
    "Person vs. Society",
    "Person vs. Nature",
    "Person vs. Technology",
    "Person vs. Supernatural",
    "Person vs. Fate"
]


class PromptTemplates:
    """Templates for generating different story elements"""
    
    @staticmethod
    def character_prompt(themes=None, personality_traits=None, physical_traits=None, 
                        archetype=None, custom_details=None):
        """Generate a character creation prompt"""
        base = "Create a detailed, compelling character with the following attributes:\n\n"
        
        if themes:
            base += f"Genre/Theme: {', '.join(themes)}\n"
        if archetype:
            base += f"Archetype: {archetype}\n"
        if personality_traits:
            base += f"Personality Traits: {', '.join(personality_traits)}\n"
        if physical_traits:
            base += f"Physical Traits: {', '.join(physical_traits)}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please provide a comprehensive character profile including:
1. Name and age
2. Physical appearance (detailed description)
3. Personality (in-depth psychological profile)
4. Backstory (origin, key life events, formative experiences)
5. Motivations and goals (what drives them)
6. Fears and weaknesses (internal and external conflicts)
7. Strengths and abilities (skills, talents, powers if applicable)
8. Relationships (important connections to others)
9. Character arc potential (how they might grow/change)
10. Unique quirks or habits

Format the response as a well-structured character profile.
"""
        return base
    
    @staticmethod
    def story_prompt(themes=None, tone=None, length=None, plot_structure=None, 
                    conflict_type=None, custom_details=None):
        """Generate a story creation prompt"""
        base = "Create a compelling story outline with the following specifications:\n\n"
        
        if themes:
            base += f"Genre/Theme: {', '.join(themes)}\n"
        if tone:
            base += f"Tone: {', '.join(tone)}\n"
        if length:
            base += f"Length: {length}\n"
        if plot_structure:
            base += f"Plot Structure: {plot_structure}\n"
        if conflict_type:
            base += f"Main Conflict: {conflict_type}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please provide a comprehensive story outline including:
1. Title (compelling and thematic)
2. Premise (one-paragraph hook)
3. Setting (time, place, atmosphere)
4. Main Characters (brief descriptions of key players)
5. Plot Outline:
   - Opening/Hook
   - Rising Action (key plot points)
   - Climax (turning point)
   - Falling Action
   - Resolution
6. Themes and Subtext (deeper meanings)
7. Tone and Style notes
8. Potential Scenes (3-5 key scenes to develop)
9. Ending (satisfying conclusion)

Format the response as a detailed story outline ready for development.
"""
        return base
    
    @staticmethod
    def world_prompt(themes=None, setting=None, elements=None, custom_details=None):
        """Generate a world-building prompt"""
        base = "Design a rich, immersive world with the following characteristics:\n\n"
        
        if themes:
            base += f"Genre/Theme: {', '.join(themes)}\n"
        if setting:
            base += f"Setting Type: {', '.join(setting)}\n"
        if elements:
            base += f"Focus Elements: {', '.join(elements)}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please provide a comprehensive world description including:
1. World Name and Overview (high-level description)
2. Geography (continents, regions, notable locations)
3. Climate and Environment (weather patterns, ecosystems)
4. History (origin, major historical events, current era)
5. Cultures and Societies (different groups, customs, traditions)
6. Politics and Power Structures (governments, factions, conflicts)
7. Economy and Trade (resources, commerce, currency)
8. Magic/Technology Systems (how they work, limitations, impact on society)
9. Religion and Beliefs (deities, philosophies, spiritual practices)
10. Languages (major languages, writing systems)
11. Notable Locations (cities, landmarks, points of interest)
12. Flora and Fauna (unique creatures and plants)
13. Daily Life (what it's like for average inhabitants)

Format the response as a detailed world-building guide.
"""
        return base
    
    @staticmethod
    def scene_prompt(story_context=None, characters=None, setting=None, 
                    purpose=None, tone=None, custom_details=None):
        """Generate a scene creation prompt"""
        base = "Write a vivid, engaging scene with the following specifications:\n\n"
        
        if story_context:
            base += f"Story Context: {story_context}\n"
        if characters:
            base += f"Characters in Scene: {', '.join(characters)}\n"
        if setting:
            base += f"Setting: {setting}\n"
        if purpose:
            base += f"Scene Purpose: {purpose}\n"
        if tone:
            base += f"Tone: {', '.join(tone)}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please write a complete scene including:
1. Opening (establish setting and mood)
2. Character Actions and Dialogue (natural, meaningful interactions)
3. Sensory Details (sights, sounds, smells, textures)
4. Internal Thoughts (character perspective and emotions)
5. Tension or Conflict (drama, stakes, obstacles)
6. Character Development (reveal personality, relationships)
7. Plot Advancement (move story forward)
8. Closing (transition to next scene or moment)

Write the scene in prose format, suitable for a novel or narrative work.
"""
        return base
    
    @staticmethod
    def chapter_prompt(story_outline=None, chapter_number=None, previous_summary=None,
                      characters=None, plot_points=None, custom_details=None):
        """Generate a chapter creation prompt"""
        base = "Write a full chapter with the following specifications:\n\n"
        
        if chapter_number:
            base += f"Chapter Number: {chapter_number}\n"
        if story_outline:
            base += f"Story Outline: {story_outline}\n"
        if previous_summary:
            base += f"Previous Events: {previous_summary}\n"
        if characters:
            base += f"Characters: {', '.join(characters)}\n"
        if plot_points:
            base += f"Key Plot Points to Cover: {', '.join(plot_points)}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please write a complete chapter including:
1. Chapter Title (evocative and relevant)
2. Opening Hook (engaging first paragraph)
3. Scene Progression (2-4 scenes with smooth transitions)
4. Character Development (show growth, relationships, conflicts)
5. Dialogue (natural, purposeful conversations)
6. Description (vivid sensory details, atmosphere)
7. Plot Advancement (move story forward meaningfully)
8. Pacing (balance action, dialogue, description, reflection)
9. Tension and Stakes (maintain reader engagement)
10. Chapter Ending (satisfying close with forward momentum)

Write in a polished narrative style suitable for publication.
"""
        return base
    
    @staticmethod
    def location_prompt(world_context=None, location_type=None, importance=None,
                       themes=None, custom_details=None):
        """Generate a location creation prompt"""
        base = "Design a detailed, atmospheric location with the following specifications:\n\n"
        
        if world_context:
            base += f"World/Setting Context: {world_context}\n"
        if location_type:
            base += f"Location Type: {location_type}\n"
        if importance:
            base += f"Story Importance: {importance}\n"
        if themes:
            base += f"Themes: {', '.join(themes)}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please provide a comprehensive location description including:
1. Name and Overview (what is this place?)
2. Physical Description (architecture, landscape, size, layout)
3. Atmosphere and Mood (how does it feel?)
4. History (origin, past events, significance)
5. Current State (who lives/works here, current conditions)
6. Notable Features (landmarks, unique elements)
7. Inhabitants (who frequents this place?)
8. Sensory Details (sights, sounds, smells, textures)
9. Secrets or Hidden Elements (mysteries, discoveries)
10. Story Potential (how could this location be used in scenes?)

Format as a rich, evocative location profile.
"""
        return base
    
    @staticmethod
    def refinement_prompt(existing_content, refinement_instructions):
        """Generate a prompt for refining existing content"""
        return f"""Here is existing content that needs refinement:

{existing_content}

Please refine this content according to the following instructions:
{refinement_instructions}

Maintain the core essence and structure, but improve, expand, or adjust based on the instructions provided. Return the complete refined version.
"""
    
    @staticmethod
    def campaign_prompt(themes=None, tone=None, session_count=None, 
                       player_count=None, level_range=None, custom_details=None):
        """Generate a D&D campaign creation prompt"""
        base = "Design a complete D&D campaign with the following specifications:\n\n"
        
        if themes:
            base += f"Themes: {', '.join(themes)}\n"
        if tone:
            base += f"Tone: {', '.join(tone)}\n"
        if session_count:
            base += f"Expected Sessions: {session_count}\n"
        if player_count:
            base += f"Player Count: {player_count}\n"
        if level_range:
            base += f"Level Range: {level_range}\n"
        if custom_details:
            base += f"\nAdditional Requirements: {custom_details}\n"
        
        base += """
Please provide a comprehensive campaign outline including:
1. Campaign Title and Premise
2. World Overview (setting, major locations)
3. Main Story Arc (beginning, middle, end)
4. Major NPCs (allies, villains, neutrals)
5. Key Locations (dungeons, cities, wilderness)
6. Session Breakdown:
   - Session hooks and objectives
   - Expected encounters
   - Story beats
   - Treasure and rewards
7. Plot Twists and Reveals
8. Side Quests and Optional Content
9. Final Confrontation (epic climax)
10. Campaign Themes and Tone
11. DM Notes and Tips
12. Possible Player Choices and Consequences

Format as a complete campaign guide ready for a DM to run.
"""
        return base
    
    @staticmethod
    def character_structured_prompt(themes=None, personality_traits=None, physical_traits=None,
                                    archetype=None, custom_details=None):
        """Generate a character creation prompt optimized for structured CharacterProfile output.
        
        This prompt is designed to work with structured output schemas to guarantee all fields
        are populated with concrete, specific details. It emphasizes completeness and avoids
        vague descriptions.
        """
        base = "Create a COMPLETE, highly detailed character with specific, concrete details for EVERY field.\n\n"
        base += "CRITICAL INSTRUCTIONS:\n"
        base += "- Fill ALL fields completely - no omissions or vague placeholders\n"
        base += "- Use SPECIFIC details: exact measurements, precise descriptions, concrete examples\n"
        base += "- Example: '6 feet 5 inches' NOT 'tall'; 'jagged scar across left cheek' NOT 'scarred'\n"
        base += "- For lists, provide 3-5 specific items minimum\n"
        base += "- For descriptions, write 2-3 complete, detailed sentences minimum\n\n"
        
        if themes:
            base += f"Genre/Theme: {', '.join(themes)}\n"
        if archetype:
            base += f"Archetype: {archetype}\n"
        if personality_traits:
            base += f"Desired Personality Traits: {', '.join(personality_traits)}\n"
        if physical_traits:
            base += f"Desired Physical Traits: {', '.join(physical_traits)}\n"
        if custom_details:
            base += f"\nAdditional Specific Requirements: {custom_details}\n"
        
        base += """

REQUIRED FIELDS TO COMPLETE (all must be filled with specific details):

**BASIC IDENTITY:**
- Name: Full name with meaning/origin
- Age: Exact age (not a range)

**PHYSICAL APPEARANCE:**
- Height: Precise measurement (e.g., "5'9\"", "178 cm")
- Build: Specific body type with details (e.g., "lean and wiry with defined muscles", "stocky with broad shoulders")
- Hair: Complete description (color, length, style, texture, any distinctive features)
- Eyes: Specific color and notable characteristics (e.g., "piercing green with gold flecks", "deep brown with laugh lines")
- Distinctive Features: List 3-5 unique physical traits (scars, tattoos, birthmarks, mannerisms)
- Physical Description: 2-3 sentences synthesizing overall appearance and impression

**PERSONALITY:**
- Personality Traits: List 4-6 core traits with brief explanations
- Demeanor: How they present themselves to the world (2-3 sentences)
- Sense of Humor: Specific type and examples (dark, dry, slapstick, etc.)
- Personality Description: 3-4 sentences on psychological depth

**BACKGROUND:**
- Birthplace: Specific location with context
- Upbringing: 2-3 sentences on childhood and family situation
- Formative Events: List 2-4 key life events that shaped them
- Backstory: 3-5 sentences on their full life story

**MOTIVATIONS:**
- Primary Motivation: What drives them above all else (1-2 sentences)
- Goals: List 3-5 specific short and long-term goals
- Values: List 3-5 core values they hold dear

**FEARS AND WEAKNESSES:**
- Greatest Fear: Specific deep-seated fear with explanation
- Emotional Weaknesses: List 2-4 psychological vulnerabilities
- Physical Weaknesses: List 2-4 physical limitations or vulnerabilities

**STRENGTHS AND ABILITIES:**
- Skills: List 4-6 specific skills with proficiency levels
- Special Abilities: Any unique talents, powers, or expertise (or "None" if ordinary human)
- Combat Style: How they handle conflict (physical, verbal, or otherwise)
- Strengths Description: 2-3 sentences on what makes them formidable

**RELATIONSHIPS:**
- Key Relationships: List 3-5 important people with relationship descriptions
  Each relationship should include: name, relationship type, and 1-2 sentence description

**CHARACTER DEVELOPMENT:**
- Character Arc Potential: 2-4 sentences on how they might grow, change, or be challenged

**UNIQUE QUALITIES:**
- Unique Qualities: 2-3 sentences on what makes them truly distinct and memorable
- Quirks and Habits: List 3-5 specific behavioral quirks, habits, or mannerisms

REMEMBER: Every field must be completed with concrete, specific details. No vague descriptions, no placeholders, no omissions.
"""
        return base
    
    @staticmethod
    def world_structured_prompt(themes=None, setting=None, elements=None, custom_details=None):
        """Generate a world-building prompt optimized for structured WorldProfile output.
        
        This prompt is designed to work with structured output schemas to guarantee all fields
        are populated with rich, immersive details. It emphasizes comprehensive worldbuilding.
        """
        base = "Create a COMPLETE, richly detailed world with specific, immersive details for EVERY field.\n\n"
        base += "CRITICAL INSTRUCTIONS:\n"
        base += "- Fill ALL fields completely - no omissions or generic placeholders\n"
        base += "- Use VIVID, specific details that bring the world to life\n"
        base += "- For lists, provide 3-6 specific items minimum with descriptions\n"
        base += "- For summaries, write 3-5 complete, engaging sentences minimum\n"
        base += "- Make the world feel alive, consistent, and immersive\n\n"
        
        if themes:
            base += f"Genre/Theme: {', '.join(themes)}\n"
        if setting:
            base += f"Setting Type: {', '.join(setting)}\n"
        if elements:
            base += f"Focus Elements: {', '.join(elements)}\n"
        if custom_details:
            base += f"\nAdditional Specific Requirements: {custom_details}\n"
        
        base += """

REQUIRED FIELDS TO COMPLETE (all must be filled with specific details):

**WORLD OVERVIEW:**
- Name: Evocative world name with meaning
- World Type: Classification (fantasy, sci-fi, post-apocalyptic, etc.)
- Tagline: Compelling one-sentence hook that captures the essence
- Overview: 3-4 sentences on what makes this world unique and interesting

**HISTORY:**
- Age: How old is this world/civilization? (e.g., "ancient - over 10,000 years", "young colony - 200 years")
- Origin Story: 2-3 sentences on how this world/civilization came to be
- Major Historical Events: List 4-6 pivotal events with dates/eras and descriptions
  Each event: {"event": "name", "era": "when", "description": "what happened"}
- Current Era: Name and description of the present time period
- History Summary: 3-4 sentences synthesizing the historical arc

**GEOGRAPHY:**
- Size and Scale: Specific dimensions or scope (continent, planet, galaxy, pocket dimension, etc.)
- Climate Zones: List 3-5 distinct climate regions with characteristics
- Major Regions: List 4-6 key regions/territories with brief descriptions
  Each region: {"name": "region name", "description": "key features"}
- Natural Wonders: List 3-5 spectacular natural landmarks or phenomena
- Geography Summary: 3-4 sentences on the physical world and how it shapes life

**CULTURE AND SOCIETY:**
- Dominant Species: What intelligent beings inhabit this world?
- Population Estimate: Rough population size and distribution
- Major Civilizations: List 3-5 distinct cultures/nations with descriptions
  Each civilization: {"name": "culture name", "description": "key characteristics"}
- Languages: List 3-4 major languages with characteristics
- Religions and Beliefs: List 2-4 faiths/philosophies with core tenets
- Cultural Norms: List 4-6 social customs, traditions, or taboos
- Culture Summary: 4-5 sentences on social life and cultural diversity

**MAGIC/TECHNOLOGY SYSTEM:**
- Power System: What drives this world? (magic, technology, psionics, divine power, etc.)
- Power Level: How prevalent/powerful? (rare and weak, common and moderate, omnipresent and godlike)
- Limitations: What are the rules, costs, or restrictions?
- Notable Artifacts: List 3-5 legendary items, inventions, or relics

**CONFLICTS AND THEMES:**
- Major Conflicts: List 3-4 current wars, tensions, or struggles
- Central Themes: What are the core ideas this world explores?
- Current Threats: What dangers loom over this world?

**LORE AND MYSTERIES:**
- Legends and Myths: 2-3 famous stories passed down through generations
- Unsolved Mysteries: 2-3 enigmas that intrigue inhabitants
- Prophecies: Any foretold destinies or predictions (or "None known")
- Lore Summary: 3-4 sentences on the mystique and deeper lore

**STORY POTENTIAL:**
- Adventure Hooks: List 4-6 compelling story ideas or quest possibilities
- Notable Locations: List 5-8 specific places of interest with descriptions
  Each location: {"name": "place name", "type": "location type", "description": "what makes it notable"}
- Unique Aspects: 3-4 sentences on what makes this world perfect for storytelling

REMEMBER: Every field must be completed with rich, immersive details. Make the world feel real, consistent, and captivating.
"""
        return base
