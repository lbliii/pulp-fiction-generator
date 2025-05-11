"""
CrewFactory handles the creation of different types of agent crews.
"""

from typing import Any, Dict, List, Optional
import time
import json
import os
import re
import os.path
import uuid

from crewai import Agent, Crew, Process, Task
from crewai.security import Fingerprint

from ..agents.agent_factory import AgentFactory
from ..agents.manager_agent import StoryManagerAgent
from ..utils.errors import logger
from .event_listeners import get_default_listeners


def get_logs_dir() -> str:
    """
    Get the absolute path to the logs directory.
    
    Returns:
        Absolute path to the logs directory
    """
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the package root
    package_root = os.path.dirname(current_dir)
    # Go up one more level to the project root
    project_root = os.path.dirname(package_root)
    # Return the absolute path to the logs directory
    return os.path.join(project_root, "logs")


def step_callback(
    formatted_answer: Any,
    agent_action: Optional[str] = None,
    agent_name: Optional[str] = None, 
    task_description: Optional[str] = None,
    step_output: Optional[str] = None
) -> None:
    """
    Step callback for tracking agent actions during crew execution.
    
    Args:
        formatted_answer: The formatted answer from the agent
        agent_action: Action the agent is taking
        agent_name: Name of the agent
        task_description: Optional description of the current task
        step_output: Optional output from the step
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Try to extract agent name from formatted_answer if not provided
    if not agent_name:
        if isinstance(formatted_answer, str):
            agent_name_match = re.search(r"Agent:\s*([^\n]+)", formatted_answer)
            if agent_name_match:
                agent_name = agent_name_match.group(1)
            else:
                agent_name = "Unknown Agent"
        else:
            # Handle AgentFinish or other objects
            if hasattr(formatted_answer, "agent_name"):
                agent_name = formatted_answer.agent_name
            elif hasattr(formatted_answer, "return_values") and hasattr(formatted_answer.return_values, "get"):
                agent_name = formatted_answer.return_values.get("agent_name", "Unknown Agent")
            else:
                agent_name = "Unknown Agent"
    
    # Extract action if not provided
    action = agent_action or "thinking"
    
    logger.info(f"[{timestamp}] Agent '{agent_name}' {action}")
    
    try:
        # Save step information to file
        steps_dir = os.path.join(get_logs_dir(), "steps")
        os.makedirs(steps_dir, exist_ok=True)
        
        # Convert formatted_answer to a string if it's not already one
        formatted_answer_str = str(formatted_answer) if formatted_answer is not None else "None"
        formatted_answer_preview = formatted_answer_str[:100] + "..." if len(formatted_answer_str) > 100 else formatted_answer_str
        
        step_file_path = os.path.join(steps_dir, f"step_{timestamp.replace(' ', '_').replace(':', '-')}.json")
        with open(step_file_path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "agent_name": agent_name,
                "agent_action": action,
                "task_description": task_description,
                "step_output_preview": step_output[:100] + "..." if step_output and len(step_output) > 100 else step_output,
                "formatted_answer_preview": formatted_answer_preview
            }, f, indent=2)
        logger.info(f"Saved step information to {step_file_path}")
    except Exception as e:
        logger.error(f"Error saving step information: {str(e)}")


def task_callback(
    task_output: Any,
    task_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    task_description: Optional[str] = None
) -> None:
    """
    Task callback for tracking task completion during crew execution.
    
    Args:
        task_output: Output from the task (can be TaskOutput object or string)
        task_id: ID of the task (optional)
        agent_name: Name of the agent that completed the task (optional)
        task_description: Description of the task (optional)
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    task_id = task_id or "unknown_task"
    agent_name = agent_name or "unknown_agent"
    
    logger.info(f"[{timestamp}] Task '{task_id}' completed by '{agent_name}'")
    
    # Convert task_output to string if it's an object
    task_output_str = ""
    if task_output is not None:
        if isinstance(task_output, str):
            task_output_str = task_output
        elif hasattr(task_output, 'output') and isinstance(task_output.output, str):
            # Handle TaskOutput object which has an output attribute
            task_output_str = task_output.output
        elif hasattr(task_output, '__str__'):
            # Use string representation as fallback
            task_output_str = str(task_output)
    
    try:
        # Save task information to file
        tasks_dir = os.path.join(get_logs_dir(), "tasks")
        os.makedirs(tasks_dir, exist_ok=True)
        
        # Save metadata with preview to one file
        task_file_path = os.path.join(tasks_dir, f"task_{task_id}.json")
        with open(task_file_path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "task_id": task_id,
                "agent_name": agent_name,
                "task_description": task_description or "No description provided",
                "task_output_preview": task_output_str[:100] + "..." if len(task_output_str) > 100 else task_output_str
            }, f, indent=2)
        
        # Save full output to a separate file
        full_output_path = os.path.join(tasks_dir, f"full_output_{task_id}.txt")
        with open(full_output_path, "w") as f:
            f.write(task_output_str)
            
        logger.info(f"Saved task information to {task_file_path}")
        logger.info(f"Saved full task output to {full_output_path}")
    except Exception as e:
        logger.error(f"Error saving task information: {str(e)}")


