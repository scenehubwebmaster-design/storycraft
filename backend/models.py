from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    genre = Column(String(100))
    content = Column(Text)  # Full story content
    generation_log = Column(JSON)  # Track AI generation history
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
    order = Column(Integer, default=0)  # For ordering chapters
    generation_log = Column(JSON)  # Track AI generation history
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
    order = Column(Integer, default=0)  # For ordering scenes
    location = Column(String(255))
    generation_log = Column(JSON)  # Track AI generation history
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stories = relationship("Story", secondary="story_characters", back_populates="characters")


class World(Base):
    __tablename__ = "worlds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    lore = Column(Text)  # Full world lore/content
    history = Column(Text)
    geography = Column(Text)
    culture = Column(Text)
    magic_system = Column(Text)
    technology_level = Column(String(100))
    generation_log = Column(JSON)  # Track AI generation history
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
