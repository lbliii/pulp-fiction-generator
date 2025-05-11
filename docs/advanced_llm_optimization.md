# Advanced LLM Optimization Features

This document explains the advanced Large Language Model (LLM) optimization features available in Pulp Fiction Generator and how to use them effectively.

## Structured Responses with Pydantic Models

The application now supports structured responses using Pydantic models, allowing for consistent, validated outputs in specific formats:

```python
# Example of using a structured response
from pulp_fiction_generator.models.schema import StoryOutline
from pulp_fiction_generator.models.model_service import ModelService

# Get a model service
model_service = get_model_service()

# Get an LLM specifically for story outlines
outline_llm = model_service.get_story_outline_llm()

# The response will be validated against the StoryOutline schema
response = outline_llm.call(messages=[
    {"role": "user", "content": "Create an outline for a noir detective story"}
])

# Access structured data
if "structured_data" in response:
    outline = response["structured_data"]
    print(f"Title: {outline.title}")
    print(f"Premise: {outline.premise}")
    
    # Access nested fields
    for character in outline.characters:
        print(f"Character: {character.name} - {character.role}")
```

## Specialized LLMs for Different Tasks

The system automatically assigns specialized LLMs to different tasks based on their requirements:

| Task Type | Specialized LLM | Configuration |
|-----------|-----------------|--------------|
| Planning | `planning_llm` | Low temperature (0.2), focused planning |
| Research | `historical_analysis_llm` | Low temperature (0.3), factual responses |
| Worldbuilding | `worldbuilding_llm` | Moderate-high temperature (0.75), creative |
| Character Creation | Character Pydantic model | Structured output format |
| Writing | `creative_llm` + streaming | High temperature (0.8), streaming support |
| Editing | `feedback_llm` | Moderate temperature (0.4), structured feedback |

To configure specialized LLMs, update the `agent` section in `config.yaml`:

```yaml
agent:
  # ...
  use_specialized_llms: true  # Enable role-specialized LLMs
  use_structured_output: true  # Enable structured Pydantic responses
```

## Context Window Management

The system now intelligently manages context windows based on task requirements:

- Automatically respects context window limits (activated by default)
- Uses different context window sizes for different task types:
  - Research/planning: 4K-8K tokens
  - Creative writing: 8K-16K tokens
  - Editing: 16K+ tokens for full story context

Configure in `config.yaml`:

```yaml
llm_optimization:
  context_window_sizes:
    planning: 4096
    worldbuilding: 8192
    writing: 16384
    # ...
```

## Streaming Responses

For longer outputs (like story drafts), the system now supports streaming responses:

```python
# Example of using streaming
streaming_llm = model_service.get_streaming_llm()

# Start streaming response
for chunk in streaming_llm.stream_call(messages=[
    {"role": "user", "content": "Write a 1000-word detective story"}
]):
    print(chunk["choices"][0]["delta"]["content"], end="", flush=True)
```

Enable streaming in `config.yaml`:

```yaml
agent:
  # ...
  enable_streaming: true
```

## Performance Optimization

The system includes these performance optimizations:

1. **Temperature Optimization**: Different temperature settings for different tasks:
   - Planning/research: 0.2-0.3 (focused, factual)
   - Creative tasks: 0.7-0.8 (more creative, varied)

2. **Token Usage Monitoring**: Track token usage across generations

3. **Caching**: Efficient caching of common prompts and responses

## Using with CrewAI Flows

The optimizations are automatically applied when using CrewAI Flows:

```python
from pulp_fiction_generator.flow.flow_factory import FlowFactory

# Create a flow factory
flow_factory = FlowFactory(crew_factory)

# Create a flow with optimization enabled
flow = flow_factory.create_story_flow(
    genre="noir",
    custom_inputs={"setting": "1940s San Francisco"}
)

# The flow will automatically use specialized LLMs for each phase
result = flow_factory.execute_flow(flow, timeout_seconds=300)
```

## Debug and Monitoring

To see which specialized LLMs are being used, enable debug logging:

```yaml
app:
  log_level: "debug"
```

The logs will show which specialized LLM is being used for each task and agent. 