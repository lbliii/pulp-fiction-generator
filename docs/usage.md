# Pulp Fiction Generator Usage Guide

This document provides detailed instructions on how to use the Pulp Fiction Generator from the command line.

## Installation Options

The Pulp Fiction Generator can be used in several ways:

### Option 1: Developer Install (Recommended for Development)

Use the module directly after cloning the repository:

```bash
git clone https://github.com/yourusername/pulp-fiction-generator.git
cd pulp-fiction-generator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Option 2: Installable Package (Recommended for Users)

Install the CLI as a package to make it available as a command in your system:

```bash
git clone https://github.com/yourusername/pulp-fiction-generator.git
cd pulp-fiction-generator
pip install -e .
```

This makes the `pulp-fiction` command available globally in your environment.

### Option 3: Executable Script

The repository includes a standalone executable script:

```bash
git clone https://github.com/yourusername/pulp-fiction-generator.git
cd pulp-fiction-generator
chmod +x pulp-fiction  # Make the script executable
./pulp-fiction --help
```

## Configuration with .env

The Pulp Fiction Generator uses environment variables for configuration, which can be set in a `.env` file:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_THREADS=8
OLLAMA_GPU_LAYERS=32
OLLAMA_CTX_SIZE=8192
OLLAMA_BATCH_SIZE=512
```

You can copy the `.env.example` file to `.env` and customize the values:

```bash
cp .env.example .env
nano .env  # Edit with your preferred settings
```

## Command Overview

The Pulp Fiction Generator CLI offers the following commands:

| Command | Description |
|---------|-------------|
| `generate` | Generate a new pulp fiction story |
| `interactive` | Launch an interactive guide to configure and generate stories |
| `setup-model` | Create an optimized model configuration for Ollama |
| `list-genres` | Display available genres |
| `list-plots` | Display available plot templates |
| `list-stories` | List all saved stories |
| `search-stories` | Search for stories by title or content |
| `check-model` | Check if a model is available and get its details |
| `check-consistency` | Check a story for character and plot consistency |

## General Usage

To see all available commands, use one of the following depending on your installation method:

### For Developer Installation:
```bash
python -m pulp_fiction_generator --help
```

### For Package Installation:
```bash
pulp-fiction --help
```

### For Executable Script:
```bash
./pulp-fiction --help
```

To get help on a specific command:

```bash
pulp-fiction COMMAND --help
```

## Detailed Command Usage

### Generate Stories

The `generate` command creates new pulp fiction stories:

```bash
pulp-fiction generate --genre noir --chapters 1
```

#### Options

- `--genre`, `-g`: Genre of the story (noir, sci-fi, adventure, etc.)
- `--chapters`, `-c`: Number of chapters to generate
- `--output`, `-o`: File to save the generated story to
- `--model`, `-m`: Ollama model to use (default: llama3.2)
- `--title`, `-t`: Title for the story (optional)
- `--save-state/--no-save-state`: Whether to save the story state (default: save)
- `--continue`, `-C`: Continue from an existing story file
- `--plot`, `-p`: Plot template to use
- `--verbose`, `-v`: Enable verbose output

#### Ollama Resource Configuration Options

- `--ollama-threads`: Number of CPU threads for Ollama to use (defaults to OLLAMA_THREADS in .env)
- `--ollama-gpu-layers`: Number of layers to run on GPU (defaults to OLLAMA_GPU_LAYERS in .env)
- `--ollama-ctx-size`: Context window size (defaults to OLLAMA_CTX_SIZE in .env)
- `--ollama-batch-size`: Batch size for processing tokens (defaults to OLLAMA_BATCH_SIZE in .env)

#### Examples

Generate a 2-chapter sci-fi story:
```bash
pulp-fiction generate --genre sci-fi --chapters 2 --title "Space Odyssey"
```

Continue a story from a saved file:
```bash
pulp-fiction generate --continue story_20240510_123456.json --chapters 1
```

Use a specific plot template:
```bash
pulp-fiction generate --genre adventure --plot three_act --chapters 1
```

Generate with increased resources for faster processing:
```bash
pulp-fiction generate --genre noir --chapters 1 --ollama-threads 8 --ollama-gpu-layers 42 --ollama-ctx-size 16384 --ollama-batch-size 1024
```

### Setup Optimized Model

The `setup-model` command creates an optimized model configuration for Ollama:

```bash
pulp-fiction setup-model --model llama3.2 --save-as llama3.2-fast
```

This command:
1. Creates a custom Modelfile with optimized parameters
2. Builds a new model with those parameters
3. Makes it available for use with the `generate` command

#### Options

- `--model`, `-m`: Base Ollama model to configure (default: llama3.2)  
- `--save-as`, `-s`: Name to save the configured model as (default: model-optimized)
- `--threads`: Number of CPU threads (default: from .env or 4)
- `--gpu-layers`: Number of layers to run on GPU (default: from .env or 0)
- `--ctx-size`: Context window size (default: from .env or 4096)
- `--batch-size`: Batch size for processing tokens (default: from .env or 256)
- `--verbose`, `-v`: Enable verbose output

