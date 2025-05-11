#!/usr/bin/env python3
"""
Test script for knowledge sources in the pulp-fiction-generator.

This script tests the functionality of the knowledge sources, particularly
the GenreDatabaseKnowledge class.
"""

import sys
from pulp_fiction_generator.agents.knowledge.genre_database import GenreDatabaseKnowledge
from pulp_fiction_generator.agents.knowledge.default_sources import get_default_knowledge_sources

def test_genre_database_knowledge():
    """Test the GenreDatabaseKnowledge class."""
    print("Testing GenreDatabaseKnowledge...")
    
    # Test with default genre
    knowledge = GenreDatabaseKnowledge()
    print(f"Created knowledge source with default genre: {knowledge.genre}")
    
    # Test content loading
    content = knowledge.load_content()
    print(f"Loaded content: {content}")
    
    # Test with specific genre
    noir_knowledge = GenreDatabaseKnowledge(genre="noir")
    print(f"Created knowledge source with noir genre: {noir_knowledge.genre}")
    
    # Test content loading for noir
    noir_content = noir_knowledge.load_content()
    print(f"Loaded noir content: {noir_content}")
    
    # Test validate_content method
    print(f"Validate content method returns: {noir_knowledge.validate_content('test content')}")
    
    # Test add method
    noir_knowledge.add()
    print(f"Added noir knowledge, chunks: {len(noir_knowledge.chunks)}")
    
    # Use assertion instead of return
    assert knowledge.genre is not None
    assert noir_knowledge.genre == "noir"
    assert content is not None
    assert noir_content is not None
    assert len(noir_knowledge.chunks) > 0

def test_default_knowledge_sources():
    """Test the default knowledge sources."""
    print("\nTesting default knowledge sources...")
    
    # Get default knowledge sources
    sources = get_default_knowledge_sources()
    print(f"Got {len(sources)} default knowledge sources")
    
    # Check that we have knowledge sources for all default genres
    genres = ["noir", "sci-fi", "adventure"]
    for genre in genres:
        found = False
        for source in sources:
            if hasattr(source, 'genre') and source.genre == genre:
                found = True
                break
        print(f"Found knowledge source for {genre}: {found}")
        assert found, f"Knowledge source for {genre} not found"
    
    # Use assertion instead of return
    assert len(sources) > 0

if __name__ == "__main__":
    print("Running knowledge sources tests...")
    
    success = test_genre_database_knowledge()
    if not success:
        print("GenreDatabaseKnowledge test failed!")
        sys.exit(1)
    
    success = test_default_knowledge_sources()
    if not success:
        print("Default knowledge sources test failed!")
        sys.exit(1)
    
    print("\nAll knowledge sources tests passed!") 