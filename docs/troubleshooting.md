# Troubleshooting Guide

This document provides solutions for common issues encountered when working with the Pulp Fiction Generator.

## Table of Contents

1. [CrewAI Task Execution Issues](#crewai-task-execution-issues)
2. [Performance Optimization](#performance-optimization)
3. [Model Setup and Configuration](#model-setup-and-configuration)

## CrewAI Task Execution Issues

### Problem: Tasks Failing with "Task has no execute method" or "LiteLLM Provider NOT provided"

Recent versions of CrewAI use LiteLLM as a backend for handling model interactions. This can cause issues with our custom OllamaAdapter since LiteLLM expects model names to include a provider prefix.

#### Symptoms:
- Tasks fail with errors like `'Task' object has no attribute 'execute'`
- Or: `LiteLLM Provider NOT provided. Pass in the LLM provider you are trying to call`
- Models that work directly fail when used in CrewAI tasks

#### Solution:
We implemented a compatibility adapter called `CrewAIModelAdapter` that wraps our OllamaAdapter and makes it compatible with CrewAI's expectations:

1. The adapter is in `pulp_fiction_generator/models/crewai_adapter.py`
2. It formats the model name in the way LiteLLM expects (with the provider prefix)
3. It provides a compatible interface that CrewAI can work with

#### Usage:

```python
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
from pulp_fiction_generator.models.crewai_adapter import CrewAIModelAdapter

# Create the OllamaAdapter
ollama_adapter = OllamaAdapter(
    model_name="llama3.2",
    api_base="http://localhost:11434"
)

# Create the CrewAIModelAdapter wrapper
crewai_adapter = CrewAIModelAdapter(
    ollama_adapter=ollama_adapter
)

# Use the wrapped adapter in CrewAI
from crewai import Agent
agent = Agent(
    role="Researcher",
    goal="Research a topic",
    backstory="I am a researcher",
    llm=crewai_adapter  # Pass the wrapped adapter
)
```

#### Technical Details:

The `CrewAIModelAdapter` handles:
1. Formatting model names with the provider prefix (e.g., "ollama/llama3.2")
2. Converting between CrewAI's expected message format and OllamaAdapter's interface
3. Formatting responses in the way CrewAI and LiteLLM expect

## Performance Optimization

### Problem: High CPU/Memory Usage

If you're experiencing high CPU or memory usage during generation, this may be due to model configuration issues.

#### Solution:

1. Use environment variables to control Ollama resources:
   - `OLLAMA_THREADS`: Number of CPU threads (default: 4)
   - `OLLAMA_GPU_LAYERS`: Number of layers to offload to GPU (default: 0)
   - `OLLAMA_CTX_SIZE`: Context window size (default: 4096)
   - `OLLAMA_BATCH_SIZE`: Batch size for processing (default: 256)

2. Alternatively, use the `setup-model` command to create an optimized version:
   ```
   ./pulp-fiction setup-model -m llama3.2 --threads 8 --gpu-layers 32
   ```

## Model Setup and Configuration

### Problem: Model Not Found

If you're seeing errors about models not being found, make sure you've pulled the model properly with Ollama.

#### Solution:

1. List available models:
   ```
   ollama list
   ```

2. Pull a model if not available:
   ```
   ollama pull llama3
   ```

3. Use the exact model name including tags:
   ```
   ./pulp-fiction generate -m llama3.2:latest -g noir
   ```

### Problem: Connection to Ollama Failed

If you can't connect to Ollama, make sure the service is running.

#### Solution:

1. Start the Ollama service:
   ```
   ollama serve
   ```

2. Set a custom Ollama host if needed:
   ```
   export OLLAMA_HOST="http://localhost:11434"
   ```

3. Run the health check to verify everything is working:
   ```
   ./pulp-fiction health-check
   ``` 