"""
Data models for story generation.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class StoryOutput(BaseModel):
    """Structured output for story content."""
    content: str
    word_count: int = Field(default=0)


class StoryArtifacts(BaseModel):
    """Container for all story generation artifacts."""
    genre: str
    title: str
    research: Optional[str] = None
    worldbuilding: Optional[str] = None
    characters: Optional[str] = None
    plot: Optional[str] = None
    draft: Optional[str] = None
    final_story: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if all story artifacts have been generated."""
        return all([
            self.research,
            self.worldbuilding,
            self.characters,
            self.plot,
            self.draft,
            self.final_story
        ]) 