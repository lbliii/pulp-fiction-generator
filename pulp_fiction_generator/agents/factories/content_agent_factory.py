"""
Factory for creating content generation agents.
"""

from typing import Any, Dict, Optional
from crewai import Agent

from ..config.config_loader import AgentConfigLoader
from ..builder.agent_builder import AgentBuilder


class ContentAgentFactory:
    """
    Factory for creating content generation agents like plotters and writers.
    
    This class specializes in creating agents focused on the narrative and 
    writing aspects of story generation.
    """
    
    def __init__(
        self, 
        config_loader: AgentConfigLoader,
        agent_builder: AgentBuilder,
        verbose: bool = False
    ):
        """
        Initialize the content agent factory.
        
        Args:
            config_loader: Configuration loader
            agent_builder: Agent builder
            verbose: Whether to enable verbose output for agents
        """
        self.config_loader = config_loader
        self.agent_builder = agent_builder
        self.verbose = verbose
    
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
        agent_config = self.config_loader.get_config("plotter", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return self.agent_builder.build_agent(agent_config, self.verbose)
    
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
        agent_config = self.config_loader.get_config("writer", genre)
        
        # Apply any overrides
        if config:
            agent_config.update(config)
        
        # Create the agent
        return self.agent_builder.build_agent(agent_config, self.verbose) 