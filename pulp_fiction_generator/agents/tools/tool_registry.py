"""
Registry for agent tools.
"""

from typing import Any, Callable, Dict, Optional, Type


class ToolRegistry:
    """
    Registry for agent tools.
    
    This class maintains a registry of available tools that can be used by agents.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Type[Any]] = {}
        self._factories: Dict[str, Callable[..., Any]] = {}
        
    def register_tool(self, name: str, tool_class: Type[Any]) -> None:
        """
        Register a tool class with the registry.
        
        Args:
            name: Name of the tool
            tool_class: Class of the tool
        """
        self._tools[name] = tool_class
        
    def register_tool_factory(self, name: str, factory: Callable[..., Any]) -> None:
        """
        Register a tool factory function with the registry.
        
        Args:
            name: Name of the tool
            factory: Factory function for creating tool instances
        """
        self._factories[name] = factory
        
    def get_tool_class(self, name: str) -> Optional[Type[Any]]:
        """
        Get a tool class by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool class if found, None otherwise
        """
        return self._tools.get(name)
        
    def get_tool_factory(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Get a tool factory function by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool factory function if found, None otherwise
        """
        return self._factories.get(name)
        
    def create_tool(self, name: str, **kwargs) -> Any:
        """
        Create a tool instance by name.
        
        Args:
            name: Name of the tool
            **kwargs: Arguments to pass to the tool constructor or factory
            
        Returns:
            Tool instance
            
        Raises:
            ValueError: If the tool is not registered
        """
        factory = self.get_tool_factory(name)
        if factory:
            return factory(**kwargs)
            
        tool_class = self.get_tool_class(name)
        if tool_class:
            return tool_class(**kwargs)
            
        raise ValueError(f"Tool '{name}' is not registered")
        
    def list_tools(self) -> Dict[str, str]:
        """
        List all registered tools.
        
        Returns:
            Dictionary mapping tool names to their descriptions
        """
        tools = {}
        
        for name, tool_class in self._tools.items():
            tools[name] = tool_class.__doc__ or "No description available"
            
        for name, factory in self._factories.items():
            tools[name] = factory.__doc__ or "No description available"
            
        return tools


# Create a singleton instance
registry = ToolRegistry() 