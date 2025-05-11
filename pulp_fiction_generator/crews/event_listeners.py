"""
Event listeners for CrewAI crews.

This module implements various event listeners that can be used to monitor
and respond to events during CrewAI crew execution.
"""

import time
import json
import os
from typing import Dict, Any, Optional, List

# Updated imports to match available CrewAI events
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
    LLMCallFailedEvent
)
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.utilities.events import crewai_event_bus
from crewai.security import Fingerprint

from ..utils.errors import logger

# Add import for delegation events if available
# Note: If these aren't available, we'll create placeholders
try:
    from crewai.utilities.events import (
        AgentDelegationStartedEvent,
        AgentDelegationCompletedEvent
    )
    DELEGATION_EVENTS_AVAILABLE = True
except ImportError:
    # Create placeholder event classes for backwards compatibility
    class AgentDelegationStartedEvent:
        """Placeholder for delegation started event when not available."""
        pass
    
    class AgentDelegationCompletedEvent:
        """Placeholder for delegation completed event when not available."""
        pass
    
    DELEGATION_EVENTS_AVAILABLE = False
    logger.warning("Delegation events not available in this CrewAI version.")

from ..utils.collaborative_memory import CollaborativeMemory


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
        
        # Track fingerprints for better correlation
        self.fingerprint_registry = {}
        
    def setup_listeners(self, crewai_event_bus):
        """
        Set up event listeners for various CrewAI events.
        
        Args:
            crewai_event_bus: The CrewAI event bus
        """
        # Crew Events
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            # Extract and store crew fingerprint for future reference
            crew = event.crew
            crew_fingerprint = crew.fingerprint.uuid_str if hasattr(crew, 'fingerprint') else None
            
            # Register the crew fingerprint
            if crew_fingerprint:
                crew_metadata = crew.fingerprint.metadata or {}
                crew_name = str(crew)
                self.fingerprint_registry[crew_fingerprint] = {
                    "type": "crew",
                    "name": crew_name,
                    "metadata": crew_metadata,
                    "timestamp": time.time()
                }
            
            self._log_event("crew_started", {
                "message": f"Crew execution started",
                "crew_id": str(crew),
                "crew_fingerprint": crew_fingerprint,
                "num_agents": len(crew.agents) if hasattr(crew, 'agents') else 0,
                "num_tasks": len(crew.tasks) if hasattr(crew, 'tasks') else 0,
                "crew_metadata": crew_metadata if crew_fingerprint else {}
            })
            
        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            crew = event.crew
            crew_fingerprint = crew.fingerprint.uuid_str if hasattr(crew, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if crew_fingerprint and crew_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[crew_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("crew_completed", {
                "message": f"Crew execution completed successfully",
                "crew_id": str(crew),
                "crew_fingerprint": crew_fingerprint,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "result": str(event.output)[:100] + "..." if len(str(event.output)) > 100 else str(event.output)
            })
            
        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event):
            crew = event.crew
            crew_fingerprint = crew.fingerprint.uuid_str if hasattr(crew, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if crew_fingerprint and crew_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[crew_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("crew_failed", {
                "message": f"Crew execution failed",
                "crew_id": str(crew),
                "crew_fingerprint": crew_fingerprint,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "error": str(event.error)
            })
        
        # Agent Events
        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_execution_started(source, event):
            agent = event.agent
            agent_fingerprint = agent.fingerprint.uuid_str if hasattr(agent, 'fingerprint') else None
            
            # Register the agent fingerprint
            if agent_fingerprint:
                agent_metadata = agent.fingerprint.metadata or {}
                agent_role = agent.role if hasattr(agent, 'role') else str(agent)
                self.fingerprint_registry[agent_fingerprint] = {
                    "type": "agent",
                    "role": agent_role,
                    "metadata": agent_metadata,
                    "timestamp": time.time()
                }
            
            self._log_event("agent_execution_started", {
                "message": f"Agent execution started",
                "agent_role": agent.role if hasattr(agent, 'role') else str(agent),
                "agent_fingerprint": agent_fingerprint,
                "agent_metadata": agent_metadata if agent_fingerprint else {}
            })
        
        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_execution_completed(source, event):
            agent = event.agent
            agent_fingerprint = agent.fingerprint.uuid_str if hasattr(agent, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if agent_fingerprint and agent_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[agent_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("agent_execution_completed", {
                "message": f"Agent execution completed",
                "agent_role": agent.role if hasattr(agent, 'role') else str(agent),
                "agent_fingerprint": agent_fingerprint,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "result": str(event.output)[:100] + "..." if len(str(event.output)) > 100 else str(event.output)
            })
        
        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_execution_error(source, event):
            agent = event.agent
            agent_fingerprint = agent.fingerprint.uuid_str if hasattr(agent, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if agent_fingerprint and agent_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[agent_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("agent_execution_error", {
                "message": f"Agent execution error",
                "agent_role": agent.role if hasattr(agent, 'role') else str(agent),
                "agent_fingerprint": agent_fingerprint,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "error": str(event.error)
            })
        
        # Task Events
        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event):
            task = event.task
            task_fingerprint = task.fingerprint.uuid_str if hasattr(task, 'fingerprint') else None
            
            # Register the task fingerprint
            if task_fingerprint:
                task_metadata = task.fingerprint.metadata or {}
                self.fingerprint_registry[task_fingerprint] = {
                    "type": "task",
                    "description": task.description if hasattr(task, 'description') else str(task),
                    "metadata": task_metadata,
                    "timestamp": time.time()
                }
            
            self._log_event("task_started", {
                "message": f"Task started",
                "task_description": task.description if hasattr(task, 'description') else str(task),
                "task_fingerprint": task_fingerprint,
                "agent_role": task.agent.role if hasattr(task, 'agent') and hasattr(task.agent, 'role') else "Unknown",
                "agent_fingerprint": task.agent.fingerprint.uuid_str if hasattr(task, 'agent') and hasattr(task.agent, 'fingerprint') else None
            })
        
        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            task = event.task
            task_fingerprint = task.fingerprint.uuid_str if hasattr(task, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if task_fingerprint and task_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[task_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("task_completed", {
                "message": f"Task completed",
                "task_description": task.description if hasattr(task, 'description') else str(task),
                "task_fingerprint": task_fingerprint,
                "agent_role": task.agent.role if hasattr(task, 'agent') and hasattr(task.agent, 'role') else "Unknown",
                "agent_fingerprint": task.agent.fingerprint.uuid_str if hasattr(task, 'agent') and hasattr(task.agent, 'fingerprint') else None,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "result": str(event.output)[:100] + "..." if len(str(event.output)) > 100 else str(event.output)
            })
        
        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event):
            task = event.task
            task_fingerprint = task.fingerprint.uuid_str if hasattr(task, 'fingerprint') else None
            
            # Calculate execution time if we have the start time in the registry
            execution_time = None
            if task_fingerprint and task_fingerprint in self.fingerprint_registry:
                start_time = self.fingerprint_registry[task_fingerprint].get("timestamp")
                if start_time:
                    execution_time = time.time() - start_time
            
            self._log_event("task_failed", {
                "message": f"Task failed",
                "task_description": task.description if hasattr(task, 'description') else str(task),
                "task_fingerprint": task_fingerprint,
                "agent_role": task.agent.role if hasattr(task, 'agent') and hasattr(task.agent, 'role') else "Unknown",
                "agent_fingerprint": task.agent.fingerprint.uuid_str if hasattr(task, 'agent') and hasattr(task.agent, 'fingerprint') else None,
                "execution_time": f"{execution_time:.2f}s" if execution_time else None,
                "error": str(event.error)
            })
        
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
        
        # Add fingerprint tracking info
        if "crew_fingerprint" in data or "agent_fingerprint" in data or "task_fingerprint" in data:
            fingerprint = data.get("crew_fingerprint") or data.get("agent_fingerprint") or data.get("task_fingerprint")
            data["fingerprint_info"] = self.fingerprint_registry.get(fingerprint, {}) if fingerprint else {}
        
        # Log the event
        logger.info(f"[{timestamp}] Event {event_type}: {data.get('message', '')}")
        
        # Save to file
        try:
            # Create a unique filename with event type and count
            filename = f"{self.log_dir}/event_{time.strftime('%Y%m%d_%H%M%S')}_{self.event_count:04d}_{event_type}.json"
            with open(filename, "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "type": event_type,
                    **data
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving event log: {str(e)}")


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


class CollaborationEventListener(BaseEventListener):
    """
    Event listener for collaboration events.
    
    This listener tracks delegations between agents and other collaborative events,
    storing the information in the collaborative memory system.
    """
    
    def __init__(self, memory: Optional[CollaborativeMemory] = None):
        """
        Initialize the collaboration event listener.
        
        Args:
            memory: Optional collaborative memory instance, will be created if not provided
        """
        super().__init__()
        self.memory = memory or CollaborativeMemory()
        
    def setup_listeners(self, event_bus):
        """
        Set up event listeners.
        
        Args:
            event_bus: The event bus to attach listeners to
        """
        # Only register delegation event handlers if the events are available
        if DELEGATION_EVENTS_AVAILABLE:
            @event_bus.on(AgentDelegationStartedEvent)
            def on_delegation_started(source, event):
                delegator = event.delegator.role if hasattr(event.delegator, "role") else "Unknown"
                delegatee = event.delegatee.role if hasattr(event.delegatee, "role") else "Unknown"
                
                logger.info(f"Delegation started: {delegator} → {delegatee}")
                
                # Record delegation in collaborative memory
                self.memory.record_delegation(
                    delegator=delegator,
                    delegatee=delegatee,
                    task_description=event.task_description,
                    context={
                        "task_id": event.task_id if hasattr(event, "task_id") else None,
                        "timestamp": time.time()
                    }
                )
            
            @event_bus.on(AgentDelegationCompletedEvent)
            def on_delegation_completed(source, event):
                delegator = event.delegator.role if hasattr(event.delegator, "role") else "Unknown"
                delegatee = event.delegatee.role if hasattr(event.delegatee, "role") else "Unknown"
                
                logger.info(f"Delegation completed: {delegator} → {delegatee}")
                
                # Generate a delegation ID to match the one created during started event
                delegation_id = f"{int(event.timestamp)}_{delegator}_to_{delegatee}"
                
                # Update delegation record
                self.memory.complete_delegation(
                    delegation_id=delegation_id,
                    result=event.result if hasattr(event, "result") else "Task completed",
                    success=True
                )
                
                # Add collaborative insight
                self.memory.add_collaborative_insight(
                    insight=f"Task delegated by {delegator} to {delegatee} was completed: {event.task_description[:100]}...",
                    agents_involved=[delegator, delegatee]
                )
        else:
            # If delegation events aren't available, use task events to infer delegations
            logger.info("Using task events to infer delegations since delegation events aren't available")
        
        # Track task completion for potential collaboration detection
        @event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            # Get the agent role
            agent_name = event.task.agent.role if hasattr(event.task, "agent") and hasattr(event.task.agent, "role") else "Unknown"
            
            # Record task completion in shared context
            self.memory.update_shared_context(
                key=f"task_completed_{int(time.time())}",
                value={
                    "agent": agent_name,
                    "task_description": event.task.description if hasattr(event.task, "description") else "Unknown task",
                    "timestamp": time.time()
                },
                agent_name=agent_name
            )
            
            # Check if this task has context from other tasks, which might indicate collaboration
            if hasattr(event.task, "context") and event.task.context:
                context_agents = []
                for ctx_task in event.task.context:
                    if hasattr(ctx_task, "agent") and hasattr(ctx_task.agent, "role"):
                        context_agents.append(ctx_task.agent.role)
                
                if context_agents:
                    # This is a collaborative task that used context from other agents
                    collaborators = list(set(context_agents + [agent_name]))
                    
                    if len(collaborators) > 1:  # Only if there's actual collaboration
                        self.memory.add_collaborative_insight(
                            insight=f"Collaborative task completed by {agent_name} using input from {', '.join(context_agents)}",
                            agents_involved=collaborators
                        )


# Function to get CrewAI event listeners
def get_crewai_listeners() -> List[BaseEventListener]:
    """
    Get a list of CrewAI event listeners.
    
    Returns:
        List of CrewAI event listeners
    """
    listeners = [
        CrewAILoggingListener(),
        ProgressTrackingListener()
    ]
    
    # Add the collaboration listener
    memory = CollaborativeMemory()
    listeners.append(CollaborationEventListener(memory=memory))
    
    return listeners


# Initialize CrewAI event listeners
for listener in get_crewai_listeners():
    listener.setup_listeners(crewai_event_bus) 