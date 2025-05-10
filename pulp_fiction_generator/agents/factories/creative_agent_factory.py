"""
Factory for creating creative agents.
"""

from typing import Any, Dict, Optional
from crewai import Agent

from ..config.config_loader import AgentConfigLoader
from ..builder.agent_builder import AgentBuilder


class CreativeAgentFactory:
    """
    Factory for creating creative agents like worldbuilders and character creators.
    
    This class specializes in creating agents focused on the creative aspects
    of story generation.
    """
    
    def __init__(
        self, 
        config_loader: AgentConfigLoader,
        agent_builder: AgentBuilder,
        verbose: bool = False
    ):
        """
        Initialize the creative agent factory.
        
        Args:
            config_loader: Configuration loader
            agent_builder: Agent builder
            verbose: Whether to enable verbose output for agents
        """
        self.config_loader = config_loader
        self.agent_builder = agent_builder
        self.verbose = verbose
    
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
        agent_config = self.config_loader.get_config("worldbuilder", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return self.agent_builder.build_agent(agent_config, self.verbose)
    
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
        agent_config = self.config_loader.get_config("character_creator", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return self.agent_builder.build_agent(agent_config, self.verbose) 