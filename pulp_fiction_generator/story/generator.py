"""
Story generator orchestration.

This module contains the main StoryGenerator class that orchestrates
the story generation process using the component classes.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Type
import os
import traceback
import json
import copy

from crewai import Task, Crew

from .tasks import TaskFactory
from .execution import ExecutionEngine
from .validation import StoryValidator
from .state import StoryStateManager
from .models import StoryArtifacts, StoryOutput
from ..utils.errors import logger, timeout, TimeoutError, with_error_handling

class GenerationError(Exception):
    """Exception raised when story generation fails"""
    pass

class StoryGenerator:
    """
    Responsible for generating stories using agent crews.
    
    This class orchestrates the story generation process by coordinating
    the task factory, execution engine, and state manager components.
    It follows the SOLID principles, particularly Single Responsibility
    and Dependency Injection.
    """
    
    def __init__(
        self,
        crew_factory,  # Circular import prevention
        task_factory: Optional[TaskFactory] = None,
        execution_engine: Optional[ExecutionEngine] = None,
        state_manager: Optional[StoryStateManager] = None,
        debug_mode: bool = False
    ):
        """
        Initialize the story generator with its component dependencies.
        
        Args:
            crew_factory: Factory for creating crews
            task_factory: Factory for creating tasks
            execution_engine: Engine for executing tasks and crews
            state_manager: Manager for story state
            debug_mode: Whether debugging is enabled
        """
        self.crew_factory = crew_factory
        self.task_factory = task_factory or TaskFactory(crew_factory.agent_factory)
        self.execution_engine = execution_engine or ExecutionEngine(debug_mode=debug_mode)
        self.state_manager = state_manager or StoryStateManager()
        self.debug_mode = debug_mode
        
        # Fallback templates for emergency recovery
        self.fallback_templates = {
            "research": "This is placeholder research text for the {genre} genre. The real story generation is currently experiencing technical difficulties.",
            "worldbuilding": "This is a placeholder world for a {genre} story. The real story generation is currently experiencing technical difficulties.",
            "characters": "The main character is a typical {genre} protagonist with a strong motivation. The real story generation is currently experiencing technical difficulties.",
            "plot": "A standard {genre} plot with beginning, middle, and end. The real story generation is currently experiencing technical difficulties.",
            "draft": "This is a placeholder draft for a {genre} story. The real story generation is currently experiencing technical difficulties.",
            "final_story": "Your {genre} story is currently experiencing technical difficulties. Please try regenerating it or consider fixing the CrewFactory issue."
        }
    
    @with_error_handling
    def generate_story(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        debug_mode: Optional[bool] = None,
        timeout_seconds: int = 300  # 5 minute default timeout
    ) -> str:
        """
        Generate a complete story.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            debug_mode: Override the default debug mode setting
            timeout_seconds: Maximum time in seconds to wait for generation
            
        Returns:
            The generated story
        """
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            self.execution_engine.debug_mode = debug_mode
        
        try:
            logger.info(f"Creating basic crew for genre: {genre}")
            
            # Use the create_basic_crew_with_inputs method when custom_inputs are provided
            # This method will store custom_inputs in the CrewFactory's storage
            if custom_inputs:
                logger.info(f"Using create_basic_crew_with_inputs with {len(custom_inputs)} custom inputs")
                crew = self.crew_factory.create_basic_crew_with_inputs(
                    genre=genre,
                    custom_inputs=custom_inputs, 
                    config=config
                )
            else:
                logger.info(f"Using standard create_basic_crew without custom inputs")
                crew = self.crew_factory.create_basic_crew(
                    genre=genre, 
                    config=config
                )
            
            logger.info(f"Starting crew execution with timeout of {timeout_seconds} seconds")
            # We pass the crew_factory to the ExecutionEngine so it can retrieve the stored custom inputs
            result = self.execution_engine.execute_crew(
                crew, 
                custom_inputs=custom_inputs,
                timeout_seconds=timeout_seconds,
                crew_factory=self.crew_factory
            )
            
            # Log the result for debugging
            logger.info(f"Story generation complete, result length: {len(result)} characters")
            
            return result
        except Exception as e:
            logger.error(f"Error during story generation: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Try to generate a story using the phased approach as fallback
            try:
                logger.info("Attempting fallback phased story generation...")
                result = self.generate_story_phased(
                    genre=genre,
                    custom_inputs=custom_inputs,
                    config=config,
                    timeout_seconds=timeout_seconds
                )
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback story generation also failed: {str(fallback_error)}")
                
                # Use our placeholder story if all else fails
                try:
                    logger.info("Generating placeholder story as last resort")
                    placeholder = self._get_fallback_content("final_story", genre)
                    return placeholder
                except:
                    # If even placeholder generation fails, raise the original error
                    raise GenerationError(f"Story generation failed: {str(e)}") from e
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            self.execution_engine.debug_mode = original_debug_mode
    
    def generate_story_chunked(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        chunk_callback: Optional[Callable] = None,
        debug_mode: Optional[bool] = None,
        story_state: Optional[StoryStateManager] = None,
        timeout_seconds: int = 120  # Add timeout_seconds parameter with default of 120
    ) -> StoryArtifacts:
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
            StoryArtifacts object with all generated content
        """
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            self.execution_engine.debug_mode = debug_mode
        
        try:
            # Get the chapter number from custom inputs or default to 1
            chapter_num = custom_inputs.get("chapter_number", 1) if custom_inputs else 1
            title = custom_inputs.get("title", "Untitled Story") if custom_inputs else "Untitled Story"
            project_dir = title.lower().replace(" ", "_")
            
            # Use provided story state or default manager
            story_state = story_state or self.state_manager
            story_state.set_project_directory(title)
            
            # Initialize results
            artifacts = StoryArtifacts(
                genre=genre,
                title=title
            )
            
            # Create task output callback
            def task_output_callback(task: Task) -> None:
                """Process task output and store it in story state."""
                task_type = task.name if hasattr(task, "name") else "unknown"
                
                # Get raw output from TaskOutput object
                task_output = None
                if hasattr(task, "output"):
                    task_output = task.output.raw
                
                # Store the task output in story state
                story_state.add_task_output(task_type, chapter_num, task_output)
                
                # Update artifacts
                if task_type in artifacts.__dict__:
                    setattr(artifacts, task_type, task_output)
                
                # Call user-provided callback if available
                if chunk_callback:
                    chunk_callback(task_type, task_output)
            
            # Process each story generation phase
            self._process_research_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            self._process_worldbuilding_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            self._process_character_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            self._process_plot_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            self._process_draft_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            self._process_final_phase(genre, chapter_num, project_dir, task_output_callback, story_state, artifacts, timeout_seconds)
            
            return artifacts
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            self.execution_engine.debug_mode = original_debug_mode
    
    def _process_research_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the research phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("research", chapter_num):
            logger.info("Found existing research output in story state")
            research_results = story_state.get_task_output("research", chapter_num)
            artifacts.research = research_results
        else:
            logger.info(f"Starting research phase for {genre} story")
            research_task = self.task_factory.create_research_task(
                genre=genre,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback
            )
            
            research_results = self.execution_engine.execute_task(research_task, timeout_seconds)
            artifacts.research = research_results
    
    def _process_worldbuilding_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the worldbuilding phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("worldbuilding", chapter_num):
            logger.info("Found existing worldbuilding output in story state")
            world = story_state.get_task_output("worldbuilding", chapter_num)
            artifacts.worldbuilding = world
        else:
            logger.info(f"Starting worldbuilding phase for {genre} story")
            worldbuilding_task = self.task_factory.create_worldbuilding_task(
                genre=genre,
                context=artifacts.research,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback
            )
            
            world = self.execution_engine.execute_task(worldbuilding_task, timeout_seconds)
            artifacts.worldbuilding = world
    
    def _process_character_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the character creation phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("characters", chapter_num):
            logger.info("Found existing characters output in story state")
            characters = story_state.get_task_output("characters", chapter_num)
            artifacts.characters = characters
        else:
            logger.info(f"Starting character creation phase for {genre} story")
            context = f"Research: {artifacts.research}\n\nWorld: {artifacts.worldbuilding}"
            
            char_task = self.task_factory.create_character_task(
                genre=genre,
                context=context,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback
            )
            
            characters = self.execution_engine.execute_task(char_task, timeout_seconds)
            artifacts.characters = characters
    
    def _process_plot_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the plot development phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("plot", chapter_num):
            logger.info("Found existing plot output in story state")
            plot = story_state.get_task_output("plot", chapter_num)
            artifacts.plot = plot
        else:
            logger.info(f"Starting plot development phase for {genre} story")
            context = f"Research: {artifacts.research}\n\nWorld: {artifacts.worldbuilding}\n\nCharacters: {artifacts.characters}"
            
            plot_task = self.task_factory.create_plot_task(
                genre=genre,
                context=context,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback
            )
            
            plot = self.execution_engine.execute_task(plot_task, timeout_seconds)
            artifacts.plot = plot
    
    def _process_draft_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the draft writing phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("draft", chapter_num):
            logger.info("Found existing draft output in story state")
            draft = story_state.get_task_output("draft", chapter_num)
            artifacts.draft = draft
        else:
            logger.info(f"Starting draft writing phase for {genre} story")
            context = f"Research: {artifacts.research}\n\nWorld: {artifacts.worldbuilding}\n\n" \
                    f"Characters: {artifacts.characters}\n\nPlot: {artifacts.plot}"
            
            writing_task = self.task_factory.create_writing_task(
                genre=genre,
                context=context,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback
            )
            
            draft = self.execution_engine.execute_task(writing_task, timeout_seconds)
            artifacts.draft = draft
    
    def _process_final_phase(
        self, 
        genre: str, 
        chapter_num: int, 
        project_dir: str, 
        callback: Callable, 
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process the final editing phase of story generation.
        
        Args:
            genre: The genre to generate for
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts to update
            timeout_seconds: Maximum time in seconds to wait for the phase
        """
        if story_state.has_completed_task("final_story", chapter_num):
            logger.info("Found existing final story output in story state")
            final_story = story_state.get_task_output("final_story", chapter_num)
            artifacts.final_story = final_story
        else:
            logger.info(f"Starting final editing phase for {genre} story")
            context = f"Draft: {artifacts.draft}\n\nResearch: {artifacts.research}\n\n" \
                    f"World: {artifacts.worldbuilding}\n\nCharacters: {artifacts.characters}\n\n" \
                    f"Plot: {artifacts.plot}"
            
            editing_task = self.task_factory.create_editing_task(
                genre=genre,
                context=context,
                chapter_num=chapter_num,
                project_dir=project_dir,
                callback=callback,
                output_pydantic=StoryOutput
            )
            
            final_story = self.execution_engine.execute_task(editing_task, timeout_seconds)
            artifacts.final_story = final_story
    
    def execute_detailed_research(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a detailed research process with multiple subtasks.
        
        Args:
            genre: The genre to research
            custom_inputs: Optional custom inputs
            
        Returns:
            Comprehensive research results
        """
        # Get chapter number and project directory
        chapter_num = custom_inputs.get("chapter_number", 1) if custom_inputs else 1
        title = custom_inputs.get("title", f"{genre} Research") if custom_inputs else f"{genre} Research"
        project_dir = title.lower().replace(" ", "_")
        
        logger.info(f"Starting detailed research for {genre}")
        
        # Get research subtasks
        research_tasks = self.task_factory.create_research_subtasks(
            genre=genre,
            chapter_num=chapter_num,
            project_dir=project_dir
        )
        
        # Execute each research subtask
        results = []
        for task in research_tasks:
            logger.info(f"Executing research subtask: {task.name}")
            result = self.execution_engine.execute_task(task)
            results.append(result)
        
        # Compile all research results
        compiled_research = f"""# {genre.title()} Pulp Fiction Research Brief

## Core Genre Elements
{results[0] if len(results) > 0 else ""}

## Historical Context
{results[1] if len(results) > 1 else ""}

## Writing Style Guide
{results[2] if len(results) > 2 else ""}
"""
        
        # Save the compiled results
        try:
            # Create the directory structure first
            output_file = f"output/{project_dir}/chapter_{chapter_num}/research.txt"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Use FileWriteTool if available from crewai_tools
            try:
                from crewai_tools import FileWriteTool
                file_tool = FileWriteTool()
                file_tool.write(path=output_file, content=compiled_research)
                logger.info(f"Saved compiled research to {output_file} using FileWriteTool")
            except ImportError:
                # Fallback to direct file writing if tool not available
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(compiled_research)
                logger.info(f"Saved compiled research to {output_file}")
        except Exception as e:
            logger.error(f"Error saving compiled research: {e}")
        
        return compiled_research
    
    def _get_fallback_content(self, step_type: str, genre: str) -> str:
        """
        Get fallback content for a generation step when normal generation fails.
        
        Args:
            step_type: The type of generation step (research, worldbuilding, etc.)
            genre: The genre of the story
            
        Returns:
            Fallback content for the step
        """
        template = self.fallback_templates.get(
            step_type, 
            "Placeholder content for {genre} {step_type}."
        )
        return template.format(genre=genre, step_type=step_type)
    
    def _process_step_with_fallback(
        self, 
        step_name: str,
        process_func: Callable,
        genre: str,
        chapter_num: int,
        project_dir: str,
        callback: Callable,
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process a story generation step with fallback to ensure robustness.
        
        Args:
            step_name: Name of the step
            process_func: Function to process the step
            genre: Genre of the story
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: Story state manager
            artifacts: Story artifacts
            timeout_seconds: Timeout in seconds
        """
        try:
            if not story_state.has_completed_task(step_name, chapter_num):
                # Execute the step process
                process_func(genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds)
            else:
                # Load existing content
                logger.info(f"Found existing {step_name} output in story state")
                content = story_state.get_task_output(step_name, chapter_num)
                if hasattr(artifacts, step_name):
                    setattr(artifacts, step_name, content)
        except Exception as e:
            logger.error(f"Error in {step_name} phase: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Use fallback content only if no existing content
            if not hasattr(artifacts, step_name) or getattr(artifacts, step_name) is None:
                fallback_content = self._get_fallback_content(step_name, genre)
                logger.warning(f"Using fallback content for {step_name}")
                
                if hasattr(artifacts, step_name):
                    setattr(artifacts, step_name, fallback_content)
                
                story_state.add_task_output(step_name, chapter_num, fallback_content)
    
    def generate_story_phased(
        self,
        genre: str,
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 60,  # Per-phase timeout
        callback: Optional[Callable] = None
    ) -> str:
        """
        Generate a story using the phased approach with robust error recovery.
        
        Args:
            genre: The genre to generate
            custom_inputs: Custom inputs for the generation
            config: Configuration overrides
            timeout_seconds: Timeout for each phase
            callback: Optional callback function
            
        Returns:
            The generated story
        """
        # Parse the project directory from custom inputs or use default
        project_dir = custom_inputs.get("project_dir", "default_project") if custom_inputs else "default_project"
        
        # Initialize the story state manager with the project directory
        story_state = copy.deepcopy(self.state_manager)
        story_state.set_project_directory(project_dir)
        
        # Create story artifacts container
        artifacts = StoryArtifacts(
            genre=genre,
            title=project_dir
        )
        
        # Chapter number - currently we just generate one chapter
        chapter_num = 1
        
        # Process each phase with fallback handling
        self._process_step_with_fallback(
            "research", self._process_research_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        self._process_step_with_fallback(
            "worldbuilding", self._process_worldbuilding_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        self._process_step_with_fallback(
            "characters", self._process_character_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        self._process_step_with_fallback(
            "plot", self._process_plot_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        self._process_step_with_fallback(
            "draft", self._process_draft_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        self._process_step_with_fallback(
            "final_story", self._process_final_phase,
            genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds
        )
        
        # Return the final story
        return artifacts.final_story or self._get_fallback_content("final_story", genre)
    
    def generate_story_with_flow(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        debug_mode: Optional[bool] = None,
        timeout_seconds: int = 300
    ) -> str:
        """
        Generate a story using the CrewAI Flow approach.
        
        This method creates and executes a StoryGenerationFlow to generate
        a complete story. The flow approach provides better orchestration,
        state management, and visualization capabilities.
        
        Args:
            genre: The genre to generate for
            custom_inputs: Optional custom inputs
            config: Optional configuration overrides
            debug_mode: Override the default debug mode setting
            timeout_seconds: Maximum time for generation
            
        Returns:
            The generated story
        """
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            self.execution_engine.debug_mode = debug_mode
        
        try:
            logger.info(f"Creating story flow for genre: {genre}")
            
            # Import flow components (avoid circular imports)
            from ..flow.flow_factory import FlowFactory
            
            # Create flow factory
            flow_factory = FlowFactory(self.crew_factory)
            
            # Generate the story using the flow
            logger.info(f"Executing story flow with timeout of {timeout_seconds} seconds")
            result = flow_factory.generate_story(
                genre=genre,
                custom_inputs=custom_inputs,
                timeout_seconds=timeout_seconds
            )
            
            # Log the result for debugging
            logger.info(f"Flow-based story generation complete, result length: {len(result)} characters")
            
            return result
        except Exception as e:
            logger.error(f"Error during flow-based story generation: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Fall back to traditional approach
            logger.info("Falling back to traditional story generation approach")
            try:
                return self.generate_story(
                    genre=genre,
                    custom_inputs=custom_inputs,
                    config=config,
                    debug_mode=debug_mode,
                    timeout_seconds=timeout_seconds
                )
            except Exception as fallback_error:
                logger.error(f"Fallback story generation also failed: {str(fallback_error)}")
                
                # Use our placeholder story if all else fails
                logger.info("Generating placeholder story as last resort")
                placeholder = self._get_fallback_content("final_story", genre)
                return placeholder
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            self.execution_engine.debug_mode = original_debug_mode
    
    def visualize_story_flow(
        self, 
        genre: str, 
        output_file: str = "story_flow.html",
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a visualization of the story generation flow.
        
        Args:
            genre: The genre for visualization
            output_file: The output file path for the visualization
            custom_inputs: Optional custom inputs for the flow
            
        Returns:
            Path to the saved visualization
        """
        from ..flow.flow_factory import FlowFactory
        
        flow_factory = FlowFactory(self.crew_factory)
        return flow_factory.visualize_story_flow(
            genre=genre,
            output_file=output_file,
            custom_inputs=custom_inputs
        ) 