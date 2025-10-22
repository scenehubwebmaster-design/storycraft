"""
Pydantic models for D&D 5e content.

These models provide type safety and validation for data retrieved
from the D&D MCP server.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class AbilityScore(BaseModel):
    """D&D ability score"""
    name: str
    value: int
    modifier: Optional[int] = None


class Damage(BaseModel):
    """Damage information"""
    damage_type: Optional[str] = None
    damage_dice: Optional[str] = None


class DC(BaseModel):
    """Difficulty Class for saving throws"""
    dc_type: str
    dc_value: Optional[int] = None
    success_type: Optional[str] = None


class Spell(BaseModel):
    """D&D 5e Spell"""
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: List[str] = Field(default_factory=list)
    duration: str
    description: str
    higher_levels: Optional[str] = None
    classes: List[str] = Field(default_factory=list)
    damage: Optional[Damage] = None
    dc: Optional[DC] = None
    concentration: bool = False
    ritual: bool = False
    material: Optional[str] = None
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields from API


class Speed(BaseModel):
    """Creature movement speeds"""
    walk: Optional[str] = None
    fly: Optional[str] = None
    swim: Optional[str] = None
    climb: Optional[str] = None
    burrow: Optional[str] = None


class Action(BaseModel):
    """Creature action"""
    name: str
    description: str
    attack_bonus: Optional[int] = None
    damage: Optional[List[Damage]] = None
    dc: Optional[DC] = None


class SpecialAbility(BaseModel):
    """Creature special ability"""
    name: str
    description: str
    usage: Optional[Dict[str, Any]] = None


class Monster(BaseModel):
    """D&D 5e Monster"""
    name: str
    size: str
    type: str
    alignment: str
    armor_class: int
    hit_points: int
    hit_dice: str
    speed: Union[Dict[str, str], Speed]
    
    # Ability scores
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    
    # Challenge
    challenge_rating: float
    proficiency_bonus: Optional[int] = None
    xp: Optional[int] = None
    
    # Combat
    actions: List[Action] = Field(default_factory=list)
    special_abilities: List[SpecialAbility] = Field(default_factory=list)
    legendary_actions: Optional[List[Action]] = None
    
    # Additional info
    damage_vulnerabilities: List[str] = Field(default_factory=list)
    damage_resistances: List[str] = Field(default_factory=list)
    damage_immunities: List[str] = Field(default_factory=list)
    condition_immunities: List[str] = Field(default_factory=list)
    senses: Optional[Dict[str, str]] = None
    languages: Optional[str] = None
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class Cost(BaseModel):
    """Item cost"""
    quantity: float
    unit: str  # gp, sp, cp, etc.


class Equipment(BaseModel):
    """D&D 5e Equipment"""
    name: str
    equipment_category: str
    cost: Optional[Cost] = None
    weight: Optional[float] = None
    description: Optional[str] = None
    
    # Weapon properties
    weapon_category: Optional[str] = None
    weapon_range: Optional[str] = None
    damage: Optional[Damage] = None
    range: Optional[Dict[str, int]] = None
    properties: List[str] = Field(default_factory=list)
    
    # Armor properties
    armor_category: Optional[str] = None
    armor_class: Optional[Dict[str, Any]] = None
    str_minimum: Optional[int] = None
    stealth_disadvantage: Optional[bool] = None
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class MagicItem(BaseModel):
    """D&D 5e Magic Item"""
    name: str
    rarity: str
    type: str
    requires_attunement: bool = False
    description: str
    properties: Optional[Dict[str, Any]] = None
    
    # Variants
    variants: List[str] = Field(default_factory=list)
    variant: Optional[bool] = None
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class CharacterClass(BaseModel):
    """D&D 5e Character Class"""
    name: str
    hit_die: int
    proficiency_choices: Optional[List[Dict[str, Any]]] = None
    proficiencies: List[str] = Field(default_factory=list)
    saving_throws: List[str] = Field(default_factory=list)
    
    # Spellcasting
    spellcasting: Optional[Dict[str, Any]] = None
    spells: Optional[List[str]] = None
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class Race(BaseModel):
    """D&D 5e Race"""
    name: str
    speed: int
    ability_bonuses: List[Dict[str, Any]] = Field(default_factory=list)
    alignment: Optional[str] = None
    age: Optional[str] = None
    size: str
    size_description: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    language_desc: Optional[str] = None
    traits: List[str] = Field(default_factory=list)
    
    # Subraces
    subraces: List[str] = Field(default_factory=list)
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class Feature(BaseModel):
    """D&D 5e Feature (class or race feature)"""
    name: str
    level: Optional[int] = None
    description: List[str] = Field(default_factory=list)
    class_: Optional[str] = Field(None, alias="class")
    subclass: Optional[str] = None
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"
        populate_by_name = True


class Condition(BaseModel):
    """D&D 5e Condition"""
    name: str
    description: List[str] = Field(default_factory=list)
    
    index: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        extra = "allow"


class SearchResult(BaseModel):
    """Search result item"""
    name: str
    index: str
    url: str
    description: Optional[str] = None
    score: Optional[float] = None
    category: Optional[str] = None
    attribution_id: Optional[str] = None


class SearchResults(BaseModel):
    """Search results from MCP"""
    query: str
    total_count: int
    spells: List[SearchResult] = Field(default_factory=list)
    monsters: List[SearchResult] = Field(default_factory=list)
    equipment: List[SearchResult] = Field(default_factory=list)
    magic_items: List[SearchResult] = Field(default_factory=list, alias="magic-items")
    classes: List[SearchResult] = Field(default_factory=list)
    races: List[SearchResult] = Field(default_factory=list)
    features: List[SearchResult] = Field(default_factory=list)
    conditions: List[SearchResult] = Field(default_factory=list)
    
    # Metadata
    sources: List[str] = Field(default_factory=list)
    attribution: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"
        populate_by_name = True


class HealthStatus(BaseModel):
    """MCP server health status"""
    status: str
    error: Optional[str] = None
    timestamp: str


class ApiHealthStatus(BaseModel):
    """D&D API health status"""
    status: str
    available_endpoints: List[str] = Field(default_factory=list)
    total_resources: Optional[int] = None
    categories: Optional[Dict[str, int]] = None
    sources: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


# Helper functions to convert API responses to models

def parse_spell(data: Dict[str, Any]) -> Spell:
    """Parse spell data into Spell model"""
    return Spell(**data)


def parse_monster(data: Dict[str, Any]) -> Monster:
    """Parse monster data into Monster model"""
    return Monster(**data)


def parse_equipment(data: Dict[str, Any]) -> Equipment:
    """Parse equipment data into Equipment model"""
    return Equipment(**data)


def parse_magic_item(data: Dict[str, Any]) -> MagicItem:
    """Parse magic item data into MagicItem model"""
    return MagicItem(**data)


def parse_search_results(data: Dict[str, Any]) -> SearchResults:
    """Parse search results into SearchResults model"""
    return SearchResults(**data)
