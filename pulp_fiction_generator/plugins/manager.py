"""
Plugin Manager for the Pulp Fiction Generator.

This module provides functionality for discovering, loading, and managing plugins
from various sources including:
1. User-specific plugin directories (~/.pulp-fiction/plugins/)
2. Project-local plugin directories (./plugins/)
3. Installed Python packages with the prefix 'pulp-fiction-plugin-'

The plugin manager automatically discovers plugins from these sources and registers
them with the plugin registry, making them available for use throughout the application.

Example Usage:
    ```python
    # Create a plugin manager
    manager = PluginManager()
    
    # Discover available plugins
    manager.discover_plugins()
    
    # Get all registered plugins
    all_plugins = manager.get_plugins()
    
    # Get plugins of a specific type
    genre_plugins = manager.get_plugins(GenrePlugin)
    
    # Get a specific plugin by ID
    noir_plugin = manager.get_plugin('noir')
    ```
"""

from typing import Dict, List, Type, Optional, Any
import os
import sys
import importlib
import pkgutil
import inspect
from pathlib import Path

from .base import BasePlugin, PluginMeta
from .registry import PluginRegistry
from .exceptions import PluginLoadError, PluginValidationError

class PluginManager:
    """
    Plugin Manager for the Pulp Fiction Generator.
    
    The PluginManager handles discovery, loading, validation, and registration of plugins
    from multiple sources:
    - User-specific plugins (~/.pulp-fiction/plugins/)
    - Project-local plugins (./plugins/)
    - Installed Python packages (pulp-fiction-plugin-*)
    
    The manager automatically discovers plugin classes within modules and registers
    them with the plugin registry. It provides methods for retrieving plugins
    by type or ID.
    
    Attributes:
        registry (PluginRegistry): Registry where discovered plugins are registered
        plugin_paths (List[Path]): Paths where the manager looks for plugins
    
    Methods:
        discover_plugins(): Discover and register all available plugins
        get_plugins(plugin_type=None): Get all plugins or plugins of a specific type
        get_plugin(plugin_id): Get a specific plugin by ID
    """
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.plugin_paths = [
            Path.home() / ".pulp-fiction" / "plugins",
            Path.cwd() / "plugins",
        ]
        
    def discover_plugins(self) -> None:
        """
        Discover and register all available plugins.
        
        This method searches for plugins in multiple locations:
        1. User plugin directory (~/.pulp-fiction/plugins/)
        2. Project plugin directory (./plugins/)
        3. Installed Python packages with the prefix 'pulp-fiction-plugin-'
        
        Each discovered plugin is validated and registered with the plugin registry.
        Any errors during discovery are caught and logged, but don't stop the discovery process.
        
        Returns:
            None
        """
        # Search in user and local plugin directories
        for plugin_path in self.plugin_paths:
            if plugin_path.exists() and plugin_path.is_dir():
                self._discover_in_path(plugin_path)
                
        # Search installed packages with the pulp-fiction-plugin prefix
        self._discover_installed_plugins()
    
    def _discover_in_path(self, path: Path) -> None:
        """
        Discover plugins in a specified directory path.
        
        Searches for Python modules or packages in the given path that may contain plugins.
        For each discovered module/package, attempts to load it and register any plugins within.
        
        The path is temporarily added to sys.path during discovery to allow for imports.
        
        Args:
            path (Path): The directory path to search for plugins
            
        Returns:
            None
        """
        # Add path to sys.path temporarily
        sys.path.insert(0, str(path))
        
        try:
            # Iterate through directories, looking for plugin modules
            for item in path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    self._load_plugin_module(item.name)
                elif item.suffix == ".py" and item.stem != "__init__":
                    self._load_plugin_module(item.stem)
        finally:
            # Remove path from sys.path
            sys.path.remove(str(path))
    
    def _discover_installed_plugins(self) -> None:
        """
        Discover plugins installed as Python packages.
        
        Searches for installed Python packages that have names starting with
        'pulp-fiction-plugin-'. For each matching package, attempts to load it
        and register any plugins it contains.
        
        This method uses pkg_resources to find installed packages. If pkg_resources
        is not available, this discovery method is skipped.
        
        Returns:
            None
        """
        try:
            import pkg_resources
            
            for dist in pkg_resources.working_set:
                if dist.project_name.startswith("pulp-fiction-plugin-"):
                    try:
                        # Load the plugin module
                        module_name = dist.project_name.replace("-", "_")
                        self._load_plugin_module(module_name)
                    except Exception as e:
                        print(f"Error loading plugin package {dist.project_name}: {e}")
        except ImportError:
            # pkg_resources not available, skip this discovery method
            pass
    
    def _load_plugin_module(self, module_name: str) -> None:
        """
        Load a plugin module and register its plugins.
        
        Imports the specified module and examines its contents to find plugin classes.
        Each plugin class found is validated and registered with the plugin registry.
        
        Plugin classes must:
        1. Be actual classes (not functions or other objects)
        2. Use the PluginMeta metaclass (inherit from BasePlugin)
        3. Be defined in the module (not imported)
        4. Not be BasePlugin itself
        
        Args:
            module_name (str): The name of the module to load
            
        Returns:
            None
        """
        try:
            module = importlib.import_module(module_name)
            
            # Look for plugin classes in the module
            for item_name in dir(module):
                item = getattr(module, item_name)
                
                # Check if the item is a plugin class
                if (inspect.isclass(item) and 
                    isinstance(item, PluginMeta) and 
                    item.__module__ == module.__name__ and
                    item is not BasePlugin):
                    
                    try:
                        # Register the plugin
                        self.registry.register_plugin(item)
                    except Exception as e:
                        print(f"Error registering plugin {item_name} from {module_name}: {e}")
        
        except Exception as e:
            print(f"Error loading plugin module {module_name}: {e}")
    
    def get_plugins(self, plugin_type: Optional[Type] = None) -> List[Type[BasePlugin]]:
        """
        Get all registered plugins, optionally filtered by type.
        
        Args:
            plugin_type (Optional[Type]): If provided, only returns plugins of this type
                                         If None, returns all plugins
                                         
        Returns:
            List[Type[BasePlugin]]: A list of plugin classes matching the criteria
        """
        return self.registry.get_plugins(plugin_type)
    
    def get_plugin(self, plugin_id: str) -> Type[BasePlugin]:
        """
        Get a specific plugin by ID.
        
        Args:
            plugin_id (str): The ID of the plugin to retrieve
            
        Returns:
            Type[BasePlugin]: The plugin class with the specified ID
            
        Raises:
            PluginNotFoundError: If no plugin with the specified ID is found
        """
        return self.registry.get_plugin(plugin_id) 