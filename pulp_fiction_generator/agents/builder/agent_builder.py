"""
Builder for creating Agent instances.
"""

from typing import Any, Dict, Optional
from crewai import Agent
from crewai.security import Fingerprint

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
    
    def build_agent(self, config: Dict[str, Any], verbose: bool = False, deterministic_id: Optional[str] = None) -> Agent:
        """
        Build an agent from a configuration.
        
        Args:
            config: Agent configuration
            verbose: Whether to enable verbose output
            deterministic_id: Optional ID string for creating deterministic fingerprints
            
        Returns:
            Configured Agent instance
        """
        # Use provided LLM config or default to the model service
        llm = config.get("llm", self.crewai_model)
        
        # Check if we should use a specialized LLM based on agent role
        agent_role = config.get("role", "")
        agent_goal = config.get("goal", "")
        genre = config.get("genre")
        
        # Try to get a specialized LLM based on the role and genre if not explicitly set
        if "llm" not in config:
            specialized_llm = self._get_specialized_llm(agent_role, agent_goal, genre)
            if specialized_llm:
                llm = specialized_llm
        
        # Load tools if specified
        tools = ToolLoader.load_tools(config.get("tools"))
        
        # Load knowledge sources if specified
        knowledge_sources = KnowledgeLoader.load_sources(config.get("knowledge_sources"))
        
        # Create the agent
        agent = Agent(
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
        
        # Enhance fingerprint with metadata if we're using deterministic IDs
        if deterministic_id:
            # Create a deterministic fingerprint for the agent
            # This would replace the auto-generated one, but not possible directly
            # So we'll add it to the metadata instead
            deterministic_fingerprint = Fingerprint.generate(seed=deterministic_id)
            self._enhance_fingerprint_metadata(agent, {
                "deterministic_id": deterministic_id,
                "deterministic_uuid": deterministic_fingerprint.uuid_str
            })
        
        # Add metadata to the fingerprint
        self._enhance_fingerprint_metadata(agent, {
            "role": agent_role,
            "goal": agent_goal,
            "genre": genre if genre else "unknown",
            "agent_type": self._infer_agent_type(agent_role),
        })
        
        return agent
    
    def _enhance_fingerprint_metadata(self, agent: Agent, metadata: Dict[str, Any]) -> None:
        """
        Enhance an agent's fingerprint with additional metadata.
        
        Args:
            agent: Agent instance
            metadata: Metadata to add to the fingerprint
        """
        # Access the fingerprint
        fingerprint = agent.security_config.fingerprint
        
        # Get existing metadata or initialize empty dict
        existing_metadata = fingerprint.metadata or {}
        
        # Update with new metadata
        existing_metadata.update(metadata)
        
        # Set the updated metadata
        fingerprint.metadata = existing_metadata
    
    def _infer_agent_type(self, role: str) -> str:
        """
        Infer the agent type from its role.
        
        Args:
            role: The agent's role
            
        Returns:
            Inferred agent type
        """
        role_lower = role.lower()
        
        if any(term in role_lower for term in ["world", "setting", "environment"]):
            return "worldbuilding"
        elif any(term in role_lower for term in ["research", "investigate", "analyze"]):
            return "research"
        elif any(term in role_lower for term in ["character", "protagonist", "antagonist"]):
            return "character"
        elif any(term in role_lower for term in ["plot", "outline", "structure"]):
            return "plotting"
        elif any(term in role_lower for term in ["write", "author", "storytell"]):
            return "writing"
        elif any(term in role_lower for term in ["edit", "review", "feedback"]):
            return "editing"
        elif any(term in role_lower for term in ["manage", "coordinate", "plan"]):
            return "management"
        else:
            return "general"
    
    def _get_specialized_llm(self, role: str, goal: str, genre: str = None) -> Any:
        """
        Get a specialized LLM for the agent based on role and genre.
        
        Args:
            role: The agent's role
            goal: The agent's goal
            genre: Optional genre context
            
        Returns:
            A specialized LLM if available, otherwise None
        """
        # Return None if model_service doesn't have the specialized methods
        if not hasattr(self.model_service, "get_planning_llm"):
            return None
            
        # Check for role-based specialization
        
        # For worldbuilding-related roles
        if any(term in role.lower() for term in ["world", "setting", "environment"]):
            try:
                return CrewAIModelAdapter(
                    ollama_adapter=self.model_service,
                    response_format=None,  # We'll handle structured output separately
                    stream=False
                )
            except Exception:
                pass
                
        # For research-related roles
        if any(term in role.lower() for term in ["research", "investigate", "analyze"]):
            if genre and genre.lower() in ["western", "noir", "historical"]:
                try:
                    return self.model_service.get_historical_analysis_llm()
                except Exception:
                    pass
            else:
                # Use low temperature for factual research
                try:
                    return CrewAIModelAdapter(
                        ollama_adapter=self.model_service,
                        response_format=None,
                        stream=False
                    )
                except Exception:
                    pass
                    
        # For character-related roles
        if any(term in role.lower() for term in ["character", "protagonist", "antagonist"]):
            try:
                from ...models.schema import Character
                return CrewAIModelAdapter(
                    ollama_adapter=self.model_service,
                    response_format=Character,
                    stream=False
                )
            except Exception:
                pass
                
        # For outline or plotting roles
        if any(term in role.lower() for term in ["plot", "outline", "structure"]):
            try:
                return self.model_service.get_story_outline_llm()
            except Exception:
                pass
                
        # For creative writing roles
        if any(term in role.lower() for term in ["write", "author", "storytell"]):
            try:
                # Use streaming for writers to handle longer outputs
                return self.model_service.get_streaming_llm()
            except Exception:
                pass
                
        # For editing and feedback roles
        if any(term in role.lower() for term in ["edit", "review", "feedback"]):
            try:
                return self.model_service.get_feedback_llm()
            except Exception:
                pass
                
        # For planning and coordination roles
        if any(term in role.lower() for term in ["manage", "coordinate", "plan"]):
            try:
                return self.model_service.get_planning_llm()
            except Exception:
                pass
                
        # Default case - no specialized LLM found
        return None 