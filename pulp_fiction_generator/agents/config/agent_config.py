"""
Configuration model for agents.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for an agent based on CrewAI's agent attributes"""
    # Required parameters
    role: str
    goal: str
    backstory: str
    
    # LLM configuration
    llm: Optional[Union[str, Any]] = None
    function_calling_llm: Optional[Any] = None
    use_system_prompt: bool = True
    
    # Tool configurations
    tools: Optional[List[Any]] = None
    
    # Memory and context configuration
    memory: bool = True
    respect_context_window: bool = True
    knowledge_sources: Optional[List[Any]] = None
    embedder: Optional[Dict[str, Any]] = None
    
    # Execution controls
    verbose: bool = False
    allow_delegation: bool = False
    max_iter: int = 20
    max_rpm: Optional[int] = None
    max_execution_time: Optional[int] = None
    max_retry_limit: int = 2
    
    # Code execution configuration
    allow_code_execution: bool = False
    code_execution_mode: Literal["safe", "unsafe"] = "safe"
    
    # Template customization
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None
    
    # Callback configuration
    step_callback: Optional[Any] = None
    
    # Miscellaneous
    cache: bool = True 