"""
CrewCoordinator manages and orchestrates the creation and execution of agent crews.
"""

from typing import Any, Dict, List, Optional, Union

from crewai import Agent, Crew, Process, Task

from ..agents.agent_factory import AgentFactory
from ..models.model_service import ModelService
from ..utils.context_visualizer import ContextVisualizer
from ..utils.error_handling import ErrorHandler, logger, timeout, TimeoutError


class CrewCoordinator:
    """
    Coordinates the creation and execution of agent crews for story generation.
    
    This class is responsible for assembling crews of agents, configuring their
    tasks, and managing the execution of the generation process.
    """
    
    def __init__(
        self, 
        agent_factory: AgentFactory,
        model_service: ModelService,
        process: Process = Process.sequential,
        verbose: bool = True,
        debug_mode: bool = False,
        debug_output_dir: Optional[str] = None
    ):
        """
        Initialize the crew coordinator.
        
        Args:
            agent_factory: Factory for creating agents
            model_service: Service for model interactions
            process: The execution process to use
            verbose: Whether crews should be verbose
            debug_mode: Whether to enable debug visualization
            debug_output_dir: Directory for debug output (if debug_mode is True)
        """
        self.agent_factory = agent_factory
        self.model_service = model_service
        self.process = process
        self.verbose = verbose
        self.debug_mode = debug_mode
        
        # Initialize context visualizer if debug mode is enabled
        self.visualizer = ContextVisualizer(
            output_dir=debug_output_dir,
            enabled=debug_mode
        ) if debug_mode else None
    
    def create_basic_crew(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Crew:
        """
        Create a basic crew with all standard agents for a genre.
        
        Args:
            genre: The genre to create the crew for
            config: Optional configuration overrides
            
        Returns:
            A configured crew
        """
        # Create agents
        researcher = self.agent_factory.create_researcher(genre)
        worldbuilder = self.agent_factory.create_worldbuilder(genre)
        character_creator = self.agent_factory.create_character_creator(genre)
        plotter = self.agent_factory.create_plotter(genre)
        writer = self.agent_factory.create_writer(genre)
        editor = self.agent_factory.create_editor(genre)
        
        # Create tasks with appropriate descriptions for the genre
        research_task = Task(
            description=f"Research essential elements of {genre} pulp fiction, "
                      f"including common tropes, historical context, and reference materials. "
                      f"Create a comprehensive research brief that other agents can use.",
            agent=researcher,
            expected_output="A detailed research brief with genre elements, tropes, historical context, and references"
        )
        
        worldbuilding_task = Task(
            description=f"Based on the research brief, create a vivid and immersive {genre} world "
                      f"with appropriate atmosphere, rules, and distinctive features. "
                      f"Define the primary locations where the story will unfold.",
            agent=worldbuilder,
            expected_output="A detailed world description with locations, atmosphere, and rules"
        )
        
        character_task = Task(
            description=f"Create compelling {genre} characters that fit the world. "
                      f"Develop a protagonist, an antagonist, and key supporting characters "
                      f"with clear motivations, backgrounds, and relationships.",
            agent=character_creator,
            expected_output="Character profiles for all main characters including motivations and relationships"
        )
        
        plot_task = Task(
            description=f"Using the established world and characters, develop a {genre} plot "
                      f"with appropriate structure, pacing, and twists. Create an outline "
                      f"of the main events and ensure it follows {genre} conventions while "
                      f"remaining fresh and engaging.",
            agent=plotter,
            expected_output="A detailed plot outline with key events, conflicts, and resolution"
        )
        
        writing_task = Task(
            description=f"Write the {genre} story based on the world, characters, and plot outline. "
                      f"Use appropriate style, voice, and dialogue for the genre. "
                      f"Create vivid descriptions and engaging narrative.",
            agent=writer,
            expected_output="A complete draft of the story with appropriate style and voice"
        )
        
        editing_task = Task(
            description=f"Review and refine the {genre} story draft. Ensure consistency in "
                      f"plot, characters, and setting. Polish the prose while maintaining "
                      f"the appropriate {genre} style. Correct any errors or inconsistencies.",
            agent=editor,
            expected_output="A polished, final version of the story"
        )
        
        # Create the crew
        crew = Crew(
            agents=[
                researcher,
                worldbuilder,
                character_creator,
                plotter,
                writer,
                editor
            ],
            tasks=[
                research_task,
                worldbuilding_task,
                character_task,
                plot_task,
                writing_task,
                editing_task
            ],
            verbose=self.verbose,
            process=self.process
        )
        
        return crew
    
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
        # Create agents
        researcher = self.agent_factory.create_researcher(genre)
        character_creator = self.agent_factory.create_character_creator(genre)
        plotter = self.agent_factory.create_plotter(genre)
        writer = self.agent_factory.create_writer(genre)
        editor = self.agent_factory.create_editor(genre)
        
        # Create tasks with appropriate descriptions for continuation
        research_task = Task(
            description=f"Review the existing {genre} story and identify key elements, "
                      f"themes, and plot points that should be continued or resolved. "
                      f"Create a brief of elements to maintain consistency with.",
            agent=researcher,
            context=previous_output,
            expected_output="A detailed brief of the story elements to maintain consistency with"
        )
        
        character_task = Task(
            description=f"Based on the existing story, update character profiles "
                      f"to reflect their development so far. Identify potential new "
                      f"characters needed for the continuation. Ensure consistency with "
                      f"established character traits and motivations.",
            agent=character_creator,
            context=previous_output,
            expected_output="Updated character profiles and potential new characters"
        )
        
        plot_task = Task(
            description=f"Using the existing story and character profiles, develop the "
                      f"next segment of the plot. Ensure it builds on previous events and "
                      f"continues the narrative in an engaging way. Create an outline for "
                      f"the continuation that fits {genre} conventions.",
            agent=plotter,
            expected_output="A plot outline for the continuation that builds on the existing story"
        )
        
        writing_task = Task(
            description=f"Write the continuation of the {genre} story based on the "
                      f"updated characters and plot outline. Maintain consistency with "
                      f"the style, voice, and narrative of the existing story. Ensure "
                      f"smooth transition from the previous segment.",
            agent=writer,
            context=previous_output,
            expected_output="A draft of the story continuation with consistent style and voice"
        )
        
        editing_task = Task(
            description=f"Review and refine the continuation draft. Ensure consistency "
                      f"with the existing story in terms of plot, characters, and setting. "
                      f"Polish the prose while maintaining the appropriate {genre} style. "
                      f"Correct any errors or inconsistencies.",
            agent=editor,
            context=previous_output,
            expected_output="A polished, final version of the story continuation"
        )
        
        # Create the crew
        crew = Crew(
            agents=[
                researcher,
                character_creator,
                plotter,
                writer,
                editor
            ],
            tasks=[
                research_task,
                character_task,
                plot_task,
                writing_task,
                editing_task
            ],
            verbose=self.verbose,
            process=self.process
        )
        
        return crew
    
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
        if len(agent_types) != len(task_descriptions):
            raise ValueError("Number of agent types must match number of task descriptions")
        
        # Create agents
        agents = [self.agent_factory.create_agent(agent_type, genre) for agent_type in agent_types]
        
        # Create tasks
        tasks = [
            Task(
                description=description,
                agent=agent,
                expected_output=f"Output for task: {description[:50]}..."
            ) for description, agent in zip(task_descriptions, agents)
        ]
        
        # Create the crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=self.verbose,
            process=self.process
        )
        
        return crew
    
    def kickoff_crew(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the execution of a crew.
        
        Args:
            crew: The crew to execute
            inputs: Optional inputs for the crew
            
        Returns:
            The final output from the crew
        """
        # Initialize inputs if needed
        inputs = inputs or {}
        
        # Visualize initial context if debugging is enabled
        if self.debug_mode and self.visualizer:
            self.visualizer.visualize_context(inputs, stage="Initial Inputs")
        
        # Set up task callback if debugging is enabled
        if self.debug_mode and self.visualizer:
            original_execute = Task.execute
            
            def execute_with_debug(task_self, *args, **kwargs):
                # Capture the context before task execution
                agent_name = task_self.agent.name if hasattr(task_self.agent, 'name') else "Unknown Agent"
                context_before = kwargs.get('context', {})
                
                # Show prompt template if available
                if hasattr(task_self.agent, 'llm_config') and 'prompt_template' in task_self.agent.llm_config:
                    self.visualizer.show_prompt_template(
                        agent_name,
                        task_self.agent.llm_config['prompt_template'],
                        {
                            "task": task_self.description,
                            "context": context_before
                        }
                    )
                
                # Execute the original task
                result = original_execute(task_self, *args, **kwargs)
                
                # Capture context after execution (simplified assumption that result is the new context)
                context_after = {"result": result, **context_before}
                
                # Track the agent interaction
                self.visualizer.track_agent_interaction(
                    agent_name=agent_name,
                    input_context=context_before,
                    output_context=context_after,
                    prompt=task_self.description,
                    response=result
                )
                
                # Update visualized context
                self.visualizer.visualize_context(
                    context_after, 
                    stage=f"After {agent_name}"
                )
                
                return result
            
            # Monkey patch Task.execute for this run
            Task.execute = execute_with_debug
        
        try:
            # Run the crew
            result = crew.kickoff(inputs=inputs)
            
            # Final context visualization
            if self.debug_mode and self.visualizer:
                final_context = {"final_result": result, **inputs}
                self.visualizer.visualize_context(final_context, stage="Final Output")
                
                # Export HTML visualization
                self.visualizer.export_visualization_html()
            
            return result
        finally:
            # Restore original execute method if it was patched
            if self.debug_mode and self.visualizer:
                Task.execute = original_execute
    
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
            # Re-initialize visualizer if needed
            if self.debug_mode and not self.visualizer:
                self.visualizer = ContextVisualizer(enabled=True)
            elif not self.debug_mode and self.visualizer:
                self.visualizer.enabled = False
        
        try:
            logger.info(f"Creating basic crew for genre: {genre}")
            crew = self.create_basic_crew(genre, config)
            
            logger.info(f"Starting crew execution with timeout of {timeout_seconds} seconds")
            with timeout(timeout_seconds):
                result = self.kickoff_crew(crew, custom_inputs)
                
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
            if self.visualizer:
                self.visualizer.enabled = self.debug_mode
    
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
        # Allow per-story debug mode override
        original_debug_mode = self.debug_mode
        if debug_mode is not None:
            self.debug_mode = debug_mode
            # Re-initialize visualizer if needed
            if self.debug_mode and not self.visualizer:
                self.visualizer = ContextVisualizer(enabled=True)
            elif not self.debug_mode and self.visualizer:
                self.visualizer.enabled = False
        
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
            worldbuilding_agent = self.agent_factory.create_worldbuilder(genre)
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
            char_agent = self.agent_factory.create_character_creator(genre)
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
            plot_agent = self.agent_factory.create_plotter(genre)
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
            writer_agent = self.agent_factory.create_writer(genre)
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
            editor_agent = self.agent_factory.create_editor(genre)
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
            if self.visualizer:
                self.visualizer.enabled = self.debug_mode
    
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
        researcher = self.agent_factory.create_researcher(genre)
        
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
            verbose=self.verbose,
            process=self.process
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