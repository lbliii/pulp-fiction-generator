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
    genre: Optional[str] = None
    title: Optional[str] = None
    
    # Basic artifacts
    research: Optional[str] = None
    worldbuilding: Optional[str] = None
    characters: Optional[str] = None
    plot: Optional[str] = None
    draft: Optional[str] = None
    final_story: Optional[str] = None
    
    # Conditional task artifacts
    research_expanded: Optional[str] = None
    characters_enhanced: Optional[str] = None
    plot_twist: Optional[str] = None
    style_improved: Optional[str] = None
    consistency_fixed: Optional[str] = None
    
    # Raw tool outputs
    raw_genre_research: Optional[str] = None
    raw_reference_data: Optional[str] = None
    raw_character_references: Optional[str] = None
    raw_style_examples: Optional[str] = None
    raw_plot_structures: Optional[str] = None
    raw_image_descriptions: Optional[Dict[str, str]] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if all essential story artifacts have been generated."""
        return all([
            self.research,
            self.worldbuilding,
            self.characters,
            self.plot,
            self.draft,
            self.final_story
        ])
    
    @property
    def has_conditional_content(self) -> bool:
        """Check if any conditional task artifacts were generated."""
        return any([
            self.research_expanded,
            self.characters_enhanced,
            self.plot_twist,
            self.style_improved,
            self.consistency_fixed
        ])
    
    @property
    def has_raw_tool_outputs(self) -> bool:
        """Check if any raw tool outputs were captured."""
        return any([
            self.raw_genre_research,
            self.raw_reference_data,
            self.raw_character_references,
            self.raw_style_examples,
            self.raw_plot_structures,
            self.raw_image_descriptions
        ])
    
    def get_conditional_artifacts(self) -> Dict[str, str]:
        """Get a dictionary of all conditional artifacts that were generated."""
        result = {}
        if self.research_expanded:
            result["research_expanded"] = self.research_expanded
        if self.characters_enhanced:
            result["characters_enhanced"] = self.characters_enhanced
        if self.plot_twist:
            result["plot_twist"] = self.plot_twist
        if self.style_improved:
            result["style_improved"] = self.style_improved
        if self.consistency_fixed:
            result["consistency_fixed"] = self.consistency_fixed
        return result
        
    def get_raw_tool_outputs(self) -> Dict[str, Any]:
        """Get a dictionary of all raw tool outputs that were captured."""
        result = {}
        if self.raw_genre_research:
            result["raw_genre_research"] = self.raw_genre_research
        if self.raw_reference_data:
            result["raw_reference_data"] = self.raw_reference_data
        if self.raw_character_references:
            result["raw_character_references"] = self.raw_character_references
        if self.raw_style_examples:
            result["raw_style_examples"] = self.raw_style_examples
        if self.raw_plot_structures:
            result["raw_plot_structures"] = self.raw_plot_structures
        if self.raw_image_descriptions:
            result["raw_image_descriptions"] = self.raw_image_descriptions
        return result 