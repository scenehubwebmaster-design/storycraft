"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Generation Request Schemas
class CharacterGenerationRequest(BaseModel):
    themes: Optional[List[str]] = None
    personality_traits: Optional[List[str]] = None
    physical_traits: Optional[List[str]] = None
    emotional_traits: Optional[List[str]] = None
    archetype: Optional[str] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, google)")
    model: Optional[str] = None
    base_content: Optional[str] = None
    refinement_instructions: Optional[str] = None
    # NEW: Genre-specific prompt variations
    genre: Optional[str] = Field(None, description="Genre category: fantasy, sci_fi, or historical")
    variation: Optional[str] = Field(None, description="Specific variation within genre (e.g., 'high_fantasy', 'cyberpunk')")
    # NEW: Cultural diversity
    cultural_origin: Optional[str] = Field(None, description="Cultural/geographic origin (e.g., 'west_african', 'japanese', 'norse')")
    # NEW: D&D 5E Integration
    is_dnd: Optional[bool] = Field(False, description="Generate as D&D 5E character")
    dnd_class: Optional[str] = Field(None, description="D&D class (e.g., 'wizard', 'fighter')")
    dnd_species: Optional[str] = Field(None, description="D&D species/race (e.g., 'elf', 'dwarf')")
    dnd_background: Optional[str] = Field(None, description="D&D background (e.g., 'sage', 'soldier')")
    dnd_alignment: Optional[str] = Field(None, description="D&D alignment (e.g., 'Neutral Good')")
    dnd_level: Optional[int] = Field(1, description="Character level (1-20)", ge=1, le=20)


class ImageGenerationRequest(BaseModel):
    character_name: str = Field(..., description="Name of the character")
    appearance_text: str = Field(..., description="Physical appearance description")
    provider: str = Field(default="google", description="Image provider (google, openai)")
    model: Optional[str] = Field(None, description="Model to use (provider-specific)")
    aspect_ratio: str = Field(default="3:4", description="Image aspect ratio")
    custom_prompt: Optional[str] = Field(None, description="Optional custom prompt override")
    style_preset: Optional[str] = Field(None, description="Style preset (realistic, fantasy_art, anime, watercolor, oil_painting, digital_art)")
    quality: Optional[str] = Field("standard", description="Image quality (standard, hd) - DALL-E 3 only")


class StoryGenerationRequest(BaseModel):
    themes: Optional[List[str]] = None
    tone: Optional[List[str]] = None
    length: Optional[str] = None
    plot_structure: Optional[str] = None
    conflict_type: Optional[str] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None
    base_content: Optional[str] = None
    refinement_instructions: Optional[str] = None


class WorldGenerationRequest(BaseModel):
    themes: Optional[List[str]] = None
    setting: Optional[List[str]] = None
    elements: Optional[List[str]] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None
    base_content: Optional[str] = None
    refinement_instructions: Optional[str] = None


class SceneGenerationRequest(BaseModel):
    story_context: Optional[str] = None
    characters: Optional[List[str]] = None
    setting: Optional[str] = None
    purpose: Optional[str] = None
    tone: Optional[List[str]] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None
    base_content: Optional[str] = None
    refinement_instructions: Optional[str] = None


class ChapterGenerationRequest(BaseModel):
    story_outline: Optional[str] = None
    chapter_number: Optional[int] = None
    previous_summary: Optional[str] = None
    characters: Optional[List[str]] = None
    plot_points: Optional[List[str]] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None


class LocationGenerationRequest(BaseModel):
    world_context: Optional[str] = None
    location_type: Optional[str] = None
    importance: Optional[str] = None
    themes: Optional[List[str]] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None


class CampaignGenerationRequest(BaseModel):
    themes: Optional[List[str]] = None
    tone: Optional[List[str]] = None
    session_count: Optional[int] = None
    player_count: Optional[int] = None
    level_range: Optional[str] = None
    custom_details: Optional[str] = None
    provider: str = Field(default="openai")
    model: Optional[str] = None


# Generation Response Schema
class GenerationResponse(BaseModel):
    content: str
    prompt_used: str
    provider: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    generation_metadata: Optional[Dict[str, Any]] = None


# Prompt Options Response
class PromptOptionsResponse(BaseModel):
    themes: List[str]
    personality_traits: List[str]
    physical_traits: List[str]
    emotional_traits: List[str]
    tones: List[str]
    settings: List[str]
    story_lengths: Dict[str, str]
    plot_structures: List[str]
    world_elements: List[str]
    character_archetypes: List[str]
    conflict_types: List[str]


