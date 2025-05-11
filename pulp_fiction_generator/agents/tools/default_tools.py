"""
Default tools for agents.

This module registers the default tools that are available to agents.
"""

from typing import List

from ..interfaces import ToolRegistry

# Import tools from crewai_tools
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    FileWriterTool,
    SerperDevTool,
    WebsiteSearchTool
)

def register_default_tools(registry: ToolRegistry) -> None:
    """
    Register the default set of tools with the registry.
    
    Args:
        registry: The tool registry to register tools with
    """
    # Register file and directory tools
    registry.register_tool("file_read", FileReadTool)
    registry.register_tool("file_write", FileWriterTool)
    registry.register_tool("directory_read", DirectoryReadTool)
    
    # Register search tools
    registry.register_tool("serper_search", SerperDevTool)
    registry.register_tool("website_search", WebsiteSearchTool)
    
    # Register any custom tools
    from .custom_tools import register_custom_tools
    register_custom_tools(registry) 