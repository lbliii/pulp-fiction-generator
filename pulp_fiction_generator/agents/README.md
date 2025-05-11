# Pulp Fiction Generator Agent System

This directory contains the agent system for the Pulp Fiction Generator, built on CrewAI.

## Agent Architecture

The system uses a factory pattern to create specialized agents for different aspects of story generation:

- **Creative Agents**: Worldbuilders and character creators
- **Content Agents**: Plotters and writers
- **Support Agents**: Researchers and editors

## Key Features

### Agent Configuration

Agents are configured using YAML files in the `configs` directory, with support for:

- Genre-specific configurations
- Default fallback configurations
- Configuration overrides at runtime

### Memory and Context

Agents maintain memory of their interactions, enabling:

- Consistent story development across multiple steps
- Contextual awareness of previous decisions
- Respect for context window limits

### Execution Controls

Agents can be controlled with parameters like:

- `max_iter`: Maximum iterations before conclusion
- `max_execution_time`: Timeout for long-running tasks
- `max_rpm`: Rate limiting for API calls
- `max_retry_limit`: Error recovery

### Collaboration

Agents can work together through:

- Task delegation between agents
- Context sharing
- Specialized roles with complementary skills

### Tool Integration

Agents can use various tools to enhance their capabilities:

- Tools are registered in the `ToolRegistry` 
- Tools can be added via YAML configuration
- The `ToolLoader` creates tool instances from configurations

Example tool configuration:

```yaml
tools:
  - name: "web_search"
    config:
      api_key: "..."
  - name: "document_reader"
    config:
      document_path: "..."
```

### Knowledge Sources

Agents can access specialized knowledge sources:

- Knowledge sources are registered in the `KnowledgeRegistry`
- Sources can be added via YAML configuration
- The `KnowledgeLoader` creates source instances from configurations

Example knowledge source configuration:

```yaml
knowledge_sources:
  - name: "pulp_fiction_db"
    config:
      genre: "detective"
  - name: "historical_context"
    config:
      era: "1930s"
```

### Custom Templates

Agents can use custom templates for system prompts, user prompts, and responses:

- Templates are available in the `templates` module
- Specialized templates for creative and analytical work
- Templates can be specified in agent configurations

Example template configuration:

```yaml
role: "Pulp Fiction Writer"
goal: "Generate engaging prose"
backstory: "Experienced pulp fiction writer..."
system_template: "CREATIVE_SYSTEM_TEMPLATE"
prompt_template: "CREATIVE_PROMPT_TEMPLATE"
response_template: "DEFAULT_RESPONSE_TEMPLATE"
```

## Creating New Agents

1. Define a configuration in `configs/{genre}/{agent_type}.yaml` or use the generic configs
2. Use the appropriate factory method from `AgentFactory` to create the agent
3. Add the agent to your crew for collaboration

## Example Configuration

```yaml
# Basic configuration
role: "Pulp Fiction Research Specialist"
goal: "Uncover genre-appropriate elements, historical context, and reference material"
backstory: "A meticulous researcher with deep knowledge of pulp fiction history across multiple genres"

# Runtime behavior
verbose: true
memory: true
respect_context_window: true
max_iter: 25
max_retry_limit: 3

# Collaboration
allow_delegation: true

# Tools and knowledge
tools:
  - "web_search"
  - name: "document_reader"
    config:
      path: "/data/pulp_fiction_corpus"

knowledge_sources:
  - "genre_database"
  - name: "era_context"
    config:
      era: "golden_age"

# Custom templates
system_template: "ANALYTICAL_SYSTEM_TEMPLATE"
```

## Registering Custom Tools

To register custom tools, use the tool registry:

```python
from pulp_fiction_generator.agents.tools import registry as tool_registry

# Register a tool class
tool_registry.register_tool("my_tool", MyToolClass)

# Register a tool factory function
tool_registry.register_tool_factory("my_factory_tool", create_my_tool)
```

## Registering Knowledge Sources

To register custom knowledge sources, use the knowledge registry:

```python
from pulp_fiction_generator.agents.knowledge import registry as knowledge_registry

# Register a knowledge source class
knowledge_registry.register_source("my_source", MySourceClass)

# Register a knowledge source factory function
knowledge_registry.register_source_factory("my_factory_source", create_my_source)
``` 