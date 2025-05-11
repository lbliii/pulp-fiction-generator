"""
Event listeners for CrewAI crews.

This module implements various event listeners that can be used to monitor
and respond to events during CrewAI crew execution.
"""

import time
import json
import os
from typing import Dict, Any, Optional, List

from crewai.utilities.events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
    LLMCallStartedEvent,
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
)
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.utilities.events import crewai_event_bus

from ..utils.errors import logger


# Legacy event listener classes (for backward compatibility)
class LoggingEventListener:
    """Event listener that logs events to files."""
    
    def __init__(self, log_dir: str = "logs/events"):
        """
        Initialize the logging event listener.
        
        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.event_count = 0
        
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """
        Handle an event.
        
        Args:
            event_type: Type of the event
            data: Event data
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.event_count += 1
        
        # Log the event
        logger.info(f"[{timestamp}] Event {event_type}: {data.get('message', '')}")
        
        # Save to file
        with open(f"{self.log_dir}/event_{self.event_count:04d}_{event_type}.json", "w") as f:
            json.dump({
                "timestamp": timestamp,
                "type": event_type,
                **data
            }, f, indent=2)


class ProgressEventListener:
    """Event listener that tracks and reports progress."""
    
    def __init__(self, total_tasks: Optional[int] = None, callback=None):
        """
        Initialize the progress event listener.
        
        Args:
            total_tasks: Total number of tasks (if known)
            callback: Optional callback function to report progress
        """
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.callback = callback
        self.start_time = None
        self.end_time = None
        
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """
        Handle an event.
        
        Args:
            event_type: Type of the event
            data: Event data
        """
        if event_type == "crew_started":
            self.start_time = time.time()
            if "total_tasks" in data:
                self.total_tasks = data["total_tasks"]
                
            logger.info(f"Starting execution with {self.total_tasks} tasks")
            
        elif event_type == "task_completed":
            self.completed_tasks += 1
            progress = 100.0 * self.completed_tasks / self.total_tasks if self.total_tasks else None
            
            # Calculate estimated time remaining
            elapsed = time.time() - self.start_time if self.start_time else 0
            remaining = None
            if progress and elapsed > 0:
                remaining = (elapsed / progress) * (100 - progress)
                
            logger.info(f"Task completed: {self.completed_tasks}/{self.total_tasks} ({progress:.1f}%)")
            if remaining:
                logger.info(f"Estimated time remaining: {int(remaining/60)} minutes, {int(remaining%60)} seconds")
                
            # Call the callback if provided
            if self.callback:
                self.callback(self.completed_tasks, self.total_tasks, progress, remaining)
                
        elif event_type == "crew_finished":
            self.end_time = time.time()
            elapsed = self.end_time - self.start_time if self.start_time else 0
            
            logger.info(f"Execution completed in {elapsed:.2f} seconds")
            
            
class ErrorEventListener:
    """Event listener that tracks and responds to errors."""
    
    def __init__(self, error_dir: str = "logs/errors", error_callback=None):
        """
        Initialize the error event listener.
        
        Args:
            error_dir: Directory to store error logs
            error_callback: Optional callback function to handle errors
        """
        self.error_dir = error_dir
        os.makedirs(error_dir, exist_ok=True)
        self.error_count = 0
        self.error_callback = error_callback
        
    def on_event(self, event_type: str, data: Dict[str, Any]):
        """
        Handle an event.
        
        Args:
            event_type: Type of the event
            data: Event data
        """
        if event_type in ["task_error", "crew_error", "agent_error"]:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.error_count += 1
            
            # Log the error
            logger.error(f"[{timestamp}] Error in {event_type}: {data.get('message', '')}")
            
            # Save to file
            with open(f"{self.error_dir}/error_{self.error_count:04d}_{event_type}.json", "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "type": event_type,
                    **data
                }, f, indent=2)
                
            # Call the error callback if provided
            if self.error_callback:
                self.error_callback(event_type, data)


def get_default_listeners() -> List:
    """
    Get a list of default event listeners.
    
    Returns:
        List of default event listeners
    """
    return [
        LoggingEventListener(),
        ProgressEventListener(),
        ErrorEventListener()
    ]


# New CrewAI Event Listeners

