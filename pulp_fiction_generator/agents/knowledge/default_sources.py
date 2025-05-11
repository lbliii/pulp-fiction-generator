"""
Default knowledge sources for agents.

This module registers the default knowledge sources that are available to agents.
"""

from .knowledge_registry import registry
from .genre_database import GenreDatabaseKnowledge, create_genre_database


def register_default_sources():
    """Register the default knowledge sources in the registry."""
    
    # Register the genre database knowledge source
    registry.register_source("genre_database", GenreDatabaseKnowledge)
    registry.register_source_factory("genre_database", create_genre_database)
    

def get_default_knowledge_sources():
    """
    Get a list of default knowledge sources for all supported genres.
    
    Returns:
        list: List of knowledge source instances
    """
    default_genres = ["noir", "sci-fi", "adventure"]
    sources = []
    
    for genre in default_genres:
        source = create_genre_database(genre=genre)
        sources.append(source)
    
    return sources


# Register default sources when the module is imported
register_default_sources() 