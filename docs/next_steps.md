# Next Steps for Pulp Fiction Generator

This document outlines the specific tasks, approaches, and priorities for the immediate next steps in developing the Pulp Fiction Generator. It serves as a more detailed companion to the implementation plan.

## 1. Genre System Implementation

The genre system is a core component that needs to be completed to move forward with high-quality generation.

### Tasks

1. **Create GenreDefinition Interface**: 
   ```python
   class GenreDefinition(ABC):
       @property
       @abstractmethod
       def name(self) -> str:
           """Return the internal name of the genre"""
           pass
           
       @property
       @abstractmethod
       def display_name(self) -> str:
           """Return the display name of the genre"""
           pass
           
       @abstractmethod
       def get_researcher_prompt_enhancer(self) -> str:
           """Return the prompt enhancer for the researcher agent"""
           pass
           
       # Additional methods for other agents...
       
       @abstractmethod
       def get_character_templates(self) -> List[Dict[str, Any]]:
           """Return character templates for this genre"""
           pass
   ```

2. **Implement Noir Genre**:
   - Complete implementation of the NoirGenre class
   - Create character templates
   - Develop specialized prompts for each agent
   - Add example passages and tropes

3. **Implement Sci-Fi Genre**:
   - Complete implementation of the SciFiGenre class
   - Create character templates
   - Develop specialized prompts for each agent
   - Add example passages and tropes

4. **Create GenreRegistry**:
   - Implement a registry for discovering and loading genres
   - Add configuration for enabling/disabling genres
   - Create documentation for adding new genres

### Approach

1. Start with the core interfaces in `pulp_fiction_generator/genres/base.py`
2. Implement concrete classes in separate files (e.g., `noir.py`, `scifi.py`)
3. Create a registry mechanism in `pulp_fiction_generator/genres/registry.py`
4. Add tests for each genre to ensure they work as expected

## 2. Testing Framework Enhancement

A robust testing framework is essential for maintaining quality as the project grows.

### Tasks

1. **Set Up Unit Testing**:
   - Create tests for ModelService and OllamaAdapter
   - Implement tests for AgentFactory
   - Add tests for CrewCoordinator
   - Create mocks for external services

2. **Implement Integration Testing**:
   - Create end-to-end tests for story generation
   - Add tests for genre implementation
   - Implement tests for serialization/deserialization
   - Test CLI functionality

3. **Add CI/CD Pipeline**:
   - Configure GitHub Actions or similar CI/CD service
   - Implement automated testing on pull requests
   - Add code coverage reporting
   - Create linting and formatting checks

### Approach

1. Use pytest for all testing needs
2. Create mocks to avoid real LLM calls in tests
3. Implement fixtures for common test scenarios
4. Add regression tests for any bugs found

## 3. Prompt Engineering

Improving the prompts is crucial for generating high-quality stories.

### Tasks

1. **Create Prompt Template System**:
   ```python
   class PromptTemplate:
       def __init__(self, template: str, variables: Optional[Dict[str, str]] = None):
           self.template = template
           self.variables = variables or {}
           
       def render(self, context: Dict[str, Any]) -> str:
           """Render the template with the provided context"""
           template = self.template
           for key, value in {**self.variables, **context}.items():
               template = template.replace(f"{{{{{key}}}}}", str(value))
           return template
   ```

2. **Create Genre-Specific Prompts**:
   - Develop specialized prompts for each agent in each genre
   - Add examples and guidance to prompts
   - Create a prompt library for reuse

3. **Implement Prompt Testing**:
   - Create a mechanism to test prompt effectiveness
   - Add metrics for evaluating prompt quality
   - Implement A/B testing for prompt variations

### Approach

1. Start with a simple template system in `pulp_fiction_generator/prompts/templates.py`
2. Create a prompt library in `pulp_fiction_generator/prompts/library.py`
3. Add genre-specific prompts in `pulp_fiction_generator/prompts/genres/`
4. Implement prompt testing tools in `pulp_fiction_generator/prompts/testing.py`

## 4. Story Persistence

Implementing story persistence is essential for serialized storytelling.

### Tasks

