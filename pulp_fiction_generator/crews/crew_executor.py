"""
CrewExecutor handles the execution of agent crews and debugging visualization.
"""

from typing import Any, Dict, Optional

from crewai import Crew, Task

from ..utils.context_visualizer import ContextVisualizer
from ..utils.errors import logger


class CrewExecutor:
    """
    Responsible for executing crews and handling debugging visualization.
    
    This class encapsulates the logic for running crews, monitoring their execution,
    and collecting diagnostic information during execution.
    """
    
    def __init__(
        self,
        visualizer: Optional[ContextVisualizer] = None,
        debug_mode: bool = False
    ):
        """
        Initialize the crew executor.
        
        Args:
            visualizer: Optional context visualizer for debugging
            debug_mode: Whether debugging is enabled
        """
        self.visualizer = visualizer
        self.debug_mode = debug_mode
    
    def kickoff_crew(self, crew: Crew, inputs: Optional[Dict[str, Any]] = None) -> str:
        """
        Start the execution of a crew.
        
        Args:
            crew: The crew to execute
            inputs: Optional inputs for the crew
            
        Returns:
            The final output from the crew
        """
        # Initialize inputs if needed
        inputs = inputs or {}
        
        # Visualize initial context if debugging is enabled
        if self.debug_mode and self.visualizer:
            self.visualizer.visualize_context(inputs, stage="Initial Inputs")
        
        # Set up task callback if debugging is enabled
        if self.debug_mode and self.visualizer:
            original_execute = Task.execute
            
            def execute_with_debug(task_self, *args, **kwargs):
                # Capture the context before task execution
                agent_name = task_self.agent.name if hasattr(task_self.agent, 'name') else "Unknown Agent"
                context_before = kwargs.get('context', {})
                
                # Show prompt template if available
                if hasattr(task_self.agent, 'llm_config') and 'prompt_template' in task_self.agent.llm_config:
                    self.visualizer.show_prompt_template(
                        agent_name,
                        task_self.agent.llm_config['prompt_template'],
                        {
                            "task": task_self.description,
                            "context": context_before
                        }
                    )
                
                # Execute the original task
                result = original_execute(task_self, *args, **kwargs)
                
                # Capture context after execution (simplified assumption that result is the new context)
                context_after = {"result": result, **context_before}
                
                # Track the agent interaction
                self.visualizer.track_agent_interaction(
                    agent_name=agent_name,
                    input_context=context_before,
                    output_context=context_after,
                    prompt=task_self.description,
                    response=result
                )
                
                # Update visualized context
                self.visualizer.visualize_context(
                    context_after, 
                    stage=f"After {agent_name}"
                )
                
                return result
            
            # Monkey patch Task.execute for this run
            Task.execute = execute_with_debug
        
        try:
            # Run the crew
            result = crew.kickoff(inputs=inputs)
            
            # Final context visualization
            if self.debug_mode and self.visualizer:
                final_context = {"final_result": result, **inputs}
                self.visualizer.visualize_context(final_context, stage="Final Output")
                
                # Export HTML visualization
                self.visualizer.export_visualization_html()
            
            return result
        finally:
            # Restore original execute method if it was patched
            if self.debug_mode and self.visualizer:
                Task.execute = original_execute 