"""
Interfaces for agent components.
"""

from typing import Any, Callable, Dict, List, Protocol, Type, runtime_checkable


@runtime_checkable
class ToolRegistry(Protocol):
    """Protocol for tool registries."""
    
    def register_tool(self, name: str, tool_class: Any) -> None:
        """
        Register a tool with the registry.
        
        Args:
            name: Name to register the tool under
            tool_class: The tool class to register
        """
        ...
    
    def register_tool_factory(self, name: str, factory: Callable) -> None:
        """
        Register a tool factory with the registry.
        
        Args:
            name: Name to register the factory under
            factory: The factory function to register
        """
        ...
    
    def get_tool(self, name: str) -> Any:
        """
        Get a tool from the registry.
        
        Args:
            name: Name of the tool to get
            
        Returns:
            The requested tool
        """
        ...
    
    def get_tool_factory(self, name: str) -> Callable:
        """
        Get a tool factory from the registry.
        
        Args:
            name: Name of the factory to get
            
        Returns:
            The requested factory function
        """
        ...
    
    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tools.
        
        Returns:
            List of tool names
        """
        ... 