1. **Design Serialization Format**:
   ```json
   {
     "metadata": {
       "title": "The Shadow's Edge",
       "genre": "noir",
       "created_at": "2025-01-01T00:00:00Z",
       "updated_at": "2025-01-02T00:00:00Z",
       "version": "1.0"
     },
     "content": {
       "chapters": [
         {
           "number": 1,
           "title": "Into the Darkness",
           "content": "It was a cold night in the city...",
           "created_at": "2025-01-01T00:00:00Z"
         }
       ]
     },
     "world": {
       "setting": "Los Angeles, 1940s",
       "locations": [
         {
           "name": "Marlowe's Office",
           "description": "A small, dusty office..."
         }
       ]
     },
     "characters": [
       {
         "name": "Philip Marlowe",
         "role": "protagonist",
         "description": "Hard-boiled detective...",
         "traits": ["cynical", "determined", "intelligent"]
       }
     ],
     "plot": {
       "synopsis": "A detective investigates...",
       "arcs": [
         {
           "description": "Marlowe discovers...",
           "status": "completed"
         }
       ]
     },
     "state": {
       "current_chapter": 1,
       "plot_points_revealed": ["murder", "betrayal"],
       "character_knowledge": {
         "Marlowe": ["knows about the murder", "suspects the wife"]
       }
     }
   }
   ```

2. **Implement Story Repository**:
   - Create a repository interface
   - Implement file-based storage
   - Add metadata management
   - Implement search capabilities

3. **Add Save/Load Functionality**:
   - Implement save functionality in CLI
   - Add load and continue options
   - Create automatic backups
   - Add export capabilities

### Approach

1. Start with the story model in `pulp_fiction_generator/models/story.py`
2. Implement serialization in `pulp_fiction_generator/utils/serialization.py`
3. Create the repository in `pulp_fiction_generator/repositories/story_repository.py`
4. Add CLI commands for save/load in `pulp_fiction_generator/__main__.py`

## 5. Performance Optimization

Optimizing performance is essential for a good user experience, especially with local LLMs.

### Tasks

1. **Profile Current Performance**:
   - Measure token usage for different operations
   - Time the execution of various components
   - Identify bottlenecks in the generation process

2. **Implement Caching**:
   - Add response caching for common queries
   - Implement disk-based cache for persistence
   - Create cache invalidation strategies

3. **Optimize Prompts**:
   - Reduce token usage in prompts
   - Implement better context management
   - Add streaming support for real-time output

### Approach

1. Create profiling tools in `pulp_fiction_generator/utils/profiling.py`
2. Implement caching in `pulp_fiction_generator/utils/caching.py`
3. Optimize prompts based on profiling data
4. Add async support for non-blocking operations

## Timeline and Priorities

### Week 1-2: Genre System Implementation
- Focus on completing the Genre interface and first two genres
- Integrate genre system with existing components
- Create tests for the genre system

### Week 3-4: Testing and Prompt Engineering
- Enhance test coverage across the system
- Implement prompt template system
- Create genre-specific prompts
- Set up CI/CD pipeline

### Week 5-6: Story Persistence and Performance
- Implement story serialization format
- Create Story Repository
- Add save/load functionality to CLI
- Profile and optimize performance
- Implement caching system

## Success Metrics

We'll measure success for these next steps by:

1. **Functionality**: Can the system generate stories in at least two genres?
2. **Quality**: Are the generated stories coherent and genre-appropriate?
3. **Persistence**: Can stories be saved and continued across sessions?
4. **Performance**: Is generation time acceptable (< 5 minutes per chapter)?
5. **Test Coverage**: Is the codebase well-tested with > 80% coverage?

## Resources and References

1. **Genre Research**:
   - [Pulp Fiction Archive](https://pulparchive.com/)
   - [Noir Fiction Elements](https://writing-the-craft.tumblr.com/post/25487940626/writing-noir-fiction-the-basics)
   - [Science Fiction Tropes](https://tvtropes.org/pmwiki/pmwiki.php/Main/ScienceFictionTropes)

2. **LLM Optimization**:
   - [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
   - [Prompt Engineering Guide](https://www.promptingguide.ai/)
   - [Token Optimization Techniques](https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/guides/prompts-advanced-usage.md)

3. **Testing Resources**:
   - [Pytest Documentation](https://docs.pytest.org/)
   - [Mocking LLM APIs](https://docs.pytest.org/en/latest/how-to/monkeypatch.html)
   - [Testing Async Code](https://pytest-asyncio.readthedocs.io/en/latest/) 