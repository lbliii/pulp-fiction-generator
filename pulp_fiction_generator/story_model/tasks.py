"""
Task factory for story generation.

Creates and configures tasks for different story generation steps.
"""

from typing import Any, Dict, Optional, Callable, List, Type, Union
import os
import copy

from crewai import Task
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from pydantic import BaseModel

from .validation import StoryValidator
from .models import StoryOutput
from ..utils.errors import logger
from .conditions import (
    needs_research_expansion,
    needs_character_development,
    needs_plot_twist,
    needs_style_improvement,
    has_inconsistencies
)


class TaskFactory:
    """
    Factory for creating story generation tasks.
    
    This class handles creation of properly configured tasks
    for each step of the story generation process, applying
    appropriate validation and output handling.
    """
    
    def __init__(self, agent_factory=None):
        """
        Initialize the task factory.
        
        Args:
            agent_factory: Factory for creating agents
        """
        self.agent_factory = agent_factory
        self.validator = StoryValidator()
    
    def create_research_task(
        self, 
        genre: str,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a research task for a genre.
        
        Args:
            genre: The genre to research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured research task
        """
        research_agent = self.agent_factory.create_researcher(genre)
        
        return Task(
            name="research",
            description=f"Research the essential elements and history of {genre} pulp fiction.",
            agent=research_agent,
            expected_output="A comprehensive research brief on the genre",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/research.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_research
        )
    
    def create_worldbuilding_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a worldbuilding task for a genre.
        
        Args:
            genre: The genre for worldbuilding
            context: Research context or tasks
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured worldbuilding task
        """
        worldbuilding_agent = self.agent_factory.create_worldbuilder(genre)
        
        return Task(
            name="worldbuilding",
            description=f"Based on the research brief, create a vivid and immersive {genre} world "
                      f"with appropriate atmosphere, rules, and distinctive features. "
                      f"Define the primary locations where the story will unfold.",
            agent=worldbuilding_agent,
            expected_output="A detailed world description with locations, atmosphere, and rules",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/worldbuilding.txt",
            create_directory=True,
            callback=callback,
            guardrail="Ensure the world description includes at least 3 distinct locations"
        )
    
    def create_character_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a character creation task for a genre.
        
        Args:
            genre: The genre for characters
            context: Research and worldbuilding context or tasks
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured character creation task
        """
        char_agent = self.agent_factory.create_character_creator(genre)
        
        return Task(
            name="characters",
            description=f"Create compelling {genre} characters that fit the world. "
                      f"Develop a protagonist, an antagonist, and key supporting characters "
                      f"with clear motivations, backgrounds, and relationships.",
            agent=char_agent,
            expected_output="Character profiles for all main characters including motivations and relationships",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/characters.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_characters
        )
    
    def create_plot_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a plot development task for a genre.
        
        Args:
            genre: The genre for plot development
            context: Previous context or tasks
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured plot development task
        """
        plot_agent = self.agent_factory.create_plotter(genre)
        
        return Task(
            name="plot",
            description=f"Using the established world and characters, develop a {genre} plot "
                      f"with appropriate structure, pacing, and twists. Create an outline "
                      f"of the main events and ensure it follows {genre} conventions while "
                      f"remaining fresh and engaging.",
            agent=plot_agent,
            expected_output="A detailed plot outline with key events, conflicts, and resolution",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/plot.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_plot
        )
    
    def create_writing_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a writing task for a genre.
        
        Args:
            genre: The genre for writing
            context: Previous context or tasks
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured writing task
        """
        writer_agent = self.agent_factory.create_writer(genre)
        
        return Task(
            name="draft",
            description=f"Write the {genre} story based on the world, characters, and plot outline. "
                      f"Use appropriate style, voice, and dialogue for the genre. "
                      f"Create vivid descriptions and engaging narrative.",
            agent=writer_agent,
            expected_output="A complete draft of the story with appropriate style and voice",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/draft.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_story_content
        )
    
    def create_editing_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None,
        output_pydantic: Type[BaseModel] = StoryOutput
    ) -> Task:
        """
        Create an editing task for a genre.
        
        Args:
            genre: The genre for editing
            context: Previous context or tasks
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            output_pydantic: Pydantic model for structured output
            
        Returns:
            Configured editing task
        """
        editor_agent = self.agent_factory.create_editor(genre)
        
        return Task(
            name="final_story",
            description=f"Review and refine the {genre} story draft. Ensure consistency in "
                      f"plot, characters, and setting. Polish the prose while maintaining "
                      f"the appropriate {genre} style. Correct any errors or inconsistencies.",
            agent=editor_agent,
            expected_output="A polished, final version of the story",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/final_story.txt",
            create_directory=True,
            callback=callback,
            output_pydantic=output_pydantic,
            guardrail="Ensure the final story has proper formatting and no grammatical errors"
        )
    
    def create_research_subtasks(
        self, 
        genre: str,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> List[Task]:
        """
        Create a set of more granular research subtasks.
        
        Args:
            genre: The genre to research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            List of research subtasks
        """
        researcher = self.agent_factory.create_researcher(genre)
        subtasks = []
        
        # First subtask: Core genre elements
        genre_research_task = Task(
            name="genre_elements",
            description=f"Research the essential elements and history of {genre} pulp fiction. "
                      f"Focus only on identifying the core tropes, themes, and conventions. "
                      f"Keep this brief and focused on the most important elements.",
            agent=researcher,
            expected_output="A concise brief on the core elements of the genre",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/genre_elements.txt",
            create_directory=True,
            callback=callback,
            guardrail="Ensure the research identifies at least 5 core tropes or conventions"
        )
        subtasks.append(genre_research_task)
        
        # Second subtask: Historical context
        historical_context_task = Task(
            name="historical_context",
            description=f"Based on your initial research on {genre} pulp fiction elements, "
                      f"provide historical context and key time periods or movements that "
                      f"influenced this genre. Keep this brief and focused.",
            agent=researcher,
            expected_output="Historical context brief for the genre",
            context=[genre_research_task],
            output_file=f"output/{project_dir}/chapter_{chapter_num}/historical_context.txt",
            create_directory=True,
            callback=callback,
            guardrail="Ensure the historical context mentions at least 2 specific time periods"
        )
        subtasks.append(historical_context_task)
        
        # Third subtask: Writing style
        style_research_task = Task(
            name="style_guide",
            description=f"Research the distinctive writing style, language patterns, and "
                      f"vocabulary commonly found in {genre} pulp fiction. Include examples "
                      f"of typical phrasing, dialogue patterns, and narrative voice.",
            agent=researcher,
            expected_output="Writing style guide for the genre",
            context=[genre_research_task, historical_context_task],
            output_file=f"output/{project_dir}/chapter_{chapter_num}/style_guide.txt",
            create_directory=True,
            callback=callback,
            guardrail="Ensure the style guide includes specific examples of dialogue patterns"
        )
        subtasks.append(style_research_task)
        
        return subtasks 

    def create_conditional_task(
        self,
        name: str,
        description: str,
        agent: Any,
        condition: Callable[[TaskOutput], bool],
        expected_output: str,
        context: Optional[Union[str, List[Task]]] = None,
        output_file: Optional[str] = None,
        create_directory: bool = False,
        callback: Optional[Callable] = None,
        guardrail: Optional[Union[str, Callable]] = None,
        output_pydantic: Optional[Type[BaseModel]] = None
    ) -> ConditionalTask:
        """
        Create a conditional task that executes only if a condition is met.
        
        Args:
            name: Task name
            description: Task description
            agent: Agent to perform the task
            condition: Function to determine if task should run
            expected_output: Expected output description
            context: Previous context or tasks
            output_file: File path for task output
            create_directory: Whether to create output directory
            callback: Optional callback function
            guardrail: Optional validation function or string
            output_pydantic: Optional Pydantic model for structured output
            
        Returns:
            Configured conditional task
        """
        task_args = {
            "name": name,
            "description": description,
            "agent": agent,
            "condition": condition,
            "expected_output": expected_output,
            "context": context
        }
        
        if output_file:
            task_args["output_file"] = output_file
            task_args["create_directory"] = create_directory
            
        if callback:
            task_args["callback"] = callback
            
        if guardrail:
            task_args["guardrail"] = guardrail
            
        if output_pydantic:
            task_args["output_pydantic"] = output_pydantic
            
        return ConditionalTask(**task_args)

    def create_research_expansion_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> ConditionalTask:
        """
        Create a conditional task for expanding research when needed.
        
        Args:
            genre: The genre to research further
            context: Initial research context
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured conditional research expansion task
        """
        research_agent = self.agent_factory.create_researcher(genre)
        
        return self.create_conditional_task(
            name="research_expansion",
            description=f"Based on the initial research, investigate deeper into the specific {genre} elements that need more detail.",
            agent=research_agent,
            condition=needs_research_expansion,
            expected_output="Expanded research with detailed information on specific topics",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/research_expanded.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_research
        )
        
    def create_character_development_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> ConditionalTask:
        """
        Create a conditional task for developing characters further when needed.
        
        Args:
            genre: The genre for character development
            context: Initial character creation context
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured conditional character development task
        """
        char_agent = self.agent_factory.create_character_creator(genre)
        
        return self.create_conditional_task(
            name="character_development",
            description=f"Develop more depth for the {genre} characters. Add more psychological complexity, backstory, and unique traits to make them more compelling.",
            agent=char_agent,
            condition=needs_character_development,
            expected_output="Enhanced character profiles with deeper psychology and backstory",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/characters_enhanced.txt",
            create_directory=True,
            callback=callback,
            guardrail=self.validator.validate_characters
        )
        
    def create_plot_twist_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> ConditionalTask:
        """
        Create a conditional task for adding a plot twist when the story needs one.
        
        Args:
            genre: The genre for the plot twist
            context: Plot development context
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured conditional plot twist task
        """
        plot_agent = self.agent_factory.create_plotter(genre)
        
        return self.create_conditional_task(
            name="plot_twist",
            description=f"Create an unexpected but logical plot twist for the {genre} story that increases tension and reader engagement.",
            agent=plot_agent,
            condition=needs_plot_twist,
            expected_output="A compelling plot twist that can be integrated into the story",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/plot_twist.txt",
            create_directory=True,
            callback=callback
        )
        
    def create_style_improvement_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> ConditionalTask:
        """
        Create a conditional task for improving writing style when needed.
        
        Args:
            genre: The genre for style improvement
            context: Draft context
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured conditional style improvement task
        """
        editor_agent = self.agent_factory.create_editor(genre)
        
        return self.create_conditional_task(
            name="style_improvement",
            description=f"Enhance the writing style of the {genre} story draft. Improve prose, descriptions, and dialogue to better match genre conventions.",
            agent=editor_agent,
            condition=needs_style_improvement,
            expected_output="An improved draft with better writing style",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/style_improved.txt",
            create_directory=True,
            callback=callback
        )
        
    def create_consistency_check_task(
        self, 
        genre: str,
        context: Union[str, List[Task]],
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> ConditionalTask:
        """
        Create a conditional task for fixing inconsistencies when needed.
        
        Args:
            genre: The genre for consistency check
            context: Draft context
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Configured conditional consistency check task
        """
        editor_agent = self.agent_factory.create_editor(genre)
        
        return self.create_conditional_task(
            name="consistency_check",
            description=f"Fix any plot holes, character inconsistencies, or timeline issues in the {genre} story draft.",
            agent=editor_agent,
            condition=has_inconsistencies,
            expected_output="A version of the story with inconsistencies fixed",
            context=context,
            output_file=f"output/{project_dir}/chapter_{chapter_num}/consistency_fixed.txt",
            create_directory=True,
            callback=callback
        )

    def prepare_tool_with_forced_output(self, tool: Any) -> Any:
        """
        Prepare a tool to use forced output as result.
        
        Args:
            tool: The tool to modify
            
        Returns:
            Tool with forced output configured
        """
        tool_copy = copy.deepcopy(tool)
        tool_copy.result_as_answer = True
        return tool_copy
    
    def create_raw_research_task(
        self, 
        genre: str,
        tool: Any,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a task that uses a tool with forced output as result for research.
        
        Args:
            genre: The genre to research
            tool: The tool to use for research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Task with forced tool output
        """
        # Prepare the tool with forced output
        forced_output_tool = self.prepare_tool_with_forced_output(tool)
        
        # Create the agent with the forced output tool
        research_agent = self.agent_factory.create_researcher(
            genre=genre, 
            tools=[forced_output_tool]
        )
        
        return Task(
            name="raw_genre_research",
            description=f"Use the provided tool to research essential elements of {genre} pulp fiction. "
                      f"The tool's output will be captured directly as the task result.",
            agent=research_agent,
            expected_output="Raw research data about the genre from the tool",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/raw_genre_research.txt",
            create_directory=True,
            callback=callback
        )
    
    def create_raw_character_references_task(
        self, 
        genre: str,
        tool: Any,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a task that uses a tool with forced output as result for character references.
        
        Args:
            genre: The genre to research
            tool: The tool to use for character research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Task with forced tool output
        """
        # Prepare the tool with forced output
        forced_output_tool = self.prepare_tool_with_forced_output(tool)
        
        # Create the agent with the forced output tool
        char_agent = self.agent_factory.create_character_creator(
            genre=genre, 
            tools=[forced_output_tool]
        )
        
        return Task(
            name="raw_character_references",
            description=f"Use the provided tool to gather reference information about archetypical {genre} characters. "
                      f"The tool's output will be captured directly as the task result.",
            agent=char_agent,
            expected_output="Raw character reference data from the tool",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/raw_character_references.txt",
            create_directory=True,
            callback=callback
        )
    
    def create_raw_style_examples_task(
        self, 
        genre: str,
        tool: Any,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a task that uses a tool with forced output as result for style examples.
        
        Args:
            genre: The genre to research
            tool: The tool to use for style research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Task with forced tool output
        """
        # Prepare the tool with forced output
        forced_output_tool = self.prepare_tool_with_forced_output(tool)
        
        # Create the agent with the forced output tool
        writer_agent = self.agent_factory.create_writer(
            genre=genre, 
            tools=[forced_output_tool]
        )
        
        return Task(
            name="raw_style_examples",
            description=f"Use the provided tool to gather examples of writing style in {genre} pulp fiction. "
                      f"The tool's output will be captured directly as the task result.",
            agent=writer_agent,
            expected_output="Raw style examples from the tool",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/raw_style_examples.txt",
            create_directory=True,
            callback=callback
        )
    
    def create_raw_plot_structures_task(
        self, 
        genre: str,
        tool: Any,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None
    ) -> Task:
        """
        Create a task that uses a tool with forced output as result for plot structures.
        
        Args:
            genre: The genre to research
            tool: The tool to use for plot research
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            
        Returns:
            Task with forced tool output
        """
        # Prepare the tool with forced output
        forced_output_tool = self.prepare_tool_with_forced_output(tool)
        
        # Create the agent with the forced output tool
        plot_agent = self.agent_factory.create_plotter(
            genre=genre, 
            tools=[forced_output_tool]
        )
        
        return Task(
            name="raw_plot_structures",
            description=f"Use the provided tool to gather information about common plot structures in {genre} pulp fiction. "
                      f"The tool's output will be captured directly as the task result.",
            agent=plot_agent,
            expected_output="Raw plot structure data from the tool",
            output_file=f"output/{project_dir}/chapter_{chapter_num}/raw_plot_structures.txt",
            create_directory=True,
            callback=callback
        )
        
    def create_tool_task(
        self,
        name: str,
        description: str,
        agent: Any,
        tool: Any,
        expected_output: str,
        chapter_num: int = 1,
        project_dir: str = "default_project",
        callback: Optional[Callable] = None,
        guardrail: Optional[Union[str, Callable]] = None
    ) -> Task:
        """
        Generic method to create a task with a tool that uses forced output as result.
        
        Args:
            name: Task name
            description: Task description
            agent: Agent to perform the task
            tool: Tool to use with forced output
            expected_output: Expected output description
            chapter_num: Chapter number
            project_dir: Project directory for output
            callback: Optional callback function
            guardrail: Optional validation function or string
            
        Returns:
            Task with forced tool output
        """
        # Prepare the tool with forced output
        forced_output_tool = self.prepare_tool_with_forced_output(tool)
        
        # Assign the tool to the agent
        agent_with_tool = copy.deepcopy(agent)
        agent_with_tool.tools = [forced_output_tool]
        
        task_args = {
            "name": name,
            "description": description,
            "agent": agent_with_tool,
            "expected_output": expected_output,
            "output_file": f"output/{project_dir}/chapter_{chapter_num}/{name}.txt",
            "create_directory": True
        }
        
        if callback:
            task_args["callback"] = callback
            
        if guardrail:
            task_args["guardrail"] = guardrail
            
        return Task(**task_args) 