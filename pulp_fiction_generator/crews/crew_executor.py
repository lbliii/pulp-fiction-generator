"""
CrewExecutor handles the execution of agent crews and debugging visualization.
"""

from typing import Any, Dict, Optional, List
import time

from crewai import Crew, Task
from crewai.utilities.events import crewai_event_bus
from crewai.utilities.events.base_event_listener import BaseEventListener

from ..utils.context_visualizer import ContextVisualizer
from ..utils.errors import logger
from .event_listeners import get_crewai_listeners, CrewAILoggingListener, ProgressTrackingListener


class CrewExecutor:
    """
    Responsible for executing crews and handling debugging visualization.
    
    This class encapsulates the logic for running crews, monitoring their execution,
    and collecting diagnostic information during execution.
    """
    
    def __init__(
        self,
        visualizer: Optional[ContextVisualizer] = None,
        debug_mode: bool = False,
        event_listeners: Optional[List[BaseEventListener]] = None
    ):
        """
        Initialize the crew executor.
        
        Args:
            visualizer: Optional context visualizer for debugging
            debug_mode: Whether debugging is enabled
            event_listeners: Optional list of event listeners to use
        """
        self.visualizer = visualizer
        self.debug_mode = debug_mode
        
        # Initialize event listeners if provided, otherwise use defaults
        self.event_listeners = event_listeners
        
        # If listeners weren't explicitly provided, use the ones initialized in event_listeners.py
        # They're already registered when the module is imported
    
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
                agent_name = task_self.agent.role if hasattr(task_self.agent, 'role') else "Unknown Agent"
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
            # Run the crew with temporary scoped handlers if needed for specific functionality
            with crewai_event_bus.scoped_handlers() as scope:
                # Optionally add additional temporary event handlers specific to this execution
                if self.debug_mode:
                    # Example: Add a temporary token counter for this execution
                    token_counts = {"total": 0}
                    
                    @crewai_event_bus.on("LLMCallCompletedEvent")
                    def count_tokens(source, event):
                        if hasattr(event, 'tokens_used'):
                            token_counts["total"] += event.tokens_used
                            logger.debug(f"Token usage: +{event.tokens_used} = {token_counts['total']} total")
                
                # Run the crew
                start_time = time.time()
                result = crew.kickoff(inputs=inputs)
                execution_time = time.time() - start_time
                
                # Log execution metrics
                if self.debug_mode:
                    logger.info(f"Crew execution completed in {execution_time:.2f} seconds")
                    if "total" in token_counts:
                        logger.info(f"Total tokens used: {token_counts['total']}")
            
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
    
    def create_custom_event_listener(self, callback) -> BaseEventListener:
        """
        Create a custom event listener with a callback.
        
        Args:
            callback: Function to call on events
            
        Returns:
            A configured event listener
        """
        progress_listener = ProgressTrackingListener(callback=callback)
        progress_listener.setup_listeners(crewai_event_bus)
        return progress_listener
    
    def add_token_tracking_listener(self, log_dir: str = "logs/token_usage") -> BaseEventListener:
        """
        Add a listener that tracks token usage.
        
        Args:
            log_dir: Directory to store token usage logs
            
        Returns:
            The configured token tracking listener
        """
        class TokenTrackingListener(BaseEventListener):
            def __init__(self, log_dir):
                super().__init__()
                self.log_dir = log_dir
                import os
                os.makedirs(log_dir, exist_ok=True)
                self.token_counts = {"total": 0, "by_model": {}}
                
            def setup_listeners(self, crewai_event_bus):
                from crewai.utilities.events import LLMCallCompletedEvent
                
                @crewai_event_bus.on(LLMCallCompletedEvent)
                def on_llm_call_completed(source, event):
                    self.token_counts["total"] += event.tokens_used
                    
                    # Track by model
                    model_key = f"{event.provider}/{event.model}"
                    if model_key not in self.token_counts["by_model"]:
                        self.token_counts["by_model"][model_key] = 0
                    self.token_counts["by_model"][model_key] += event.tokens_used
                    
                    # Log
                    logger.debug(f"Token usage: +{event.tokens_used} ({model_key}) = {self.token_counts['total']} total")
                
                from crewai.utilities.events import CrewKickoffCompletedEvent
                
                @crewai_event_bus.on(CrewKickoffCompletedEvent)
                def on_crew_completed(source, event):
                    # Write token usage to file
                    import json
                    from datetime import datetime
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    with open(f"{self.log_dir}/token_usage_{timestamp}.json", "w") as f:
                        json.dump({
                            "timestamp": timestamp,
                            "crew_name": event.crew_name,
                            "token_counts": self.token_counts
                        }, f, indent=2)
                    
                    logger.info(f"Total tokens used: {self.token_counts['total']}")
                    for model, count in self.token_counts["by_model"].items():
                        logger.info(f"  {model}: {count}")
        
        # Create and register the listener
        token_listener = TokenTrackingListener(log_dir)
        token_listener.setup_listeners(crewai_event_bus)
        return token_listener 