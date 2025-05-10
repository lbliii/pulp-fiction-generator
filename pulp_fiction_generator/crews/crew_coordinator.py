"""
CrewCoordinator manages and orchestrates the creation and execution of agent crews.
"""

from typing import Any, Dict, List, Optional, Union

from crewai import Agent, Crew, Process, Task

from ..agents.agent_factory import AgentFactory
from ..models.model_service import ModelService
from ..utils.errors import ErrorHandler, logger, timeout, TimeoutError
from .config.crew_coordinator_config import CrewCoordinatorConfig
from .crew_factory import CrewFactory
from .crew_executor import CrewExecutor
from .story_generator import StoryGenerator
from .visualization_handler import VisualizationHandler


class CrewCoordinator:
    """
    Coordinates the creation and execution of agent crews for story generation.
    
    This class serves as a high-level orchestrator that delegates specialized
    functionality to dedicated components for improved modularity and maintainability.
    """
    
    def __init__(
        self, 
        agent_factory: AgentFactory,
        model_service: ModelService,
        config: Optional[CrewCoordinatorConfig] = None
    ):
        """
        Initialize the crew coordinator.
        
        Args:
            agent_factory: Factory for creating agents
            model_service: Service for model interactions
            config: Configuration for the coordinator
        """
        self.agent_factory = agent_factory
        self.model_service = model_service
        self.config = config or CrewCoordinatorConfig()
        
        # Initialize visualization handler
        self.visualization_handler = VisualizationHandler(
            debug_mode=self.config.debug_mode,
            output_dir=self.config.debug_output_dir
        )
        
        # Initialize component classes
        self.crew_factory = CrewFactory(
            agent_factory=agent_factory,
            process=self.config.process,
            verbose=self.config.verbose
        )
        
        self.crew_executor = CrewExecutor(
            visualizer=self.visualization_handler.visualizer,
            debug_mode=self.config.debug_mode
        )
        
        self.story_generator = StoryGenerator(
            crew_factory=self.crew_factory,
            crew_executor=self.crew_executor,
            debug_mode=self.config.debug_mode
        )
    
    def create_basic_crew(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Crew:
        """
        Create a basic crew with all standard agents for a genre.
        
        Args:
            genre: The genre to create the crew for
            config: Optional configuration overrides
            
        Returns:
            A configured crew
        """
        return self.crew_factory.create_basic_crew(genre, config)
    
    def create_continuation_crew(
        self, 
        genre: str, 
        previous_output: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a crew for continuing a previously generated story.
        
        Args:
            genre: The genre of the story
            previous_output: The output from the previous generation
            config: Optional configuration overrides
            
        Returns:
            A configured crew for continuation
        """
        return self.crew_factory.create_continuation_crew(genre, previous_output, config)
    
    def create_custom_crew(
        self, 
        genre: str, 
        agent_types: List[str], 
        task_descriptions: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a custom crew with specific agents and tasks.
        
        Args:
            genre: The genre to create the crew for
            agent_types: List of agent types to include
            task_descriptions: List of task descriptions (should match agent_types)
            config: Optional configuration overrides
            
        Returns:
            A configured custom crew
        """
        return self.crew_factory.create_custom_crew(genre, agent_types, task_descriptions, config)
    
    def kickoff_crew(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the execution of a crew.
        
        Args:
            crew: The crew to execute
            inputs: Optional inputs for the crew
            
        Returns:
            The final output from the crew
        """
        result = self.crew_executor.kickoff_crew(crew, inputs)
        
        # Visualize the execution if debug mode is enabled
        if inputs:
            self.visualization_handler.visualize_crew_execution(
                crew_name=crew.name,
                inputs=inputs,
                output=result
            )
            
        return result
    
    def generate_story(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        debug_mode: Optional[bool] = None,
        timeout_seconds: int = 300  # 5 minute default timeout
    ) -> str:
        """
        Generate a complete story using the default crew for a genre.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            debug_mode: Override the default debug mode setting
            timeout_seconds: Maximum time in seconds to wait for generation
            
        Returns:
            The generated story
        """
        # Set debug mode override if specified
        current_debug_mode = self.config.debug_mode
        if debug_mode is not None and debug_mode != current_debug_mode:
            self.visualization_handler = VisualizationHandler(
                debug_mode=debug_mode,
                output_dir=self.config.debug_output_dir
            )
            self.crew_executor.debug_mode = debug_mode
            self.crew_executor.visualizer = self.visualization_handler.visualizer
            self.story_generator.debug_mode = debug_mode
        
        result = self.story_generator.generate_story(
            genre=genre,
            custom_inputs=custom_inputs,
            config=config,
            debug_mode=debug_mode,
            timeout_seconds=timeout_seconds
        )
        
        # Visualize the story generation if debug mode is enabled
        if custom_inputs:
            self.visualization_handler.visualize_story_generation(
                genre=genre,
                inputs=custom_inputs,
                output=result
            )
            
        return result
    
    def generate_story_chunked(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        chunk_callback: Optional[callable] = None,
        debug_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Generate a story using a chunked approach with checkpoints after each major phase.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            chunk_callback: Optional callback function to execute after each chunk is completed
            debug_mode: Override the default debug mode setting
            
        Returns:
            Dictionary with all generated artifacts
        """
        # Set debug mode override if specified
        if debug_mode is not None and debug_mode != self.config.debug_mode:
            self.visualization_handler = VisualizationHandler(
                debug_mode=debug_mode,
                output_dir=self.config.debug_output_dir
            )
            self.crew_executor.debug_mode = debug_mode
            self.crew_executor.visualizer = self.visualization_handler.visualizer
            self.story_generator.debug_mode = debug_mode
            
        return self.story_generator.generate_story_chunked(
            genre=genre,
            custom_inputs=custom_inputs,
            config=config,
            chunk_callback=chunk_callback,
            debug_mode=debug_mode
        ) 