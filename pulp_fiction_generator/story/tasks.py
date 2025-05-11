"""
Task factory for story generation.

Creates and configures tasks for different story generation steps.
"""

from typing import Any, Dict, Optional, Callable, List, Type, Union
import os

from crewai import Task
from pydantic import BaseModel

from .validation import StoryValidator
from .models import StoryOutput
from ..utils.errors import logger


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