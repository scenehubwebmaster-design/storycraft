"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
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


class ImageGenerationRequest(BaseModel):
    character_name: str = Field(..., description="Name of the character")
    appearance_text: str = Field(..., description="Physical appearance description")
    model: str = Field(default="imagen-4.0-fast-generate-001", description="Imagen model")
    aspect_ratio: str = Field(default="3:4", description="Image aspect ratio")
    custom_prompt: Optional[str] = Field(None, description="Optional custom prompt override")


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
