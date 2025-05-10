"""
CrewFactory handles the creation of different types of agent crews.
"""

from typing import Any, Dict, List, Optional

from crewai import Agent, Crew, Process, Task

from ..agents.agent_factory import AgentFactory


class CrewFactory:
    """
    Factory class responsible for creating various types of agent crews.
    
    This class encapsulates the logic for assembling crews of agents and configuring
    their tasks based on different story generation needs.
    """
    
    def __init__(
        self, 
        agent_factory: AgentFactory,
        process: Process = Process.sequential,
        verbose: bool = True
    ):
        """
        Initialize the crew factory.
        
        Args:
            agent_factory: Factory for creating agents
            process: The execution process to use for crews
            verbose: Whether crews should be verbose
        """
        self.agent_factory = agent_factory
        self.process = process
        self.verbose = verbose
    
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