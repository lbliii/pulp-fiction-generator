"""
Builder for creating Agent instances.
"""

from typing import Any, Dict
from crewai import Agent

from ...models.model_service import ModelService
from ...models.crewai_adapter import CrewAIModelAdapter


class AgentBuilder:
    """
    Responsible for building Agent instances from configurations.
    
    This class handles the actual creation of Agent objects based on 
    configurations and model services.
    """
    
    def __init__(self, model_service: ModelService):
        """
        Initialize the agent builder.
        
        Args:
            model_service: Service for model interactions
        """
        self.model_service = model_service
        # Create a CrewAI-compatible wrapper for the model service
        self.crewai_model = CrewAIModelAdapter(ollama_adapter=model_service)
    
    def build_agent(self, config: Dict[str, Any], verbose: bool = False) -> Agent:
        """
        Build an agent from a configuration.
        
        Args:
            config: Agent configuration
            verbose: Whether to enable verbose output
            
        Returns:
            Configured Agent instance
        """
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", verbose),
            allow_delegation=config.get("allow_delegation", False),
            llm=self.crewai_model,
            tools=config.get("tools", [])
        ) 