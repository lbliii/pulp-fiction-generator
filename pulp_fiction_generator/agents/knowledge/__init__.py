"""
Knowledge source management for agents.

This module provides a registry and loader for agent knowledge sources.
"""

from .knowledge_registry import KnowledgeRegistry, registry
from .knowledge_loader import KnowledgeLoader

# Import default sources to register them
from . import default_sources

__all__ = [
    'KnowledgeRegistry',
    'KnowledgeLoader',
    'registry',
    'default_sources'
] 