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
│   └── utils/                   # Utility functions
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