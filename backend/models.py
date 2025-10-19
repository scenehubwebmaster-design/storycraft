from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="story", cascade="all, delete-orphan")
    characters = relationship("Character", secondary="story_characters", back_populates="stories")
    worlds = relationship("World", secondary="story_worlds", back_populates="stories")


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    chapter_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    story = relationship("Story", back_populates="chapters")
    scenes = relationship("Scene", back_populates="chapter", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(255))
    content = Column(Text)
    scene_number = Column(Integer)
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="scenes")


class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    background = Column(Text)
    personality = Column(Text)
    appearance = Column(Text)
    motivations = Column(Text)
    relationships = Column(JSON)  # Store as JSON for flexibility
    portrait_image = Column(Text)  # Base64 encoded image data
    image_prompt = Column(Text)  # Store the prompt used to generate the image
    generation_log = Column(JSON)  # Track AI generation history
    structured_data = Column(JSON)  # Store full CharacterProfile from structured generation
    
    # D&D 5E Integration Fields
    is_dnd = Column(Boolean, default=False)  # Flag to indicate D&D character
    dnd_class = Column(String(100))  # Character class (e.g., "Wizard", "Fighter")
    dnd_level = Column(Integer, default=1)  # Character level
    dnd_species = Column(String(100))  # Species/Race (e.g., "Elf", "Dwarf")
    dnd_background = Column(String(100))  # Background (e.g., "Sage", "Soldier")
    dnd_alignment = Column(String(50))  # Alignment (e.g., "Neutral Good")
    dnd_ability_scores = Column(JSON)  # {"strength": 15, "dexterity": 14, ...}
    dnd_hit_points = Column(Integer)  # Maximum hit points
    dnd_armor_class = Column(Integer)  # Armor class
    dnd_initiative = Column(String(10))  # Initiative modifier (e.g., "+2")
    dnd_speed = Column(Integer)  # Movement speed in feet
    dnd_proficiency_bonus = Column(String(10))  # Proficiency bonus (e.g., "+2")
    dnd_skills = Column(JSON)  # ["Arcana", "History", "Investigation", ...]
    dnd_proficiencies = Column(JSON)  # {"saves": [...], "armor": [...], "weapons": [...], "tools": [...]}
    dnd_features = Column(JSON)  # {"racial": [...], "class": [...], "background": {...}}
    dnd_equipment = Column(JSON)  # {"weapons": [...], "armor": [...], "gear": [...]}
    dnd_spellcasting = Column(JSON)  # {"ability": "Intelligence", "dc": 12, "attack": 4, ...} or null
    dnd_languages = Column(JSON)  # ["Common", "Elvish", ...]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Soft-delete support
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    stories = relationship("Story", secondary="story_characters", back_populates="characters")


class World(Base):
    __tablename__ = "worlds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    history = Column(Text)
    geography = Column(Text)
    culture = Column(Text)
    magic_system = Column(Text)
    technology_level = Column(String(100))
    structured_data = Column(Text)  # Store full WorldProfile from structured generation (stored as JSON string)
    # New image and metadata fields
    world_image = Column(Text)  # Base64 encoded landscape/overview image
    world_map = Column(Text)    # Base64 encoded map image
    image_prompt = Column(Text) # Prompt used to generate world image
    climate = Column(String(100))
    population_level = Column(String(50))  # sparse, moderate, dense
    danger_level = Column(String(50))      # safe, moderate, dangerous
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stories = relationship("Story", secondary="story_worlds", back_populates="worlds")
    locations = relationship("Location", back_populates="world", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    world_id = Column(Integer, ForeignKey("worlds.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location_type = Column(String(100))  # city, region, building, etc.
    generation_log = Column(JSON)  # Track AI generation history
    # New image and hierarchy fields
    location_image = Column(Text)  # Base64 encoded image data for location
    image_prompt = Column(Text)
    parent_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    coordinates = Column(String(50))
    notable_features = Column(Text)
    inhabitants = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    world = relationship("World", back_populates="locations")


class Plot(Base):
    __tablename__ = "plots"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    plot_type = Column(String(100))  # main, subplot, character arc, etc.
    status = Column(String(50))  # planned, in_progress, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Association tables for many-to-many relationships
story_characters = Table(
    'story_characters',
    Base.metadata,
    Column('story_id', Integer, ForeignKey('stories.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

story_worlds = Table(
    'story_worlds',
    Base.metadata,
    Column('story_id', Integer, ForeignKey('stories.id'), primary_key=True),
    Column('world_id', Integer, ForeignKey('worlds.id'), primary_key=True)
)
