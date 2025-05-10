"""
Base classes for plot templates and structures.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional


class NarrativeArc(Enum):
    """Enumeration of common narrative arc types"""
    
    HEROS_JOURNEY = "hero's_journey"
    THREE_ACT = "three_act"
    FIVE_ACT = "five_act"
    FREYTAGS_PYRAMID = "freytags_pyramid"
    SEVEN_POINT = "seven_point"
    SAVE_THE_CAT = "save_the_cat"
    KISHŌTENKETSU = "kishōtenketsu"
    SINNER_SAINT = "sinner_saint"


class PlotPoint:
    """
    A plot point represents a specific event or story beat in a plot.
    """
    
    def __init__(
        self, 
        name: str,
        description: str,
        examples: Optional[List[str]] = None,
        features: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a plot point.
        
        Args:
            name: The name of the plot point
            description: Description of what this plot point entails
            examples: Optional examples of this plot point in well-known stories
            features: Additional features or metadata for this plot point
        """
        self.name = name
        self.description = description
        self.examples = examples or []
        self.features = features or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plot point to a dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "examples": self.examples,
            "features": self.features,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlotPoint':
        """Create a plot point from a dictionary"""
        return cls(
            name=data["name"],
            description=data["description"],
            examples=data.get("examples", []),
            features=data.get("features", {})
        )


class PlotStructure:
    """
    A plot structure defines a sequence of plot points that form a narrative.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        plot_points: List[PlotPoint],
        narrative_arc: Optional[NarrativeArc] = None,
        genre_affinities: Optional[Dict[str, float]] = None
    ):
        """
        Initialize a plot structure.
        
        Args:
            name: The name of this plot structure
            description: Description of what this plot structure represents
            plot_points: The sequence of plot points that make up this structure
            narrative_arc: The narrative arc this structure follows
            genre_affinities: How well this structure works with different genres
                            (keys are genre names, values 0.0-1.0)
        """
        self.name = name
        self.description = description
        self.plot_points = plot_points
        self.narrative_arc = narrative_arc
        self.genre_affinities = genre_affinities or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the plot structure to a dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "plot_points": [pp.to_dict() for pp in self.plot_points],
            "narrative_arc": self.narrative_arc.value if self.narrative_arc else None,
            "genre_affinities": self.genre_affinities,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlotStructure':
        """Create a plot structure from a dictionary"""
        narrative_arc = None
        if data.get("narrative_arc"):
            try:
                narrative_arc = NarrativeArc(data["narrative_arc"])
            except ValueError:
                pass
                
        return cls(
            name=data["name"],
            description=data["description"],
            plot_points=[PlotPoint.from_dict(pp) for pp in data["plot_points"]],
            narrative_arc=narrative_arc,
            genre_affinities=data.get("genre_affinities", {})
        )


class PlotTemplate(ABC):
    """
    Abstract base class for plot templates.
    
    A plot template provides a blueprint for a story structure,
    including plot points, narrative arc, and genre-specific elements.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the plot template."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the plot template."""
        pass
    
    @property
    @abstractmethod
    def narrative_arc(self) -> NarrativeArc:
        """Return the narrative arc this plot template follows."""
        pass
    
    @abstractmethod
    def get_plot_structure(self) -> PlotStructure:
        """Return the plot structure for this template."""
        pass
    
    @abstractmethod
    def get_prompt_enhancement(self, agent_type: str) -> str:
        """
        Return a prompt enhancement for the given agent type.
        
        Args:
            agent_type: The type of agent (researcher, plotter, etc.)
            
        Returns:
            A prompt enhancement specific to this plot template
        """
        pass
    
    def get_suitable_genres(self) -> Dict[str, float]:
        """
        Return a dictionary of genres and their compatibility scores.
        
        Returns:
            Dict with genre names as keys and compatibility scores (0.0-1.0) as values
        """
        return {}


class PlotValidator:
    """
    Validates that a story follows a given plot structure.
    """
    
    def __init__(self, plot_structure: PlotStructure):
        """
        Initialize with a plot structure.
        
        Args:
            plot_structure: The plot structure to validate against
        """
        self.plot_structure = plot_structure
        
    def validate(self, story_text: str) -> Dict[str, Any]:
        """
        Validate a story against the plot structure.
        
        Args:
            story_text: The text of the story to validate
            
        Returns:
            A dict with validation results
        """
        # This would use AI to analyze the story and check if it follows the structure
        # For now we return a placeholder
        return {
            "valid": True,
            "missing_plot_points": [],
            "out_of_order_plot_points": [],
            "strength": 0.8,
            "suggestions": []
        } 