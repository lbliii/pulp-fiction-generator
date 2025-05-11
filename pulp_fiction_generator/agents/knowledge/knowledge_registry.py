"""
Registry for agent knowledge sources.
"""

from typing import Any, Callable, Dict, Optional, Type


class KnowledgeRegistry:
    """
    Registry for agent knowledge sources.
    
    This class maintains a registry of available knowledge sources that can be used by agents.
    """
    
    def __init__(self):
        """Initialize the knowledge source registry."""
        self._sources: Dict[str, Type[Any]] = {}
        self._factories: Dict[str, Callable[..., Any]] = {}
        
    def register_source(self, name: str, source_class: Type[Any]) -> None:
        """
        Register a knowledge source class with the registry.
        
        Args:
            name: Name of the knowledge source
            source_class: Class of the knowledge source
        """
        self._sources[name] = source_class
        
    def register_source_factory(self, name: str, factory: Callable[..., Any]) -> None:
        """
        Register a knowledge source factory function with the registry.
        
        Args:
            name: Name of the knowledge source
            factory: Factory function for creating knowledge source instances
        """
        self._factories[name] = factory
        
    def get_source_class(self, name: str) -> Optional[Type[Any]]:
        """
        Get a knowledge source class by name.
        
        Args:
            name: Name of the knowledge source
            
        Returns:
            Knowledge source class if found, None otherwise
        """
        return self._sources.get(name)
        
    def get_source_factory(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Get a knowledge source factory function by name.
        
        Args:
            name: Name of the knowledge source
            
        Returns:
            Knowledge source factory function if found, None otherwise
        """
        return self._factories.get(name)
        
    def create_source(self, name: str, **kwargs) -> Any:
        """
        Create a knowledge source instance by name.
        
        Args:
            name: Name of the knowledge source
            **kwargs: Arguments to pass to the knowledge source constructor or factory
            
        Returns:
            Knowledge source instance
            
        Raises:
            ValueError: If the knowledge source is not registered
        """
        factory = self.get_source_factory(name)
        if factory:
            return factory(**kwargs)
            
        source_class = self.get_source_class(name)
        if source_class:
            return source_class(**kwargs)
            
        raise ValueError(f"Knowledge source '{name}' is not registered")
        
    def list_sources(self) -> Dict[str, str]:
        """
        List all registered knowledge sources.
        
        Returns:
            Dictionary mapping knowledge source names to their descriptions
        """
        sources = {}
        
        for name, source_class in self._sources.items():
            sources[name] = source_class.__doc__ or "No description available"
            
        for name, factory in self._factories.items():
            sources[name] = factory.__doc__ or "No description available"
            
        return sources


# Create a singleton instance
registry = KnowledgeRegistry() 