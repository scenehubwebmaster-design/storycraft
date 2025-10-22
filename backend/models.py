from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table, Boolean, Float
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


# Reference table for official documentation (classes, species, equipment, etc.)
class Reference(Base):
    __tablename__ = "references"

    id = Column(Integer, primary_key=True, index=True)
    ref_type = Column(String(100), nullable=False, index=True)  # e.g., 'class', 'species', 'equipment', 'origin'
    key = Column(String(255), nullable=False, index=True)  # machine key/slug
    title = Column(String(255), nullable=False)
    content = Column(Text)  # Markdown or HTML content
    source_url = Column(String(1024))
    
    # Metadata fields for filtering and enhanced search
    level = Column(Integer, nullable=True, index=True)  # Spell level (0-9), character level, item level
    rarity = Column(String(50), nullable=True, index=True)  # Common, Uncommon, Rare, Very Rare, Legendary, Artifact
    school = Column(String(100), nullable=True)  # Spell school: Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation
    category = Column(String(100), nullable=True)  # Item category: Weapon, Armor, Wondrous Item, Potion, etc.
    tags = Column(JSON, nullable=True)  # Flexible tagging: ["fire", "area", "damage"], ["healing"], ["stealth"], etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ref_type": self.ref_type,
            "key": self.key,
            "title": self.title,
            "content": self.content,
            "source_url": self.source_url,
            "level": self.level,
            "rarity": self.rarity,
            "school": self.school,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Monster stats table for structured D&D monsters
class MonsterStat(Base):
    __tablename__ = "monster_stats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), unique=True)
    url = Column(String(1024))
    cr = Column(String(50))
    numeric_cr = Column(Float)
    ac = Column(String(255))
    hp = Column(String(255))
    speed = Column(String(255))
    str = Column(Integer)
    dex = Column(Integer)
    con = Column(Integer)
    int = Column(Integer)
    wis = Column(Integer)
    cha = Column(Integer)
    senses = Column(String(255))
    languages = Column(String(255))
    damage = Column(Text)
    saving_throws = Column(Text)
    damage_resistances = Column(Text)
    damage_immunities = Column(Text)
    condition_immunities = Column(Text)
    traits = Column(Text)  # JSON or plain text
    actions = Column(Text)
    reactions = Column(Text)
    legendary_actions = Column(Text)
    source = Column(String(255))
    raw_html = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Embeddings for monsters stored via ORM for faster retrieval
class MonsterEmbedding(Base):
    __tablename__ = "monster_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    monster_id = Column(Integer, ForeignKey("monster_stats.id"), unique=True, index=True)
    vector = Column(Text)  # JSON-encoded vector
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Embeddings for references (classes, spells, equipment, etc.) for RAG retrieval
class ReferenceEmbedding(Base):
    __tablename__ = "reference_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(Integer, ForeignKey("references.id"), unique=True, index=True)
    vector = Column(Text)  # JSON-encoded vector
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Document chunks for better RAG retrieval (split long documents into retrievable chunks)
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("references.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order within document (0, 1, 2, ...)
    chunk_text = Column(Text, nullable=False)  # The actual chunk content
    heading = Column(String(255), nullable=True)  # Section heading if any
    token_count = Column(Integer, nullable=True)  # Approximate token count
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Embeddings for document chunks
class ChunkEmbedding(Base):
    __tablename__ = "chunk_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), unique=True, index=True)
    vector = Column(Text)  # JSON-encoded vector (384-dim from sentence-transformers)
    model = Column(String(100), nullable=True)  # Track which model was used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Chat session storage for persistent DM conversations (RAG-ready)
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    provider = Column(String(100), nullable=True)  # e.g., 'groq', 'openai'
    model = Column(String(255), nullable=True)
    include_context = Column(Boolean, default=True)  # whether to include retrieval context
    top_k = Column(Integer, default=5)
    meta = Column(JSON, nullable=True)  # misc session-level metadata
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.message_index",
    )

    def to_dict(self, include_messages=True):
        base = {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "provider": self.provider,
            "model": self.model,
            "include_context": self.include_context,
            "top_k": self.top_k,
            "metadata": self.meta,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            base["messages"] = [m.to_dict() for m in (self.messages or [])]
        return base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # 'user', 'dm', 'system', 'assistant'
    content = Column(Text, nullable=False)
    message_index = Column(Integer, nullable=False, default=0, index=True)
    tokens = Column(Integer, nullable=True)
    meta = Column(JSON, nullable=True)  # per-message metadata (e.g., retrieval provenance)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to session
    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "message_index": self.message_index,
            "tokens": self.tokens,
            "metadata": self.meta,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

