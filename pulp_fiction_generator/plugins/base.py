"""
Base classes for the plugin system.
"""

from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Any, List, Type

class PluginMeta(type):
    """Metaclass for plugins to register attributes"""
    
    def __new__(mcs, name, bases, attrs):
        # Create the class
        cls = super().__new__(mcs, name, bases, attrs)
        
        # Skip validation for BasePlugin and direct subclasses that serve as abstract base classes
        if name == "BasePlugin" or any(b.__name__ == "BasePlugin" for b in bases):
            return cls
        
        # Skip validation for abstract classes (those that don't define implementations)
        if hasattr(cls, "__abstractmethods__") and cls.__abstractmethods__:
            return cls
            
        # Validate required attributes for concrete implementations
        required_attrs = ["plugin_id", "plugin_name", "plugin_description"]
        for attr in required_attrs:
            if not hasattr(cls, attr) or getattr(cls, attr) is None:
                raise TypeError(f"Plugin class {name} must define {attr}")
        
        return cls

# Define an ABC-compatible metaclass
class ABCPluginMeta(PluginMeta, type(ABC)):
    """Metaclass combining ABC and PluginMeta functionality"""
    pass

class BasePlugin(ABC, metaclass=ABCPluginMeta):
    """Base class for all plugins"""
    
    plugin_id: ClassVar[str] = None
    plugin_name: ClassVar[str] = None
    plugin_description: ClassVar[str] = None
    plugin_version: ClassVar[str] = "0.1.0"
    
    @classmethod
    def get_plugin_info(cls) -> Dict[str, Any]:
        """Get information about the plugin"""
        return {
            "id": cls.plugin_id,
            "name": cls.plugin_name,
            "description": cls.plugin_description,
            "version": cls.plugin_version,
            "type": cls.__name__
        }

class GenrePlugin(BasePlugin):
    """Base class for genre plugins"""
    
    @abstractmethod
    def get_prompt_enhancers(self) -> Dict[str, str]:
        """Get prompt enhancers for different agent types"""
        pass
    
    @abstractmethod
    def get_character_templates(self) -> List[Dict[str, Any]]:
        """Get character templates for this genre"""
        pass
    
    @abstractmethod
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        """Get plot templates for this genre"""
        pass
    
    @abstractmethod
    def get_example_passages(self) -> List[Dict[str, str]]:
        """Get example passages for this genre"""
        pass

class AgentPlugin(BasePlugin):
    """Base class for agent plugins"""
    
    @abstractmethod
    def get_agent_class(self) -> Type:
        """Get the agent class"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration for this agent"""
        pass
    
    @abstractmethod
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get prompt templates for this agent"""
        pass

class ModelPlugin(BasePlugin):
    """Base class for model plugins"""
    
    @abstractmethod
    def get_model_service(self) -> Type:
        """Get the model service class"""
        pass
    
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """Get a list of features supported by this model"""
        pass
    
    @abstractmethod
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this model"""
        pass 