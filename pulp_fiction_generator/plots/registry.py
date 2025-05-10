"""
Registry for plot templates and structures.
"""

import importlib
import os
from typing import Dict, List, Optional, Type, Any

from .base import PlotTemplate, PlotStructure, NarrativeArc


class PlotRegistry:
    """
    Registry for managing available plot templates and structures.
    
    This class maintains a registry of available plot templates and provides methods
    for accessing and managing them.
    """
    
    def __init__(self):
        """Initialize the plot registry."""
        self._templates: Dict[str, Type[PlotTemplate]] = {}
        self._instances: Dict[str, PlotTemplate] = {}
        
    def register_template(self, template_name: str, template_class: Type[PlotTemplate]) -> None:
        """
        Register a plot template with the registry.
        
        Args:
            template_name: The name of the template
            template_class: The template class
        """
        self._templates[template_name] = template_class
        
    def get_template(self, template_name: str) -> PlotTemplate:
        """
        Get a plot template instance by name.
        
        Args:
            template_name: The name of the template to get
            
        Returns:
            An instance of the requested template
            
        Raises:
            ValueError: If the template is not found
        """
        if template_name not in self._templates:
            raise ValueError(f"Unknown plot template: {template_name}")
        
        # Create an instance if one doesn't exist
        if template_name not in self._instances:
            self._instances[template_name] = self._templates[template_name]()
            
        return self._instances[template_name]
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available plot templates.
        
        Returns:
            A list of dictionaries with name, description, and narrative_arc
        """
        result = []
        
        for template_name in self._templates:
            template = self.get_template(template_name)
            result.append({
                "name": template.name,
                "description": template.description,
                "narrative_arc": template.narrative_arc.value if template.narrative_arc else None
            })
            
        return result
    
    def get_templates_for_genre(self, genre_name: str, threshold: float = 0.5) -> List[PlotTemplate]:
        """
        Get plot templates suitable for a particular genre.
        
        Args:
            genre_name: The name of the genre
            threshold: Minimum compatibility score (0.0-1.0)
            
        Returns:
            List of plot templates compatible with the genre
        """
        result = []
        
        for template_name in self._templates:
            template = self.get_template(template_name)
            genre_scores = template.get_suitable_genres()
            
            if genre_name in genre_scores and genre_scores[genre_name] >= threshold:
                result.append(template)
            
        return result
    
    def has_template(self, template_name: str) -> bool:
        """
        Check if a template exists in the registry.
        
        Args:
            template_name: The name of the template to check
            
        Returns:
            True if the template exists, False otherwise
        """
        return template_name in self._templates
    
    def discover_templates(self, templates_dir: Optional[str] = None) -> None:
        """
        Discover and register plot templates from a directory.
        
        This method looks for Python modules in the specified directory
        and registers any PlotTemplate subclasses found.
        
        Args:
            templates_dir: Directory to look for template modules, or None to use
                          the package's plots directory
        """
        if not templates_dir:
            # Use the package's plots directory
            templates_dir = os.path.dirname(__file__)
            
        # Get all Python files in the directory
        for filename in os.listdir(templates_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py" and filename != "registry.py":
                module_name = filename[:-3]  # Remove .py extension
                try:
                    # Import the module
                    module_path = f"pulp_fiction_generator.plots.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # Look for PlotTemplate subclasses
                    for name in dir(module):
                        obj = getattr(module, name)
                        if (isinstance(obj, type) and 
                            issubclass(obj, PlotTemplate) and
                            obj != PlotTemplate):
                            # Create an instance to get its name
                            instance = obj()
                            self.register_template(instance.name, obj)
                except (ImportError, AttributeError) as e:
                    print(f"Error loading plot template module {module_name}: {e}")


# Create a singleton instance
plot_registry = PlotRegistry() 