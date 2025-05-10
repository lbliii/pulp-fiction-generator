"""
Configuration loading for agents.
"""

import os
import yaml
from typing import Any, Dict


class AgentConfigLoader:
    """
    Responsible for loading and managing agent configurations.
    
    This class handles the configuration file loading, creation of default
    configurations, and management of configuration overrides.
    """
    
    def __init__(self, config_dir: str = "pulp_fiction_generator/agents/configs"):
        """
        Initialize the configuration loader.
        
        Args:
            config_dir: Directory containing agent configurations
        """
        self.config_dir = config_dir
        
        # Ensure config directories exist
        self._ensure_config_dirs()
    
    def _ensure_config_dirs(self):
        """
        Ensure the configuration directories exist, create them if they don't.
        Also create default configs if none exist.
        """
        # Ensure base config dir exists
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            
        # Ensure generic config dir exists
        generic_dir = os.path.join(self.config_dir, "generic")
        if not os.path.exists(generic_dir):
            os.makedirs(generic_dir, exist_ok=True)
            
        # Create default configs if they don't exist
        self._create_default_config_if_missing(
            "researcher", 
            {
                "role": "Pulp Fiction Research Specialist",
                "goal": "Uncover genre-appropriate elements, historical context, and reference material",
                "backstory": "A meticulous researcher with deep knowledge of pulp fiction history across multiple genres",
                "verbose": True,
                "allow_delegation": False
            }
        )
        
        self._create_default_config_if_missing(
            "worldbuilder", 
            {
                "role": "Pulp Fiction World Architect",
                "goal": "Create vivid, immersive settings with appropriate atmosphere and rules",
                "backstory": "A visionary designer who excels at crafting the perfect backdrop for pulp stories",
                "verbose": True,
                "allow_delegation": False
            }
        )
        
        self._create_default_config_if_missing(
            "character_creator", 
            {
                "role": "Pulp Character Designer",
                "goal": "Develop memorable, genre-appropriate characters with clear motivations",
                "backstory": "A character specialist who understands the archetypes and psychology of pulp fiction protagonists and antagonists",
                "verbose": True,
                "allow_delegation": False
            }
        )
        
        self._create_default_config_if_missing(
            "plotter", 
            {
                "role": "Pulp Fiction Narrative Architect",
                "goal": "Craft engaging plot structures with appropriate pacing and twists",
                "backstory": "A master storyteller with expertise in pulp narrative structures and cliffhangers",
                "verbose": True,
                "allow_delegation": False
            }
        )
        
        self._create_default_config_if_missing(
            "writer", 
            {
                "role": "Pulp Fiction Prose Specialist",
                "goal": "Generate engaging, genre-appropriate prose that brings the story to life",
                "backstory": "A wordsmith with a knack for capturing the distinctive voice of various pulp fiction genres",
                "verbose": True,
                "allow_delegation": False
            }
        )
        
        self._create_default_config_if_missing(
            "editor", 
            {
                "role": "Pulp Fiction Refiner",
                "goal": "Polish and improve the story while maintaining voice and consistency",
                "backstory": "A detail-oriented editor with experience improving pulp fiction while preserving its essence",
                "verbose": True,
                "allow_delegation": False
            }
        )
    
    def _create_default_config_if_missing(self, agent_type: str, config: Dict[str, Any]):
        """
        Create a default configuration file if one doesn't exist.
        
        Args:
            agent_type: Type of agent
            config: Configuration to save
        """
        config_path = os.path.join(self.config_dir, "generic", f"{agent_type}.yaml")
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
    
    def get_config(self, agent_type: str, genre: str) -> Dict[str, Any]:
        """
        Get the configuration for an agent.
        
        Args:
            agent_type: Type of agent
            genre: Genre for the agent
            
        Returns:
            Dictionary with the agent's configuration
            
        Raises:
            ValueError: If the configuration file is not found
        """
        # Try to find a genre-specific configuration
        genre_config_path = os.path.join(self.config_dir, genre, f"{agent_type}.yaml")
        
        # Fall back to a generic configuration if genre-specific not found
        generic_config_path = os.path.join(self.config_dir, "generic", f"{agent_type}.yaml")
        
        config_path = genre_config_path if os.path.exists(genre_config_path) else generic_config_path
        
        if not os.path.exists(config_path):
            raise ValueError(f"Cannot find configuration for {agent_type} in genre {genre}")
            
        # Load the configuration
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            
        return config 