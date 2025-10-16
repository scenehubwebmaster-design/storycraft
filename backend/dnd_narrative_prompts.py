"""
D&D Character Narrative Prompt System

Modular, context-aware prompts for generating specific character aspects
informed by D&D 5E stats, class, species, background, and alignment.
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class NarrativeStyle(str, Enum):
    """Narrative generation styles"""
    CONCISE = "concise"
    DETAILED = "detailed"
    DRAMATIC = "dramatic"
    POETIC = "poetic"
    GRITTY = "gritty"


class NarrativeAspect(str, Enum):
    """Character narrative aspects that can be generated"""
    APPEARANCE = "appearance"
    PERSONALITY = "personality"
    BACKSTORY = "backstory"
    MOTIVATIONS = "motivations"
    QUIRKS = "quirks"
    VOICE = "voice"
    BELIEFS = "beliefs"
    RELATIONSHIPS = "relationships"
    FEARS = "fears"
    DREAMS = "dreams"
    SECRETS = "secrets"
    NAME = "name"


class DnDNarrativePromptBuilder:
    """
    Builds context-aware prompts for D&D character narrative generation.
    Each prompt is informed by the character's mechanical stats.
    """
    
    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize with character data from D&D generation.
        
        Args:
            character_data: Dict containing D&D character stats
        """
        self.character = character_data
        self.class_name = character_data.get("dnd_class", "unknown")
        self.species = character_data.get("dnd_species", "unknown")
        self.background = character_data.get("dnd_background", "unknown")
        self.alignment = character_data.get("dnd_alignment", "True Neutral")
        self.level = character_data.get("dnd_level", 1)
        self.abilities = character_data.get("dnd_ability_scores", {})
        
    def get_base_context(self) -> str:
        """Generate base context string used in all prompts"""
        ability_summary = self._get_ability_summary()
        
        return f"""
D&D 5E Character Context:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Class: {self.class_name.title()}
Species: {self.species.title()}
Background: {self.background.title()}
Alignment: {self.alignment}
Level: {self.level}

Ability Scores:
{ability_summary}

Physical Traits: {self._get_physical_traits()}
Mental Traits: {self._get_mental_traits()}
Social Traits: {self._get_social_traits()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _get_ability_summary(self) -> str:
        """Format ability scores with modifiers"""
        scores = []
        for ability in ["strength", "dexterity", "constitution", 
                       "intelligence", "wisdom", "charisma"]:
            score = self.abilities.get(ability, 10)
            modifier = (score - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            scores.append(f"  {ability.upper()[:3]}: {score} ({mod_str})")
        return "\n".join(scores)
    
    def _get_physical_traits(self) -> str:
        """Infer physical traits from STR, DEX, CON"""
        str_score = self.abilities.get("strength", 10)
        dex_score = self.abilities.get("dexterity", 10)
        con_score = self.abilities.get("constitution", 10)
        
        traits = []
        if str_score >= 16:
            traits.append("Muscular")
        elif str_score <= 8:
            traits.append("Slight build")
        
        if dex_score >= 16:
            traits.append("Agile")
        elif dex_score <= 8:
            traits.append("Clumsy")
        
        if con_score >= 16:
            traits.append("Hardy")
        elif con_score <= 8:
            traits.append("Frail")
        
        return ", ".join(traits) if traits else "Average"
    
    def _get_mental_traits(self) -> str:
        """Infer mental traits from INT, WIS"""
        int_score = self.abilities.get("intelligence", 10)
        wis_score = self.abilities.get("wisdom", 10)
        
        traits = []
        if int_score >= 16:
            traits.append("Brilliant")
        elif int_score <= 8:
            traits.append("Simple")
        
        if wis_score >= 16:
            traits.append("Perceptive")
        elif wis_score <= 8:
            traits.append("Oblivious")
        
        return ", ".join(traits) if traits else "Average"
    
    def _get_social_traits(self) -> str:
        """Infer social traits from CHA"""
        cha_score = self.abilities.get("charisma", 10)
        
        if cha_score >= 16:
            return "Charismatic, magnetic presence"
        elif cha_score <= 8:
            return "Awkward, off-putting"
        else:
            return "Unremarkable"
    
    def build_prompt(
        self,
        aspect: NarrativeAspect,
        style: NarrativeStyle = NarrativeStyle.DETAILED,
        custom_context: Optional[str] = None,
        length: str = "3-4 sentences"
    ) -> str:
        """
        Build a prompt for generating a specific narrative aspect.
        
        Args:
            aspect: Which narrative aspect to generate
            style: Writing style for the generation
            custom_context: Additional user-provided context
            length: Desired output length
            
        Returns:
            Complete prompt string
        """
        base = self.get_base_context()
        
        if custom_context:
            base += f"\nAdditional Context: {custom_context}\n"
        
        aspect_prompts = {
            NarrativeAspect.APPEARANCE: self._appearance_prompt,
            NarrativeAspect.PERSONALITY: self._personality_prompt,
            NarrativeAspect.BACKSTORY: self._backstory_prompt,
            NarrativeAspect.MOTIVATIONS: self._motivations_prompt,
            NarrativeAspect.QUIRKS: self._quirks_prompt,
            NarrativeAspect.VOICE: self._voice_prompt,
            NarrativeAspect.BELIEFS: self._beliefs_prompt,
            NarrativeAspect.RELATIONSHIPS: self._relationships_prompt,
            NarrativeAspect.FEARS: self._fears_prompt,
            NarrativeAspect.DREAMS: self._dreams_prompt,
            NarrativeAspect.SECRETS: self._secrets_prompt,
            NarrativeAspect.NAME: self._name_prompt,
        }
        
        specific_prompt = aspect_prompts[aspect](style, length)
        
        return f"{base}\n{specific_prompt}"
    
    def _appearance_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate a vivid physical appearance description for this D&D character.

REQUIREMENTS:
- Consider species-specific traits (size, features, coloring)
- Reflect STR, DEX, CON in body build and physical presence
- Include CHA in overall attractiveness and magnetism
- Mention distinctive marks, scars, or unique features
- Describe typical clothing/armor style appropriate to class
- Account for background influences (e.g., soldier bearing, sage's bookishness)

STYLE: {style.value}
LENGTH: {length}

Generate the appearance description now:"""

    def _personality_prompt(self, style: NarrativeStyle, length: str) -> str:
        alignment_traits = self._get_alignment_traits()
        return f"""
TASK: Generate a rich personality profile for this D&D character.

REQUIREMENTS:
- Alignment ({self.alignment}) should strongly influence core values: {alignment_traits}
- High INT characters are analytical, curious, strategic
- High WIS characters are insightful, cautious, empathetic
- High CHA characters are confident, persuasive, socially adept
- Low scores create opposite tendencies
- Background shapes worldview ({self.background})
- Class influences outlook (e.g., clerics are faithful, rogues are cunning)

STYLE: {style.value}
LENGTH: {length}

Generate the personality description now:"""

    def _backstory_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate a compelling backstory for this D&D character.

