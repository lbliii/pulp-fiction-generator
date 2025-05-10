"""
Plugin discovery and loading manager.
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
    """Manages discovery and loading of plugins"""
    
    def __init__(self):
        self.registry = PluginRegistry()
        self.plugin_paths = [
            Path.home() / ".pulp-fiction" / "plugins",
            Path.cwd() / "plugins",
        ]
        
    def discover_plugins(self) -> None:
        """Discover and register all available plugins"""
        # Search in user and local plugin directories
        for plugin_path in self.plugin_paths:
            if plugin_path.exists() and plugin_path.is_dir():
                self._discover_in_path(plugin_path)
                
        # Search installed packages with the pulp-fiction-plugin prefix
        self._discover_installed_plugins()
    
    def _discover_in_path(self, path: Path) -> None:
        """Discover plugins in a specified path"""
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
        """Discover plugins installed as Python packages"""
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
        """Load a plugin module and register its plugins"""
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
        """Get all registered plugins of a specific type"""
        return self.registry.get_plugins(plugin_type)
    
    def get_plugin(self, plugin_id: str) -> Type[BasePlugin]:
        """Get a specific plugin by ID"""
        return self.registry.get_plugin(plugin_id) 