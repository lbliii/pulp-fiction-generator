"""
Builder for creating Agent instances.
"""

from typing import Any, Dict
from crewai import Agent

from ...models.model_service import ModelService
from ...models.crewai_adapter import CrewAIModelAdapter
from ..tools.tool_loader import ToolLoader
from ..knowledge.knowledge_loader import KnowledgeLoader


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
        # Use provided LLM config or default to the model service
        llm = config.get("llm", self.crewai_model)
        
        # Load tools if specified
        tools = ToolLoader.load_tools(config.get("tools"))
        
        # Load knowledge sources if specified
        knowledge_sources = KnowledgeLoader.load_sources(config.get("knowledge_sources"))
        
        return Agent(
            # Core attributes
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            
            # LLM configuration
            llm=llm,
            function_calling_llm=config.get("function_calling_llm"),
            use_system_prompt=config.get("use_system_prompt", True),
            
            # Tool configurations
            tools=tools,
            
            # Memory and context configuration
            memory=config.get("memory", True),
            respect_context_window=config.get("respect_context_window", True),
            knowledge_sources=knowledge_sources,
            embedder=config.get("embedder"),
            
            # Execution controls
            verbose=config.get("verbose", verbose),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 20),
            max_rpm=config.get("max_rpm"),
            max_execution_time=config.get("max_execution_time"),
            max_retry_limit=config.get("max_retry_limit", 2),
            
            # Code execution configuration
            allow_code_execution=config.get("allow_code_execution", False),
            code_execution_mode=config.get("code_execution_mode", "safe"),
            
            # Template customization
            system_template=config.get("system_template"),
            prompt_template=config.get("prompt_template"),
            response_template=config.get("response_template"),
            
            # Callback configuration
            step_callback=config.get("step_callback"),
            
            # Miscellaneous
            cache=config.get("cache", True)
        ) 