REQUIREMENTS:
- Explain how they gained their background ({self.background})
- Describe their class training origin and mentors
- Include formative experiences that shaped alignment ({self.alignment})
- Mention species/cultural influences on upbringing
- Explain why they became an adventurer at level {self.level}
- Include 1-2 key relationships (mentor, rival, loved one)
- Reference one unresolved past event that drives them

STYLE: {style.value}
LENGTH: 4-6 sentences

Generate the backstory now:"""

    def _motivations_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate clear motivations and goals for this D&D character.

REQUIREMENTS:
- Primary long-term goal (what they ultimately seek)
- Short-term objectives (immediate concerns)
- Personal desires influenced by alignment ({self.alignment})
- Professional aspirations related to class advancement
- 1-2 fears or concerns that complicate their goals
- How background ({self.background}) drives their ambitions

STYLE: {style.value}
LENGTH: {length}

Generate the motivations now:"""

    def _quirks_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate memorable quirks, habits, and mannerisms for this D&D character.

REQUIREMENTS:
- 2-3 distinctive behavioral quirks
- Speech patterns or catchphrases
- Nervous habits or tics (especially for low WIS/CHA)
- Unique preferences or obsessions
- Body language traits
- How they react under stress (combat, social, etc.)
- Species-influenced behaviors

