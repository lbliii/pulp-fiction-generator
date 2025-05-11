"""
YAML-based crew configurations using the CrewBase decorator.

This module implements crews using the recommended YAML configuration
approach from the CrewAI documentation.
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Try to import the CrewBase decorator, but provide fallback for older CrewAI versions
try:
    from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
    YAML_SUPPORT = True
except ImportError:
    logger.warning(
        "CrewAI YAML project decorators not available. "
        "Using fallback implementation. Consider upgrading to CrewAI >=0.25.0"
    )
    YAML_SUPPORT = False
    
    # Define dummy decorators as fallbacks
    def CrewBase(cls):
        return cls
        
    def agent(func):
        return func
        
    def task(func):
        return func
        
    def crew(func):
        return func
        
    def before_kickoff(func):
        return func
        
    def after_kickoff(func):
        return func

from crewai import Agent, Task, Crew, Process

from ..agents.agent_factory import AgentFactory
from ..models.model_service import ModelService
from .event_listeners import get_default_listeners
from .process_utils import validate_process_config, get_process_from_string, get_process_description


@CrewBase
class StoryGenerationCrew:
    """Base crew for story generation using YAML configuration."""
    
    def __init__(
        self, 
        genre: str,
        agent_factory: AgentFactory,
        model_service: ModelService,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the story generation crew.
        
        Args:
            genre: The genre for story generation
            agent_factory: Factory for creating agents
            model_service: Service for model interactions
            config: Optional configuration overrides
        """
        self.genre = genre
        self.agent_factory = agent_factory
        self.model_service = model_service
        self.config = config or {}
        
    @agent
    def researcher(self) -> Agent:
        """Create a researcher agent for the crew."""
        return self.agent_factory.create_researcher(self.genre)
    
    @agent
    def worldbuilder(self) -> Agent:
        """Create a worldbuilder agent for the crew."""
        return self.agent_factory.create_worldbuilder(self.genre)
    
    @agent
    def character_creator(self) -> Agent:
        """Create a character creator agent for the crew."""
        return self.agent_factory.create_character_creator(self.genre)
    
    @agent
    def plotter(self) -> Agent:
        """Create a plotter agent for the crew."""
        return self.agent_factory.create_plotter(self.genre)
    
    @agent
    def writer(self) -> Agent:
        """Create a writer agent for the crew."""
        return self.agent_factory.create_writer(self.genre)
    
    @agent
    def editor(self) -> Agent:
        """Create an editor agent for the crew."""
        return self.agent_factory.create_editor(self.genre)
    
    @agent
    def manager(self) -> Agent:
        """Create a manager agent for hierarchical processes."""
        # Use model_service to get a suitable LLM for the manager
        manager_llm = self.model_service.get_planning_llm()
        
        # Create a manager agent with enhanced capabilities
        return Agent(
            role="Story Manager",
            goal="Coordinate the story creation process and ensure all components work together harmoniously",
            backstory="An experienced editor-in-chief with deep knowledge of storytelling and team coordination",
            verbose=True,
            llm=manager_llm,
            allow_delegation=True  # Important for hierarchical process
        )
    
    @task
    def research_task(self) -> Task:
        """Create a research task for the crew."""
        return Task(
            description=f"Research essential elements of {self.genre} pulp fiction, "
                      f"including common tropes, historical context, and reference materials. "
                      f"Create a comprehensive research brief that other agents can use.",
            agent=self.researcher(),
            expected_output="A detailed research brief with genre elements, tropes, historical context, and references"
        )
    
    @task
    def worldbuilding_task(self) -> Task:
        """Create a worldbuilding task for the crew."""
        return Task(
            description=f"Based on the research brief, create a vivid and immersive {self.genre} world "
                      f"with appropriate atmosphere, rules, and distinctive features. "
                      f"Define the primary locations where the story will unfold.",
            agent=self.worldbuilder(),
            expected_output="A detailed world description with locations, atmosphere, and rules"
        )
    
    @task
    def character_task(self) -> Task:
        """Create a character creation task for the crew."""
        return Task(
            description=f"Create compelling {self.genre} characters that fit the world. "
                      f"Develop a protagonist, an antagonist, and key supporting characters "
                      f"with clear motivations, backgrounds, and relationships.",
            agent=self.character_creator(),
            expected_output="Character profiles for all main characters including motivations and relationships"
        )
    
    @task
    def plot_task(self) -> Task:
        """Create a plot development task for the crew."""
        return Task(
            description=f"Using the established world and characters, develop a {self.genre} plot "
                      f"with appropriate structure, pacing, and twists. Create an outline "
                      f"of the main events and ensure it follows {self.genre} conventions while "
                      f"remaining fresh and engaging.",
            agent=self.plotter(),
            expected_output="A detailed plot outline with key events, conflicts, and resolution"
        )
    
    @task
    def writing_task(self) -> Task:
        """Create a writing task for the crew."""
        return Task(
            description=f"Write the {self.genre} story based on the world, characters, and plot outline. "
                      f"Use appropriate style, voice, and dialogue for the genre. "
                      f"Create vivid descriptions and engaging narrative.",
            agent=self.writer(),
            expected_output="A complete draft of the story with appropriate style and voice"
        )
    
    @task
    def editing_task(self) -> Task:
        """Create an editing task for the crew."""
        return Task(
            description=f"Review and refine the {self.genre} story draft. Ensure consistency in "
                      f"plot, characters, and setting. Polish the prose while maintaining "
                      f"the appropriate {self.genre} style. Correct any errors or inconsistencies.",
            agent=self.editor(),
            expected_output="A polished, final version of the story"
        )
    
    @before_kickoff
    def setup(self):
        """Set up before the crew is kicked off."""
        print(f"Starting story generation for {self.genre} genre...")
    
    @after_kickoff
    def cleanup(self, result):
        """Clean up after the crew has finished execution."""
        print(f"Story generation for {self.genre} genre completed!")
        # You could save results to file, update a database, etc.
        return result
    
    @crew
    def build(self) -> Crew:
        """Build the crew with all components."""
        # Get process type from config
        process_type = self.config.get("process", "sequential")
        
        # Convert string to Process enum
        try:
            process = get_process_from_string(process_type)
        except ValueError as e:
            logger.warning(f"Invalid process type '{process_type}': {e}. Falling back to sequential.")
            process = Process.sequential
        
        # Validate process configuration
        is_valid, error_message = validate_process_config(process, self.config)
        if not is_valid:
            logger.warning(f"Invalid process configuration: {error_message}. Falling back to sequential.")
            process = Process.sequential
        
        # Log the process being used
        logger.info(f"Using {process} process: {get_process_description(process)}")
        
        # Get memory configuration from config
        memory_enabled = self.config.get("memory", True)
        
        # Get detailed memory configuration from config or use defaults
        memory_config = self.config.get("memory_config", {"provider": "local"})
        
        # Enhanced memory configuration
        from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
        from crewai.memory.storage.rag_storage import RAGStorage
        from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
        import os
        
        # Set up storage directory - use config setting if available, or default to .memory
        storage_dir = self.config.get("memory_storage_dir", "./.memory")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Set up base path for memory components
        base_path = os.path.join(storage_dir, self.genre.lower().replace(" ", "_"))
        os.makedirs(base_path, exist_ok=True)
        
        # Configure embeddings
        default_embedder = {"provider": "openai", "config": {"model": "text-embedding-3-small"}}
        embedder_config = self.config.get("embedder", default_embedder)
        
        # Create memory components if enabled
        long_term_memory = None
        short_term_memory = None
        entity_memory = None
        
        if memory_enabled:
            # Configure long-term memory
            if self.config.get("long_term_memory_enabled", True):
                ltm_path = os.path.join(base_path, "long_term_memory.db")
                long_term_memory = LongTermMemory(
                    storage=LTMSQLiteStorage(db_path=ltm_path)
                )
            
            # Configure short-term memory with RAG
            if self.config.get("short_term_memory_enabled", True):
                short_term_memory = ShortTermMemory(
                    storage=RAGStorage(
                        embedder_config=embedder_config,
                        type="short_term",
                        path=base_path
                    )
                )
            
            # Configure entity memory with RAG
            if self.config.get("entity_memory_enabled", True):
                entity_memory = EntityMemory(
                    storage=RAGStorage(
                        embedder_config=embedder_config,
                        type="entity",
                        path=base_path
                    )
                )
        
        # Configure function calling LLM if needed
        function_calling_llm = None
        if self.config.get("use_function_calling_llm", True):
            function_calling_llm = self.model_service.get_function_calling_llm()
            
        # Determine if we need a manager agent
        manager_agent = None
        if process == Process.hierarchical:
            manager_agent = self.manager()
            
        # Get event listeners
        event_listeners = []
        if self.config.get("use_event_listeners", True):
            # Handle both dictionary and list format for event_listeners in config
            config_listeners = self.config.get("event_listeners", {})
            if isinstance(config_listeners, dict) and "listeners" in config_listeners:
                event_listeners = config_listeners["listeners"]
            elif isinstance(config_listeners, list):
                event_listeners = config_listeners
            else:
                # Use default listeners as a fallback
                event_listeners = get_default_listeners()
            
        # Build tasks list (the order matters for sequential process)
        tasks = [
            self.research_task(),
            self.worldbuilding_task(),
            self.character_task(),
            self.plot_task(),
            self.writing_task(),
            self.editing_task()
        ]
        
        # Build agents list
        agents = [
            self.researcher(),
            self.worldbuilder(),
            self.character_creator(),
            self.plotter(),
            self.writer(),
            self.editor()
        ]
        
        # Add manager to agents if using hierarchical process
        if process == Process.hierarchical and manager_agent:
            agents.append(manager_agent)
            
        # Build and return the crew
        return Crew(
            agents=agents,
            tasks=tasks,
            verbose=self.config.get("verbose", True),
            process=process,
            memory=memory_enabled,
            memory_config=memory_config,
            output_log_file=self.config.get("output_log_file", f"logs/{self.genre}_story_generation.json"),
            cache=self.config.get("cache", True),
            name=f"{self.genre.capitalize()}StoryGenerationCrew",
            step_callback=self.config.get("step_callback"),
            task_callback=self.config.get("task_callback"),
            planning=self.config.get("enable_planning", True),
            planning_llm=self.model_service.get_planning_llm() if self.config.get("enable_planning", True) else None,
            callbacks=event_listeners,
            function_calling_llm=function_calling_llm,
            manager_agent=manager_agent,
            prompt_file=self.config.get("prompt_file"),
            embedder=embedder_config,
            # Enhanced memory components
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,
            entity_memory=entity_memory
        ) 