class CrewFactory:
    """
    Factory class responsible for creating various types of agent crews.
    
    This class encapsulates the logic for assembling crews of agents and configuring
    their tasks based on different story generation needs.
    """
    
    # Dictionary to store custom inputs by crew name
    _crew_custom_inputs = {}
    
    def __init__(
        self, 
        agent_factory: AgentFactory,
        process: Process = Process.hierarchical,
        verbose: bool = True,
        enable_planning: bool = True,
        use_event_listeners: bool = True
    ):
        """
        Initialize the crew factory.
        
        Args:
            agent_factory: Factory for creating agents
            process: The execution process to use for crews (default: hierarchical)
            verbose: Whether crews should be verbose
            enable_planning: Whether to enable planning for crews (default: True)
            use_event_listeners: Whether to use event listeners
        """
        self.agent_factory = agent_factory
        self.process = process
        self.verbose = verbose
        self.enable_planning = enable_planning
        self.use_event_listeners = use_event_listeners
        self.event_listeners = get_default_listeners() if use_event_listeners else []
        
        # Create a StoryManagerAgent instance
        self.story_manager_agent = StoryManagerAgent(
            llm_config=self.agent_factory.get_default_llm_config(),
        )
    
    def validate_process_configuration(self, process: Process, config: Dict[str, Any]) -> bool:
        """
        Validate that the process configuration is valid.
        
        Args:
            process: The process to validate
            config: The configuration to validate
            
        Returns:
            True if the configuration is valid, False otherwise
            
        Raises:
            ValueError: If the configuration is invalid
        """
        if process == Process.hierarchical:
            # For hierarchical process, we need either manager_llm or manager_agent
            has_manager_llm = config.get("manager_llm") is not None
            has_manager_agent = config.get("manager_agent") is not None
            
            if not (has_manager_llm or has_manager_agent):
                raise ValueError(
                    "Hierarchical process requires either 'manager_llm' or 'manager_agent' "
                    "to be specified in the configuration."
                )
                
        # We'll add support for the consensual process when it becomes available
        # elif process == Process.consensual:
        #     # Add validation for consensual process when implemented
        #     pass
            
        return True
    
    def _get_effective_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the effective configuration by applying defaults and user config.
        
        Args:
            config: User-provided configuration
            
        Returns:
            Effective configuration with defaults applied
        """
        # Define default configuration
        default_config = {
            "memory": True,
            "cache": True,
            "memory_config": {"provider": "local"},
            "output_log_file": None,
            "manager_llm": None,
            "function_calling_llm": None
        }
        
        # Apply user config over defaults
        effective_config = {**default_config, **config}
        
        return effective_config
    
    def store_custom_inputs(self, crew: Crew, custom_inputs: Dict[str, Any]) -> None:
        """
        Store custom inputs for a crew in the class dictionary.
        
        Args:
            crew: The crew object
            custom_inputs: The custom inputs to store
        """
        if not custom_inputs:
            return
            
        # Use the crew's name as the key
        if hasattr(crew, 'name') and crew.name:
            self._crew_custom_inputs[crew.name] = custom_inputs
            logger.info(f"Stored custom inputs for crew '{crew.name}'")
        # Fallback to object ID if no name
        else:
            crew_id = id(crew)
            self._crew_custom_inputs[crew_id] = custom_inputs
            logger.info(f"Stored custom inputs for crew with ID {crew_id}")
    
    def get_custom_inputs(self, crew: Crew) -> Optional[Dict[str, Any]]:
        """
        Get custom inputs for a crew from the class dictionary.
        
        Args:
            crew: The crew object
            
        Returns:
            The custom inputs for the crew, if any
        """
        # Try to get by name first
        if hasattr(crew, 'name') and crew.name and crew.name in self._crew_custom_inputs:
            return self._crew_custom_inputs[crew.name]
        
        # Fallback to object ID
        crew_id = id(crew)
        if crew_id in self._crew_custom_inputs:
            return self._crew_custom_inputs[crew_id]
            
        return None
    
    def _enhance_crew_fingerprint(self, crew: Crew, metadata: Dict[str, Any]) -> None:
        """
        Enhance a crew's fingerprint with additional metadata.
        
        Args:
            crew: The crew instance
            metadata: The metadata to add to the fingerprint
        """
        fingerprint = crew.security_config.fingerprint
        
        # Get existing metadata or initialize empty dict
        existing_metadata = fingerprint.metadata or {}
        
        # Update with new metadata
        existing_metadata.update(metadata)
        
        # Set the updated metadata
        fingerprint.metadata = existing_metadata
    
    def _generate_crew_identifier(self, crew_type: str, genre: str) -> str:
        """
        Generate a unique identifier for a crew based on type and genre.
        
        Args:
            crew_type: The type of crew (e.g., basic, continuation, custom)
            genre: The genre of the crew
            
        Returns:
            A unique identifier string
        """
        timestamp = int(time.time())
        return f"{crew_type}_{genre}_{timestamp}"
    
    def _get_agent_fingerprints(self, agents: List[Agent]) -> Dict[str, str]:
        """
        Get a dictionary of agent names and their fingerprint UUIDs.
        
        Args:
            agents: List of agent instances
            
        Returns:
            Dictionary mapping agent names to fingerprint UUIDs
        """
        return {
            agent.role: agent.fingerprint.uuid_str
            for agent in agents
        }
        
    def _create_crew_with_fingerprinting(
        self,
        crew_type: str,
        agents: List[Agent],
        tasks: List[Task],
        genre: str,
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a crew with fingerprinting metadata.
        
        Args:
            crew_type: Type identifier for the crew
            agents: List of agent instances for the crew
            tasks: List of tasks for the crew
            genre: Genre of the story being created
            custom_inputs: Optional custom inputs for the crew
            config: Optional configuration overrides
            
        Returns:
            Configured Crew instance with fingerprinting
        """
        # Get effective configuration
        effective_config = self._get_effective_config(config or {})
        
        # Generate a deterministic ID for the crew
        crew_id = self._generate_crew_identifier(crew_type, genre)
        
        # Create the crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=effective_config.get("verbose", self.verbose),
            manager_llm=effective_config.get("manager_llm"),
            manager_agent=self.story_manager_agent.get_agent() if effective_config.get("use_manager", True) else None,
            process=effective_config.get("process", self.process),
            full_output=effective_config.get("full_output", True),
            memory=effective_config.get("memory", True),
            max_rpm=effective_config.get("max_rpm"),
            cache=effective_config.get("cache", True),
            enable_planning=effective_config.get("enable_planning", self.enable_planning),
            event_listeners=self.event_listeners if self.use_event_listeners else None
        )
        
        # Add metadata to the crew's fingerprint
        self._enhance_crew_fingerprint(crew, {
            "crew_type": crew_type,
            "genre": genre,
            "crew_id": crew_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent_fingerprints": self._get_agent_fingerprints(agents),
            "task_count": len(tasks),
            "custom_inputs": custom_inputs or {}
        })
        
        # Store custom inputs (if any)
        if custom_inputs:
            self.store_custom_inputs(crew, custom_inputs)
            
        return crew

    def create_basic_crew_with_inputs(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a basic crew for generating stories with custom inputs.
        
        Args:
            genre: Genre of the story to create
            custom_inputs: Dictionary of custom inputs for agents
            config: Optional configuration overrides
            
        Returns:
            Configured crew instance
        """
        # Create the basic crew
        crew = self.create_basic_crew(genre=genre, config=config)
        
        # Store custom inputs in our dictionary instead of trying to attach them directly
        if custom_inputs:
            self.store_custom_inputs(crew, custom_inputs)
            
        return crew
    
    def create_basic_crew(self, genre: str, config: Optional[Dict[str, Any]] = None) -> Crew:
        """
        Create a basic crew with all standard agents for a genre.
        
        Args:
            genre: The genre to create the crew for
            config: Optional configuration overrides
            
        Returns:
            A configured crew
            
        Raises:
            ValueError: If the process configuration is invalid
        """
        # Get effective configuration
        effective_config = self._get_effective_config(config or {})
        
        # Validate process configuration
        process = effective_config.get("process", self.process)
        self.validate_process_configuration(process, effective_config)
        
        # Create agents
        researcher = self.agent_factory.create_researcher(genre)
        worldbuilder = self.agent_factory.create_worldbuilder(genre)
        character_creator = self.agent_factory.create_character_creator(genre)
        plotter = self.agent_factory.create_plotter(genre)
        writer = self.agent_factory.create_writer(genre)
        editor = self.agent_factory.create_editor(genre)
        
        # Create a manager agent if hierarchical process is used
        manager_agent = None
        if process == Process.hierarchical:
            manager_agent = self.story_manager_agent.create_agent(genre)
            effective_config["manager_agent"] = manager_agent
        
        # Create tasks with appropriate descriptions for the genre
        research_task = Task(
            description=f"Research essential elements of {genre} pulp fiction, "
                      f"including common tropes, historical context, and reference materials. "
                      f"Create a comprehensive research brief that other agents can use.",
            agent=researcher,
            expected_output="A detailed research brief with genre elements, tropes, historical context, and references",
            async_execution=False,  # Force synchronous execution for better collaboration
            delegation_enabled=True  # Enable delegation for this task
        )
        
        worldbuilding_task = Task(
            description=f"Based on the research brief, create a vivid and immersive {genre} world "
                      f"with appropriate atmosphere, rules, and distinctive features. "
                      f"Define the primary locations where the story will unfold.",
            agent=worldbuilder,
            expected_output="A detailed world description with locations, atmosphere, and rules",
            context=[research_task],  # Use context to explicitly link to previous tasks
            async_execution=False,
            delegation_enabled=True
        )
        
        character_task = Task(
            description=f"Create compelling {genre} characters that fit the world. "
                      f"Develop a protagonist, an antagonist, and key supporting characters "
                      f"with clear motivations, backgrounds, and relationships.",
            agent=character_creator,
            expected_output="Character profiles for all main characters including motivations and relationships",
            context=[research_task, worldbuilding_task],
            async_execution=False,
            delegation_enabled=True
        )
        
        plot_task = Task(
            description=f"Using the established world and characters, develop a {genre} plot "
                      f"with appropriate structure, pacing, and twists. Create an outline "
                      f"of the main events and ensure it follows {genre} conventions while "
                      f"remaining fresh and engaging.",
            agent=plotter,
            expected_output="A detailed plot outline with key events, conflicts, and resolution",
            context=[research_task, worldbuilding_task, character_task],
            async_execution=False,
            delegation_enabled=True
        )
        
        writing_task = Task(
            description=f"Write the {genre} story based on the world, characters, and plot outline. "
                      f"Use appropriate style, voice, and dialogue for the genre. "
                      f"Create vivid descriptions and engaging narrative.",
            agent=writer,
            expected_output="A complete draft of the story with appropriate style and voice",
            context=[research_task, worldbuilding_task, character_task, plot_task],
            async_execution=False,
            delegation_enabled=True
        )
        
        editing_task = Task(
            description=f"Review and refine the {genre} story draft. Ensure consistency in "
                      f"plot, characters, and setting. Polish the prose while maintaining "
                      f"the appropriate {genre} style. Correct any errors or inconsistencies.",
            agent=editor,
            expected_output="A polished, final version of the story",
            context=[writing_task],  # Only need the writing task as direct context
            async_execution=False,
            delegation_enabled=True
        )
        
        # Apply any configuration overrides
        crew_config = effective_config
        
        # Check if planning should be enabled
        enable_planning = crew_config.get("enable_planning", self.enable_planning)
        planning_llm = None
        
        if enable_planning and hasattr(self.agent_factory, "model_service"):
            # Use the model service from agent factory if available
            planning_llm = self.agent_factory.model_service.get_planning_llm()
            
        # Get event listeners if enabled
        event_listeners = []
        if crew_config.get("use_event_listeners", self.use_event_listeners):
            event_listeners = crew_config.get("event_listeners", self.event_listeners)
        
        # Build the list of agents, adding manager if it exists
        agents = [
            researcher,
            worldbuilder,
            character_creator,
            plotter,
            writer,
            editor
        ]
        
        # Create the crew with enhanced features
        crew = Crew(
            agents=agents,
            tasks=[
                research_task,
                worldbuilding_task,
                character_task,
                plot_task,
                writing_task,
                editing_task
            ],
            verbose=self.verbose,
            process=process,
            memory=crew_config.get("memory", True),  # Enable memory by default
            memory_config=crew_config.get("memory_config", {"provider": "local"}),
            output_log_file=crew_config.get("output_log_file", f"logs/{genre}_story_generation.json"),
            cache=crew_config.get("cache", True),
            name=f"{genre.capitalize()}StoryGenerationCrew",
            step_callback=step_callback,
            task_callback=task_callback,
            planning=enable_planning,
            planning_llm=planning_llm,
            callbacks=event_listeners,
            manager_agent=manager_agent if process == Process.hierarchical else None
        )
        
        return crew
    
    def create_continuation_crew(
        self, 
        genre: str, 
        previous_output: str,
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a crew for continuing a previously generated story.
        
        Args:
            genre: Genre of the story
            previous_output: Previously generated story content
            custom_inputs: Optional custom inputs for agents
            config: Optional configuration overrides
            
        Returns:
            Configured crew instance
        """
        # Create a basic crew first
        crew = self.create_basic_crew(genre=genre, config=config)
        
        # Store the previous output for later use
        # We'll just store it in the custom inputs if they're provided, or create a new dictionary
        previous_output_data = {'previous_output': previous_output}
        
        if custom_inputs:
            # Combine custom inputs with previous output
            combined_inputs = {**custom_inputs, **previous_output_data}
            self.store_custom_inputs(crew, combined_inputs)
        else:
            # Just store the previous output
            self.store_custom_inputs(crew, previous_output_data)
            
        # Create the crew with fingerprinting
        return self._create_crew_with_fingerprinting(
            crew_type="continuation",
            agents=crew.agents,
            tasks=crew.tasks,
            genre=genre,
            custom_inputs=custom_inputs,
            config=config
        )
    
    def create_custom_crew(
        self, 
        genre: str, 
        agent_types: List[str], 
        task_descriptions: List[str],
        custom_inputs: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a crew with custom agents and tasks.
        
        Args:
            genre: Genre of the story
            agent_types: List of agent types to include
            task_descriptions: List of task descriptions
            custom_inputs: Optional custom inputs for agents
            config: Optional configuration overrides
            
        Returns:
            Configured crew instance
        """
        if len(agent_types) != len(task_descriptions):
            raise ValueError("Number of agent types must match number of task descriptions")
        
        # Create the agents
        agents = []
        for agent_type in agent_types:
            agent = self.agent_factory.create_agent(role=agent_type, genre=genre)
            agents.append(agent)
        
        # Create the tasks
        tasks = []
        for i, (agent, description) in enumerate(zip(agents, task_descriptions)):
            tasks.append(
                Task(
                    description=description,
                    agent=agent
                )
            )
        
        # Create the crew with fingerprinting
        return self._create_crew_with_fingerprinting(
            crew_type="custom",
            agents=agents,
            tasks=tasks,
            genre=genre,
            custom_inputs=custom_inputs,
            config=config
        )
        
    def create_specialized_crew(
        self, 
        phase_type: str, 
        genre: str, 
        inputs: Optional[Dict[str, Any]] = None
    ) -> Crew:
        """
        Create a specialized crew for a specific phase of story generation.
        
        Args:
            phase_type: Type of story phase ("worldbuilding", "character", etc.)
            genre: Genre of the story
            inputs: Optional inputs for the crew
            
        Returns:
            Configured crew instance
        """
        # Define agent types and task descriptions for each phase
        phase_configs = {
            "research": {
                "agent_types": ["researcher"],
                "task_descriptions": ["Research the genre, tropes, and key elements of a pulp fiction story in the specified genre."]
            },
            "worldbuilding": {
                "agent_types": ["worldbuilder"],
                "task_descriptions": ["Create a detailed world for the story based on the research."]
            },
            "characters": {
                "agent_types": ["character_creator"],
                "task_descriptions": ["Create detailed characters for the story based on the world and research."]
            },
            "plot": {
                "agent_types": ["plotter"],
                "task_descriptions": ["Develop a compelling plot based on the characters, world, and research."]
            },
            "draft": {
                "agent_types": ["writer"],
                "task_descriptions": ["Write a draft of the story based on the plot, characters, world, and research."]
            },
            "final": {
                "agent_types": ["editor"],
                "task_descriptions": ["Edit and finalize the story draft into a polished final story."]
            }
        }
        
        # Check if the phase type is supported
        if phase_type not in phase_configs:
            raise ValueError(f"Unsupported phase type: {phase_type}")
        
        # Get the configuration for the phase
        phase_config = phase_configs[phase_type]
        
        # Create the crew with fingerprinting
        return self._create_crew_with_fingerprinting(
            crew_type=f"specialized_{phase_type}",
            agents=self.agent_factory.create_agents(phase_config["agent_types"], genre),
            tasks=self.agent_factory.create_tasks(phase_config["task_descriptions"], genre),
            genre=genre,
            custom_inputs=inputs,
            config=None
        ) 