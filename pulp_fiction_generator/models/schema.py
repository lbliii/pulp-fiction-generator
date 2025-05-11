"""
Pydantic schema models for structured LLM responses.

This module defines structured data models that can be used with the LLM
for getting consistent, validated output formats.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Character model with key attributes."""
    name: str = Field(..., description="Character's full name")
    role: str = Field(..., description="Character's role in the story (e.g., protagonist, villain)")
    description: str = Field(..., description="Brief physical and personality description")
    motivation: str = Field(..., description="What drives this character's actions")
    background: Optional[str] = Field(None, description="Character's relevant backstory")


class PlotPoint(BaseModel):
    """A single plot point in the story."""
    summary: str = Field(..., description="Brief summary of what happens")
    characters_involved: List[str] = Field(..., description="Names of characters involved in this plot point")
    setting: str = Field(..., description="Location or setting where this occurs")
    impact: str = Field(..., description="How this plot point affects the story progression")


class Genre(str, Enum):
    """Supported genre types."""
    WESTERN = "western"
    NOIR = "noir"
    SCIFI = "science fiction"
    ADVENTURE = "adventure"
    HORROR = "horror"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    MYSTERY = "mystery"
    OTHER = "other"


class StoryOutline(BaseModel):
    """Complete story outline with structured components."""
    title: str = Field(..., description="Catchy title for the story")
    genre: Genre = Field(..., description="Primary genre of the story")
    premise: str = Field(..., description="One or two sentence summary of the story concept")
    setting: str = Field(..., description="Time period and location of the story")
    characters: List[Character] = Field(..., description="List of main characters")
    plot_points: List[PlotPoint] = Field(..., description="Major plot events in sequence")
    themes: List[str] = Field(..., description="Main themes explored in the story")
    tone: str = Field(..., description="Overall emotional tone of the story")


class StoryFeedback(BaseModel):
    """Structured feedback on a story."""
    strengths: List[str] = Field(..., description="Positive aspects of the story")
    weaknesses: List[str] = Field(..., description="Areas that need improvement")
    suggestions: List[str] = Field(..., description="Specific suggestions for improvement")
    overall_rating: int = Field(..., ge=1, le=10, description="Rating from 1-10")
    

class CreativeQuestion(BaseModel):
    """Model for creative questions and answers."""
    question: str = Field(..., description="The original question")
    direct_answer: str = Field(..., description="Direct answer to the question")
    creative_expansion: str = Field(..., description="Creative ideas building on the answer")
    references: List[str] = Field(default_factory=list, description="Optional references or examples")


class WorldBuildingElement(BaseModel):
    """A specific element of world-building."""
    name: str = Field(..., description="Name of the element")
    category: str = Field(..., description="Category (e.g., location, technology, custom)")
    description: str = Field(..., description="Detailed description of the element")
    significance: str = Field(..., description="How this element impacts the story world")


class WorldBuildingSchema(BaseModel):
    """Complete world-building information for a story setting."""
    setting_name: str = Field(..., description="Name of the world or setting")
    time_period: str = Field(..., description="Time period or era")
    physical_environment: str = Field(..., description="Description of geography, climate, etc.")
    cultural_elements: List[WorldBuildingElement] = Field(..., description="Cultural aspects")
    technology: List[WorldBuildingElement] = Field(..., description="Technology elements")
    political_structure: str = Field(..., description="Political system description")
    economic_system: str = Field(..., description="Economic system description")
    unique_elements: List[WorldBuildingElement] = Field(..., description="Unique or distinctive elements")


class WeaponsAnalysis(BaseModel):
    """Analysis of weapons for a story."""
    weapon_name: str = Field(..., description="Name of the weapon")
    type: str = Field(..., description="Type of weapon (e.g., firearm, melee)")
    description: str = Field(..., description="Physical description")
    historical_accuracy: str = Field(..., description="Assessment of historical accuracy")
    combat_effectiveness: str = Field(..., description="How effective it would be in combat")
    character_fit: Dict[str, str] = Field(..., description="How well it fits different character types")


class DateLocaleAnalysis(BaseModel):
    """Analysis of historical date and locale information."""
    time_period: str = Field(..., description="Time period being analyzed")
    location: str = Field(..., description="Geographic location")
    historical_events: List[str] = Field(..., description="Relevant historical events")
    cultural_details: List[str] = Field(..., description="Important cultural details")
    common_technology: List[str] = Field(..., description="Technology available in this period")
    speech_patterns: List[str] = Field(..., description="Typical speech patterns or phrases")
    clothing_styles: List[str] = Field(..., description="Common clothing styles")
    accuracy_notes: Optional[str] = Field(None, description="Notes on historical accuracy")


class DialogueSuggestions(BaseModel):
    """Suggestions for character dialogue."""
    character_name: str = Field(..., description="Name of the character")
    speaking_style: str = Field(..., description="Description of character's speech patterns")
    example_phrases: List[str] = Field(..., description="Example phrases this character might say")
    dialect_notes: Optional[str] = Field(None, description="Notes on dialect or accent")
    dialogue_suggestions: List[str] = Field(..., description="Suggested dialogue lines") 