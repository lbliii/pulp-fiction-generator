"""
Configuration model for agents.
"""

from typing import Any, List, Optional
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    tools: Optional[List[Any]] = None 