"""
AgentFactory creates and configures specialized agents for the story generation process.
"""

import os
from typing import Any, Dict, List, Optional, Union

import yaml
import glob

from crewai import Agent, Task
from pydantic import BaseModel

from ..models.model_service import ModelService
from ..models.crewai_adapter import CrewAIModelAdapter


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    tools: Optional[List[Any]] = None


class AgentFactory:
    """
    Factory for creating specialized agents for story generation.
    
    This factory handles the creation and configuration of specialized agents
    based on genre, user preferences, and other parameters.
    """
    
    def __init__(
        self, 
        model_service: ModelService,
        config_dir: str = "pulp_fiction_generator/agents/configs",
        verbose: bool = False
    ):
        """
        Initialize the agent factory.
        
        Args:
            model_service: Service for model interactions
            config_dir: Directory containing agent configurations
            verbose: Whether to enable verbose output for agents
        """
        self.model_service = model_service
        self.config_dir = config_dir
        self.verbose = verbose
        
        # Create a CrewAI-compatible wrapper for the model service
        self.crewai_model = CrewAIModelAdapter(ollama_adapter=model_service)
        
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
    
    def create_researcher(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a researcher agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured researcher agent
        """
        # Get base configuration
        agent_config = self._get_base_config("researcher", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_worldbuilder(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a worldbuilder agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured worldbuilder agent
        """
        # Get base configuration
        agent_config = self._get_base_config("worldbuilder", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_character_creator(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a character creator agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured character creator agent
        """
        # Get base configuration
        agent_config = self._get_base_config("character_creator", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_plotter(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a plotter agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured plotter agent
        """
        # Get base configuration
        agent_config = self._get_base_config("plotter", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_writer(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a writer agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured writer agent
        """
        # Get base configuration
        agent_config = self._get_base_config("writer", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_editor(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create an editor agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured editor agent
        """
        # Get base configuration
        agent_config = self._get_base_config("editor", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=agent_config.get("verbose", self.verbose),
            allow_delegation=agent_config.get("allow_delegation", False),
            llm=self.crewai_model,  # Use the CrewAI-compatible adapter
            tools=agent_config.get("tools", [])
        )
    
    def create_agent(self, agent_type: str, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            genre: Genre for the agent
            config: Optional configuration overrides
            
        Returns:
            A configured agent of the specified type
            
        Raises:
            ValueError: If the agent type is not recognized
        """
        create_methods = {
            "researcher": self.create_researcher,
            "worldbuilder": self.create_worldbuilder,
            "character_creator": self.create_character_creator,
            "plotter": self.create_plotter,
            "writer": self.create_writer,
            "editor": self.create_editor
        }
        
        if agent_type not in create_methods:
            raise ValueError(f"Unknown agent type: {agent_type}. Valid types: {', '.join(create_methods.keys())}")
            
        return create_methods[agent_type](genre, config)
    
    def _get_base_config(self, agent_type: str, genre: str) -> Dict[str, Any]:
        """
        Get the base configuration for an agent.
        
        Args:
            agent_type: Type of agent
            genre: Genre for the agent
            
        Returns:
            Dictionary with the agent's base configuration
            
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