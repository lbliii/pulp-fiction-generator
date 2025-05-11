# Story Generation Package

This package contains a modular implementation of story generation functionality based on SOLID design principles. It replaces the original monolithic `StoryGenerator` class that was previously in `pulp_fiction_generator/crews/story_generator.py`.

## Structure

The package consists of several specialized components:

- **`StoryGenerator`** (`generator.py`): Main orchestration class that handles the story generation process
- **`TaskFactory`** (`tasks.py`): Creates and configures specialized tasks for each story generation phase
- **`ExecutionEngine`** (`execution.py`): Executes tasks and crews with robust error handling and timeout management
- **`StoryValidator`** (`validation.py`): Provides validation functions used as guardrails to ensure quality content
- **`StoryStateManager`** (`state.py`): Manages persistence and retrieval of story generation artifacts
- **Models** (`models.py`): Contains Pydantic models for structured data representation

## SOLID Principles Applied

This refactoring follows SOLID principles:

1. **Single Responsibility**: Each class has a single, focused purpose
2. **Open/Closed**: The components are open for extension but closed for modification
3. **Liskov Substitution**: Components can be replaced with alternative implementations
4. **Interface Segregation**: Clean interfaces between components
5. **Dependency Injection**: Dependencies are injected rather than hardcoded

## Usage Example

```python
from pulp_fiction_generator.story import StoryGenerator
from pulp_fiction_generator.crews import CrewFactory

# Create a story generator
crew_factory = CrewFactory()
story_generator = StoryGenerator(crew_factory)

# Generate a story
story = story_generator.generate_story("noir")

# Generate a story with checkpoints
artifacts = story_generator.generate_story_chunked(
    "sci-fi", 
    custom_inputs={"title": "Space Adventure"}
)

# Access structured output
final_story = artifacts.final_story
``` 