STYLE: {style.value}
FORMAT: Bullet list of 2-3 specific, memorable quirks

Generate the quirks now:"""

    def _voice_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate a distinctive voice and speaking style for this D&D character.

REQUIREMENTS:
- Speech patterns (formal, casual, eloquent, crude)
- Vocabulary level (reflects INT score)
- Accent or dialect (species/background influence)
- Common phrases or expressions
- How CHA affects persuasiveness and charisma in speech
- Vocal qualities (tone, pitch, volume)

STYLE: {style.value}
LENGTH: {length}

Generate the voice description now:"""

    def _beliefs_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate core beliefs and values for this D&D character.

REQUIREMENTS:
- Moral code driven by alignment ({self.alignment})
- Religious or spiritual views (especially for clerics/paladins)
- Political leanings
- Views on law, chaos, good, evil
- Personal philosophy about life and death
- Cultural/species beliefs they hold or reject

STYLE: {style.value}
LENGTH: {length}

Generate the beliefs now:"""

    def _relationships_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate key relationships for this D&D character.

REQUIREMENTS:
- 1-2 important past relationships (family, mentor, rival)
- Current relationship status and desires
- How CHA affects their social connections
- Background-influenced connections ({self.background})
- One relationship that could become a plot hook
- Attitudes toward different groups (nobility, commoners, other species)

STYLE: {style.value}
LENGTH: {length}

Generate the relationships now:"""

    def _fears_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate fears and vulnerabilities for this D&D character.

REQUIREMENTS:
- 1-2 deep-seated fears or phobias
- Insecurities (especially for low-score abilities)
- What they stand to lose
- Moral boundaries they fear crossing
- How alignment affects their fears
- One fear that could be exploited by enemies

STYLE: {style.value}
LENGTH: 2-3 sentences

Generate the fears now:"""

    def _dreams_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate dreams and aspirations for this D&D character.

REQUIREMENTS:
- Ultimate life goal or dream
- Ideal future they envision
- Legacy they want to leave
- How class advancement fits into their dreams
- Alignment-appropriate aspirations
- One "impossible dream" that drives them

STYLE: {style.value}
LENGTH: {length}

Generate the dreams now:"""

    def _secrets_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate secrets and hidden aspects for this D&D character.

REQUIREMENTS:
- 1-2 secrets they actively hide
- Past mistakes or regrets
- Hidden knowledge or abilities
- Dual identities or false backgrounds
- Something that could change how others view them
- How their alignment complicates their secrets

STYLE: {style.value}
LENGTH: {length}

Generate the secrets now:"""

    def _name_prompt(self, style: NarrativeStyle, length: str) -> str:
        return f"""
TASK: Generate an appropriate name for this D&D character.

REQUIREMENTS:
- Species-appropriate naming conventions for {self.species}
- Reflects background ({self.background}) and social status
- Consider cultural origins
- If {self.class_name}, might have a title or epithet
- Alignment may influence name choice (e.g., dark names for evil)
- Generate: First name, surname (if appropriate), and optional title/nickname

FORMAT: Provide name with brief explanation of its meaning or origin