class CrewAILoggingListener(BaseEventListener):
    """
    Event listener that logs CrewAI events to files using the official CrewAI event system.
    """
    
    def __init__(self, log_dir: str = "logs/crewai_events"):
        """
        Initialize the CrewAI logging event listener.
        
        Args:
            log_dir: Directory to store log files
        """
        super().__init__()
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.event_count = 0
    
    def setup_listeners(self, crewai_event_bus):
        """
        Set up event listeners for various CrewAI events.
        
        Args:
            crewai_event_bus: The CrewAI event bus
        """
        # Crew Events
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            self._log_event("crew_kickoff_started", {
                "crew_name": event.crew_name,
                "timestamp": event.timestamp
            })
            logger.info(f"Crew '{event.crew_name}' started execution")
        
        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            self._log_event("crew_kickoff_completed", {
                "crew_name": event.crew_name,
                "output": event.output,
                "timestamp": event.timestamp
            })
            logger.info(f"Crew '{event.crew_name}' completed execution")
        
        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event):
            self._log_event("crew_kickoff_failed", {
                "crew_name": event.crew_name,
                "error": str(event.error),
                "timestamp": event.timestamp
            })
            logger.error(f"Crew '{event.crew_name}' failed: {event.error}")
        
        # Agent Events
        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_execution_started(source, event):
            self._log_event("agent_execution_started", {
                "agent_name": event.agent.role,
                "agent_id": str(event.agent.id),
                "task": event.task.description if event.task else "No task",
                "timestamp": event.timestamp
            })
            logger.info(f"Agent '{event.agent.role}' started execution")
        
        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_execution_completed(source, event):
            self._log_event("agent_execution_completed", {
                "agent_name": event.agent.role,
                "agent_id": str(event.agent.id),
                "output": event.output,
                "timestamp": event.timestamp
            })
            logger.info(f"Agent '{event.agent.role}' completed execution")
        
        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_execution_error(source, event):
            self._log_event("agent_execution_error", {
                "agent_name": event.agent.role,
                "agent_id": str(event.agent.id),
                "error": str(event.error),
                "timestamp": event.timestamp
            })
            logger.error(f"Agent '{event.agent.role}' error: {event.error}")
        
        # Task Events
        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event):
            self._log_event("task_started", {
                "task_description": event.task.description,
                "task_id": str(event.task.id),
                "agent": event.task.agent.role if event.task.agent else "No agent",
                "timestamp": event.timestamp
            })
            logger.info(f"Task '{event.task.description[:50]}...' started")
        
        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            self._log_event("task_completed", {
                "task_description": event.task.description,
                "task_id": str(event.task.id),
                "output": event.output,
                "timestamp": event.timestamp
            })
            logger.info(f"Task '{event.task.description[:50]}...' completed")
        
        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event):
            self._log_event("task_failed", {
                "task_description": event.task.description,
                "task_id": str(event.task.id),
                "error": str(event.error),
                "timestamp": event.timestamp
            })
            logger.error(f"Task '{event.task.description[:50]}...' failed: {event.error}")
        
        # Tool Usage Events
        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_usage_started(source, event):
            self._log_event("tool_usage_started", {
                "tool_name": event.tool_name,
                "inputs": str(event.inputs),
                "timestamp": event.timestamp
            })
            logger.info(f"Tool '{event.tool_name}' usage started")
        
        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_usage_finished(source, event):
            self._log_event("tool_usage_finished", {
                "tool_name": event.tool_name,
                "output": str(event.output),
                "timestamp": event.timestamp
            })
            logger.info(f"Tool '{event.tool_name}' usage finished")
        
        # LLM Events
        @crewai_event_bus.on(LLMCallStartedEvent)
        def on_llm_call_started(source, event):
            self._log_event("llm_call_started", {
                "provider": event.provider,
                "model": event.model,
                "timestamp": event.timestamp
            })
            logger.debug(f"LLM call started: {event.provider}/{event.model}")
        
        @crewai_event_bus.on(LLMCallCompletedEvent)
        def on_llm_call_completed(source, event):
            self._log_event("llm_call_completed", {
                "provider": event.provider,
                "model": event.model,
                "tokens_used": event.tokens_used,
                "timestamp": event.timestamp
            })
            logger.debug(f"LLM call completed: {event.provider}/{event.model} (tokens: {event.tokens_used})")
        
        @crewai_event_bus.on(LLMCallFailedEvent)
        def on_llm_call_failed(source, event):
            self._log_event("llm_call_failed", {
                "provider": event.provider,
                "model": event.model,
                "error": str(event.error),
                "timestamp": event.timestamp
            })
            logger.error(f"LLM call failed: {event.provider}/{event.model} - {event.error}")
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event to a file.
        
        Args:
            event_type: Type of the event
            data: Event data
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.event_count += 1
        
        # Save to file
        with open(f"{self.log_dir}/{self.event_count:04d}_{event_type}.json", "w") as f:
            json.dump({
                "timestamp": timestamp,
                "type": event_type,
                **data
            }, f, indent=2)


class ProgressTrackingListener(BaseEventListener):
    """
    Event listener that tracks progress of CrewAI execution using the official event system.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the progress tracking listener.
        
        Args:
            callback: Optional callback function to report progress
        """
        super().__init__()
        self.total_tasks = 0
        self.completed_tasks = 0
        self.callback = callback
        self.start_time = None
        self.end_time = None
    
    def setup_listeners(self, crewai_event_bus):
        """
        Set up event listeners for tracking progress.
        
        Args:
            crewai_event_bus: The CrewAI event bus
        """
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            self.start_time = time.time()
            # Try to count tasks in the crew
            if hasattr(source, 'tasks'):
                self.total_tasks = len(source.tasks)
            
            logger.info(f"Starting execution with approximately {self.total_tasks} tasks")
        
        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            self.completed_tasks += 1
            progress = 100.0 * self.completed_tasks / self.total_tasks if self.total_tasks else None
            
            # Calculate estimated time remaining
            elapsed = time.time() - self.start_time if self.start_time else 0
            remaining = None
            if progress and elapsed > 0 and progress < 100:
                remaining = (elapsed / progress) * (100 - progress)
                
            logger.info(f"Task completed: {self.completed_tasks}/{self.total_tasks} ({progress:.1f}% if known)")
            if remaining:
                logger.info(f"Estimated time remaining: {int(remaining/60)} minutes, {int(remaining%60)} seconds")
                
            # Call the callback if provided
            if self.callback:
                self.callback(self.completed_tasks, self.total_tasks, progress, remaining)
        
        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            self.end_time = time.time()
            elapsed = self.end_time - self.start_time if self.start_time else 0
            
            logger.info(f"Execution completed in {elapsed:.2f} seconds")


# Function to get CrewAI event listeners
def get_crewai_listeners() -> List[BaseEventListener]:
    """
    Get a list of CrewAI event listeners.
    
    Returns:
        List of CrewAI event listeners
    """
    return [
        CrewAILoggingListener(),
        ProgressTrackingListener()
    ]


# Initialize CrewAI event listeners
for listener in get_crewai_listeners():
    listener.setup_listeners(crewai_event_bus) 