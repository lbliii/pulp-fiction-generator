"""
Context visualization orchestrator for debugging agent interactions.

This module provides the main orchestrator that delegates to specialized 
components for visualizing context flow between agents.
"""

import os
from typing import Any, Dict, List, Optional

from .context.context_data import ContextData
from .context.diff_calculator import ContextDiffCalculator 
from .visualization.console_visualizer import ConsoleVisualizer
from .visualization.file_storage import FileStorage


class ContextVisualizer:
    """
    Orchestrates visualization of agent context and interactions for debugging.
    
    This class delegates to specialized components to handle different aspects
    of context visualization.
    """
    
    def __init__(self, output_dir: Optional[str] = None, enabled: bool = True):
        """
        Initialize the context visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            enabled: Whether visualization is enabled
        """
        self.enabled = enabled
        
        # Set up output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(os.getcwd(), "debug_output")
        
        # Initialize components
        self.data = ContextData()
        self.diff_calculator = ContextDiffCalculator()
        self.console_visualizer = ConsoleVisualizer()
        self.file_storage = FileStorage(self.output_dir) if enabled else None
    
    def visualize_context(self, context: Dict[str, Any], stage: str = "unnamed"):
        """
        Visualize the current context state.
        
        Args:
            context: The current context object
            stage: Name of the current processing stage
        """
        if not self.enabled:
            return
        
        # Save context to history
        snapshot = self.data.add_context_snapshot(context, stage)
        
        # Create visualization in console
        self.console_visualizer.visualize_context(context, stage)
        
        # Save JSON snapshot
        if self.file_storage:
            self.file_storage.save_context_snapshot(
                context,
                stage,
                snapshot["timestamp"]
            )
    
    def track_agent_interaction(
        self,
        agent_name: str,
        input_context: Dict[str, Any],
        output_context: Dict[str, Any],
        prompt: Optional[str] = None,
        response: Optional[str] = None
    ):
        """
        Track and visualize an agent interaction.
        
        Args:
            agent_name: Name of the agent
            input_context: Context before agent processing
            output_context: Context after agent processing
            prompt: The prompt sent to the agent (optional)
            response: The response from the agent (optional)
        """
        if not self.enabled:
            return
        
        # Save interaction
        interaction = self.data.add_agent_interaction(
            agent_name,
            input_context,
            output_context,
            prompt,
            response
        )
        
        # Calculate differences in context
        context_diff = self.diff_calculator.calculate_diff(input_context, output_context)
        
        # Visualize in console
        self.console_visualizer.visualize_agent_interaction(
            agent_name,
            input_context,
            output_context,
            context_diff
        )
        
        # Save detailed interaction log
        if self.file_storage:
            self.file_storage.save_interaction_log(
                interaction,
                agent_name,
                interaction["timestamp"]
            )
    
    def show_prompt_template(self, agent_name: str, template: str, variables: Dict[str, Any]):
        """
        Visualize a prompt template with its variables.
        
        Args:
            agent_name: Name of the agent using the prompt
            template: The prompt template
            variables: Variables used in the template
        """
        if not self.enabled:
            return
        
        self.console_visualizer.visualize_prompt_template(agent_name, template, variables)
    
    def export_visualization_html(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Export the visualization history as an HTML file.
        
        Args:
            output_path: Path to save the HTML file, or None to use default location
            
        Returns:
            The path to the exported file, or None if export failed
        """
        if not self.enabled or not self.data.get_context_history() or not self.file_storage:
            return None
        
        # Export to the appropriate path
        result_path = self.file_storage.export_html(
            self.data.get_context_history(),
            self.data.get_agent_interactions()
        )
        
        self.console_visualizer.show_export_confirmation(result_path)
        return result_path 