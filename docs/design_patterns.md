# Design Patterns

The Pulp Fiction Generator employs several established design patterns to ensure a maintainable, extensible, and robust architecture. This document outlines the key patterns used and how they're applied in the system.

## Creational Patterns

### Factory Pattern

The Factory Pattern is used extensively to create agents and tools without exposing the instantiation logic to the client code.

**Implementation**: `AgentFactory` creates specialized agents based on genre and configuration.

```python
class AgentFactory:
    def create_agent(self, agent_type, genre, config=None):
        """
        Create an agent of the specified type for the given genre
        """
        if agent_type == "researcher":
            return self._create_researcher_agent(genre, config)
        elif agent_type == "worldbuilder":
            return self._create_worldbuilder_agent(genre, config)
        # ...other agent types
```

**Benefits**:
- Centralizes agent creation logic
- Encapsulates configuration details
- Makes adding new agent types easier

### Builder Pattern

The Builder Pattern separates the construction of complex objects from their representation.

**Implementation**: `StoryBuilder` constructs a complete story through a step-by-step process.

```python
class StoryBuilder:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self._story = Story()
        
    def set_genre(self, genre):
        self._story.genre = genre
        return self
        
    def set_characters(self, characters):
        self._story.characters = characters
        return self
        
    # Additional building steps...
        
    def build(self):
        result = self._story
        self.reset()
        return result
```

**Benefits**:
- Allows step-by-step construction of complex story objects
- Makes the construction process explicit and controllable

## Structural Patterns

### Facade Pattern

The Facade Pattern provides a simplified interface to a complex subsystem.

**Implementation**: `StoryGenerator` provides a simple interface for the entire story generation process.

```python
class StoryGenerator:
    def __init__(self, model_service, genre_library):
        self.model_service = model_service
        self.genre_library = genre_library
        self.agent_factory = AgentFactory()
        # ...other subsystems
        
    def generate_story(self, genre, length, parameters=None):
        """
        Generate a pulp fiction story with the specified parameters
        """
        # Internal complexity hidden from client
        crew = self._assemble_crew(genre, parameters)
        return crew.kickoff()
```

**Benefits**:
- Hides complexity of the multi-agent system
- Provides a clean, simple interface for clients
- Decouples client code from subsystem implementations

### Adapter Pattern

The Adapter Pattern allows classes with incompatible interfaces to work together.

**Implementation**: `OllamaAdapter` adapts the Ollama API to the common `ModelService` interface used by the system.

```python
class ModelService(ABC):
    @abstractmethod
    def generate(self, prompt, parameters=None):
        pass
        
class OllamaAdapter(ModelService):
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        
    def generate(self, prompt, parameters=None):
        """
        Adapt Ollama API to the ModelService interface
        """
        # Convert parameters to Ollama format
        ollama_params = self._convert_parameters(parameters)
        
        # Call Ollama API
        response = self._call_ollama_api(prompt, ollama_params)
        
        # Convert response to standard format
        return self._convert_response(response)
```

**Benefits**:
- Allows integration with different LLM backends without changing client code
- Encapsulates the specifics of the Ollama API
- Enables easy switching between model providers

## Behavioral Patterns

### Strategy Pattern

The Strategy Pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Implementation**: Different generation strategies can be selected based on genre and requirements.

```python
class GenerationStrategy(ABC):
    @abstractmethod
    def generate_plot(self, world, characters, requirements):
        pass
        
class NoirGenerationStrategy(GenerationStrategy):
    def generate_plot(self, world, characters, requirements):
        # Noir-specific plot generation logic
        pass
        
class SciFiGenerationStrategy(GenerationStrategy):
    def generate_plot(self, world, characters, requirements):
        # Sci-fi-specific plot generation logic
        pass
```

**Benefits**:
- Encapsulates genre-specific generation algorithms
- Allows runtime selection of appropriate strategy
- Facilitates adding new genre strategies

### Observer Pattern

The Observer Pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified.

**Implementation**: `StoryGenerationObserver` monitors the generation process and notifies subscribers of progress and events.

```python
class StoryGenerationObserver:
    def __init__(self):
        self._subscribers = []
        
    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)
        
    def unsubscribe(self, subscriber):
        self._subscribers.remove(subscriber)
        
    def notify(self, event_type, data=None):
        for subscriber in self._subscribers:
            subscriber.update(event_type, data)
```

**Benefits**:
- Allows loose coupling between generation process and UI/logging
- Enables real-time monitoring and feedback
- Simplifies adding new monitoring features

### Command Pattern

The Command Pattern encapsulates a request as an object, allowing parameterization of clients with different requests.

**Implementation**: `Task` objects represent operations that agents can perform.

```python
class Task:
    def __init__(self, description, agent, expected_output, context=None):
        self.description = description
        self.agent = agent
        self.expected_output = expected_output
        self.context = context or {}
        
    def execute(self):
        return self.agent.execute(self)
```

**Benefits**:
- Enables queuing and scheduling of agent tasks
- Provides a common interface for different operations
- Facilitates undo/retry functionality

## Architectural Patterns

### Repository Pattern

The Repository Pattern isolates data access logic and maps data between persistence and domain layers.

**Implementation**: `StoryRepository` handles story persistence and retrieval.

```python
class StoryRepository:
    def __init__(self, storage_provider):
        self.storage = storage_provider
        
    def save(self, story):
        """Save a story to storage"""
        serialized = self._serialize(story)
        self.storage.write(story.id, serialized)
        
    def get_by_id(self, story_id):
        """Retrieve a story by ID"""
        serialized = self.storage.read(story_id)
        return self._deserialize(serialized)
        
    def list(self, filters=None):
        """List stories matching filters"""
        # Implementation...
```

**Benefits**:
- Centralizes data access logic
- Abstracts storage implementation details
- Simplifies testing by allowing mock storage providers

### Dependency Injection

While not strictly a design pattern, Dependency Injection is used throughout the system to promote loose coupling and testability.

**Implementation**: Dependencies are provided to components rather than created internally.

```python
# Constructor injection
class CrewCoordinator:
    def __init__(self, agent_factory, model_service, story_repository):
        self.agent_factory = agent_factory
        self.model_service = model_service
        self.story_repository = story_repository
        
# Method injection
def generate_chapter(chapter_outline, world_context, model_service=None):
    model_service = model_service or get_default_model_service()
    # Implementation...
```

**Benefits**:
- Promotes loose coupling between components
- Simplifies unit testing through mock objects
- Enhances flexibility by allowing component substitution

## Application of Patterns

These design patterns are applied thoughtfully, not indiscriminately. The focus is on solving actual design problems rather than forcing patterns where they're not needed. Each pattern is selected based on its applicability to the specific problem at hand and the benefits it provides to the overall architecture. 