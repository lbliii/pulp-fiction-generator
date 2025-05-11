# Pulp Fiction Generator

An AI-powered pulp fiction story generator leveraging agent-based architecture to create engaging, serialized fiction in the style of classic pulp magazines.

## Overview

This project uses CrewAI and Ollama (with Llama 3.2) to create a local, cost-effective system for generating pulp fiction stories. The system utilizes a crew of specialized AI agents that work together to plan, research, write, and edit serialized fiction across various pulp genres.

## Features

- **Local Model Deployment**: Uses Ollama with Llama 3.2 to keep costs down and maintain privacy
- **Specialized Agent Roles**: Different agents for different aspects of story creation
- **Genre Flexibility**: Supports various pulp fiction genres (noir, sci-fi, adventure, etc.)
- **Serialized Output**: Creates stories that can continue across multiple sessions
- **Modular Architecture**: Easy to extend with new capabilities
- **Enhanced Agent Tools**: Integrated with CrewAI tools for web search, file operations, and RAG capabilities
- **Advanced Memory System**: Comprehensive memory system for maintaining context across story generations

## New Features

### Enhanced Memory System
The project now features an advanced memory system that allows agents to maintain context and consistency across story generations:

- **Short-Term Memory**: Temporarily stores recent interactions and context during story creation
- **Long-Term Memory**: Preserves valuable insights and story elements for continuity across sessions
- **Entity Memory**: Tracks and organizes information about characters, places, and concepts
- **Configurable Storage**: Custom storage paths and extensive configuration options
- **Memory Management CLI**: Commands for viewing, resetting, and exporting memory

Memory management example:
```bash
# List memory for all genres
pulp-fiction memory list

# List memory for a specific genre
pulp-fiction memory list --genre noir

# Reset memory for a genre
pulp-fiction memory reset --genre scifi --type all

# Export memory to a directory
pulp-fiction memory export ./memory_backup --genre western
```

Memory is configured in the config.yaml file:
```yaml
# Memory settings
memory:
  enable: true
  storage_dir: "./.memory"
  # Memory component configuration
  long_term:
    enabled: true
    db_path: "long_term_memory.db"
  short_term:
    enabled: true 
    provider: "rag"
  entity:
    enabled: true
    track_entities: true
  # Embedding configuration
  embedder:
    provider: "openai"
    model: "text-embedding-3-small"
```

### Enhanced Agent Tools
The project now integrates a comprehensive set of CrewAI tools to enhance agent capabilities:

- **Web Search**: Agents can research topics to improve accuracy and realism
- **File Operations**: Read and analyze reference material and previously generated content
- **Directory Management**: Work with collections of reference documents
- **RAG Capabilities**: Use PDF, CSV, and other document types for reference
- **Extensible Tool System**: Easy to add custom tools via the tool registry

Tool usage example:
```python
# Create an agent with web search capabilities
researcher = agent_factory.create_agent(
    role="Researcher",
    tools=["web_search"]
)

# Create an agent with multiple tools
writer = agent_factory.create_agent(
    role="Writer",
    tools=[
        "file_read",
        "directory_read",
        "rag"
    ]
)
```

### Code Modularization
The codebase has been significantly refactored to improve maintainability and extensibility:
- Command-line interface has been modularized with separate modules for each command
- New command registration system allows easy addition of new commands
- Consistent error handling across all commands

### Plugin Architecture
A new plugin architecture has been implemented to allow extending the system without modifying core code:
- Genre plugins for adding new pulp fiction genres
- Agent plugins for creating specialized AI agent types
- Model plugins for adding support for additional LLM providers
- Custom plugins can be created and installed independently

To use plugins:
```bash
# List available plugins
pulp-fiction plugins

# List only genre plugins
pulp-fiction plugins --genre

# Generate a story using a plugin genre
pulp-fiction generate --genre <plugin-id> --chapters 1
```

### Enhanced Error Handling
A comprehensive error handling system has been implemented to improve reliability:
- Specific exception classes for different error types
- Automatic recovery strategies for common failure scenarios
- Detailed error logging with contextual information
- Easy application of error handling via decorators

Error handling examples:
```python
# Apply error handling to a function
from pulp_fiction_generator.utils.errors import with_error_handling

@with_error_handling
def my_function():
    # Function code here
    pass

# Use specific exception types
from pulp_fiction_generator.utils.errors import ModelConnectionError

try:
    # Code that interacts with the model
except ModelConnectionError as e:
    # Handle specifically model connection issues
```

### Performance Benchmarking
A comprehensive benchmarking system has been implemented for tracking performance:
- Measure execution time, memory usage, and custom metrics
- Compare benchmark results to identify improvements or regressions
- Save and analyze benchmark history
- Easy application of benchmarking via decorators

Benchmarking examples:
```python
# Apply benchmarking to a function
from pulp_fiction_generator.utils.benchmarks import benchmark

@benchmark(iterations=5, name="my_benchmark")
def my_function():
    # Function code here
    pass

# Manual benchmarking
from pulp_fiction_generator.utils.benchmarks import Benchmark

benchmark = Benchmark("custom_benchmark")
result = benchmark.run(my_function, arg1, arg2)
benchmark.save_results()
```

### Custom Plugin Development
Plugins can be created and installed in several ways:
1. Place in `~/.pulp-fiction/plugins/` (user-specific plugins)
2. Place in `./plugins/` (project-local plugins) 
3. Install as Python packages with the naming pattern `pulp-fiction-plugin-*`

For detailed instructions on creating your own plugins, see [Plugin Development Guide](docs/plugin_development.md).

### CrewAI Flows Integration

