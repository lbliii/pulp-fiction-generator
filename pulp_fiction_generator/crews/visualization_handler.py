"""
Handler for crew visualization and debug output.
"""

from typing import Optional, Dict, Any, List
from crewai import Crew
from crewai.security import Fingerprint

from ..utils.context_visualizer import ContextVisualizer


class VisualizationHandler:
    """
    Handles visualization and debug output for crews.
    
    This class encapsulates visualization logic, separating it from
    coordination concerns to follow the Single Responsibility Principle.
    """
    
    def __init__(self, debug_mode: bool = False, output_dir: Optional[str] = None):
        """
        Initialize the visualization handler.
        
        Args:
            debug_mode: Whether visualization is enabled
            output_dir: Directory for debug output
        """
        self.debug_mode = debug_mode
        self.visualizer = ContextVisualizer(
            output_dir=output_dir,
            enabled=debug_mode
        ) if debug_mode else None
        
        # Store fingerprint mappings
        self.fingerprint_registry = {}
    
    def register_crew(self, crew: Crew) -> None:
        """
        Register a crew for visualization.
        
        Args:
            crew: The crew to register
        """
        if not hasattr(crew, 'fingerprint'):
            return
            
        crew_fingerprint = crew.fingerprint.uuid_str
        crew_metadata = crew.fingerprint.metadata or {}
        
        # Get agent fingerprints from the crew
        agent_fingerprints = {}
        for agent in crew.agents:
            if hasattr(agent, 'fingerprint'):
                agent_fingerprint = agent.fingerprint.uuid_str
                agent_metadata = agent.fingerprint.metadata or {}
                agent_role = agent.role if hasattr(agent, 'role') else str(agent)
                
                # Register agent fingerprint
                self.fingerprint_registry[agent_fingerprint] = {
                    "type": "agent",
                    "role": agent_role,
                    "metadata": agent_metadata,
                    "parent_crew": crew_fingerprint
                }
                
                # Add to agent fingerprints
                agent_fingerprints[agent_role] = agent_fingerprint
        
        # Register crew fingerprint
        self.fingerprint_registry[crew_fingerprint] = {
            "type": "crew",
            "name": crew_metadata.get("crew_id", str(crew)),
            "metadata": crew_metadata,
            "agent_fingerprints": agent_fingerprints
        }
    
    def is_enabled(self) -> bool:
        """
        Check if visualization is enabled.
        
        Returns:
            True if visualization is enabled, False otherwise
        """
        return self.debug_mode and self.visualizer is not None
    
    def visualize_crew_execution(self, crew: Crew, inputs: dict, output: str) -> None:
        """
        Visualize the execution of a crew.
        
        Args:
            crew: The crew that executed
            inputs: Inputs to the crew
            output: Output from the crew
        """
        if not self.is_enabled() or self.visualizer is None:
            return
        
        # Register the crew if not already registered
        if hasattr(crew, 'fingerprint') and crew.fingerprint.uuid_str not in self.fingerprint_registry:
            self.register_crew(crew)
        
        # Get crew fingerprint
        crew_fingerprint = crew.fingerprint.uuid_str if hasattr(crew, 'fingerprint') else None
        
        # Enhanced visualization data with fingerprinting
        visualization_data = {
            "crew_fingerprint": crew_fingerprint,
            "crew_metadata": self.fingerprint_registry.get(crew_fingerprint, {}).get("metadata", {}) if crew_fingerprint else {},
            "inputs": inputs,
            "output": output
        }
            
        self.visualizer.visualize_execution(
            component=f"crew_{str(crew)}",
            inputs=visualization_data,
            output=output,
            fingerprint=crew_fingerprint
        )
    
    def visualize_story_generation(self, genre: str, inputs: dict, output: str, crew: Optional[Crew] = None) -> None:
        """
        Visualize a story generation process.
        
        Args:
            genre: The genre of the story
            inputs: Inputs to the generation process
            output: The generated story
            crew: Optional crew that generated the story
        """
        if not self.is_enabled() or self.visualizer is None:
            return
            
        # Get crew fingerprint if available
        crew_fingerprint = None
        crew_metadata = {}
        if crew and hasattr(crew, 'fingerprint'):
            crew_fingerprint = crew.fingerprint.uuid_str
            crew_metadata = self.fingerprint_registry.get(crew_fingerprint, {}).get("metadata", {})
        
        # Enhanced visualization data with fingerprinting
        visualization_data = {
            "genre": genre,
            "crew_fingerprint": crew_fingerprint,
            "crew_metadata": crew_metadata,
            "inputs": inputs
        }
            
        self.visualizer.visualize_execution(
            component=f"story_generation_{genre}",
            inputs=visualization_data,
            output=output,
            fingerprint=crew_fingerprint
        )
        
    def visualize_agent_execution(self, agent_fingerprint: str, task_description: str, inputs: dict, output: str) -> None:
        """
        Visualize the execution of an agent.
        
        Args:
            agent_fingerprint: Fingerprint of the agent
            task_description: Description of the task
            inputs: Inputs to the agent
            output: Output from the agent
        """
        if not self.is_enabled() or self.visualizer is None:
            return
            
        # Get agent info from registry
        agent_info = self.fingerprint_registry.get(agent_fingerprint, {})
        agent_role = agent_info.get("role", "Unknown Agent")
        agent_metadata = agent_info.get("metadata", {})
        
        # Enhanced visualization data with fingerprinting
        visualization_data = {
            "agent_fingerprint": agent_fingerprint,
            "agent_metadata": agent_metadata,
            "task_description": task_description,
            "inputs": inputs
        }
            
        self.visualizer.visualize_execution(
            component=f"agent_{agent_role}",
            inputs=visualization_data,
            output=output,
            fingerprint=agent_fingerprint
        )
        
    def generate_fingerprint_graph(self, crew: Crew) -> Dict[str, Any]:
        """
        Generate a graph representation of crew and agent fingerprints.
        
        Args:
            crew: The crew to generate a graph for
            
        Returns:
            Dictionary representing the graph structure
        """
        if not hasattr(crew, 'fingerprint'):
            return {}
            
        crew_fingerprint = crew.fingerprint.uuid_str
        
        # Register the crew if not already registered
        if crew_fingerprint not in self.fingerprint_registry:
            self.register_crew(crew)
            
        # Get crew info
        crew_info = self.fingerprint_registry.get(crew_fingerprint, {})
        crew_metadata = crew_info.get("metadata", {})
        agent_fingerprints = crew_info.get("agent_fingerprints", {})
        
        # Build agents nodes
        agent_nodes = []
        for agent_role, agent_fingerprint in agent_fingerprints.items():
            agent_info = self.fingerprint_registry.get(agent_fingerprint, {})
            agent_metadata = agent_info.get("metadata", {})
            
            agent_nodes.append({
                "id": agent_fingerprint,
                "type": "agent",
                "role": agent_role,
                "metadata": agent_metadata
            })
        
        # Build graph
        graph = {
            "id": crew_fingerprint,
            "type": "crew",
            "name": crew_metadata.get("crew_id", str(crew)),
            "metadata": crew_metadata,
            "agents": agent_nodes,
            "created_at": crew_metadata.get("created_at")
        }
        
        return graph 