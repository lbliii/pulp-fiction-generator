# Technical Stack

## Overview

The Pulp Fiction Generator is built on modern, efficient technologies selected to achieve both high performance and ease of development. The stack is optimized for local deployment with Ollama/Llama 3.2, while maintaining flexibility for future enhancements.

## Core Technologies

### Python

**Version**: 3.10+ (3.12 recommended)

Python serves as the primary programming language for the system due to its:
- Rich ecosystem for AI/ML applications
- Excellent support for agent-based systems
- Extensive libraries for natural language processing
- Strong integration capabilities with various APIs

### CrewAI

**Version**: 0.119.0+

CrewAI provides the foundation for the agent-based architecture:
- Framework for orchestrating role-playing autonomous AI agents
- Support for collaborative intelligence between agents
- Built-in agent management and communication
- Sequential and hierarchical process support

Key CrewAI components utilized:
- `Agent` class for implementing specialized agents
- `Task` class for defining agent operations
- `Crew` class for coordinating agent interactions
- `Process` enums for defining execution strategies

### Ollama

**Version**: Latest

Ollama enables local deployment of LLMs:
- Simple API for model interaction
- Local model hosting and management
- Low-latency model inference
- Cross-platform support (Linux, macOS, Windows)

### Llama 3.2

Llama 3.2 is the primary language model:
- Open-source foundation model from Meta
- Strong performance in creative text generation
- Reasonable context window (up to 8K tokens)
- Available in various sizes (we use 3B version by default)

## Dependencies Management

### UV

**Version**: Latest

UV is used for package management and virtual environment creation:
- Fast dependency resolution and installation
- Enhanced caching for faster builds
- Compatible with standard Python packaging
- Support for lockfiles to ensure consistent environments

Key UV commands used:
- `uv venv` for creating virtual environments
- `uv pip install` for installing dependencies
- `uv pip sync` for synchronizing from requirements files

## Additional Libraries

### FastAPI (Optional)

**Version**: 0.104.0+

FastAPI can be used for providing a REST API when needed:
- High-performance asynchronous API framework
- Auto-generated OpenAPI documentation
- Type checking and validation
- Efficient concurrency with asynchronous request handling

### SQLModel (Optional)

**Version**: 0.0.8+

SQLModel for data persistence when needed:
- Combines SQLAlchemy Core and Pydantic
- Type-checked database models
- ORM capabilities with strong typing
- Seamless integration with FastAPI

### Rich

**Version**: 13.6.0+

Rich for enhanced terminal output:
- Colorful, formatted console output
- Progress bars for long-running operations
- Tables for structured data display
- Markdown rendering in terminal

### Markdown

**Version**: 3.5+

Markdown for content generation and formatting:
- Lightweight markup for generated content
- Easy conversion to various output formats
- Human-readable source format
- Widely supported in documentation systems

## Development Tools

### Pytest

**Version**: 7.4.0+

Pytest for testing:
- Comprehensive testing framework
- Fixture support for test setup/teardown
- Parameterized testing capabilities
- Integration with coverage tools

### Ruff

**Version**: 0.1.2+

Ruff for code linting and formatting:
- Extremely fast Python linter
- Comprehensive rule set
- Auto-fixing capabilities
- Configurable enforcement levels

### Pre-commit

**Version**: 3.5.0+

Pre-commit for git hooks:
- Enforces code quality checks before commit
- Ensures consistent code formatting
- Prevents accidental commits of sensitive data
- Runs tests to catch issues early

## Deployment and Execution

### Docker (Optional)

**Version**: Latest

Docker for containerized deployment when needed:
- Consistent execution environment
- Isolation of dependencies
- Simplified deployment process
- Scalability options

### CLI

A custom command-line interface for the generator:
- Simple parameter passing
- Progress reporting
- Output formatting
- Configuration management

## System Requirements

### Minimum Requirements

- **CPU**: 4 cores
- **RAM**: 8GB (4GB for application, 4GB for model)
- **Storage**: 5GB free space
- **OS**: Any modern Linux, macOS, or Windows version

### Recommended Requirements

- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 20GB+ SSD
- **GPU**: Not required but beneficial for faster inference
- **OS**: Ubuntu 22.04+, macOS 12+, or Windows 11

## Extensibility

The technical stack is designed to be extensible:

1. **Model Flexibility**: The `ModelService` abstraction allows integration with different LLMs beyond Llama 3.2
2. **Persistence Options**: Multiple storage backends can be supported through the Repository abstraction
3. **API Integrations**: The system can be extended to use external services for research or reference
4. **Frontend Options**: The core system can be integrated with various UIs (CLI, web, desktop)

## Future Considerations

While the current stack is optimized for local deployment with open-source components, the architecture allows for future enhancements:

1. **Cloud Deployment**: The system can be adapted for cloud deployment with minimal changes
2. **Alternative Models**: Support for other models like Mistral, Phi-3, or vendor APIs
3. **Distributed Processing**: Agent tasks could be distributed across multiple processes or machines
4. **Web UI**: A browser-based interface could be added for easier interaction 