# Structured Output Schemas for Character Profiles
class CharacterProfile(BaseModel):
    """Structured character profile with all essential details"""
    name: str = Field(..., description="Character's full name")
    age: int = Field(..., description="Character's age in years", ge=0, le=10000)
    
    # Physical Appearance
    height: str = Field(..., description="Character's height (e.g., '6ft 2in', '175cm')")
    build: str = Field(..., description="Physical build/body type")
    hair: str = Field(..., description="Hair color, length, and style")
    eyes: str = Field(..., description="Eye color and notable features")
    distinctive_features: List[str] = Field(..., description="Scars, tattoos, unique characteristics")
    physical_description: str = Field(..., description="Complete physical appearance description")
    
    # Personality
    personality_traits: List[str] = Field(..., description="Core personality traits (3-5 traits)")
    demeanor: str = Field(..., description="Overall demeanor and how they present themselves")
    sense_of_humor: Optional[str] = Field(None, description="Type of humor they exhibit")
    personality_description: str = Field(..., description="Detailed personality description")
    
    # Background
    birthplace: str = Field(..., description="Where the character was born")
    upbringing: str = Field(..., description="Details about their childhood and upbringing")
    formative_events: List[str] = Field(..., description="Key events that shaped them (2-4 events)")
    backstory: str = Field(..., description="Complete backstory narrative")
    
    # Motivations and Goals
    primary_motivation: str = Field(..., description="Main driving force")
    goals: List[str] = Field(..., description="Short and long-term goals (2-4 goals)")
    values: List[str] = Field(..., description="Core values and beliefs (3-5 values)")
    
    # Fears and Weaknesses
    greatest_fear: str = Field(..., description="What they fear most")
    emotional_weaknesses: List[str] = Field(..., description="Emotional vulnerabilities (2-3)")
    physical_weaknesses: List[str] = Field(..., description="Physical limitations or vulnerabilities (1-3)")
    
    # Strengths and Abilities
    skills: List[str] = Field(..., description="Notable skills and expertise (3-6 skills)")
    special_abilities: List[str] = Field(..., description="Unique abilities, powers, or talents")
    combat_style: Optional[str] = Field(None, description="Fighting style or combat approach if applicable")
    strengths_description: str = Field(..., description="Detailed description of strengths")
    
    # Relationships
    key_relationships: List[Dict[str, str]] = Field(
        ..., 
        description="Important relationships - each with 'name', 'relationship', and 'description' keys"
    )
    
    # Character Arc
    character_arc_potential: str = Field(
        ..., 
        description="Potential character development and growth opportunities"
    )
    
    # Unique Qualities
    unique_qualities: List[str] = Field(
        ..., 
        description="What makes this character truly unique (2-4 qualities)"
    )
    quirks_and_habits: List[str] = Field(
        ..., 
        description="Notable quirks, habits, or mannerisms (2-4 items)"
    )
    
    # Validators to handle LLM sometimes returning strings instead of lists
    @field_validator('distinctive_features', 'personality_traits', 'formative_events', 'goals', 
                     'values', 'emotional_weaknesses', 'physical_weaknesses', 'skills', 
                     'special_abilities', 'unique_qualities', 'quirks_and_habits', mode='before')
    @classmethod
    def convert_string_to_list(cls, v):
        """Convert string to list if LLM returns string instead of array"""
        if isinstance(v, str):
            # If it's a string, wrap it in a list
            return [v]
        return v
    
    @field_validator('key_relationships', mode='before')
    @classmethod
    def ensure_relationships_list(cls, v):
        """Ensure relationships is a list of dicts"""
        if isinstance(v, str):
            # If it's a string, return empty list
            return []
        if isinstance(v, dict):
            # If it's a single dict, wrap in list
            return [v]
        return v


