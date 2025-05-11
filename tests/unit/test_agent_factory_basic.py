"""
Test script for checking agent factory functionality.
This is a quick test to validate agent creation and identify potential bugs.
"""

import os
import sys
from pulp_fiction_generator.agents.agent_factory import AgentFactory
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter

def test_agent_factory():
    """Test the basic functionality of the agent factory."""
    print("Testing agent factory...")
    
    # Initialize model service
    try:
        model_service = OllamaAdapter(model_name="llama3.2")
        print(f"Connected to model service: {model_service}")
    except Exception as e:
        print(f"Failed to connect to model service: {e}")
        return
    
    # Initialize agent factory
    try:
        agent_factory = AgentFactory(model_service, verbose=True)
        print(f"Created agent factory: {agent_factory}")
    except Exception as e:
        print(f"Failed to create agent factory: {e}")
        return
    
    # Test creating agents for each type and genre
    agent_types = ["researcher", "worldbuilder", "character_creator", "plotter", "writer", "editor"]
    genres = ["noir", "sci-fi", "adventure"]
    
    for agent_type in agent_types:
        for genre in genres:
            try:
                print(f"Creating {agent_type} for {genre} genre...")
                agent = agent_factory.create_agent(agent_type, genre)
                print(f"Successfully created {agent_type} for {genre} genre: {agent}")
            except Exception as e:
                print(f"ERROR: Failed to create {agent_type} for {genre} genre: {e}")
    
    # Test with invalid parameters
    try:
        print("Testing with invalid agent type...")
        agent = agent_factory.create_agent("invalid_type", "noir")
        print(f"Unexpected success with invalid agent type: {agent}")
    except Exception as e:
        print(f"Expected error with invalid agent type: {e}")
    
    try:
        print("Testing with invalid genre...")
        agent = agent_factory.create_agent("researcher", "invalid_genre")
        print(f"Successfully created researcher for invalid genre: {agent}")
    except Exception as e:
        print(f"Failed with invalid genre: {e}")
    
    # Test with various configuration overrides
    try:
        print("Testing with config override...")
        config_override = {
            "verbose": False,
            "allow_delegation": True,
            "max_iter": 5,
            "tools": ["web_search"],
            "non_existent_param": "value"  # Should be ignored
        }
        agent = agent_factory.create_agent("researcher", "noir", config=config_override)
        print(f"Successfully created agent with config override: {agent}")
    except Exception as e:
        print(f"Failed with config override: {e}")
    
    # Test with knowledge sources
    try:
        print("Testing with knowledge sources...")
        config_with_knowledge = {
            "knowledge_sources": ["genre_database"]
        }
        agent = agent_factory.create_agent("researcher", "noir", config=config_with_knowledge)
        print(f"Successfully created agent with knowledge sources: {agent}")
    except Exception as e:
        print(f"Failed with knowledge sources: {e}")
    
    # Test with knowledge source configuration
    try:
        print("Testing with configured knowledge sources...")
        config_with_knowledge_config = {
            "knowledge_sources": [
                {
                    "name": "genre_database",
                    "config": {
                        "genre": "noir"
                    }
                }
            ]
        }
        agent = agent_factory.create_agent("researcher", "noir", config=config_with_knowledge_config)
        print(f"Successfully created agent with configured knowledge sources: {agent}")
    except Exception as e:
        print(f"Failed with configured knowledge sources: {e}")

if __name__ == "__main__":
    test_agent_factory() 