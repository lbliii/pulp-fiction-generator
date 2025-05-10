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

## New Features

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