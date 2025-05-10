"""
Registry for available genres in the pulp fiction generator.
"""

import importlib
import os
from typing import Dict, List, Optional, Type

from .base import GenreDefinition
from .noir import NoirGenre
from .scifi import SciFiGenre
from .adventure import AdventureGenre


class GenreRegistry:
    """
    Registry for managing available genres.
    
    This class maintains a registry of available genres and provides methods
    for accessing and managing them.
    """
    
    def __init__(self):
        """Initialize the genre registry with built-in genres."""
        self._genres: Dict[str, Type[GenreDefinition]] = {}
        self._instances: Dict[str, GenreDefinition] = {}
        
        # Register built-in genres
        self.register_genre("noir", NoirGenre)
        self.register_genre("sci-fi", SciFiGenre)
        self.register_genre("adventure", AdventureGenre)
        
        # TODO: Register additional genres as they are implemented
        
    def register_genre(self, genre_name: str, genre_class: Type[GenreDefinition]) -> None:
        """
        Register a genre with the registry.
        
        Args:
            genre_name: The name of the genre
            genre_class: The genre class
        """
        self._genres[genre_name] = genre_class
        
    def get_genre(self, genre_name: str) -> GenreDefinition:
        """
        Get a genre instance by name.
        
        Args:
            genre_name: The name of the genre to get
            
        Returns:
            An instance of the requested genre
            
        Raises:
            ValueError: If the genre is not found
        """
        if genre_name not in self._genres:
            raise ValueError(f"Unknown genre: {genre_name}")
        
        # Create an instance if one doesn't exist
        if genre_name not in self._instances:
            self._instances[genre_name] = self._genres[genre_name]()
            
        return self._instances[genre_name]
    
    def list_genres(self) -> List[Dict[str, str]]:
        """
        List all available genres.
        
        Returns:
            A list of dictionaries with name, display_name, and description
        """
        result = []
        
        for genre_name in self._genres:
            genre = self.get_genre(genre_name)
            result.append({
                "name": genre.name,
                "display_name": genre.display_name,
                "description": genre.description
            })
            
        return result
    
    def has_genre(self, genre_name: str) -> bool:
        """
        Check if a genre exists in the registry.
        
        Args:
            genre_name: The name of the genre to check
            
        Returns:
            True if the genre exists, False otherwise
        """
        return genre_name in self._genres
    
    def discover_genres(self, genres_dir: Optional[str] = None) -> None:
        """
        Discover and register genres from a directory.
        
        This method looks for Python modules in the specified directory
        and registers any GenreDefinition subclasses found.
        
        Args:
            genres_dir: Directory to look for genre modules, or None to use
                        the package's genres directory
        """
        if not genres_dir:
            # Use the package's genres directory
            genres_dir = os.path.dirname(__file__)
            
        # Get all Python files in the directory
        for filename in os.listdir(genres_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py" and filename != "registry.py":
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module
                    module_path = f"pulp_fiction_generator.genres.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # Look for GenreDefinition subclasses
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (isinstance(obj, type) and 
                            issubclass(obj, GenreDefinition) and
                            obj != GenreDefinition):
                            # Create an instance to get its name
                            instance = obj()
                            self.register_genre(instance.name, obj)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading genre module {module_name}: {e}")
                    

# Create a singleton instance
genre_registry = GenreRegistry() 