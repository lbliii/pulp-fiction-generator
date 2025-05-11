# CrewAI Event Listeners

This document describes how to use CrewAI's event listener system in the Pulp Fiction Generator project.

## Overview

CrewAI provides a powerful event system that allows you to monitor and react to various events during crew execution. The Pulp Fiction Generator implements both a legacy custom event system (for backward compatibility) and the newer, more powerful CrewAI event system.

## Available Event Listeners

The project includes several pre-configured event listeners:

1. **CrewAILoggingListener**: Logs all CrewAI events to JSON files in the `logs/crewai_events` directory.
2. **ProgressTrackingListener**: Tracks progress of crew execution, including task completion and estimated time remaining.
3. **TokenTrackingListener**: Tracks token usage by model and writes summary reports.

Additionally, the legacy event listeners are still available:

1. **LoggingEventListener**: Legacy listener that logs events to files.
2. **ProgressEventListener**: Legacy listener that tracks and reports progress.
3. **ErrorEventListener**: Legacy listener that tracks and responds to errors.

## Using Event Listeners

### Default Configuration

By default, the event listeners are initialized automatically when the `event_listeners.py` module is imported. You don't need to do anything special to use them in your code.

```python
from pulp_fiction_generator.crews.crew_coordinator import CrewCoordinator

# Create a coordinator
coordinator = CrewCoordinator(...)

# Event listeners are already initialized
result = coordinator.generate_story("noir")
```

### Custom Event Listeners

If you want to create a custom event listener with specific behavior:

```python
from pulp_fiction_generator.crews.crew_executor import CrewExecutor
from crewai.utilities.events.base_event_listener import BaseEventListener
from crewai.utilities.events import crewai_event_bus

# Create a custom event listener
class MyCustomListener(BaseEventListener):
    def __init__(self):
        super().__init__()
    
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on("CrewKickoffStartedEvent")
        def on_crew_started(source, event):
            print(f"Crew '{event.crew_name}' has started execution!")

# Initialize and register your listener
my_listener = MyCustomListener()
my_listener.setup_listeners(crewai_event_bus)

# Now use the executor as normal
executor = CrewExecutor()
```

### Using Progress Callbacks

You can register a callback function to be notified of progress:

```python
def progress_callback(completed_tasks, total_tasks, progress, remaining):
    print(f"Progress: {progress:.1f}% ({completed_tasks}/{total_tasks})")
    if remaining:
        print(f"Estimated time remaining: {int(remaining/60)} minutes")

executor = CrewExecutor()
progress_listener = executor.create_custom_event_listener(callback=progress_callback)

# Now use the executor as normal
result = executor.kickoff_crew(crew, inputs)
```

### Tracking Token Usage

To track token usage during crew execution:

```python
executor = CrewExecutor(debug_mode=True)
token_listener = executor.add_token_tracking_listener(log_dir="logs/token_usage")

# Now use the executor as normal
result = executor.kickoff_crew(crew, inputs)

# Token usage will be logged and saved to files
```

## Event Types

CrewAI provides a wide range of events that you can listen for:

### Crew Events

* **CrewKickoffStartedEvent**: Emitted when a Crew starts execution
* **CrewKickoffCompletedEvent**: Emitted when a Crew completes execution
* **CrewKickoffFailedEvent**: Emitted when a Crew fails to complete execution

### Agent Events

* **AgentExecutionStartedEvent**: Emitted when an Agent starts executing a task
* **AgentExecutionCompletedEvent**: Emitted when an Agent completes executing a task
* **AgentExecutionErrorEvent**: Emitted when an Agent encounters an error during execution

### Task Events

* **TaskStartedEvent**: Emitted when a Task starts execution
* **TaskCompletedEvent**: Emitted when a Task completes execution
* **TaskFailedEvent**: Emitted when a Task fails to complete execution

### Tool Usage Events

* **ToolUsageStartedEvent**: Emitted when a tool execution is started
* **ToolUsageFinishedEvent**: Emitted when a tool execution is completed

### LLM Events

* **LLMCallStartedEvent**: Emitted when an LLM call starts
* **LLMCallCompletedEvent**: Emitted when an LLM call completes
* **LLMCallFailedEvent**: Emitted when an LLM call fails

## Scoped Event Handlers

For temporary event handling, you can use the `scoped_handlers` context manager:

```python
from crewai.utilities.events import crewai_event_bus, LLMCallCompletedEvent

with crewai_event_bus.scoped_handlers():
    @crewai_event_bus.on(LLMCallCompletedEvent)
    def temp_handler(source, event):
        print(f"LLM call completed with {event.tokens_used} tokens")

    # Do something that emits events

# Outside the context, the temporary handler is removed
```

## Best Practices

1. **Keep handlers light**: Event handlers should be lightweight and avoid blocking operations
2. **Error handling**: Include proper error handling in your event handlers
3. **Selective listening**: Only listen for events you actually need to handle
4. **Logging**: Use appropriate log levels in your handlers

## Creating Custom Event Listeners

To create a custom event listener:

1. Create a class that inherits from `BaseEventListener`
2. Implement the `setup_listeners` method
3. Register handlers for the events you're interested in

Example:

```python
from crewai.utilities.events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
)
from crewai.utilities.events.base_event_listener import BaseEventListener

class MyCustomListener(BaseEventListener):
    def __init__(self):
        super().__init__()

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            print(f"Crew '{event.crew_name}' has started execution!")

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            print(f"Crew '{event.crew_name}' has completed execution!")
            print(f"Output: {event.output}")
```

## Additional Resources

For more information on CrewAI's event system, see the [official documentation](https://docs.crewai.com/concepts/event-listener/). 