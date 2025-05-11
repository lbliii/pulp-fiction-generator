# Command Line Interface (CLI) Guide

The Pulp Fiction Generator provides a command-line interface (CLI) for generating and managing pulp fiction stories. This guide explains the available commands and their options.

## Basic Command Syntax

All commands follow this pattern:

```bash
pulp-fiction <command> [options]
```

For help with any command:

```bash
pulp-fiction <command> --help
```

## Primary Commands

### Generating Stories

The primary command for generating stories is `generate`:

```bash
pulp-fiction generate --genre noir --chapters 1
```

#### Available Options

- `--genre`, `-g`: Pulp fiction genre to generate (default: noir)
- `--chapters`, `-c`: Number of chapters to generate (default: 1)
- `--output`, `-o`: File to save the generated story to
- `--model`, `-m`: Ollama model to use (default: llama3.2)
- `--title`, `-t`: Custom title for the story
- `--plot`, `-p`: Plot template to use for the story
- `--verbose`, `-v`: Enable verbose output
- `--continue`, `-C`: Continue from an existing story file
- `--resume`, `-R`: Resume a project by name
- `--timeout`, `-T`: Maximum time to wait for generation (seconds)

### Listing Available Resources

List available genres:
```bash
pulp-fiction list-genres
```

List installed plugins:
```bash
pulp-fiction list-plugins
```

List saved story projects:
```bash
pulp-fiction list-projects
```

### Flow-based Generation

For more advanced, flow-based story generation:

```bash
pulp-fiction flow generate --genre sci-fi
```

#### Flow Visualization

To visualize the generation flow:

```bash
pulp-fiction flow generate --genre adventure --visualize
```

### Memory Management

View memory for all genres:
```bash
pulp-fiction memory list
```

View memory for a specific genre:
```bash
pulp-fiction memory list --genre noir
```

Reset memory for a genre:
```bash
pulp-fiction memory reset --genre scifi --type all
```

Export memory to a directory:
```bash
pulp-fiction memory export ./memory_backup --genre western
```

## Common Use Cases

### Basic Story Generation

Generate a noir detective story:
```bash
pulp-fiction generate --genre noir --chapters 1
```

Generate a sci-fi adventure with a custom title:
```bash
pulp-fiction generate --genre sci-fi --chapters 2 --title "Beyond the Stars"
```

### Advanced Generation

Generate a story with chunked processing and a specific model:
```bash
pulp-fiction generate --genre adventure --chapters 1 --chunked --model llama3.2
```

### Continuing Stories

Continue from a previously saved story file:
```bash
pulp-fiction generate --continue ./output/my_story.json --chapters 1
```

Resume a named project:
```bash
pulp-fiction generate --resume my_noir_story --chapters 1
```

### Customizing Output

Save the story to a specific file with markdown formatting:
```bash
pulp-fiction generate --genre sci-fi --output ./my_stories/space_adventure.md --format markdown
```

## Configuration Options

The CLI behavior can be customized through environment variables or a configuration file (`~/.pulp-fiction/config.yaml` or `./config.yaml`).

### Key Configuration Options

#### Ollama Settings
- `OLLAMA_HOST`: Host for Ollama API (default: http://localhost:11434)
- `OLLAMA_MODEL`: Default model to use (default: llama3.2)
- `OLLAMA_THREADS`: Number of CPU threads for Ollama
- `OLLAMA_GPU_LAYERS`: Number of layers to run on GPU

#### Generation Settings
- `GENERATION_TIMEOUT`: Maximum time for generation in seconds
- `TEMPERATURE`: Temperature for text generation (0.0-1.0)
- `TOP_P`: Top-p sampling value (0.0-1.0)

#### Cache Settings
- `ENABLE_CACHE`: Enable or disable caching
- `CACHE_DIR`: Directory for cache files
- `MAX_CACHE_SIZE`: Maximum cache size in MB

#### Agent Settings
- `ENABLE_AGENT_DELEGATION`: Enable delegation between agents
- `AGENT_VERBOSE`: Enable verbose agent output 