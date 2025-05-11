"""
StoryManager agent to coordinate collaboration between other agents in the story creation process.
"""

from typing import Dict, Any, List, Optional
from crewai import Agent

class StoryManagerAgent:
    """
    Specialized agent responsible for orchestrating the story creation process.
    
    The StoryManager agent oversees the work of other agents, delegates tasks,
    handles agent collaboration, and ensures the story maintains coherence and quality.
    """
    
    def __init__(
        self,
        llm_config: Dict[str, Any],
        tools: Optional[List[Any]] = None,
        verbose: bool = True
    ):
        """
        Initialize the StoryManager agent.
        
        Args:
            llm_config: Configuration for the language model
            tools: Optional list of tools for the agent to use
            verbose: Whether the agent should be verbose in logging
        """
        self.llm_config = llm_config
        self.tools = tools or []
        self.verbose = verbose
        
    def create_agent(self, genre: str) -> Agent:
        """
        Create the StoryManager agent for a specific genre.
        
        Args:
            genre: The genre for this story
            
        Returns:
            An initialized Agent instance with manager capabilities
        """
        return Agent(
            role=f"{genre.capitalize()} Story Manager",
            goal=f"Orchestrate the creation of a compelling {genre} pulp fiction story by coordinating specialized agents",
            backstory=(
                f"You are an experienced {genre} pulp fiction editor, responsible for "
                f"overseeing the entire story creation process. You understand the nuances of {genre} fiction "
                f"and how to blend research, worldbuilding, character development, and plotting "
                f"into a cohesive narrative. Your role is to coordinate the work of specialized agents, "
                f"delegate tasks appropriately, and ensure the final product meets the standards of "
                f"classic pulp fiction."
            ),
            tools=self.tools,
            verbose=self.verbose,
            llm_config=self.llm_config,
            allow_delegation=True,  # Enable delegation capabilities
            # Manager-specific configuration
            delegation_config={
                "delegation_trigger": (
                    "When an agent indicates they need specialized help from a different domain, "
                    "or when you detect a task would be more efficiently handled by an agent with different expertise."
                ),
                "delegation_prompt": (
                    "Consider which agent would be best suited to handle this task. "
                    "Delegate it clearly, specifying what information they need and what output you expect."
                )
            }
        ) 