# Structured Output Schema for World Profiles
class WorldProfile(BaseModel):
    """Structured world profile with comprehensive details"""
    name: str = Field(..., description="Name of the world/realm")
    world_type: str = Field(..., description="Type of world (e.g., 'Fantasy Realm', 'Sci-Fi Universe', 'Modern Earth')")
    
    # Overview
    tagline: str = Field(..., description="Brief one-sentence description")
    overview: str = Field(..., description="Comprehensive overview of the world (2-3 paragraphs)")
    
    # History
    age: str = Field(..., description="How old is this world/civilization")
    origin_story: str = Field(..., description="How the world came to be")
    major_historical_events: List[Dict[str, str]] = Field(
        ..., 
        description="Key historical events - each with 'era', 'event', and 'impact' keys (3-5 events)"
    )
    current_era: str = Field(..., description="Current time period or era")
    history_summary: str = Field(..., description="Detailed historical narrative")
    
    # Geography
    size_and_scale: str = Field(..., description="Physical dimensions and scale of the world")
    climate_zones: List[str] = Field(..., description="Major climate regions (3-6 zones)")
    major_regions: List[Dict[str, str]] = Field(
        ..., 
        description="Major geographical regions - each with 'name', 'description', and 'notable_features' keys (4-8 regions)"
    )
    natural_wonders: List[str] = Field(..., description="Remarkable natural features (2-5 wonders)")
    geography_summary: str = Field(..., description="Complete geographical description")
    
    # Culture and Society
    dominant_species: List[str] = Field(..., description="Main intelligent species or races")
    population_estimate: str = Field(..., description="Estimated population")
    major_civilizations: List[Dict[str, str]] = Field(
        ..., 
        description="Major societies/nations - each with 'name', 'description', and 'governance' keys (3-6 civilizations)"
    )
    languages: List[str] = Field(..., description="Major languages spoken (2-5 languages)")
    religions_and_beliefs: List[Dict[str, str]] = Field(
        ..., 
        description="Major religions/belief systems - each with 'name' and 'description' keys (2-4 religions)"
    )
    cultural_norms: List[str] = Field(..., description="Common cultural practices and social norms (3-6 norms)")
    culture_summary: str = Field(..., description="Detailed cultural and societal description")
    
    # Magic/Technology
    power_system: str = Field(..., description="How magic/technology/powers work in this world")
    power_level: str = Field(..., description="Common level of magic/tech (e.g., 'Low Magic', 'High Tech', 'Medieval')")
    limitations: List[str] = Field(..., description="Limitations or rules of the power system (2-4 limitations)")
    notable_artifacts: List[str] = Field(..., description="Important magical items or technological devices (2-5 items)")
    
    # Conflicts and Themes
    major_conflicts: List[Dict[str, str]] = Field(
        ..., 
        description="Current or historical conflicts - each with 'name', 'parties', and 'description' keys (2-4 conflicts)"
    )
    central_themes: List[str] = Field(..., description="Core themes explored in this world (3-5 themes)")
    current_threats: List[str] = Field(..., description="Present dangers or challenges (2-4 threats)")
    
    # Validators to handle LLM sometimes returning strings instead of lists
    @field_validator('climate_zones', 'natural_wonders', 'dominant_species', 'languages', 
                     'cultural_norms', 'limitations', 'notable_artifacts', 'central_themes', 
                     'current_threats', mode='before')
    @classmethod
    def convert_string_to_list(cls, v):
        """Convert string to list if LLM returns string instead of array"""
        if isinstance(v, str):
            return [v]
        return v
    
    @field_validator('major_historical_events', 'major_regions', 'major_civilizations', 
                     'religions_and_beliefs', 'major_conflicts', mode='before')
    @classmethod
    def ensure_dict_list(cls, v):
        """Ensure field is a list of dicts"""
        if isinstance(v, str):
            return []
        if isinstance(v, dict):
            return [v]
        return v
    
    # Lore and Mysteries
    legends_and_myths: List[Dict[str, str]] = Field(
        ..., 
        description="Important legends - each with 'title' and 'story' keys (2-4 legends)"
    )
    unsolved_mysteries: List[str] = Field(..., description="Enigmas and unanswered questions (2-4 mysteries)")
    prophecies: List[str] = Field(..., description="Important prophecies or predictions if applicable")
    lore_summary: str = Field(..., description="Rich lore and worldbuilding details")
    
    # Story Potential
    adventure_hooks: List[str] = Field(
        ..., 
        description="Potential story ideas and adventure hooks (4-6 hooks)"
    )
    notable_locations: List[Dict[str, str]] = Field(
        ..., 
        description="Important places - each with 'name', 'type', and 'description' keys (4-8 locations)"
    )
    unique_aspects: List[str] = Field(
        ..., 
        description="What makes this world truly unique and memorable (3-5 aspects)"
    )


