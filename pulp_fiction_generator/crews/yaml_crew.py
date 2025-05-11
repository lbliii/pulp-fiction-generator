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
        # Get the configured agents
        agents = self.get_agents()
        
        # Get the configured tasks
        tasks = self.get_tasks(agents)
        
        # Get configured process
        process = self.get_process()
        
        # Check if memory is enabled
        memory_enabled = self.config.get("memory", True)
        
        # Get memory configuration
        memory_config = {
            "memory_retriever": self.config.get("memory_retriever"),
            "auto_embedding": self.config.get("auto_embedding", True),
            "memory_window": self.config.get("memory_window", 10)
        }
        
        # Get event listeners
        event_listeners = self.config.get("event_listeners", get_default_listeners())
        
        # Get function calling LLM
        function_calling_llm = None
        if self.config.get("use_function_calling_llm", True):
            function_calling_llm = self.model_service.get_function_calling_llm()
        
        # Get manager agent if specified
        manager_agent = None
        if self.config.get("manager_agent"):
            manager_agent = agents.get(self.config.get("manager_agent"))
            
        # Get embedder configuration
        embedder_config = self.config.get("embedder")
        
        # Check for enhanced memory components
        long_term_memory = self.config.get("long_term_memory")
        short_term_memory = self.config.get("short_term_memory")
        entity_memory = self.config.get("entity_memory")
        
        # Configure specialized LLMs based on phase
        planning_llm = None
        if self.config.get("enable_planning", True):
            planning_llm = self.model_service.get_planning_llm()
        
        # Use specialized LLMs for different phases of story generation
        worldbuilding_llm = None 
        if self.genre in ["fantasy", "scifi", "adventure"]:
            worldbuilding_llm = self.model_service.get_worldbuilding_llm()
            
        # Create a streaming LLM for longer outputs if supported
        streaming_llm = None
        if self.config.get("use_streaming", True):
            try:
                streaming_llm = self.model_service.get_streaming_llm()
            except Exception as e:
                logger.warning(f"Failed to create streaming LLM: {e}")
                
        # For outline phase, use structured output
        outline_llm = None
        if "outline" in self.config.get("enabled_phases", []):
            try:
                outline_llm = self.model_service.get_story_outline_llm()
            except Exception as e:
                logger.warning(f"Failed to create outline LLM: {e}")
                
        # For feedback or editing phases, use feedback LLM
        feedback_llm = None 
        if "feedback" in self.config.get("enabled_phases", []) or "editing" in self.config.get("enabled_phases", []):
            try:
                feedback_llm = self.model_service.get_feedback_llm()
            except Exception as e:
                logger.warning(f"Failed to create feedback LLM: {e}")
        
        # For creative writing, use the creative LLM
        creative_llm = None
        if "creative" in self.config.get("enabled_phases", []) or "draft" in self.config.get("enabled_phases", []):
            try:
                creative_llm = self.model_service.get_creative_llm()
            except Exception as e:
                logger.warning(f"Failed to create creative LLM: {e}")
        
        # For historical research, use historical analysis LLM
        historical_llm = None
        if "research" in self.config.get("enabled_phases", []) and self.genre in ["western", "noir", "historical"]:
            try:
                historical_llm = self.model_service.get_historical_analysis_llm()
            except Exception as e:
                logger.warning(f"Failed to create historical LLM: {e}")
                
        # Add all specialized LLMs to a dictionary
        specialized_llms = {
            "planning_llm": planning_llm,
            "worldbuilding_llm": worldbuilding_llm,
            "streaming_llm": streaming_llm,
            "outline_llm": outline_llm,
            "feedback_llm": feedback_llm,
            "creative_llm": creative_llm,
            "historical_llm": historical_llm
        }
        
        # Filter out None values
        specialized_llms = {k: v for k, v in specialized_llms.items() if v is not None}
        
        # Add specialized LLMs to the config for access in tasks
        for task in tasks:
            # Identify task phase from its description or ID
            task_id = getattr(task, "id", "")
            task_desc = getattr(task, "description", "")
            
            # Assign appropriate LLM based on the task
            if "outline" in task_id.lower() or "outline" in task_desc.lower():
                task.llm = outline_llm or task.llm
            elif "worldbuilding" in task_id.lower() or "worldbuilding" in task_desc.lower():
                task.llm = worldbuilding_llm or task.llm
            elif "draft" in task_id.lower() or "writing" in task_desc.lower():
                task.llm = creative_llm or streaming_llm or task.llm
            elif "feedback" in task_id.lower() or "feedback" in task_desc.lower():
                task.llm = feedback_llm or task.llm
            elif "research" in task_id.lower() or "research" in task_desc.lower():
                task.llm = historical_llm or task.llm
            
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
            planning_llm=planning_llm,
            callbacks=event_listeners,
            function_calling_llm=function_calling_llm,
            manager_agent=manager_agent,
            prompt_file=self.config.get("prompt_file"),
            embedder=embedder_config,
            # Enhanced memory components
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,
            entity_memory=entity_memory,
            # Add specialized LLMs to the crew context for access in tasks
            context={"specialized_llms": specialized_llms}
        ) 