#### Examples

Create a CPU-optimized model:
```bash
pulp-fiction setup-model --model llama3.2 --save-as llama3.2-cpu --threads 16
```

Create a GPU-optimized model:
```bash
pulp-fiction setup-model --model llama3.2 --save-as llama3.2-gpu --gpu-layers 42
```

Create a model optimized for long content:
```bash
pulp-fiction setup-model --model llama3.2 --save-as llama3.2-long --ctx-size 16384
```

### Interactive Mode

The interactive mode guides you through story generation with prompts:

```bash
pulp-fiction interactive
```

This mode will walk you through:
- Selecting a model
- Choosing a genre
- Selecting plot templates
- Setting the number of chapters
- Saving options
- Continuing existing stories

### Working with Stories

#### List All Stories

See all saved stories:

```bash
pulp-fiction list-stories
```

#### Search Stories

Find stories by title or content:

```bash
pulp-fiction search-stories "detective"
```

#### Check Consistency

Check a story for plot holes and character inconsistencies:

```bash
pulp-fiction check-consistency my_story_20240510_123456.json
```

Options:
- `--output`, `-o`: Save the consistency report to a file
- `--model`, `-m`: Model to use for AI-assisted checks
- `--ai-checks/--no-ai-checks`: Enable/disable AI-assisted checks

### Exploring Available Options

#### List Genres

View all available pulp fiction genres:

```bash
pulp-fiction list-genres
```

#### List Plot Templates

View all available plot templates:

```bash
pulp-fiction list-plots
```

#### Check Model

Verify if a model is available and see its details:

```bash
pulp-fiction check-model --model llama3.2
```

## Advanced Usage

### Output Formats

By default, stories are displayed in the terminal. To save to a file:

```bash
pulp-fiction generate --genre noir --chapters 1 --output my_story.md
```

### Continuing Stories

To continue a story:

1. First, find your saved story file:
```bash
pulp-fiction list-stories
```

2. Then continue it:
```bash
pulp-fiction generate --continue your_story_file.json --chapters 1
```

### Optimizing Performance

#### Creating Optimized Model Profiles

For the best performance, create an optimized model profile once using `setup-model`:

```bash
# Create an optimized model for your system
pulp-fiction setup-model --model llama3.2 --save-as llama3.2-optimized

# Then use this model for all your generations
pulp-fiction generate --model llama3.2-optimized --genre noir

# Make it the default by setting in .env
# OLLAMA_MODEL=llama3.2-optimized
```

This approach is preferred over specifying parameters for each generation because:
1. The model is loaded with optimal settings once
2. Subsequent generations use the optimized model directly
3. You can create different profiles for different needs (speed vs quality)

> **Note:** Ollama uses parameter names like `num_thread`, `num_gpu`, `num_ctx`, and `num_batch` internally. Our CLI simplifies this with more intuitive parameter names like `--threads`, `--gpu-layers`, `--ctx-size`, and `--batch-size`.

#### Ollama Resource Allocation

For one-off adjustments, you can configure Ollama's resource usage per command:

```bash
# Use more CPU threads
pulp-fiction generate --genre noir --chapters 1 --ollama-threads 8

# Increase GPU usage for faster generation
pulp-fiction generate --genre noir --chapters 1 --ollama-gpu-layers 42

# Increase context window for longer content understanding
pulp-fiction generate --genre noir --chapters 1 --ollama-ctx-size 16384

# Set larger batch size for faster processing
pulp-fiction generate --genre noir --chapters 1 --ollama-batch-size 1024

# Combine multiple settings
pulp-fiction generate --genre noir --chapters 1 --ollama-threads 8 --ollama-gpu-layers 42 --ollama-ctx-size 16384
```

Different models and hardware will benefit from different settings:
- For CPU-heavy systems, increase `--ollama-threads`
- For GPU-heavy systems, increase `--ollama-gpu-layers`
- For systems with lots of RAM, increase `--ollama-ctx-size` and `--ollama-batch-size`

### Shell Completion

Install shell completion for a better command-line experience:

```bash
pulp-fiction --install-completion
```

This will add tab completion for commands and options in your shell.

### Performance Tips

- For faster generation, use smaller models:
```bash
pulp-fiction generate --model llama3.2 --genre noir --chapters 1
```

- Set verbose mode for detailed progress:
```bash
pulp-fiction generate --genre sci-fi --chapters 1 --verbose
```

## Troubleshooting

If you encounter issues:

1. Ensure Ollama is running with: `ollama serve`
2. Make sure the model is pulled: `ollama pull llama3.2`
3. Check model availability: `pulp-fiction check-model`
4. Use verbose mode to see more details: add `--verbose` to any command 