# Structured Output Schema for D&D Character Narrative
class DnDCharacterNarrative(BaseModel):
    """
    Structured narrative profile for D&D 5E characters.
    
    Aligned with official D&D 5E character sheet sections.
    Focuses on storytelling "flavor" elements that complement mechanical stats.
    Avoids duplicating rules-based information (abilities, HP, AC, etc.).
    """
    
    # Character Information
    character_name: str = Field(
        ...,
        description=(
            "The character's full name, incorporating species naming conventions. "
            "For Dragonborn: clan names, draconic-sounding names. "
            "For Elves: flowing, melodic names. Consider cultural background."
        )
    )
    age: str = Field(
        ...,
        description=(
            "Age appropriate for species. "
            "Dragonborn: young adult (15-20), adult (30-60), elder (80+). "
            "Elves: young (20-100), adult (100-500), elder (600+). "
            "Include context like 'young for her kind' or 'seasoned veteran'."
        )
    )
    height: str = Field(..., description="Height appropriate for species and build")
    weight: str = Field(..., description="Weight reflecting build and species")
    eyes: str = Field(
        ...,
        description=(
            "Eye color and appearance. For Dragonborn: bright, reptilian eyes matching "
            "draconic ancestry (copper, gold, red, etc.). May glow or have slit pupils."
        )
    )
    skin: str = Field(
        ...,
        description=(
            "Skin tone/type. For Dragonborn: scale color matching ancestry "
            "(brass, bronze, copper, gold, red, etc.), texture, patterns. "
            "For other species: complexion, distinguishing marks."
        )
    )
    hair: str = Field(
        ...,
        description=(
            "Hair color, style, length. For Dragonborn: often none, but may have "
            "decorative crests, frills, or horn decorations instead."
        )
    )
    
    # Character Appearance (narrative description for portrait reference)
    character_appearance: str = Field(
        ...,
        description=(
            "Rich visual description for portrait generation and visualization. "
            "Include clothing style, armor type, carried weapons, distinctive gear, "
            "posture, overall impression. This complements the portrait generator. "
            "3-4 sentences focusing on visual elements."
        )
    )
    
    # Allies & Organizations
    allies_and_organizations: str = Field(
        ...,
        description=(
            "Important allies, contacts, factions, or organizations the character "
            "is connected to. Include guilds, religious orders, noble houses, "
            "adventuring companies, or mentors. Mention relationship nature. "
            "2-3 sentences."
        )
    )
    
    # Character Backstory
    character_backstory: str = Field(
        ...,
        description=(
            "Compelling backstory incorporating background feature, species history, "
            "class training origin, and alignment influences. Include origins, "
            "formative experiences, key relationships, and path to becoming an adventurer. "
            "For Dragonborn: consider clan ties, draconic ancestry connection, "
            "relationship with dragon progenitors (Bahamut/Tiamat). "
            "4-6 sentences of rich narrative."
        )
    )
    
    # Additional Features & Traits (narrative flavor)
    additional_features_and_traits: str = Field(
        ...,
        description=(
            "Unique quirks, habits, mannerisms, and distinguishing characteristics. "
            "For Dragonborn: draconic behaviors (hissing when angry, hoarding tendencies, "
            "territorial instincts, preference for heat, gravelly voice). "
            "Include speech patterns, nervous habits, talents, or unusual knowledge. "
            "3-5 distinctive traits as flowing text."
        )
    )
    
    # Character Motivations (D&D 5E standard fields)
    personality_traits: List[str] = Field(
        ...,
        description=(
            "2 distinct personality traits from background or custom traits. "
            "Should reflect character's behavior, attitudes, and mannerisms. "
            "D&D 5E expects exactly 2 traits."
        ),
        min_length=2,
        max_length=2
    )
    ideals: str = Field(
        ...,
        description=(
            "One ideal that drives the character. Should align with alignment "
            "(Good, Evil, Lawful, Chaotic, Neutral, or Any). "
            "Format: 'Ideal: Description' (e.g., 'Honor: I don't steal from others'). "
            "D&D 5E expects 1 ideal."
        )
    )
    bonds: str = Field(
        ...,
        description=(
            "One bond connecting character to people, places, or events. "
            "Should create story hooks and emotional investment. "
            "D&D 5E expects 1 bond."
        )
    )
    flaws: str = Field(
        ...,
        description=(
            "One flaw or weakness. Should create interesting roleplay challenges "
            "and character growth opportunities. D&D 5E expects 1 flaw."
        )
    )
    
    # Validators for backwards compatibility and string-to-list conversion
    @field_validator('personality_traits', mode='before')
    @classmethod
    def convert_personality_to_list(cls, v):
        """Convert string to list of exactly 2 traits if needed"""
        if isinstance(v, str):
            # Split by common delimiters and take first 2
            traits = [t.strip() for t in v.replace('\n', ',').split(',') if t.strip()]
            return traits[:2] if len(traits) >= 2 else traits + ['Adaptable'] * (2 - len(traits))
        if isinstance(v, list):
            # Ensure exactly 2 traits
            if len(v) < 2:
                return v + ['Adaptable'] * (2 - len(v))
            return v[:2]
        return v


