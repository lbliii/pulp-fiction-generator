# System Architecture

## Overview

The Pulp Fiction Generator uses a modular, agent-based architecture built on CrewAI to create compelling serialized fiction. The system is designed to be:

1. **Modular**: Components can be developed and replaced independently
2. **Extensible**: New genres, agents, or capabilities can be added easily
3. **Efficient**: Optimized to work well with local LLM deployments

## High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  User Interface │────▶│ Crew Coordinator │────▶│ Agent Factory  │
└─────────────────┘     └──────────────────┘     └────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌──────────────────┐     ┌────────────────┐
                        │     Agents       │◀───▶│ Model Service  │
                        └──────────────────┘     └────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌──────────────────┐     ┌────────────────┐
                        │ Genre Library    │     │ Ollama/Llama   │
                        └──────────────────┘     └────────────────┘
                                │                        
                                ▼                        
                        ┌──────────────────┐     
                        │ Story Repository │     
                        └──────────────────┘     
```

## Core Components

### User Interface
Simple CLI or web interface for interacting with the system, setting parameters, and viewing generated content.

### Crew Coordinator
Orchestrates the workflow between agents, manages the state of story generation, and ensures proper sequencing of agent activities.

### Agent Factory
Creates and configures specialized agents based on story requirements, genre, and user preferences.

### Agents
Specialized AI agents that fulfill different roles in the story creation process:
- **Researcher**: Gathers relevant information and reference material
- **Worldbuilder**: Creates the setting, background, and rules for the story world
- **Character Creator**: Designs compelling, consistent characters
- **Plotter**: Develops narrative arcs and plot points
- **Writer**: Generates the actual prose of the story
- **Editor**: Polishes, refines, and ensures consistency

### Model Service
Abstracts the interaction with the underlying LLM, handling prompt formatting, context management, and response parsing.

### Genre Library
Contains genre-specific templates, tropes, styles, and examples that inform the generation process.

### Story Repository
Persists generated stories, metadata, and state information to enable serialized storytelling across sessions.

### Ollama/Llama Integration
Low-level integration with Ollama running Llama 3.2, optimizing performance for local deployment.

## Design Patterns

### Factory Pattern
Used in the Agent Factory to create the appropriate agents based on configuration.

### Strategy Pattern
Applied to allow different generation strategies based on genre and style.

### Observer Pattern
Implemented to allow monitoring of the generation process and state changes.

### Facade Pattern
Encapsulates the complexity of the agent system behind a simpler interface.

### Repository Pattern
Used for story persistence and retrieval.

## Data Flow

1. **User Configuration**: User selects genre, parameters, and generation goals
2. **Crew Assembly**: Coordinator assembles the appropriate agent crew via the Agent Factory
3. **Research Phase**: Research agents gather relevant information for the story
4. **World & Character Creation**: World and character agents establish the story foundation
5. **Plot Development**: Plot agents create the narrative structure
6. **Writing**: Writer agents generate the actual prose
7. **Editing**: Editor agents refine and polish the content
8. **Storage**: The completed story segment is saved to the repository
9. **Continuation**: For serialized stories, state is maintained for future continuation

## Technical Considerations

### Memory Management
Careful attention to context window limitations of Llama 3.2, with strategies for long-context handling.

### Prompt Engineering
Specialized prompts for each agent role to maximize the quality of generation within the limitations of the model.

### Error Handling
Graceful degradation strategies when model responses don't meet expectations.

### Serialization
Efficient state serialization to maintain story consistency across sessions. 