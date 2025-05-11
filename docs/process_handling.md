# CrewAI Process Handling

This document explains the process handling capabilities in the Pulp Fiction Generator based on CrewAI processes.

## Overview

CrewAI provides different process types for orchestrating tasks among agents:

1. **Sequential Process**: Tasks are executed in a predefined order, with each task's output serving as context for subsequent tasks.

2. **Hierarchical Process**: A manager agent oversees task execution, including planning, delegation, and validation. Tasks are dynamically allocated based on agent capabilities.

3. **Consensual Process** (Future): A planned process type in CrewAI for collaborative decision-making among agents.

Our implementation adds validation, fallback mechanisms, and preparation for future process types.

## Configuration

Process types can be specified in the following ways:

### In YAML Configuration

```yaml
# Config.yaml or genre-specific config
process: sequential  # or hierarchical
```

For hierarchical processes, you must specify either a manager_llm or configure a manager agent:

```yaml
process: hierarchical
manager_llm: gpt-4o  # Required for hierarchical process
```

### In Code

```python
from crewai import Process
from pulp_fiction_generator.crews.config.crew_coordinator_config import CrewCoordinatorConfig

# Create a configuration with sequential process
config = CrewCoordinatorConfig()  # Default is sequential

# Create a configuration with hierarchical process
config = CrewCoordinatorConfig(process=Process.hierarchical)

# Update the process
config = config.with_process(Process.hierarchical)

# Using string representations
config = config.with_process("hierarchical")
```

### Extended Process Types

We've implemented an `ExtendedProcessType` enum that includes the planned consensual process:

```python
from pulp_fiction_generator.crews.process_utils import ExtendedProcessType

# Get the extended process type
extended_type = ExtendedProcessType.CONSENSUAL

# Convert to CrewAI process (currently falls back to sequential)
crewai_process = extended_type.to_crewai_process()
```

## Validation

The system automatically validates process configurations:

1. For hierarchical processes, it checks for the presence of a manager_llm or manager_agent
2. If validation fails, it gracefully falls back to the sequential process with appropriate warnings

```python
from pulp_fiction_generator.crews.process_utils import validate_process_config

# Validate a process configuration
is_valid, error_message = validate_process_config(Process.hierarchical, config_dict)
if not is_valid:
    print(f"Error: {error_message}")
```

## Process Utilities

We provide several utility functions for working with processes:

- `get_process_from_string(process_name: str) -> Process`: Convert a string to a Process enum
- `get_process_description(process: Process) -> str`: Get a human-readable description of a process
- `validate_process_config(process, config) -> Tuple[bool, Optional[str]]`: Validate process configuration

## Testing

Comprehensive tests for process handling are available in `tests/test_process_handling.py`. Run with:

```bash
pytest tests/test_process_handling.py
```

## Future Considerations

When CrewAI adds support for the consensual process:

1. Update the `process_utils.py` module to use the new process type
2. Implement appropriate validation in `validate_process_config()`
3. Add a test case in `test_process_handling.py`

No other code changes should be necessary as we've designed the system to be extensible.

## Error Handling

The system provides clear error messages when processes are misconfigured and automatically falls back to safer defaults:

```
WARNING: Invalid process configuration: Hierarchical process requires either 'manager_llm' or 'manager_agent' to be specified in the configuration. Falling back to sequential.
``` 