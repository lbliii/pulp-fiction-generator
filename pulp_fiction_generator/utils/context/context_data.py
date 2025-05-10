"""
Data models for storing context information.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ContextData:
    """
    Data model for storing context information.
    
    This class encapsulates the data structure for storing and
    accessing context history and agent interactions.
    """
    
    def __init__(self):
        """Initialize the context data."""
        self.context_history = []
        self.agent_interactions = []
    
    def add_context_snapshot(self, context: Dict[str, Any], stage: str):
        """
        Add a context snapshot to the history.
        
        Args:
            context: The current context object
            stage: Name of the current processing stage
        """
        timestamp = datetime.now().isoformat()
        snapshot = {
            "stage": stage,
            "timestamp": timestamp,
            "context": context.copy() if isinstance(context, dict) else context
        }
        self.context_history.append(snapshot)
        return snapshot
    
    def add_agent_interaction(
        self,
        agent_name: str,
        input_context: Dict[str, Any],
        output_context: Dict[str, Any],
        prompt: Optional[str] = None,
        response: Optional[str] = None
    ):
        """
        Add an agent interaction to the history.
        
        Args:
            agent_name: Name of the agent
            input_context: Context before agent processing
            output_context: Context after agent processing
            prompt: The prompt sent to the agent (optional)
            response: The response from the agent (optional)
        """
        timestamp = datetime.now().isoformat()
        interaction = {
            "agent": agent_name,
            "timestamp": timestamp,
            "input_context": input_context.copy() if isinstance(input_context, dict) else input_context,
            "output_context": output_context.copy() if isinstance(output_context, dict) else output_context,
            "prompt": prompt,
            "response": response
        }
        self.agent_interactions.append(interaction)
        return interaction
    
    def get_context_history(self):
        """Get the context history."""
        return self.context_history
    
    def get_agent_interactions(self):
        """Get the agent interactions."""
        return self.agent_interactions 