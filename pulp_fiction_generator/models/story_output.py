"""
Structured story output models using Pydantic.

These models enable consistent, typed responses from CrewAI for story generation.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Character model for structured story output."""
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role (protagonist, antagonist, etc.)")
    description: str = Field(..., description="Character description")
    motivation: Optional[str] = Field(None, description="Character motivation")
    background: Optional[str] = Field(None, description="Character background")


class Location(BaseModel):
    """Location model for structured story output."""
    name: str = Field(..., description="Location name")
    description: str = Field(..., description="Location description")
    significance: Optional[str] = Field(None, description="Location significance to the story")


class PlotPoint(BaseModel):
    """Plot point model for structured story output."""
    title: str = Field(..., description="Plot point title")
    description: str = Field(..., description="Plot point description")
    characters_involved: List[str] = Field(default_factory=list, description="Characters involved in this plot point")


class StoryOutput(BaseModel):
    """Story output model for structured CrewAI responses."""
    title: str = Field(..., description="Story title")
    genre: str = Field(..., description="Story genre")
    summary: str = Field(..., description="Brief summary of the story")
    characters: List[Character] = Field(default_factory=list, description="List of characters in the story")
    locations: List[Location] = Field(default_factory=list, description="List of locations in the story")
    plot_points: List[PlotPoint] = Field(default_factory=list, description="List of major plot points")
    full_text: str = Field(..., description="The complete story text")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata about the story") 