The Pulp Fiction Generator now supports CrewAI Flows for more structured and efficient story generation. Flows provide several advantages:

- **Structured Workflow**: Clearly defined phases for story generation
- **State Management**: Improved handling of state between generation steps
- **Visualization**: Visual representation of the story generation process
- **Persistence**: Automatic state persistence for recovery and analysis

#### Using CrewAI Flows

You can use CrewAI Flows through the command line interface:

```bash
# Generate a story using the flow architecture
pulp-fiction flow run --genre scifi --title "The Martian Chronicles"

# Generate a flow visualization
pulp-fiction flow plot --genre noir

# Run a complete story generation with visualization
pulp-fiction flow generate --genre western --visualize
```

#### Flow Architecture

The story generation flow follows these steps:

1. **Research**: Research the genre, tropes, and key elements
2. **Worldbuilding**: Create the story world based on research
3. **Character Development**: Create detailed characters
4. **Plot Creation**: Develop a compelling plot
5. **Draft Writing**: Write the initial story draft
6. **Final Editing**: Polish the story into its final form

Each phase builds on the previous ones, with results stored in a structured state. The state is automatically persisted to disk, allowing for recovery and analysis.

#### State Persistence

The flow state is automatically saved after each phase, creating:
- A JSON file with the complete state
- A text file with the output of each phase
- A final story file with the completed story

These files are stored in a timestamped directory structure for easy reference.

## Working with Custom Inputs

The Pulp Fiction Generator supports passing custom inputs to your story generation process. These can include variables like:

- `title`: The title of your story
- `protagonist_name`: Your main character's name
- `setting`: The story setting
- `theme`: The central theme or message of the story

### Using Custom Inputs

There are two ways to use custom inputs with the story generator:

1. **Using the CrewCoordinator**:
```python
from pulp_fiction_generator.crews import CrewCoordinator
from pulp_fiction_generator.models import StoryConfig

# Create a coordinator
coordinator = CrewCoordinator(agent_factory, model_service)

# Define custom inputs
custom_inputs = {
    "title": "The Dark Matter Mystery",
    "protagonist_name": "Commander Zara",
    "setting": "Aboard the starship Nebula"
}

# Generate a story with custom inputs
story = coordinator.generate_story(
    genre="scifi",
    custom_inputs=custom_inputs
)
```

2. **Using the StoryGenerator directly**:
```python
from pulp_fiction_generator.story import StoryGenerator

# Create a generator
generator = StoryGenerator(crew_factory)

# Define custom inputs
custom_inputs = {
    "title": "The Dark Matter Mystery",
    "protagonist_name": "Commander Zara"
}

# Generate a story with custom inputs
story = generator.generate_story(
    genre="scifi",
    custom_inputs=custom_inputs
)
```

### Implementation Details

The CrewFactory has been updated to properly handle custom inputs in the following ways:

- A new `create_basic_crew_with_inputs` method that attaches custom inputs to the crew
- Updated methods for `create_continuation_crew` and `create_custom_crew` to also support custom inputs
- Improved execution engine that checks for custom inputs in multiple places

## Setup

### Prerequisites

- Python 3.10+ 
- [Ollama](https://ollama.ai) installed locally
- [Llama 3.2](https://ollama.com/library/llama3.2) model pulled in Ollama

### Installation

#### Option 1: Developer Install (Recommended for Development)

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pulp-fiction-generator.git
cd pulp-fiction-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Ensure Ollama is running with Llama 3.2:
```bash
ollama pull llama3.2
ollama serve
```

#### Option 2: Installable Package (Recommended for Users)

You can install the CLI as a package, which will make it available as a command in your system:

```bash
git clone https://github.com/yourusername/pulp-fiction-generator.git
cd pulp-fiction-generator
pip install -e .
```

Now the `pulp-fiction` command will be available globally in your environment.

## Project Structure

```
pulp-fiction-generator/
├── docs/                        # Documentation
│   ├── architecture.md          # System architecture
│   ├── agent_design.md          # Agent role documentation
│   └── design_patterns.md       # Design patterns used
├── pulp_fiction_generator/      # Main package
│   ├── __init__.py
│   ├── agents/                  # Agent definitions
│   ├── crews/                   # Crew configurations
│   ├── prompts/                 # Agent prompts
│   ├── models/                  # Model interaction
│   ├── genres/                  # Genre-specific elements
│   ├── plugins/                 # Plugin system
│   └── utils/                   # Utility functions
│       ├── config.py            # Configuration management
│       ├── error_handling.py    # Error handling system
│       └── benchmarks.py        # Performance benchmarking
├── tests/                       # Tests directory
├── examples/                    # Example stories and usage
├── .env.example                 # Environment variable example
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## Usage

### Basic Commands

#### For Developer Installation:
```bash
python -m pulp_fiction_generator generate --genre sci-fi --chapters 1
```

#### For Package Installation:
```bash
pulp-fiction generate --genre sci-fi --chapters 1
```

#### Alternative (using the executable script):
```bash
./pulp-fiction generate --genre sci-fi --chapters 1
```

Use interactive mode with guided configuration:
```bash
pulp-fiction interactive
```

List available commands:
```bash
pulp-fiction --help
```

### Common Tasks

List available genres:
```bash
pulp-fiction list-genres
```

View plot templates:
```bash
pulp-fiction list-plots
```

Check available models:
```bash
pulp-fiction check-model
```

List saved stories:
```bash
pulp-fiction list-stories
```

Continue an existing story:
```bash
pulp-fiction generate --continue your_story_file.json --chapters 1
```

See [docs/usage.md](docs/usage.md) for complete documentation and examples.

## Development

Contributions are welcome! Please see [docs/contributing.md](docs/contributing.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 