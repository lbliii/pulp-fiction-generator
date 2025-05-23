"""
Collaborative memory system for agent collaboration.

This module extends the base memory system to support collaboration between agents,
providing shared context, delegation tracking, and collaborative knowledge building.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from crewai import Crew, Agent, Task

from .memory_utils import get_memory_path

logger = logging.getLogger(__name__)

class CollaborativeMemory:
    """
    Enhanced memory system that enables collaboration between agents.
    
    This system builds on the existing memory infrastructure to provide:
    1. Shared context between agents
    2. Delegation tracking for task handoffs
    3. Knowledge sharing mechanisms
    4. Collaborative insights tracking
    """
    
    def __init__(
        self,
        storage_dir: str = "./.memory",
        genre: Optional[str] = None,
        crew: Optional[Crew] = None
    ):
        """
        Initialize the collaborative memory system.
        
        Args:
            storage_dir: Base storage directory for memory
            genre: Optional genre context
            crew: Optional crew object to attach to
        """
        self.storage_dir = storage_dir
        self.genre = genre
        self.crew = crew
        
        # Create base memory path
        self.base_path = get_memory_path(genre, storage_dir)
        os.makedirs(self.base_path, exist_ok=True)
        
        # Create collaboration-specific directories
        self.shared_context_path = os.path.join(self.base_path, "shared_context")
        self.delegation_path = os.path.join(self.base_path, "delegations")
        self.insights_path = os.path.join(self.base_path, "insights")
        
        os.makedirs(self.shared_context_path, exist_ok=True)
        os.makedirs(self.delegation_path, exist_ok=True)
        os.makedirs(self.insights_path, exist_ok=True)
        
        # Initialize shared context
        self._init_shared_context()
    
    def _init_shared_context(self):
        """Initialize the shared context if it doesn't exist."""
        context_file = os.path.join(self.shared_context_path, "shared_context.json")
        if not os.path.exists(context_file):
            initial_context = {
                "created_at": time.time(),
                "last_updated": time.time(),
                "context_version": 1,
                "shared_knowledge": {},
                "agent_contributions": {},
                "collaborative_insights": []
            }
            
            with open(context_file, "w") as f:
                json.dump(initial_context, f, indent=2)
    
    def get_shared_context(self) -> Dict[str, Any]:
        """
        Get the current shared context.
        
        Returns:
            Dictionary containing the shared context
        """
        context_file = os.path.join(self.shared_context_path, "shared_context.json")
        try:
            with open(context_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Reinitialize if file is missing or corrupted
            self._init_shared_context()
            with open(context_file, "r") as f:
                return json.load(f)
    
    def update_shared_context(self, key: str, value: Any, agent_name: str) -> bool:
        """
        Update a specific element in the shared context.
        
        Args:
            key: The context key to update
            value: The value to set
            agent_name: Name of the agent making the update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            context = self.get_shared_context()
            
            # Update the shared knowledge
            context["shared_knowledge"][key] = value
            context["last_updated"] = time.time()
            
            # Track agent contribution
            if agent_name not in context["agent_contributions"]:
                context["agent_contributions"][agent_name] = []
                
            context["agent_contributions"][agent_name].append({
                "key": key,
                "timestamp": time.time()
            })
            
            # Save updated context
            context_file = os.path.join(self.shared_context_path, "shared_context.json")
            with open(context_file, "w") as f:
                json.dump(context, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error updating shared context: {e}")
            return False
    
    def add_collaborative_insight(self, insight: str, agents_involved: List[str]) -> bool:
        """
        Add a collaborative insight generated by multiple agents.
        
        Args:
            insight: The insight text
            agents_involved: List of agent names involved in generating the insight
            
        Returns:
            True if successful, False otherwise
        """
        try:
            context = self.get_shared_context()
            
            # Add the insight
            insight_entry = {
                "insight": insight,
                "agents_involved": agents_involved,
                "timestamp": time.time()
            }
            
            context["collaborative_insights"].append(insight_entry)
            context["last_updated"] = time.time()
            
            # Save updated context
            context_file = os.path.join(self.shared_context_path, "shared_context.json")
            with open(context_file, "w") as f:
                json.dump(context, f, indent=2)
            
            # Also save to insights directory for easier retrieval
            insight_file = os.path.join(
                self.insights_path, 
                f"insight_{int(time.time())}.json"
            )
            with open(insight_file, "w") as f:
                json.dump(insight_entry, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error adding collaborative insight: {e}")
            return False
    
    def record_delegation(
        self, 
        delegator: str, 
        delegatee: str, 
        task_description: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a task delegation between agents.
        
        Args:
            delegator: Name of the agent delegating the task
            delegatee: Name of the agent receiving the task
            task_description: Description of the delegated task
            context: Optional context information for the delegation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delegation_record = {
                "delegator": delegator,
                "delegatee": delegatee,
                "task_description": task_description,
                "context": context or {},
                "timestamp": time.time(),
                "status": "delegated",
                "completion_time": None,
                "result": None
            }
            
            # Generate a unique ID for this delegation
            delegation_id = f"{int(time.time())}_{delegator}_to_{delegatee}"
            
            # Save the delegation record
            delegation_file = os.path.join(self.delegation_path, f"{delegation_id}.json")
            with open(delegation_file, "w") as f:
                json.dump(delegation_record, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error recording delegation: {e}")
            return False
    
    def complete_delegation(
        self, 
        delegation_id: str, 
        result: str,
        success: bool = True
    ) -> bool:
        """
        Mark a delegation as complete with results.
        
        Args:
            delegation_id: ID of the delegation to complete
            result: Result of the delegated task
            success: Whether the delegation was successful
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delegation_file = os.path.join(self.delegation_path, f"{delegation_id}.json")
            
            # Check if delegation exists
            if not os.path.exists(delegation_file):
                logger.warning(f"Delegation {delegation_id} not found")
                return False
                
            # Load delegation record
            with open(delegation_file, "r") as f:
                delegation_record = json.load(f)
                
            # Update record
            delegation_record["status"] = "completed" if success else "failed"
            delegation_record["completion_time"] = time.time()
            delegation_record["result"] = result
            
            # Save updated record
            with open(delegation_file, "w") as f:
                json.dump(delegation_record, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error completing delegation: {e}")
            return False
    
    def get_agent_specific_context(self, agent_name: str) -> Dict[str, Any]:
        """
        Get context tailored for a specific agent.
        
        Args:
            agent_name: Name of the agent to get context for
            
        Returns:
            Dictionary with agent-specific context
        """
        # Get shared context
        shared_context = self.get_shared_context()
        
        # Create agent-specific view
        agent_context = {
            "shared_knowledge": shared_context["shared_knowledge"],
            "your_contributions": shared_context["agent_contributions"].get(agent_name, []),
            "collaborative_insights": shared_context["collaborative_insights"],
            "delegations": {
                "delegated_to_you": self._get_delegations_for_agent(agent_name, as_delegatee=True),
                "delegated_by_you": self._get_delegations_for_agent(agent_name, as_delegatee=False)
            }
        }
        
        return agent_context
    
    def _get_delegations_for_agent(self, agent_name: str, as_delegatee: bool = True) -> List[Dict[str, Any]]:
        """
        Get delegations for a specific agent.
        
        Args:
            agent_name: Name of the agent
            as_delegatee: If True, get delegations where agent is delegatee, otherwise delegator
            
        Returns:
            List of delegation records
        """
        delegations = []
        
        try:
            for filename in os.listdir(self.delegation_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.delegation_path, filename)
                    with open(file_path, "r") as f:
                        delegation = json.load(f)
                        
                    # Check if agent is involved in the right role
                    if as_delegatee and delegation["delegatee"] == agent_name:
                        delegations.append(delegation)
                    elif not as_delegatee and delegation["delegator"] == agent_name:
                        delegations.append(delegation)
        except Exception as e:
            logger.error(f"Error getting delegations: {e}")
            
        return delegations
    
    def reset(self, reset_type: str = "all") -> bool:
        """
        Reset collaborative memory.
        
        Args:
            reset_type: Type of reset to perform (all, shared_context, delegations, insights)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if reset_type == "all":
                # Reset everything
                if os.path.exists(self.shared_context_path):
                    for file in os.listdir(self.shared_context_path):
                        os.remove(os.path.join(self.shared_context_path, file))
                if os.path.exists(self.delegation_path):
                    for file in os.listdir(self.delegation_path):
                        os.remove(os.path.join(self.delegation_path, file))
                if os.path.exists(self.insights_path):
                    for file in os.listdir(self.insights_path):
                        os.remove(os.path.join(self.insights_path, file))
                
                # Reinitialize
                self._init_shared_context()
            elif reset_type == "shared_context":
                # Reset just shared context
                if os.path.exists(self.shared_context_path):
                    for file in os.listdir(self.shared_context_path):
                        os.remove(os.path.join(self.shared_context_path, file))
                self._init_shared_context()
            elif reset_type == "delegations":
                # Reset delegations
                if os.path.exists(self.delegation_path):
                    for file in os.listdir(self.delegation_path):
                        os.remove(os.path.join(self.delegation_path, file))
            elif reset_type == "insights":
                # Reset insights
                if os.path.exists(self.insights_path):
                    for file in os.listdir(self.insights_path):
                        os.remove(os.path.join(self.insights_path, file))
            else:
                logger.warning(f"Unknown reset type: {reset_type}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error resetting collaborative memory: {e}")
            return False 