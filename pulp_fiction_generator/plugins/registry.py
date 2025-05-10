"""
Registry for plugins.
"""

from typing import Dict, List, Type, Optional
from .base import BasePlugin, GenrePlugin, AgentPlugin, ModelPlugin
from .exceptions import PluginRegistrationError, PluginNotFoundError

class PluginRegistry:
    """Registry for plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Type[BasePlugin]] = {}
        
    def register_plugin(self, plugin_class: Type[BasePlugin]) -> None:
        """Register a plugin class"""
        plugin_id = plugin_class.plugin_id
        
        # Ensure plugin_id is not already registered
        if plugin_id in self.plugins:
            existing = self.plugins[plugin_id]
            raise PluginRegistrationError(
                f"Plugin ID '{plugin_id}' is already registered by {existing.__name__}"
            )
        
        # Register the plugin
        self.plugins[plugin_id] = plugin_class
        
        print(f"Registered plugin: {plugin_class.plugin_name} ({plugin_id})")
    
    def get_plugins(self, plugin_type: Optional[Type] = None) -> List[Type[BasePlugin]]:
        """Get all registered plugins, optionally filtered by type"""
        if plugin_type is None:
            return list(self.plugins.values())
        
        return [
            plugin for plugin in self.plugins.values()
            if issubclass(plugin, plugin_type)
        ]
    
    def get_plugin(self, plugin_id: str) -> Type[BasePlugin]:
        """Get a specific plugin by ID"""
        if plugin_id not in self.plugins:
            raise PluginNotFoundError(f"Plugin not found: {plugin_id}")
        
        return self.plugins[plugin_id]
    
    def get_genre_plugins(self) -> List[Type[GenrePlugin]]:
        """Get all genre plugins"""
        return self.get_plugins(GenrePlugin)
    
    def get_agent_plugins(self) -> List[Type[AgentPlugin]]:
        """Get all agent plugins"""
        return self.get_plugins(AgentPlugin)
    
    def get_model_plugins(self) -> List[Type[ModelPlugin]]:
        """Get all model plugins"""
        return self.get_plugins(ModelPlugin) 