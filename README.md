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
- **Agent Collaboration**: Agents can collaborate and delegate tasks to each other

## New Features

### Enhanced Agent Collaboration
The project now includes advanced collaboration features using CrewAI's latest capabilities:

- **Hierarchical Processing**: Agent crews now operate in a hierarchical process mode where a manager agent oversees the work
- **Task Delegation**: Agents can delegate specialized tasks to other agents with relevant expertise
- **Context Sharing**: Agents share context and build upon each other's work in a more integrated manner
- **Collaborative Memory**: Enhanced memory system tracks collaborative insights and delegations

To use collaborative features:
```bash
# Generate a story with enhanced collaboration
pulp-fiction generate --genre noir --collaborative

# Visualize collaboration between agents
pulp-fiction visualize --genre scifi --show-delegations

# Show collaboration statistics for a previously generated story
pulp-fiction analyze --collaboration
```

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

### Fingerprinting System
The project now implements CrewAI's fingerprinting system for enhanced traceability and debugging:

- **Unique Identifiers**: Each agent, crew, and task gets a unique fingerprint for tracking throughout its lifecycle
- **Metadata Enrichment**: Fingerprints store context-specific metadata for better understanding component relationships
- **Execution Tracing**: Complete trace of agent and task execution paths for debugging complex issues
- **Deterministic Fingerprints**: Option to create reproducible identifiers for consistent tracking
- **Visualization**: Enhanced visualization tools that leverage fingerprinting for better insights
- **Lifecycle Analysis**: Analyze component lifecycles through fingerprint tracking
- **Enhanced Logging**: All logs now include fingerprint references for better correlation

Fingerprinting examples:
```python
# Create an agent with a deterministic fingerprint
writer_agent = agent_factory.create_agent(
    agent_type="writer",
    genre="noir",
    deterministic_id="noir_writer_v1"
)

# Access fingerprint information
fingerprint = writer_agent.fingerprint
print(f"Agent UUID: {fingerprint.uuid_str}")
print(f"Agent metadata: {fingerprint.metadata}")
print(f"Creation time: {fingerprint.created_at}")

# Track execution with fingerprints
print(f"Task fingerprint: {task.fingerprint.uuid_str}")
```

CLI examples:
```bash
# Generate a story with fingerprinting enabled
pulp-fiction generate --genre noir --track-fingerprints

# Analyze fingerprint data for a specific run
pulp-fiction analyze --fingerprints --last-run

# Export fingerprint data to a file
pulp-fiction export --fingerprints --format json --output fingerprints.json
```

Configure fingerprinting in config.yaml:
```yaml
# Fingerprinting settings
fingerprinting:
  enabled: true
  deterministic: false  # Set to true for reproducible fingerprints
  metadata:
    include_version: true
    include_environment: true
  visualization:
    enabled: true
    output_dir: "./logs/fingerprint_graphs"
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

### Plugin System Testing

The Pulp Fiction Generator features a comprehensive testing framework for its plugin system, ensuring reliability and stability:

- **High Test Coverage**: 96% test coverage across the plugin system
- **Standalone Test Scripts**: Individual test scripts for each component:
  - `tests/plugins/plugin_coverage.py`: Tests core plugin functionality and registry
  - `tests/plugins/plugin_hooks_coverage.py`: Tests the plugin hook system
  - `tests/plugins/plugin_manager_coverage.py`: Tests plugin discovery and management

To run the plugin tests with coverage reporting:

```bash
# Run individual test components
python tests/plugins/plugin_coverage.py
python tests/plugins/plugin_hooks_coverage.py
python tests/plugins/plugin_manager_coverage.py

# Run all plugin tests with combined coverage report
python -m coverage run -a tests/plugins/plugin_coverage.py && \
python -m coverage run -a tests/plugins/plugin_hooks_coverage.py && \
python -m coverage run -a tests/plugins/plugin_manager_coverage.py && \
python -m coverage report -m --include="*/pulp_fiction_generator/plugins/*"

# Alternatively, use the provided shell script
./tests/plugins/run_plugin_tests.sh

# Generate HTML coverage report with the shell script
./tests/plugins/run_plugin_tests.sh --html
```

The plugin testing system includes:
- Registry functionality verification
- Hook registration and execution tests
- Plugin discovery from multiple sources
- Error handling for various failure scenarios
- Auto-discovery of installed Python package plugins
- Mocking capabilities for comprehensive testing

For more information on testing the plugin system, see [Testing Documentation](docs/testing.md).

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
pulp-fiction list-projects
```

Continue an existing story:
```bash
pulp-fiction generate --continue your_story_file.json --chapters 1
```

For complete documentation on CLI usage, see [docs/cli_usage.md](docs/cli_usage.md).

## Recent Improvements

- **Enhanced CLI Interface**: The command-line interface has been improved with standardized naming conventions (using hyphens), better error handling, and more consistent parameter parsing.
- **Improved Configuration System**: The configuration system now includes better validation, clear error messages, and structured warning logs.
- **Dependency Checking**: Startup checks for required dependencies and versions to avoid compatibility issues.
- **Comprehensive Documentation**: New detailed CLI usage guide with examples for all commands and options.

## Development

Contributions are welcome! Please see [docs/contributing.md](docs/contributing.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 