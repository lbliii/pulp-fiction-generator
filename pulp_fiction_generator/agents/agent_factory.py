"""
Main agent factory orchestrator.

This module provides the high-level agent factory that orchestrates the
creation of different types of agents by delegating to specialized factories.
"""

from typing import Any, Dict, List, Optional, Tuple
import os
import re
import yaml
import importlib.resources

from crewai import Agent, Task
# Import from crewai.tools directly only what's available
from crewai.tools import tool

from ..models.model_service import ModelService
from .config.config_loader import AgentConfigLoader
from .builder.agent_builder import AgentBuilder
from .factories.creative_agent_factory import CreativeAgentFactory
from .factories.content_agent_factory import ContentAgentFactory
from .factories.support_agent_factory import SupportAgentFactory
from ..utils.errors import logger
from ..utils.file_utils import read_yaml_file, load_templates


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
        
        self.templates = self._load_agent_templates()
        self.agent_config_cache = {}
    
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
    
    def create_agent(
        self,
        agent_type: str,
        genre: Optional[str] = None,
        deterministic_id: Optional[str] = None
    ) -> Agent:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create (e.g., "writer", "editor")
            genre: Optional genre context for the agent
            deterministic_id: Optional ID to create deterministic fingerprints
            
        Returns:
            Configured Agent instance
        """
        # Get the agent config
        agent_config = self.get_agent_config(agent_type, genre)
        
        # Clone the config to avoid modifying the cached version
        agent_config = {**agent_config}
        
        # Add genre to the config if provided
        if genre:
            agent_config["genre"] = genre
        
        # Create the agent
        agent = self.agent_builder.build_agent(
            config=agent_config,
            verbose=self.verbose,
            deterministic_id=deterministic_id or f"{agent_type}_{genre}" if genre else None
        )
        
        return agent
    
    def create_agents(self, agent_types: List[str], genre: Optional[str] = None) -> List[Agent]:
        """
        Create multiple agents.
        
        Args:
            agent_types: List of agent types to create
            genre: Optional genre context for all agents
            
        Returns:
            List of configured Agent instances
        """
        agents = []
        for i, agent_type in enumerate(agent_types):
            # Create a deterministic ID using position for consistent fingerprints within a sequence
            deterministic_id = f"{genre}_{agent_type}_{i}" if genre else f"{agent_type}_{i}"
            agent = self.create_agent(agent_type, genre, deterministic_id)
            agents.append(agent)
        return agents
    
    def create_task(
        self,
        description: str,
        agent: Optional[Agent] = None,
        agent_type: Optional[str] = None,
        genre: Optional[str] = None,
        expected_output: Optional[str] = None,
        context: Optional[str] = None
    ) -> Task:
        """
        Create a task for an agent.
        
        Args:
            description: Task description
            agent: Optional agent to assign the task to
            agent_type: Optional agent type to create if agent not provided
            genre: Optional genre context for the task
            expected_output: Optional expected output description
            context: Optional additional context for the task
            
        Returns:
            Configured Task instance
        """
        # Create an agent if needed
        if agent is None and agent_type is not None:
            agent = self.create_agent(agent_type, genre)
        elif agent is None:
            raise ValueError("Either agent or agent_type must be provided")
            
        # Apply genre-specific modifications to the task description if needed
        if genre:
            description = self._adapt_task_to_genre(description, genre)
            
        # Create the task
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context
        )
        
        # Store deterministic ID and agent information in task fingerprint metadata
        if hasattr(task, "security_config") and hasattr(task.security_config, "fingerprint"):
            fingerprint = task.security_config.fingerprint
            metadata = fingerprint.metadata or {}
            
            # Add metadata to the fingerprint
            metadata.update({
                "agent_role": agent.role if hasattr(agent, "role") else str(agent),
                "agent_fingerprint": agent.fingerprint.uuid_str if hasattr(agent, "fingerprint") else None,
                "genre": genre,
                "task_type": self._infer_task_type(description)
            })
            
            # Set the updated metadata
            fingerprint.metadata = metadata
            
        return task
    
    def create_tasks(
        self,
        descriptions: List[str],
        genre: Optional[str] = None,
        agent_types: Optional[List[str]] = None,
        agents: Optional[List[Agent]] = None
    ) -> List[Task]:
        """
        Create multiple tasks.
        
        Args:
            descriptions: List of task descriptions
            genre: Optional genre context for all tasks
            agent_types: Optional list of agent types to create if agents not provided
            agents: Optional list of agents to assign tasks to
            
        Returns:
            List of configured Task instances
        """
        tasks = []
        
        # Create agents if needed
        if agents is None and agent_types is not None:
            agents = self.create_agents(agent_types, genre)
        elif agents is None:
            raise ValueError("Either agents or agent_types must be provided")
            
        # Create tasks
        for i, (description, agent) in enumerate(zip(descriptions, agents)):
            task = self.create_task(
                description=description,
                agent=agent,
                genre=genre
            )
            tasks.append(task)
            
        return tasks
    
    def _infer_task_type(self, description: str) -> str:
        """
        Infer the task type from its description.
        
        Args:
            description: Task description
            
        Returns:
            Inferred task type
        """
        description_lower = description.lower()
        
        if any(term in description_lower for term in ["research", "analyze", "investigate"]):
            return "research"
        elif any(term in description_lower for term in ["world", "setting", "environment"]):
            return "worldbuilding"
        elif any(term in description_lower for term in ["character", "protagonist", "antagonist"]):
            return "character_development"
        elif any(term in description_lower for term in ["plot", "outline", "structure"]):
            return "plotting"
        elif any(term in description_lower for term in ["write", "author", "storytell"]):
            return "writing"
        elif any(term in description_lower for term in ["edit", "review", "feedback"]):
            return "editing"
        elif any(term in description_lower for term in ["summarize", "synopsis"]):
            return "summarization"
        else:
            return "general"
    
    def _load_agent_templates(self):
        """
        Load agent templates from the resources.
        
        Returns:
            Dictionary of loaded templates
        """
        templates = {}
        for resource in importlib.resources.contents(__name__):
            if resource.endswith('.yaml'):
                with importlib.resources.open_text(__name__, resource) as f:
                    templates[resource.split('.')[0]] = yaml.safe_load(f)
        return templates
    
    def get_agent_config(self, agent_type: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the configuration for a specific agent type.
        
        Args:
            agent_type: Type of agent to get configuration for
            genre: Optional genre context for the agent
            
        Returns:
            Configuration dictionary for the specified agent type
        """
        if (agent_type, genre) in self.agent_config_cache:
            return self.agent_config_cache[(agent_type, genre)]
        
        # Get the default configuration
        config = self.get_default_llm_config()
        
        # Apply genre-specific modifications if needed
        if genre:
            config["genre"] = genre
        
        # Apply any additional configuration overrides
        if agent_type in self.templates:
            config.update(self.templates[agent_type])
        
        # Cache the configuration
        self.agent_config_cache[(agent_type, genre)] = config
        return config
    
    def _adapt_task_to_genre(self, description: str, genre: str) -> str:
        """
        Adapt a task description to a specific genre.
        
        Args:
            description: Task description
            genre: Genre to adapt the task description for
            
        Returns:
            Adapted task description
        """
        # Implement genre-specific adaptation logic here
        return description
    
    def create_agent_from_template(self, template_name: str, genre: Optional[str] = None) -> Agent:
        """
        Create an agent from a template.
        
        Args:
            template_name: Name of the template to use
            genre: Optional genre context for the agent
            
        Returns:
            Configured Agent instance
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        # Create the agent from the template
        agent = self.create_agent(
            agent_type=template_name,
            genre=genre
        )
        
        return agent 