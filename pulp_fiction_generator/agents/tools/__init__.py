"""
Tool management for agents.

This module provides a registry and loader for agent tools.
"""

from .tool_registry import ToolRegistry, registry
from .tool_loader import ToolLoader

# Register default tools
from . import default_tools
default_tools.register_default_tools(registry)

__all__ = [
    'ToolRegistry',
    'ToolLoader',
    'registry',
    'default_tools'
] 