"""
CrewCoordinator manages and orchestrates the creation and execution of agent crews.
"""

from typing import Any, Dict, List, Optional, Union
import copy

from crewai import Agent, Crew, Process, Task

from ..agents.agent_factory import AgentFactory
from ..models.model_service import ModelService
from ..utils.errors import ErrorHandler, logger, timeout, TimeoutError
from .config.crew_coordinator_config import CrewCoordinatorConfig
from .crew_factory import CrewFactory
from ..story.execution import ExecutionEngine
from ..story.generator import StoryGenerator
from ..story.state import StoryStateManager
from ..story.models import StoryArtifacts
from .visualization_handler import VisualizationHandler
from .crew_executor import CrewExecutor
from .event_listeners import get_crewai_listeners


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
            agent_factory=self.agent_factory,
            process=self.config.process,
            verbose=self.config.verbose
        )
        
        # Initialize execution engine with proper configuration
        self.execution_engine = ExecutionEngine(
            debug_mode=self.config.debug_mode,
            verbose=self.config.verbose
        )
        
        # Initialize CrewExecutor for event handling and token tracking
        self.executor = CrewExecutor(debug_mode=self.config.debug_mode)
        
        # Add token tracking if debug mode is enabled
        if self.config.debug_mode:
            self.token_tracker = self.executor.add_token_tracking_listener()
        
        # Initialize story generator with required dependencies
        self.story_generator = StoryGenerator(
            crew_factory=self.crew_factory,
            execution_engine=self.execution_engine,
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
    
    def create_yaml_crew(
        self, 
        genre: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a crew using the recommended YAML-based CrewBase approach.
        
        This uses the more maintainable decorator-based approach from CrewAI
        for defining crews, agents, and tasks.
        
        Args:
            genre: The genre to create the crew for
            config: Optional configuration overrides
            
        Returns:
            A configured crew
        """
        try:
            from .yaml_crew import StoryGenerationCrew, YAML_SUPPORT
            
            # Create the crew with the YAML approach
            crew_builder = StoryGenerationCrew(
                genre=genre,
                agent_factory=self.agent_factory,
                model_service=self.model_service,
                config=config
            )
            
            # Check if YAML support is available
            if not YAML_SUPPORT:
                logger.warning("YAML decorator support not available. Falling back to traditional approach.")
                return self.create_basic_crew(genre, config)
            
            # Build and return the crew
            return crew_builder.build()
        except ImportError as e:
            logger.warning(f"Could not create YAML crew: {e}. Falling back to traditional approach.")
            return self.create_basic_crew(genre, config)
        except Exception as e:
            logger.error(f"Error creating YAML crew: {e}. Falling back to traditional approach.")
            return self.create_basic_crew(genre, config)
    
    def kickoff_crew(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None, crew_factory = None) -> str:
        """
        Start the execution of a crew.
        
        Args:
            crew: The crew to execute
            inputs: Optional inputs for the crew
            crew_factory: Optional crew factory to retrieve stored inputs
            
        Returns:
            The final output from the crew
        """
        result = self.execution_engine.execute_crew(
            crew, 
            custom_inputs=inputs, 
            crew_factory=crew_factory
        )
        
        # Visualize the execution if debug mode is enabled
        if inputs:
            self.visualization_handler.visualize_crew_execution(
                crew_name=crew.name,
                inputs=inputs,
                output=result
            )
            
        return result
    
    async def kickoff_crew_async(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the execution of a crew asynchronously.
        
        Args:
            crew: The crew to execute
            inputs: Optional inputs for the crew
            
        Returns:
            The final output from the crew
        """
        result = await crew.kickoff_async(inputs=inputs)
        
        # Visualize the execution if debug mode is enabled
        if inputs and self.config.debug_mode:
            self.visualization_handler.visualize_crew_execution(
                crew_name=crew.name,
                inputs=inputs,
                output=result
            )
            
        return result
    
    def kickoff_for_each(
        self, 
        crew: Crew, 
        inputs_array: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Start the execution of a crew for each input in the array.
        
        Args:
            crew: The crew to execute
            inputs_array: List of input dictionaries for each execution
            
        Returns:
            List of outputs from each execution
        """
        results = crew.kickoff_for_each(inputs=inputs_array)
        
        # Visualize if in debug mode
        if self.config.debug_mode:
            for i, (inputs, result) in enumerate(zip(inputs_array, results)):
                self.visualization_handler.visualize_crew_execution(
                    crew_name=f"{crew.name}_{i}",
                    inputs=inputs,
                    output=result
                )
                
        return results
    
    async def kickoff_for_each_async(
        self, 
        crew: Crew, 
        inputs_array: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Start the execution of a crew for each input in the array asynchronously.
        
        Args:
            crew: The crew to execute
            inputs_array: List of input dictionaries for each execution
            
        Returns:
            List of outputs from each execution
        """
        results = await crew.kickoff_for_each_async(inputs=inputs_array)
        
        # Visualize if in debug mode
        if self.config.debug_mode:
            for i, (inputs, result) in enumerate(zip(inputs_array, results)):
                self.visualization_handler.visualize_crew_execution(
                    crew_name=f"{crew.name}_{i}",
                    inputs=inputs,
                    output=result
                )
                
        return results
    
    def generate_story(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        debug_mode: Optional[bool] = None,
        timeout_seconds: int = 120,  # Reduced from 300 to 120 seconds
        use_yaml_crew: bool = True  # Use YAML crew by default
    ) -> str:
        """
        Generate a complete story.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            debug_mode: Override the default debug mode setting
            timeout_seconds: Maximum time in seconds to wait for generation
            use_yaml_crew: Whether to use the YAML crew approach
            
        Returns:
            The generated story
        """
        # Allow per-story debug mode override
        original_debug_mode = self.config.debug_mode
        if debug_mode is not None:
            self.config.debug_mode = debug_mode
            self.execution_engine.debug_mode = debug_mode
        
        try:
            # Make a copy of the config to modify
            crew_config = copy.deepcopy(config) if config else {}
            
            # Choose crew creation approach
            try:
                if use_yaml_crew:
                    logger.info("Using YAML-based crew approach for story generation")
                    crew = self.create_yaml_crew(genre, crew_config)
                    # Store custom inputs if YAML crew creation was successful
                    if custom_inputs:
                        self.crew_factory.store_custom_inputs(crew, custom_inputs)
                else:
                    logger.info("Using traditional crew approach for story generation")
                    # Use the new create_basic_crew_with_inputs method when custom_inputs are provided
                    if custom_inputs:
                        logger.info(f"Using create_basic_crew_with_inputs with {len(custom_inputs)} custom inputs")
                        crew = self.crew_factory.create_basic_crew_with_inputs(
                            genre=genre, 
                            custom_inputs=custom_inputs,
                            config=crew_config
                        )
                    else:
                        logger.info("Using standard create_basic_crew without custom inputs")
                        crew = self.create_basic_crew(genre, crew_config)
            except Exception as e:
                logger.error(f"Error using YAML crew: {e}. Falling back to traditional approach.")
                # Use the new method with custom_inputs when they are provided
                if custom_inputs:
                    crew = self.crew_factory.create_basic_crew_with_inputs(
                        genre=genre, 
                        custom_inputs=custom_inputs,
                        config=crew_config
                    )
                else:
                    crew = self.create_basic_crew(genre, crew_config)
            
            logger.info(f"Starting crew execution with timeout of {timeout_seconds} seconds")
            # Pass crew_factory to execution_engine to retrieve stored custom inputs
            result = self.kickoff_crew(crew, custom_inputs, self.crew_factory)
            
            # Log the result for debugging
            logger.info(f"Story generation complete, result length: {len(result)} characters")
            
            # If the result is empty, use a fallback story
            if not result.strip():
                fallback_story = f"Your {genre} story titled '{custom_inputs.get('title', 'Untitled')}' could not be generated due to technical issues. The CrewFactory is experiencing problems with the 'custom_inputs' parameter. Please check the code and fix the issue."
                logger.warning("Generated result was empty, using fallback story")
                return fallback_story
            
            return result
        except TimeoutError:
            error_msg = f"Story generation timed out after {timeout_seconds} seconds"
            logger.error(error_msg)
            return f"ERROR: {error_msg}. The generation process took too long. Try with a lower timeout value or check Ollama's performance."
    
    def generate_story_chunked(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        chunk_callback: Optional[callable] = None,
        debug_mode: Optional[bool] = None,
        story_state: Optional[StoryStateManager] = None,
        timeout_seconds: int = 120  # Added missing timeout_seconds parameter with default of 120
    ) -> Dict[str, Any]:
        """
        Generate a story using a chunked approach with checkpoints after each major phase.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            chunk_callback: Optional callback function to execute after each chunk is completed
            debug_mode: Override the default debug mode setting
            story_state: Optional story state to check for already completed tasks
            timeout_seconds: Maximum time in seconds to wait for each generation stage
            
        Returns:
            Dictionary with all generated artifacts
        """
        # Set debug mode override if specified
        if debug_mode is not None and debug_mode != self.config.debug_mode:
            self.visualization_handler = VisualizationHandler(
                debug_mode=debug_mode,
                output_dir=self.config.debug_output_dir
            )
            self.execution_engine.debug_mode = debug_mode
            self.story_generator.debug_mode = debug_mode
            
        artifacts = self.story_generator.generate_story_chunked(
            genre=genre,
            custom_inputs=custom_inputs,
            config=config,
            chunk_callback=chunk_callback,
            debug_mode=debug_mode,
            story_state=story_state,
            timeout_seconds=timeout_seconds  # Pass the timeout parameter to the story generator
        )
        
        # Convert StoryArtifacts to dictionary format for backward compatibility
        if isinstance(artifacts, StoryArtifacts):
            return artifacts.__dict__
        return artifacts 
    
    def replay_from_task(self, task_id: str) -> str:
        """
        Replay a crew execution from a specific task.
        
        This method uses CrewAI's task replay feature to resume execution
        from a specific task while retaining context from previous tasks.
        
        Args:
            task_id: The ID of the task to replay from
            
        Returns:
            The final output from the replayed execution
        """
        import subprocess
        import json
        
        try:
            # Use CrewAI CLI to replay from the specific task
            result = subprocess.run(
                ["crewai", "replay", "-t", task_id], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Log the result
            logger.info(f"Successfully replayed from task {task_id}")
            
            # Parse the output JSON if possible
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError:
                # Return the raw stdout if not JSON format
                return result.stdout
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Error replaying from task {task_id}: {e}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
    
    def list_latest_task_outputs(self) -> Dict[str, Any]:
        """
        List the latest task outputs from previous crew executions.
        
        Returns:
            Dictionary mapping task IDs to task information
        """
        import subprocess
        import json
        
        try:
            # Use CrewAI CLI to get the latest task outputs
            result = subprocess.run(
                ["crewai", "log-tasks-outputs"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parse the output JSON if possible
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError:
                # Return empty dict if not JSON format
                logger.error("Could not parse task outputs as JSON")
                return {}
                
        except subprocess.CalledProcessError as e:
            error_msg = f"Error listing task outputs: {e}"
            logger.error(error_msg)
            return {} 
    
    def initialize_vector_database(self, collection_name: str, dimension: int = 1536) -> bool:
        """
        Initialize a vector database collection for enhanced memory capabilities.
        
        Args:
            collection_name: Name of the collection to initialize
            dimension: Dimension of the vectors (depends on the embedding model)
            
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Import Qdrant client library
            from qdrant_client import QdrantClient
            from qdrant_client.http import models
            
            # Create a local Qdrant instance (you can configure to use a remote one in production)
            client = QdrantClient(":memory:")  # For persistent storage use path="./qdrant_data"
            
            # Check if collection exists
            collections = client.get_collections().collections
            collection_exists = any(collection.name == collection_name for collection in collections)
            
            # Create collection if it doesn't exist
            if not collection_exists:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=dimension,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created vector collection '{collection_name}' for enhanced memory")
            else:
                logger.info(f"Using existing vector collection '{collection_name}' for enhanced memory")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            return False 