Generate the name now:"""

    def _get_alignment_traits(self) -> str:
        """Get personality traits associated with alignment"""
        alignment_map = {
            "Lawful Good": "honorable, principled, compassionate",
            "Neutral Good": "kind, helpful, balanced",
            "Chaotic Good": "free-spirited, rebellious, altruistic",
            "Lawful Neutral": "orderly, disciplined, impartial",
            "True Neutral": "balanced, pragmatic, adaptable",
            "Chaotic Neutral": "unpredictable, independent, self-interested",
            "Lawful Evil": "tyrannical, manipulative, ruthless within rules",
            "Neutral Evil": "selfish, opportunistic, amoral",
            "Chaotic Evil": "destructive, sadistic, anarchistic",
        }
        return alignment_map.get(self.alignment, "complex moral code")


def generate_all_prompts(
    character_data: Dict[str, Any],
    style: NarrativeStyle = NarrativeStyle.DETAILED,
    aspects: Optional[List[NarrativeAspect]] = None
) -> Dict[str, str]:
    """
    Generate all narrative prompts for a character.
    
    Args:
        character_data: D&D character data dict
        style: Narrative style to use
        aspects: List of aspects to generate (default: all common aspects)
        
    Returns:
        Dict mapping aspect names to prompt strings
    """
    if aspects is None:
        aspects = [
            NarrativeAspect.APPEARANCE,
            NarrativeAspect.PERSONALITY,
            NarrativeAspect.BACKSTORY,
            NarrativeAspect.MOTIVATIONS,
            NarrativeAspect.QUIRKS,
        ]
    
    builder = DnDNarrativePromptBuilder(character_data)
    prompts = {}
    
    for aspect in aspects:
        prompts[aspect.value] = builder.build_prompt(aspect, style)
    
    return prompts


# Example usage
if __name__ == "__main__":
    # Test character data
    test_character = {
        "name": "Eldrin Starweaver",
        "dnd_class": "wizard",
        "dnd_species": "elf",
        "dnd_background": "sage",
        "dnd_alignment": "Neutral Good",
        "dnd_level": 1,
        "dnd_ability_scores": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 15,
            "wisdom": 13,
            "charisma": 10,
        },
    }
    
    builder = DnDNarrativePromptBuilder(test_character)
    
    # Generate appearance prompt
    appearance_prompt = builder.build_prompt(
        NarrativeAspect.APPEARANCE,
        NarrativeStyle.DETAILED
    )
    
    print("APPEARANCE PROMPT:")
    print("=" * 80)
    print(appearance_prompt)
    print("\n")
    
    # Generate all common prompts
    all_prompts = generate_all_prompts(test_character, NarrativeStyle.DRAMATIC)
    
    print("ALL NARRATIVE PROMPTS:")
    print("=" * 80)
    for aspect, prompt in all_prompts.items():
        print(f"\n{aspect.upper()}:")
        print("-" * 80)
        print(prompt[:300], "...\n")


def build_dnd_narrative_prompt(
    dnd_character: Dict[str, Any],
    style: str = "detailed",
    additional_context: Optional[str] = None
) -> str:
    """
    Build a comprehensive prompt for structured D&D character narrative generation.
    
    This function creates a single prompt that will generate all narrative aspects
    using the DnDCharacterNarrative schema structure.
    
    Args:
        dnd_character: Complete D&D character data from generator
        style: Narrative style (concise, detailed, dramatic)
        additional_context: Optional additional context from user
        
    Returns:
        Comprehensive prompt string for structured narrative generation
    """
    builder = DnDNarrativePromptBuilder(dnd_character)
    
    # Convert style string to enum
    try:
        style_enum = NarrativeStyle(style)
    except ValueError:
        style_enum = NarrativeStyle.DETAILED
    
    # Get base context
    base_context = builder.get_base_context()
    
    # Build comprehensive prompt for all narrative aspects
    prompt = f"""{base_context}

Generate a comprehensive, structured narrative profile for this D&D 5E character.
The narrative should fully integrate their mechanical stats, species traits, class features, 
and background into cohesive storytelling elements.

NARRATIVE STYLE: {style_enum.value}

IMPORTANT SPECIES-SPECIFIC CONSIDERATIONS:
"""

    # Add species-specific guidance
    species = dnd_character.get("species", "").lower()
    
    if "dragonborn" in species:
        prompt += """
- DRAGONBORN: This character is a wingless, bipedal dragon with draconic features
- Describe their scale coloration matching their draconic ancestry
- Mention their horns, thick-boned structure, bright eyes, and imposing presence
- Include how their breath weapon (Cone or Line attack) manifests in combat
- Reference their damage resistance to their ancestry's element
- At level 5+: Describe how they manifest spectral draconic wings for flight
- Consider draconic behaviors: formal speech, territorial instincts, honor-bound nature
- Connection to dragon progenitors (Bahamut/Tiamat legends)
"""
    elif "elf" in species:
        prompt += """
- ELF: Emphasize grace, longevity perspective, keen senses, and connection to nature/magic
- Describe their elegant features, pointed ears, and ageless appearance
"""
    elif "dwarf" in species:
        prompt += """
- DWARF: Emphasize stout build, resilience, craftsmanship appreciation, and clan connections
- Describe their robust frame, distinctive beard/facial features, and sturdy presence
"""
    elif "halfling" in species:
        prompt += """
