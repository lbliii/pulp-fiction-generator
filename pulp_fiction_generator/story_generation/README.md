# Story Generation Module

This module contains components for story generation in the Pulp Fiction Generator.

## Components

### GenerationConfig

The `GenerationConfig` class encapsulates all configuration parameters used for generating stories, including:
- Genre, title, chapters count
- Model configuration 
- Output settings
- Generation options like chunked mode, timeout, etc.

### StoryGenerator

The `StoryGenerator` class is responsible for the actual story generation process:
- Initializes and configures the generation environment
- Manages the generation process
- Handles progress tracking and reporting
- Finalizes and saves generated stories

### GenerationResult

A data class that represents the result of a generation operation, including:
- Success status
- Generated story text
- Error messages (if applicable)
- Generation statistics

## Usage

This module is used by the CLI commands but can also be used programmatically:

```python
from pulp_fiction_generator.story_generation.generation_config import GenerationConfig
from pulp_fiction_generator.story_generation.story_generator import StoryGenerator
from pulp_fiction_generator.utils.story_persistence import StoryPersistence, StoryState
from pulp_fiction_generator.story_model.state import StoryStateManager

# Initialize components
config = GenerationConfig(genre="noir", title="My Story")
story_persistence = StoryPersistence("./output")
story_state = StoryState("noir", "My Story")
story_state_manager = StoryStateManager()

# Create the generator
generator = StoryGenerator(
    config=config,
    story_state=story_state,
    story_state_manager=story_state_manager,
    story_persistence=story_persistence
)

# Generate the story
result = generator.generate()

# Check result
if result.success:
    print(f"Story generated: {result.story_text[:100]}...")
    print(f"Stats: {result.stats}")
else:
    print(f"Error: {result.error}")
``` 