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
            
            # Initialize story artifacts
            artifacts = StoryArtifacts()
            
            # Define callback to capture task output and dispatch to the user's callback if provided
            def task_output_callback(task: Task) -> None:
                # Get the task name
                task_name = task.name if hasattr(task, 'name') else "unknown"
                
                # Store the task output in artifacts
                if hasattr(task, 'output'):
                    task_output = task.output
                    story_state.save_task_output(task_name, task_output)
                    
                    # Store in artifacts
                    if task_name == "research":
                        artifacts.research = task_output
                    elif task_name == "research_expansion":
                        artifacts.research_expanded = task_output
                    elif task_name == "worldbuilding":
                        artifacts.worldbuilding = task_output
                    elif task_name == "characters":
                        artifacts.characters = task_output
                    elif task_name == "character_development":
                        artifacts.characters_enhanced = task_output
                    elif task_name == "plot":
                        artifacts.plot = task_output
                    elif task_name == "plot_twist":
                        artifacts.plot_twist = task_output
                    elif task_name == "draft":
                        artifacts.draft = task_output
                    elif task_name == "style_improvement":
                        artifacts.style_improved = task_output
                    elif task_name == "consistency_check":
                        artifacts.consistency_fixed = task_output
                    elif task_name == "final":
                        artifacts.final_story = task_output
                
                # Call the provided callback
                if chunk_callback:
                    chunk_callback(task_name, task_output if hasattr(task, 'output') else None)
                        
            # Process each phase with proper error handling and fallback
            self._process_step_with_fallback(
                "research", 
                self._process_research_phase,
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )

            self._process_worldbuilding_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_character_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_plot_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_draft_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_final_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
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
            genre: The genre to research
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("research") and story_state.has_task_output("research_expansion"):
            artifacts.research = story_state.get_task_output("research")
            artifacts.research_expanded = story_state.get_task_output("research_expansion")
            return
            
        # Create initial research task
        research_task = self.task_factory.create_research_task(
            genre=genre,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )

        # Execute the research task
        research_output = self.execution_engine.execute_task(
            research_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the research output
        artifacts.research = research_output
        story_state.save_task_output("research", research_output)
        
        # Create and execute conditional research expansion task
        research_expansion_task = self.task_factory.create_research_expansion_task(
            genre=genre,
            context=research_task,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        try:
            # Execute the conditional task - it will only run if the condition is met
            research_expansion_output = self.execution_engine.execute_task(
                research_expansion_task, 
                timeout_seconds=timeout_seconds
            )
            
            # Store the expanded research if task ran
            if research_expansion_output:
                artifacts.research_expanded = research_expansion_output
                story_state.save_task_output("research_expansion", research_expansion_output)
        except Exception as e:
            logger.warning(f"Research expansion task failed or was skipped: {str(e)}")

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
            genre: The genre for worldbuilding
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("worldbuilding"):
            artifacts.worldbuilding = story_state.get_task_output("worldbuilding")
            return
        
        # Determine context - if we have expanded research, use it combined with basic research
        context = artifacts.research
        if hasattr(artifacts, 'research_expanded') and artifacts.research_expanded:
            context = f"{artifacts.research}\n\nEXPANDED RESEARCH:\n{artifacts.research_expanded}"
        
        # Create and execute the worldbuilding task
        worldbuilding_task = self.task_factory.create_worldbuilding_task(
            genre=genre,
            context=context,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        worldbuilding_output = self.execution_engine.execute_task(
            worldbuilding_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the output
        artifacts.worldbuilding = worldbuilding_output
        story_state.save_task_output("worldbuilding", worldbuilding_output)
            
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
        Process the character development phase of story generation.
        
        Args:
            genre: The genre for character development
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("characters") and story_state.has_task_output("character_development"):
            artifacts.characters = story_state.get_task_output("characters")
            artifacts.characters_enhanced = story_state.get_task_output("character_development")
            return
        
        # Create and execute the character task
        character_task = self.task_factory.create_character_task(
            genre=genre,
            context=[artifacts.research, artifacts.worldbuilding],
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        character_output = self.execution_engine.execute_task(
            character_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the output
        artifacts.characters = character_output
        story_state.save_task_output("characters", character_output)
        
        # Create and execute conditional character development task
        character_dev_task = self.task_factory.create_character_development_task(
            genre=genre,
            context=character_task,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        try:
            # Execute the conditional task - it will only run if the condition is met
            character_dev_output = self.execution_engine.execute_task(
                character_dev_task, 
                timeout_seconds=timeout_seconds
            )
            
            # Store the enhanced characters if task ran
            if character_dev_output:
                artifacts.characters_enhanced = character_dev_output
                story_state.save_task_output("character_development", character_dev_output)
        except Exception as e:
            logger.warning(f"Character development task failed or was skipped: {str(e)}")
            
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
            genre: The genre for plot development
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("plot") and story_state.has_task_output("plot_twist"):
            artifacts.plot = story_state.get_task_output("plot")
            artifacts.plot_twist = story_state.get_task_output("plot_twist")
            return
        
        # Determine character context
        character_context = artifacts.characters
        if hasattr(artifacts, 'characters_enhanced') and artifacts.characters_enhanced:
            character_context = artifacts.characters_enhanced
        
        # Create and execute the plot task
        plot_task = self.task_factory.create_plot_task(
            genre=genre,
            context=[artifacts.research, artifacts.worldbuilding, character_context],
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        plot_output = self.execution_engine.execute_task(
            plot_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the output
        artifacts.plot = plot_output
        story_state.save_task_output("plot", plot_output)
        
        # Create and execute conditional plot twist task
        plot_twist_task = self.task_factory.create_plot_twist_task(
            genre=genre,
            context=plot_task,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        try:
            # Execute the conditional task - it will only run if the condition is met
            plot_twist_output = self.execution_engine.execute_task(
                plot_twist_task, 
                timeout_seconds=timeout_seconds
            )
            
            # Store the plot twist if task ran
            if plot_twist_output:
                artifacts.plot_twist = plot_twist_output
                story_state.save_task_output("plot_twist", plot_twist_output)
        except Exception as e:
            logger.warning(f"Plot twist task failed or was skipped: {str(e)}")
            
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
            genre: The genre for writing
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("draft"):
            artifacts.draft = story_state.get_task_output("draft")
            return
        
        # Determine plot context
        plot_context = artifacts.plot
        if hasattr(artifacts, 'plot_twist') and artifacts.plot_twist:
            plot_context = f"{artifacts.plot}\n\nPLOT TWIST:\n{artifacts.plot_twist}"
            
        # Determine character context
        character_context = artifacts.characters
        if hasattr(artifacts, 'characters_enhanced') and artifacts.characters_enhanced:
            character_context = artifacts.characters_enhanced
        
        # Create and execute the writing task
        writing_task = self.task_factory.create_writing_task(
            genre=genre,
            context=[artifacts.research, artifacts.worldbuilding, character_context, plot_context],
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        draft_output = self.execution_engine.execute_task(
            writing_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the output
        artifacts.draft = draft_output
        story_state.save_task_output("draft", draft_output)
            
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
            genre: The genre for editing
            chapter_num: The chapter number
            project_dir: Project directory for output
            callback: Callback for task output
            story_state: State manager for tracking progress
            artifacts: Story artifacts object for storing output
            timeout_seconds: Timeout for the task
        """
        # Skip if already completed
        if story_state.has_task_output("final"):
            artifacts.final_story = story_state.get_task_output("final")
            return
        
        # Create and execute the style improvement task if needed
        style_improvement_task = self.task_factory.create_style_improvement_task(
            genre=genre,
            context=artifacts.draft,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        improved_draft = artifacts.draft
        try:
            # Execute the conditional task - it will only run if the condition is met
            style_output = self.execution_engine.execute_task(
                style_improvement_task, 
                timeout_seconds=timeout_seconds
            )
            
            # If the task ran, use the improved style as the current draft
            if style_output:
                improved_draft = style_output
                artifacts.style_improved = style_output
                story_state.save_task_output("style_improvement", style_output)
        except Exception as e:
            logger.warning(f"Style improvement task failed or was skipped: {str(e)}")
            
        # Create and execute the consistency check task if needed    
        consistency_task = self.task_factory.create_consistency_check_task(
            genre=genre,
            context=improved_draft,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        consistent_draft = improved_draft
        try:
            # Execute the conditional task - it will only run if the condition is met
            consistency_output = self.execution_engine.execute_task(
                consistency_task, 
                timeout_seconds=timeout_seconds
            )
            
            # If the task ran, use the consistency-fixed draft as the current draft
            if consistency_output:
                consistent_draft = consistency_output
                artifacts.consistency_fixed = consistency_output
                story_state.save_task_output("consistency_check", consistency_output)
        except Exception as e:
            logger.warning(f"Consistency check task failed or was skipped: {str(e)}")
            
        # Now do the final editing with the best draft we have
        editing_task = self.task_factory.create_editing_task(
            genre=genre,
            context=consistent_draft,
            chapter_num=chapter_num,
            project_dir=project_dir,
            callback=callback
        )
        
        final_output = self.execution_engine.execute_task(
            editing_task, 
            timeout_seconds=timeout_seconds
        )
        
        # Store the output
        artifacts.final_story = final_output
        story_state.save_task_output("final", final_output)
    
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

    def _process_raw_tool_outputs(
        self,
        genre: str,
        tools: Dict[str, Any],
        chapter_num: int,
        project_dir: str,
        callback: Callable,
        story_state: StoryStateManager,
        artifacts: StoryArtifacts,
        timeout_seconds: int
    ) -> None:
        """
        Process raw tool outputs before main story generation.
        
        Args:
            genre: The genre for the tasks
            tools: Dictionary of tools to use for different tasks
            chapter_num: Chapter number
            project_dir: Project directory
            callback: Callback function
            story_state: State manager
            artifacts: Story artifacts for storing outputs
            timeout_seconds: Timeout in seconds
        """
        logger.info("Processing raw tool outputs for additional data collection")
        
        # Dictionary mapping task names to artifacts attributes
        task_to_artifact = {
            "raw_genre_research": "raw_genre_research",
            "raw_character_references": "raw_character_references",
            "raw_style_examples": "raw_style_examples",
            "raw_plot_structures": "raw_plot_structures"
        }
        
        # Check for web search tool for research
        if "search_tool" in tools:
            # Skip if already completed
            if not story_state.has_task_output("raw_genre_research"):
                logger.info("Executing raw genre research task")
                
                try:
                    # Create and execute the raw research task
                    raw_research_task = self.task_factory.create_raw_research_task(
                        genre=genre,
                        tool=tools["search_tool"],
                        chapter_num=chapter_num,
                        project_dir=project_dir,
                        callback=callback
                    )
                    
                    raw_research_output = self.execution_engine.execute_task(
                        raw_research_task, 
                        timeout_seconds=timeout_seconds
                    )
                    
                    # Store the output
                    artifacts.raw_genre_research = raw_research_output
                    story_state.save_task_output("raw_genre_research", raw_research_output)
                except Exception as e:
                    logger.warning(f"Raw genre research task failed: {str(e)}")
        
        # Check for character reference tool
        if "character_tool" in tools:
            # Skip if already completed
            if not story_state.has_task_output("raw_character_references"):
                logger.info("Executing raw character references task")
                
                try:
                    # Create and execute the raw character references task
                    raw_char_task = self.task_factory.create_raw_character_references_task(
                        genre=genre,
                        tool=tools["character_tool"],
                        chapter_num=chapter_num,
                        project_dir=project_dir,
                        callback=callback
                    )
                    
                    raw_char_output = self.execution_engine.execute_task(
                        raw_char_task, 
                        timeout_seconds=timeout_seconds
                    )
                    
                    # Store the output
                    artifacts.raw_character_references = raw_char_output
                    story_state.save_task_output("raw_character_references", raw_char_output)
                except Exception as e:
                    logger.warning(f"Raw character references task failed: {str(e)}")
        
        # Check for style examples tool
        if "style_tool" in tools:
            # Skip if already completed
            if not story_state.has_task_output("raw_style_examples"):
                logger.info("Executing raw style examples task")
                
                try:
                    # Create and execute the raw style examples task
                    raw_style_task = self.task_factory.create_raw_style_examples_task(
                        genre=genre,
                        tool=tools["style_tool"],
                        chapter_num=chapter_num,
                        project_dir=project_dir,
                        callback=callback
                    )
                    
                    raw_style_output = self.execution_engine.execute_task(
                        raw_style_task, 
                        timeout_seconds=timeout_seconds
                    )
                    
                    # Store the output
                    artifacts.raw_style_examples = raw_style_output
                    story_state.save_task_output("raw_style_examples", raw_style_output)
                except Exception as e:
                    logger.warning(f"Raw style examples task failed: {str(e)}")
        
        # Check for plot structures tool
        if "plot_tool" in tools:
            # Skip if already completed
            if not story_state.has_task_output("raw_plot_structures"):
                logger.info("Executing raw plot structures task")
                
                try:
                    # Create and execute the raw plot structures task
                    raw_plot_task = self.task_factory.create_raw_plot_structures_task(
                        genre=genre,
                        tool=tools["plot_tool"],
                        chapter_num=chapter_num,
                        project_dir=project_dir,
                        callback=callback
                    )
                    
                    raw_plot_output = self.execution_engine.execute_task(
                        raw_plot_task, 
                        timeout_seconds=timeout_seconds
                    )
                    
                    # Store the output
                    artifacts.raw_plot_structures = raw_plot_output
                    story_state.save_task_output("raw_plot_structures", raw_plot_output)
                except Exception as e:
                    logger.warning(f"Raw plot structures task failed: {str(e)}")
        
        # Process any other tools that have been provided
        for tool_name, tool in tools.items():
            if tool_name not in ["search_tool", "character_tool", "style_tool", "plot_tool"]:
                task_name = f"raw_{tool_name}"
                
                # Skip if already completed
                if story_state.has_task_output(task_name):
                    continue
                
                logger.info(f"Executing raw {tool_name} task")
                
                try:
                    # Create a generic agent for this tool
                    generic_agent = self.agent_factory.create_agent(
                        role=f"{genre.title()} Specialist",
                        goal=f"Gather information about {genre} using specialized tools",
                        backstory=f"You are an expert in {genre} fiction with access to specialized research tools."
                    )
                    
                    # Create and execute the task
                    raw_task = self.task_factory.create_tool_task(
                        name=task_name,
                        description=f"Use the provided tool to gather information related to {genre} fiction.",
                        agent=generic_agent,
                        tool=tool,
                        expected_output=f"Raw data from the {tool_name}",
                        chapter_num=chapter_num,
                        project_dir=project_dir,
                        callback=callback
                    )
                    
                    raw_output = self.execution_engine.execute_task(
                        raw_task, 
                        timeout_seconds=timeout_seconds
                    )
                    
                    # Store the output if we have a matching field in artifacts
                    if hasattr(artifacts, task_name):
                        setattr(artifacts, task_name, raw_output)
                    
                    story_state.save_task_output(task_name, raw_output)
                except Exception as e:
                    logger.warning(f"Raw {tool_name} task failed: {str(e)}")

    def generate_story_chunked_with_raw_tools(
        self, 
        genre: str, 
        tools: Dict[str, Any],
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        chunk_callback: Optional[Callable] = None,
        debug_mode: Optional[bool] = None,
        story_state: Optional[StoryStateManager] = None,
        timeout_seconds: int = 120
    ) -> StoryArtifacts:
        """
        Generate a story using a chunked approach with raw tool outputs.
        
        Args:
            genre: The genre to generate for
            tools: Dictionary of tools to use with forced output
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            chunk_callback: Optional callback function to execute after each chunk is completed
            debug_mode: Override the default debug mode setting
            story_state: Optional story state to check for already completed tasks
            timeout_seconds: Maximum time in seconds to wait for each generation stage
            
        Returns:
            StoryArtifacts object with all generated content including raw tool outputs
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
            
            # Initialize story artifacts
            artifacts = StoryArtifacts()
            
            # Define callback to capture task output and dispatch to the user's callback if provided
            def task_output_callback(task: Task) -> None:
                # Get the task name
                task_name = task.name if hasattr(task, 'name') else "unknown"
                
                # Store the task output in artifacts
                if hasattr(task, 'output'):
                    task_output = task.output
                    story_state.save_task_output(task_name, task_output)
                    
                    # Store in artifacts based on task name
                    if hasattr(artifacts, task_name):
                        setattr(artifacts, task_name, task_output)
                
                # Call the provided callback
                if chunk_callback:
                    chunk_callback(task_name, task_output if hasattr(task, 'output') else None)
            
            # First process raw tool outputs
            self._process_raw_tool_outputs(
                genre,
                tools,
                chapter_num,
                project_dir,
                task_output_callback,
                story_state,
                artifacts,
                timeout_seconds
            )
            
            # Then process regular story generation phases
            self._process_step_with_fallback(
                "research", 
                self._process_research_phase,
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )

            self._process_worldbuilding_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_character_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_plot_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_draft_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            self._process_final_phase(
                genre, 
                chapter_num, 
                project_dir, 
                task_output_callback, 
                story_state,
                artifacts,
                timeout_seconds
            )
            
            return artifacts
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            self.execution_engine.debug_mode = original_debug_mode 