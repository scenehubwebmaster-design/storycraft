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

ADDITIONAL DIVERSITY GUIDANCE (MANDATORY):
- For `skin`, `eyes`, and `hair` produce highly specific, non-repeating descriptors. Do not use the same phrasing across characters.
  • Skin: combine tone, texture, and unique marks. Prefer concrete, varied descriptors (e.g. "russet skin weathered by sun and salt, with a crescent pale scar along the jaw", "deep umber with fine, silvery tattoos trailing from the temple", "pale, almost translucent skin flecked with tiny burn scars"). Avoid vague or overused phrases.
  • Eyes: use patterns, textures, or anomalies (heterochromia, flecks, ringed irises, catlike pupils). Examples: "sea-glass green with a molten-gold ring", "amber eyes streaked with a coal-black vein", "one eye clouded like old glass".
  • Hair / crests / frills: describe cut, texture, cultural styling, and accents (threaded beads, dye streaks, shaved patterns). Examples: "warrior braids threaded with brass beads", "ashy topknot streaked with copper from years at sea".

- Tie at least one micro-detail to class or background (soldiers: service scars, chaplains: ritual tattoos, sailors: salt-bleached tips, scholars: ink faint on fingers).
- When possible, include a single unique marker per character (birthmark, ritual scar, tiny rune) to make descriptions easy to distinguish in lists of characters.

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
        # Updated prompt: ask for multiple, distinct options and explicit formatting
        return f"""
TASK: Generate 6 distinct and culturally appropriate name options for this D&D character.

REQUIREMENTS:
- Produce 6 options that are clearly different from each other (avoid reusing the same stem or obvious variations like "Thaleon" / "Thorne").
- Each option should follow species-appropriate naming conventions for {self.species} and reflect background ({self.background}) and social status when relevant.
- Consider cultural origins and phonetic variety (e.g., short/long names, soft/hard consonants, vowel-heavy vs consonant-heavy).
- If the character's class ({self.class_name}) commonly has titles or epithets, include 1 option that features an epithet/title.
- Aim for diversity across syllable structure, rhythm, and consonant/vowel patterns.
- For each option provide very short metadata: (1) whether the name is suitable for a formal address, (2) probable cultural origin or style, and (3) a 6-10 word etymology/meaning.

FORMAT (strict):
- Return a JSON array of 6 objects. Each object must contain exactly these keys: `first_name`, `surname` (use empty string if not applicable), `title` (use empty string if none), `formal` (true/false), `origin`, `meaning`.

Example:
[
    {{"first_name":"Eira","surname":"Valen","title":"","formal":true,"origin":"Northern coastal dialect","meaning":"Sea-born, swift and steady"}},
    ... (5 more objects)
]

IMPORTANT: Do not return a single combined string or conversational text — return only the JSON array so the calling code can parse it reliably.

Generate the 6 name options now:"""

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
    
    Aligned with official D&D 5E character sheet sections. Generates storytelling
    "flavor" elements that complement mechanical stats without duplicating them.
    
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
    species = dnd_character.get("dnd_species", "Human").title()
    char_class = dnd_character.get("dnd_class", "Fighter").title()
    background = dnd_character.get("dnd_background", "Folk Hero").title()
    alignment = dnd_character.get("dnd_alignment", "Neutral")
    
    # Build comprehensive prompt for all narrative aspects
    prompt = f"""{base_context}

═══════════════════════════════════════════════════════════════════════════
D&D 5E CHARACTER NARRATIVE GENERATION
Official Character Sheet Format
═══════════════════════════════════════════════════════════════════════════

Generate a comprehensive, immersive narrative profile for a {species} {char_class}.
Focus on STORYTELLING FLAVOR that brings the character to life while avoiding
duplication of mechanical stats (HP, AC, abilities, etc.).

NARRATIVE STYLE: {style_enum.value}

SPECIES-SPECIFIC GUIDANCE:
"""

    # If the incoming character dict contains explicit fields (name, class, species, level,
    # or short appearance text), signal to the model that these are authoritative and must
    # not be altered. Prefer and expand any provided descriptive text rather than overwriting it.
    provided_fields = {
        "name": dnd_character.get("name") or dnd_character.get("character_name") or dnd_character.get("character_name"),
        "class": dnd_character.get("dnd_class"),
        "species": dnd_character.get("dnd_species"),
        "level": dnd_character.get("dnd_level"),
        "appearance": dnd_character.get("character_appearance") or dnd_character.get("appearance") or dnd_character.get("description"),
    }

    # Build an immutable-fields section the model must obey
    immutable_lines = []
    for k in ("name", "class", "species", "level"):
        v = provided_fields.get(k)
        if v:
            immutable_lines.append(f"- {k}: {v}")

    if immutable_lines:
        prompt += "\nINPUT-PROVIDED FIELDS (TREAT AS AUTHORITATIVE):\n"
        prompt += "\n" + "\n".join(immutable_lines) + "\n\n"
        prompt += (
            "IMPORTANT: Preserve the provided fields above exactly. Do NOT change the character's name, class,\n"
            "species, or level. You may enrich and elaborate on appearance, backstory, and personality, but do not\n"
            "contradict or overwrite any explicit input. If an 'appearance' or 'description' field is provided,\n"
            "integrate and expand that text rather than replacing it.\n\n"
        )

        # Provide a short example to make the rule concrete
        prompt += (
            "EXAMPLE: If input contains: name=Kaelin Valtor, species=Goliath, class=Barbarian, level=1\n"
            "→ DO NOT invent a different name, class, species, or level. Expand on Kaelin's supplied details.\n\n"
        )

    # Add species-specific guidance
    species_lower = species.lower()
    
    if "dragonborn" in species_lower:
        prompt += """
🐉 DRAGONBORN - Proud Dragon-Blooded Warriors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Wingless bipedal dragons with draconic features
  - Scales matching draconic ancestry (brass, bronze, copper, gold, silver, red, etc.)
  - Distinctive horns, thick-boned build, bright reptilian eyes
  - No hair (may have decorative crests or frills)
  - Imposing, powerful presence

Cultural Elements:
  - Clan-based society with strong honor codes
  - Connection to dragon progenitors (Bahamut for good, Tiamat for evil)
  - Formal speech patterns, gravelly voices
  - Draconic behaviors: territorial, hoard keepsakes, prefer warmth

Special Abilities to Reference:
  - Breath weapon (describe in combat style or traits)
  - Damage resistance to ancestry element
  - At level 5+: Spectral draconic wings for flight
"""
    elif "elf" in species_lower or "eladrin" in species_lower:
        prompt += """
🍃 ELF - Graceful, Long-Lived Fey-Touched
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Slender, graceful build with pointed ears
  - Ageless, timeless appearance
  - Flowing hair, ethereal beauty
  - Keen eyes that miss nothing

Cultural Elements:
  - Long perspective from centuries of life
  - Deep connection to nature, magic, or ancient traditions
  - Refined, elegant mannerisms
  - May seem aloof but deeply passionate
"""
    elif "dwarf" in species_lower:
        prompt += """
⚒️ DWARF - Resilient Mountain-Folk
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Stout, broad build (4-5 feet tall but heavy)
  - Magnificent beard (or braided facial hair)
  - Weathered, hardy features
  - Strong, calloused hands

Cultural Elements:
  - Clan and family central to identity
  - Appreciation for craftsmanship and quality
  - Stubborn, loyal, traditional
  - Direct communication style
"""
    elif "halfling" in species_lower:
        prompt += """
🌾 HALFLING - Brave Hearts in Small Packages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Small stature (about 3 feet tall)
  - Nimble, quick movements
  - Curly hair, often on bare feet
  - Warm, friendly faces

Cultural Elements:
  - Community-focused, hospitable
  - Surprisingly brave and resourceful
  - Practical, down-to-earth wisdom
  - Lucky and optimistic
"""
    elif "tiefling" in species_lower:
        prompt += """
😈 TIEFLING - Infernal Heritage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Physical Features:
  - Horns (various shapes), skin in unusual tones (red, purple, blue)
  - Solid-color eyes (no pupils) or exotic eye colors
  - Tail, sometimes cloven hooves
  - Often striking or unsettling appearance

Cultural Elements:
  - Face prejudice due to infernal bloodline
  - Often develop strong sense of self-reliance
  - May embrace or reject their heritage
  - Charismatic presence
"""
    else:
        prompt += f"""
{species.upper()} Traits:
  - Incorporate appropriate species characteristics
  - Reflect cultural background and racial abilities
  - Draw from species lore and typical features
"""
    
    prompt += f"""

CLASS-SPECIFIC GUIDANCE FOR {char_class.upper()}:
"""

    # Add class guidance
    class_lower = char_class.lower()
    if class_lower in ["wizard", "sorcerer", "warlock"]:
        prompt += """
  - Describe relationship with magic (scholarly study, innate power, pact)
  - Mention magical mannerisms or effects
  - Reference spellcasting in combat approach
"""
    elif class_lower in ["fighter", "barbarian", "paladin"]:
        prompt += """
  - Emphasize combat training and martial discipline
  - Describe weapon preferences and fighting technique
  - Mention physical conditioning and warrior bearing
"""
    elif class_lower in ["rogue", "ranger"]:
        prompt += """
  - Highlight stealth, cunning, and expertise
  - Describe tactical thinking and observational skills
  - Mention preferred tools of the trade
"""
    elif class_lower == "cleric":
        prompt += """
  - Balance divine faith with practical abilities
  - Describe connection to deity and how it manifests
  - Mention holy symbols, prayers, or rituals
"""
    elif class_lower == "bard":
        prompt += """
  - Showcase artistic talents and performance style
  - Describe charisma and how they inspire others
  - Mention instrument or performance preference
"""
    elif class_lower == "monk":
        prompt += """
  - Emphasize discipline, meditation, and philosophy
  - Describe martial arts style and ki manifestation
  - Mention monastery background or training
"""
    elif class_lower == "druid":
        prompt += """
  - Highlight attunement to nature and wild places
  - Describe Wild Shape preferences
  - Mention natural symbols or druidic focus
"""
    elif class_lower == "artificer":
        prompt += """
  - Emphasize magical invention and crafting
  - Describe tools, gadgets, or infusions
  - Mention innovative thinking and experimentation
"""
    
    prompt += f"""

BACKGROUND INFLUENCE ({background}):
  - This background shapes their past, skills, and worldview
  - Incorporate background feature into backstory
  - Reference background-appropriate relationships and experiences

═══════════════════════════════════════════════════════════════════════════
REQUIRED OUTPUT STRUCTURE (D&D 5E Character Sheet Format)
═══════════════════════════════════════════════════════════════════════════

1. CHARACTER INFORMATION
   ├─ character_name: UNIQUE fantasy name following {species} naming conventions
   │   ⚠️ CRITICAL: Generate a COMPLETELY UNIQUE name each time!
   │   • Use diverse syllables, sounds, and combinations
   │   • Consider species-specific naming patterns:
   │     - Dragonborn: Strong consonants + clan names (Balasar, Ghesh, Heskan, Akra, Tarhun, Nadarr)
   │     - Elf: Flowing, melodic (Aelar, Heian, Peren, Adran, Theren, Galinndan, Ivellios, Quarion)
   │     - Dwarf: Hard consonants + clan surnames (Thorin, Baern, Rurik, Darrak, Torbin, Vondal)
   │     - Halfling: Friendly, earthy (Alton, Roscoe, Lindal, Cade, Eldon, Corrin, Garret)
   │     - Tiefling: Infernal or virtue names (Akmenios, Damakos, Iados, Kairon, Art, Glory, Hope)
   │     - Human: Varied by culture (use diverse real-world inspirations)
    │   • Use surnames sparingly and invent novel surnames by combining syllables
    │     (do not reuse any static example names or their obvious variants). The
    │     generator must produce surnames that are not simple edits of a small
    │     static pool. Instead of relying on pre-listed examples, create fresh
    │     combinations by mixing syllables (consonant clusters, vowel patterns,
    │     and cultural flavor) to maximize variety across generated characters.
   │
   ├─ age: Age appropriate for {species} (with context like "young", "seasoned", "elder")
   ├─ height: {species}-appropriate height
   ├─ weight: Weight matching build and species
   ├─ eyes: Eye color/appearance (consider species traits)
   │   ⚠️ BE CREATIVE: Avoid common combinations like "green with gold flecks"
   │   • Use unexpected colors, patterns, or descriptors
   │   • Examples: slate-gray, amber, heterochromatic, storm-blue, copper, violet
   ├─ skin: Skin tone/scales/fur appropriate to species
   │   ⚠️ CRITICAL: Generate UNIQUE skin descriptions - NO REPETITION!
   │   • Avoid clichés: "olive-toned with freckles", "porcelain pale", "sun-kissed"
   │   • Use diverse, specific descriptions:
   │     - Varied tones: russet, bronze, ochre, umber, walnut, mahogany, ash, alabaster, sienna
   │     - Unique textures: weathered, smooth, coarse, calloused, battle-scarred
   │     - Specific marks: birthmarks, sun damage, frost-touched, wind-burned, tattoos
   │   • Mix and match creatively - make EVERY character visually distinct
   └─ hair: Hair description (or species equivalent like crests, frills)
       ⚠️ AVOID REPETITION: No generic "flowing black hair" or "golden blonde"
       • Use specific styles: cropped, braided, shaved sides, dreadlocks, topknot
       • Unique colors: auburn, raven-black, salt-and-pepper, copper-streaked, ash-blonde
       • Textures: coarse, silky, wiry, curled, wavy, straight, tangled

2. CHARACTER APPEARANCE
   └─ character_appearance: Rich visual description for portrait generation
      • Include clothing, armor type, carried weapons, gear
      • Describe posture, demeanor, overall impression
      • 3-4 sentences focused on visual storytelling

3. ALLIES & ORGANIZATIONS
   └─ allies_and_organizations: Important connections and affiliations
      • Guilds, religious orders, noble houses, factions
      • Mentors, companions, or contacts
      • Nature of relationships (2-3 sentences)

4. CHARACTER BACKSTORY
   └─ character_backstory: Complete origin story
      • Birthplace and upbringing
      • How they gained class training
      • Connection to {background} background
      • Path to becoming an adventurer
      • 4-6 sentences of compelling narrative

5. ADDITIONAL FEATURES & TRAITS
   └─ additional_features_and_traits: Quirks, habits, and distinguishing characteristics
      • Unique mannerisms or behaviors (especially {species}-specific)
      • Speech patterns and voice characteristics
      • Nervous habits, talents, or unusual knowledge
      • 3-5 distinctive traits as flowing narrative

6. CHARACTER MOTIVATIONS (D&D 5E Standard Format)
   ├─ personality_traits: [EXACTLY 2 traits]
   │   • Distinct behavioral characteristics
   │   • Should drive roleplay decisions
   │
   ├─ ideals: ONE ideal aligned with {alignment}
   │   • Format: "Ideal: Description"
   │   • Should reflect alignment (Good/Evil/Lawful/Chaotic/Neutral)
   │
   ├─ bonds: ONE bond to people, places, or events
   │   • Creates emotional investment
   │   • Generates story hooks
   │
   └─ flaws: ONE character flaw
       • Creates roleplay challenges
       • Opportunity for character growth

═══════════════════════════════════════════════════════════════════════════
ABILITY SCORE CONTEXT (Use to inform personality and appearance):
═══════════════════════════════════════════════════════════════════════════

{builder._get_ability_summary()}

Physical Interpretation: {builder._get_physical_traits()}
Mental Interpretation: {builder._get_mental_traits()}
Social Interpretation: {builder._get_social_traits()}

"""
    
    if additional_context:
        prompt += f"""
═══════════════════════════════════════════════════════════════════════════
ADDITIONAL PLAYER CONTEXT:
═══════════════════════════════════════════════════════════════════════════
{additional_context}

"""
    
    prompt += """
═══════════════════════════════════════════════════════════════════════════
GENERATION GUIDELINES:
═══════════════════════════════════════════════════════════════════════════

✓ DO:
  • Create a unique, memorable individual with depth and complexity
  • Integrate species traits naturally into all aspects
  • Make personality traits, ideals, bonds, and flaws SPECIFIC and story-driven
  • Use vivid, evocative language that brings the character to life
  • Ensure backstory explains both class training and background
  • Make the name authentic to species culture
  • **VARY physical descriptions** - avoid repeating common traits across characters
  • Use unexpected combinations and creative descriptors

✗ DON'T:
  • Duplicate mechanical information (HP, AC, spell slots, etc.)
  • Use generic or cliché descriptions
  • **NEVER repeat common phrases**: "olive-toned with freckles", "piercing green eyes", "flowing black hair"
  • Ignore species or class characteristics
  • Create contradictions with alignment or background
  • Write vague personality traits ("nice", "brave", "smart")
  • Copy physical trait combinations from previous characters

Generate a complete narrative that makes this character ready to play at the table!
═══════════════════════════════════════════════════════════════════════════
"""
    
    return prompt


