"""
Main agent factory orchestrator.

This module provides the high-level agent factory that orchestrates the
creation of different types of agents by delegating to specialized factories.
"""

from typing import Any, Dict, List, Optional

from crewai import Agent
# Import from crewai.tools directly only what's available
from crewai.tools import tool

from ..models.model_service import ModelService
from .config.config_loader import AgentConfigLoader
from .builder.agent_builder import AgentBuilder
from .factories.creative_agent_factory import CreativeAgentFactory
from .factories.content_agent_factory import ContentAgentFactory
from .factories.support_agent_factory import SupportAgentFactory


class AgentFactory:
    """
    Main factory for creating specialized agents for story generation.
    
    This factory delegates to specialized factories for different types of agents
    while providing a unified interface for agent creation.
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
        self.verbose = verbose
        
        # Set up component classes
        self.config_loader = AgentConfigLoader(config_dir=config_dir)
        self.agent_builder = AgentBuilder(model_service=model_service)
        
        # Set up specialized factories
        self.creative_factory = CreativeAgentFactory(
            config_loader=self.config_loader,
            agent_builder=self.agent_builder,
            verbose=verbose
        )
        
        self.content_factory = ContentAgentFactory(
            config_loader=self.config_loader,
            agent_builder=self.agent_builder,
            verbose=verbose
        )
        
        self.support_factory = SupportAgentFactory(
            config_loader=self.config_loader,
            agent_builder=self.agent_builder,
            verbose=verbose
        )
    
    def get_default_llm_config(self) -> Dict[str, Any]:
        """
        Get the default LLM configuration for agents.
        
        Returns:
            Default LLM configuration dictionary
        """
        # Get configuration from the model service
        return {
            "provider": self.model_service.provider,
            "model": self.model_service.model_name,
            "temperature": 0.7,
            "request_timeout": 180,
        }
    
    def get_manager_tools(self) -> List[Any]:
        """
        Get the tools for the manager agent.
        
        Returns:
            List of tools for the manager agent
        """
        # Define the search tool using crewai's tool decorator
        @tool
        def search_web(query: str) -> str:
            """Search the web for information about a topic"""
            return f"Web search results for: {query}"
        
        @tool
        def read_file(file_path: str) -> str:
            """Read the contents of a file"""
            try:
                with open(file_path, 'r') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @tool
        def list_directory(directory_path: str) -> str:
            """List the contents of a directory"""
            import os
            try:
                files = os.listdir(directory_path)
                return "\n".join(files)
            except Exception as e:
                return f"Error listing directory: {str(e)}"
        
        # Return the custom tools
        return [search_web, read_file, list_directory]
    
    def create_researcher(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a researcher agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured researcher agent
        """
        return self.support_factory.create_researcher(genre, config)
    
    def create_worldbuilder(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a worldbuilder agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured worldbuilder agent
        """
        return self.creative_factory.create_worldbuilder(genre, config)
    
    def create_character_creator(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a character creator agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured character creator agent
        """
        return self.creative_factory.create_character_creator(genre, config)
    
    def create_plotter(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a plotter agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured plotter agent
        """
        return self.content_factory.create_plotter(genre, config)
    
    def create_writer(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create a writer agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured writer agent
        """
        return self.content_factory.create_writer(genre, config)
    
    def create_editor(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create an editor agent for the specified genre.
        
        Args:
            genre: The genre to create the agent for
            config: Optional configuration overrides
            
        Returns:
            A configured editor agent
        """
        return self.support_factory.create_editor(genre, config)
    
    def create_agent(self, agent_type: str = None, genre: str = None, config: Optional[Dict[str, Any]] = None, role: str = None, tools: Optional[List[str]] = None) -> Agent:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create (deprecated, use role instead)
            genre: Genre for the agent
            config: Optional configuration overrides
            role: Role of the agent (alternative to agent_type)
            tools: Optional list of tools to provide to the agent
            
        Returns:
            A configured agent of the specified type
            
        Raises:
            ValueError: If the agent type is not recognized
        """
        # Use role if provided, otherwise fall back to agent_type
        agent_role = role or agent_type
        
        if not agent_role:
            raise ValueError("Either 'role' or 'agent_type' must be provided")
            
        if not genre:
            raise ValueError("Genre must be provided")
        
        create_methods = {
            "researcher": self.create_researcher,
            "worldbuilder": self.create_worldbuilder,
            "character_creator": self.create_character_creator,
            "plotter": self.create_plotter,
            "writer": self.create_writer,
            "editor": self.create_editor
        }
        
        if agent_role not in create_methods:
            raise ValueError(f"Unknown agent type: {agent_role}. Valid types: {', '.join(create_methods.keys())}")
        
        # Create a copy of the config to avoid modifying the original
        config_copy = {**(config or {})}
        
        # Add tools to config if provided
        if tools:
            config_copy["tools"] = tools
            
        return create_methods[agent_role](genre, config_copy) 