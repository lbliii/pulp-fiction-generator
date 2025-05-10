"""
Base classes and interfaces for genre definitions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GenreDefinition(ABC):
    """
    Abstract base class defining the interface for a pulp fiction genre.
    
    All genres must implement this interface to provide consistent
    functionality across the generator.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the internal name of the genre (for referencing in the system).
        
        Returns:
            The genre's internal name (e.g., "noir", "sci-fi")
        """
        pass
        
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Return the human-readable display name of the genre.
        
        Returns:
            The genre's display name (e.g., "Noir/Hardboiled Detective", "Science Fiction")
        """
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Return a description of the genre.
        
        Returns:
            A descriptive text explaining the genre
        """
        pass
        
    @abstractmethod
    def get_researcher_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the researcher agent.
        
        Returns:
            A string that will be added to the researcher agent's prompt
        """
        pass
        
    @abstractmethod
    def get_worldbuilder_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the worldbuilder agent.
        
        Returns:
            A string that will be added to the worldbuilder agent's prompt
        """
        pass
        
    @abstractmethod
    def get_character_creator_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the character creator agent.
        
        Returns:
            A string that will be added to the character creator agent's prompt
        """
        pass
        
    @abstractmethod
    def get_plotter_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the plotter agent.
        
        Returns:
            A string that will be added to the plotter agent's prompt
        """
        pass
        
    @abstractmethod
    def get_writer_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the writer agent.
        
        Returns:
            A string that will be added to the writer agent's prompt
        """
        pass
        
    @abstractmethod
    def get_editor_prompt_enhancer(self) -> str:
        """
        Return the prompt enhancer for the editor agent.
        
        Returns:
            A string that will be added to the editor agent's prompt
        """
        pass
        
    @abstractmethod
    def get_character_templates(self) -> List[Dict[str, Any]]:
        """
        Return a list of character templates for this genre.
        
        Returns:
            A list of character template dictionaries
        """
        pass
        
    @abstractmethod
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        """
        Return a list of plot templates for this genre.
        
        Returns:
            A list of plot template dictionaries
        """
        pass
        
    @abstractmethod
    def get_example_passages(self) -> List[Dict[str, str]]:
        """
        Return a list of example passages from this genre.
        
        Each passage should include the text and an attribution.
        
        Returns:
            A list of example passage dictionaries
        """
        pass
        
    @abstractmethod
    def get_typical_settings(self) -> List[Dict[str, str]]:
        """
        Return a list of typical settings for this genre.
        
        Returns:
            A list of setting dictionaries
        """
        pass
        
    def get_prompt_enhancer_for_agent(self, agent_type: str) -> str:
        """
        Get the prompt enhancer for a specific agent type.
        
        Args:
            agent_type: The type of agent to get the enhancer for
            
        Returns:
            The prompt enhancer string for the agent
            
        Raises:
            ValueError: If the agent type is unknown
        """
        enhancer_methods = {
            "researcher": self.get_researcher_prompt_enhancer,
            "worldbuilder": self.get_worldbuilder_prompt_enhancer,
            "character_creator": self.get_character_creator_prompt_enhancer,
            "plotter": self.get_plotter_prompt_enhancer,
            "writer": self.get_writer_prompt_enhancer,
            "editor": self.get_editor_prompt_enhancer
        }
        
        enhancer_method = enhancer_methods.get(agent_type.lower())
        if not enhancer_method:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        return enhancer_method() 