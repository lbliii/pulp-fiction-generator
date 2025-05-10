"""
StoryGenerator handles the generation of stories using agent crews.
"""

from typing import Any, Dict, List, Optional, Union, Callable

from crewai import Task, Crew

from ..utils.context_visualizer import ContextVisualizer
from ..utils.errors import ErrorHandler, logger, timeout, TimeoutError


class StoryGenerator:
    """
    Responsible for generating stories using agent crews.
    
    This class encapsulates the logic for generating stories, including
    full stories and chunked stories with checkpoints.
    """
    
    def __init__(
        self,
        crew_factory,  # Circular import prevention
        crew_executor,  # Circular import prevention
        debug_mode: bool = False
    ):
        """
        Initialize the story generator.
        
        Args:
            crew_factory: Factory for creating crews
            crew_executor: Executor for running crews
            debug_mode: Whether debugging is enabled
        """
        self.crew_factory = crew_factory
        self.crew_executor = crew_executor
        self.debug_mode = debug_mode
    
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
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            # Update executor debug mode
            if hasattr(self.crew_executor, 'debug_mode'):
                self.crew_executor.debug_mode = self.debug_mode
        
        try:
            logger.info(f"Creating basic crew for genre: {genre}")
            crew = self.crew_factory.create_basic_crew(genre, config)
            
            logger.info(f"Starting crew execution with timeout of {timeout_seconds} seconds")
            with timeout(timeout_seconds):
                result = self.crew_executor.kickoff_crew(crew, custom_inputs)
                
            # Log the result for debugging
            logger.info(f"Story generation complete, result length: {len(result)} characters")
            logger.info(f"Story generation result begins with: {result[:100]}...")
            
            # Check for empty or error results
            if not result or result.startswith("ERROR:"):
                logger.error(f"Story generation failed to produce valid content: {result}")
                return result
            
            return result
        except TimeoutError:
            error_msg = f"Story generation timed out after {timeout_seconds} seconds"
            logger.error(error_msg)
            return f"ERROR: {error_msg}. This is a fallback response to prevent the process from hanging indefinitely."
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            if hasattr(self.crew_executor, 'debug_mode'):
                self.crew_executor.debug_mode = original_debug_mode
    
    def generate_story_chunked(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        chunk_callback: Optional[Callable] = None,
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
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            # Update executor debug mode
            if hasattr(self.crew_executor, 'debug_mode'):
                self.crew_executor.debug_mode = self.debug_mode
        
        try:
            # Initialize results dictionary
            results = {
                "genre": genre,
                "title": custom_inputs.get("title", None) if custom_inputs else None,
                "research": None,
                "worldbuilding": None,
                "characters": None,
                "plot": None,
                "draft": None,
                "final_story": None
            }
            
            # Execute each phase separately
            
            # Phase 1: Research (split into more granular research tasks)
            research_results = self._execute_research_phase(genre, custom_inputs, config)
            results["research"] = research_results
            
            if chunk_callback:
                chunk_callback("research", research_results)
            
            # Phase 2: Worldbuilding
            worldbuilding_agent = self.crew_factory.agent_factory.create_worldbuilder(genre)
            worldbuilding_task = Task(
                description=f"Based on the research brief, create a vivid and immersive {genre} world "
                          f"with appropriate atmosphere, rules, and distinctive features. "
                          f"Define the primary locations where the story will unfold.",
                agent=worldbuilding_agent,
                expected_output="A detailed world description with locations, atmosphere, and rules",
                context=research_results
            )
            
            world = self._execute_task(worldbuilding_task)
            results["worldbuilding"] = world
            
            if chunk_callback:
                chunk_callback("worldbuilding", world)
            
            # Phase 3: Character Creation
            char_agent = self.crew_factory.agent_factory.create_character_creator(genre)
            char_task = Task(
                description=f"Create compelling {genre} characters that fit the world. "
                          f"Develop a protagonist, an antagonist, and key supporting characters "
                          f"with clear motivations, backgrounds, and relationships.",
                agent=char_agent,
                expected_output="Character profiles for all main characters including motivations and relationships",
                context=f"Research: {research_results}\n\nWorld: {world}"
            )
            
            characters = self._execute_task(char_task)
            results["characters"] = characters
            
            if chunk_callback:
                chunk_callback("characters", characters)
            
            # Phase 4: Plot Development
            plot_agent = self.crew_factory.agent_factory.create_plotter(genre)
            plot_task = Task(
                description=f"Using the established world and characters, develop a {genre} plot "
                          f"with appropriate structure, pacing, and twists. Create an outline "
                          f"of the main events and ensure it follows {genre} conventions while "
                          f"remaining fresh and engaging.",
                agent=plot_agent,
                expected_output="A detailed plot outline with key events, conflicts, and resolution",
                context=f"Research: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}"
            )
            
            plot = self._execute_task(plot_task)
            results["plot"] = plot
            
            if chunk_callback:
                chunk_callback("plot", plot)
            
            # Phase 5: Writing
            writer_agent = self.crew_factory.agent_factory.create_writer(genre)
            writing_task = Task(
                description=f"Write the {genre} story based on the world, characters, and plot outline. "
                          f"Use appropriate style, voice, and dialogue for the genre. "
                          f"Create vivid descriptions and engaging narrative.",
                agent=writer_agent,
                expected_output="A complete draft of the story with appropriate style and voice",
                context=f"Research: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}\n\nPlot: {plot}"
            )
            
            draft = self._execute_task(writing_task)
            results["draft"] = draft
            
            if chunk_callback:
                chunk_callback("draft", draft)
            
            # Phase 6: Editing
            editor_agent = self.crew_factory.agent_factory.create_editor(genre)
            editing_task = Task(
                description=f"Review and refine the {genre} story draft. Ensure consistency in "
                          f"plot, characters, and setting. Polish the prose while maintaining "
                          f"the appropriate {genre} style. Correct any errors or inconsistencies.",
                agent=editor_agent,
                expected_output="A polished, final version of the story",
                context=f"Draft: {draft}\n\nResearch: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}\n\nPlot: {plot}"
            )
            
            final_story = self._execute_task(editing_task)
            results["final_story"] = final_story
            
            if chunk_callback:
                chunk_callback("final_story", final_story)
            
            return results
        finally:
            # Restore original debug mode
            self.debug_mode = original_debug_mode
            if hasattr(self.crew_executor, 'debug_mode'):
                self.crew_executor.debug_mode = original_debug_mode
    
    def _execute_research_phase(self, genre: str, custom_inputs: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute the research phase broken down into smaller sub-tasks.
        
        Args:
            genre: The genre to research
            custom_inputs: Optional custom inputs
            config: Optional configuration overrides
            
        Returns:
            Comprehensive research results
        """
        # Create a researcher agent
        researcher = self.crew_factory.agent_factory.create_researcher(genre)
        
        # Break down research into smaller, more manageable subtasks
        genre_research_task = Task(
            description=f"Research the essential elements and history of {genre} pulp fiction. "
                      f"Focus only on identifying the core tropes, themes, and conventions. "
                      f"Keep this brief and focused on the most important elements.",
            agent=researcher,
            expected_output="A concise brief on the core elements of the genre",
        )
        
        # Execute first subtask
        genre_elements = self._execute_task(genre_research_task)
        
        # Second research subtask based on initial findings
        historical_context_task = Task(
            description=f"Based on your initial research on {genre} pulp fiction elements, "
                      f"provide historical context and key time periods or movements that "
                      f"influenced this genre. Keep this brief and focused.",
            agent=researcher,
            expected_output="Historical context brief for the genre",
            context=genre_elements
        )
        
        # Execute second subtask
        historical_context = self._execute_task(historical_context_task)
        
        # Third research subtask for writing style and language
        style_research_task = Task(
            description=f"Research the distinctive writing style, language patterns, and "
                      f"vocabulary commonly found in {genre} pulp fiction. Include examples "
                      f"of typical phrasing, dialogue patterns, and narrative voice.",
            agent=researcher,
            expected_output="Writing style guide for the genre",
            context=f"Genre Elements: {genre_elements}\n\nHistorical Context: {historical_context}"
        )
        
        # Execute third subtask
        style_guide = self._execute_task(style_research_task)
        
        # Compile all research results
        compiled_research = f"""# {genre.title()} Pulp Fiction Research Brief

## Core Genre Elements
{genre_elements}

## Historical Context
{historical_context}

## Writing Style Guide
{style_guide}
"""
        
        return compiled_research
        
    def _execute_task(self, task: Task, timeout_seconds: int = 120) -> str:
        """
        Execute a task and return its result.
        
        This method handles the actual execution of a task, which is needed
        because Task in CrewAI doesn't have an execute method directly.
        
        Args:
            task: The task to execute
            timeout_seconds: Maximum time to wait for task completion
            
        Returns:
            The result of the task execution
        """
        # Add task context to diagnostic information
        context = {
            "task_description": task.description,
            "agent_name": task.agent.name if hasattr(task.agent, "name") else "Unknown",
            "expected_output": task.expected_output,
        }
        
        logger.info(f"Starting task execution: {context['agent_name']}")
        logger.info(f"Task description: {task.description[:100]}...")
        
        # Create a simple crew with just this task
        single_task_crew = Crew(
            agents=[task.agent],
            tasks=[task],
            verbose=self.crew_factory.verbose,
            process=self.crew_factory.process
        )
        
        try:
            # Execute the crew with a timeout
            logger.info(f"Executing crew with timeout of {timeout_seconds} seconds")
            with timeout(timeout_seconds):
                result = single_task_crew.kickoff()
                
            logger.info(f"Task completed successfully, result length: {len(result)} chars")
            return result
            
        except TimeoutError:
            error_msg = f"Task execution timed out after {timeout_seconds} seconds"
            logger.error(error_msg)
            return f"ERROR: {error_msg}. This is a fallback response to prevent the process from hanging."
            
        except Exception as e:
            # Enhance the exception with task context and diagnostic information
            error_info = ErrorHandler.handle_exception(
                e, 
                context=context,
                collect_diagnostics=True,
                show_traceback=self.debug_mode
            )
            
            # Log that we're attempting to recover
            logger.warning(f"Task execution failed. Attempting to return partial results.")
            
            # If we have a partial result in the context, use it
            if hasattr(single_task_crew, "last_result") and single_task_crew.last_result:
                logger.info("Recovered partial result from failed task.")
                return single_task_crew.last_result
                
            # Fallback to a minimal response
            fallback_message = (
                f"Task execution failed: {error_info['error_type']}: {error_info['error_message']}. "
                f"This is a fallback message to prevent the process from failing completely."
            )
            logger.warning(f"Using fallback message: {fallback_message}")
            return fallback_message 