- HALFLING: Emphasize small stature, lucky nature, courage, and community bonds
- Describe their diminutive but nimble form, cheerful demeanor, and practical nature
"""
    else:
        prompt += f"""
- {species.upper()}: Incorporate appropriate species traits and characteristics
- Reflect their unique racial abilities and cultural background
"""
    
    # Add class-specific guidance
    char_class = dnd_character.get("class", "").lower()
    if char_class in ["wizard", "sorcerer", "warlock"]:
        prompt += f"""
- {char_class.upper()}: Weave their magical abilities into combat style and personality
- Describe how they channel magical energy and their relationship with arcane forces
"""
    elif char_class in ["fighter", "barbarian", "paladin"]:
        prompt += f"""
- {char_class.upper()}: Emphasize martial prowess, combat training, and physical conditioning
- Describe their fighting technique and warrior bearing
"""
    elif char_class in ["rogue", "ranger"]:
        prompt += f"""
- {char_class.upper()}: Highlight stealth, skill expertise, and tactical thinking
- Describe their cautious approach and sharp observational skills
"""
    elif char_class == "cleric":
        prompt += """
- CLERIC: Balance divine faith with practical healing/combat abilities
- Describe their spiritual connection and how their deity influences them
"""
    elif char_class == "bard":
        prompt += """
- BARD: Showcase their charisma, artistic talents, and Jack-of-all-trades versatility
- Describe their performance style and how they inspire others
"""
    elif char_class == "monk":
        prompt += """
- MONK: Emphasize discipline, ki energy manipulation, and martial arts philosophy
- Describe their centered demeanor and fluid combat movements
"""
    elif char_class == "druid":
        prompt += """
- DRUID: Highlight connection to nature, Wild Shape abilities, and primal magic
- Describe their attunement to natural cycles and wild places
"""
    
    prompt += f"""

ABILITY SCORE INTERPRETATION:
{builder._get_ability_summary()}

Physical: {builder._get_physical_traits()}
Mental: {builder._get_mental_traits()}
Social: {builder._get_social_traits()}

REQUIRED NARRATIVE ELEMENTS:

1. PHYSICAL APPEARANCE (3-5 sentences):
   - Full physical description incorporating species traits
   - Build reflecting ability scores (STR, DEX, CON, CHA)
   - Distinctive features unique to this character
   - Clothing/armor style appropriate to class and background
   - Overall presence and first impression they make

2. PERSONALITY & DEMEANOR:
   - Core personality traits (3-5 traits) reflecting alignment and background
   - Ideals shaped by background and alignment
   - Bonds (relationships, connections, loyalties)
   - Flaws (weaknesses that create drama and depth)
   - Overall behavioral patterns and social tendencies

3. BACKSTORY (4-7 sentences):
   - Origins and upbringing reflecting background
   - How they gained their class training
   - Formative events (2-4 specific events) that shaped them
   - Key relationships from their past
   - Path that led them to become an adventurer
   - Connection to species culture/society

4. MOTIVATIONS & GOALS:
   - Primary motivation for adventuring
   - Short-term goals (2-3 immediate objectives)
   - Long-term goals (1-2 overarching ambitions)
   - Fears and concerns

5. QUIRKS & MANNERISMS (2-4 items):
   - Unique habits reflecting species and background
   - Speech patterns and communication style
   - Memorable behavioral quirks

6. COMBAT STYLE & SIGNATURE ABILITIES:
   - Narrative description of fighting approach
   - Signature abilities in story form (MUST include racial abilities like breath weapon)
   - How they use class features creatively

7. SOCIAL IDENTITY:
   - How others perceive them
   - Reputation and social standing
   - Key allies, rivals, or enemies

8. CHARACTER DEVELOPMENT:
   - Potential for growth and change
   - Internal conflicts
   - Story arc opportunities
"""
    
    if additional_context:
        prompt += f"""

ADDITIONAL CONTEXT:
{additional_context}
"""
    
    prompt += """

Generate a complete, cohesive narrative profile that brings this character to life as a 
fully-realized individual, not just a collection of stats. Make them memorable, complex, 
and ready for epic adventures!
"""
    
    return prompt

