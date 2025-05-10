"""
Tests for story persistence functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.utils.story_persistence import StoryState

@pytest.mark.integration
def test_story_persistence_basic():
    """
    Test that StoryState can be properly created and manipulated.
    """
    # Create a basic StoryState
    story_state = StoryState("noir", "Test Title")
    
    # Check initial state
    assert story_state.metadata.genre == "noir"
    assert story_state.metadata.title == "Test Title"
    assert story_state.metadata.chapter_count == 0
    assert story_state.metadata.word_count == 0
    
    # Add a chapter
    story_state.add_chapter("This is a test chapter.", [], [], [{"description": "Test plot point"}])
    
    # Check the chapter was added
    assert story_state.metadata.chapter_count == 1
    assert "This is a test chapter." in story_state.get_full_story()
    assert story_state.metadata.word_count > 0

@pytest.mark.integration
def test_story_state_metadata():
    """
    Test that story state metadata can be properly set and retrieved.
    """
    # Create a story state with title
    story_state = StoryState("sci-fi", "Space Adventure")
    
    # Set plot template
    story_state.metadata.plot_template = "three_act"
    
    # Check metadata
    assert story_state.metadata.genre == "sci-fi"
    assert story_state.metadata.title == "Space Adventure"
    assert hasattr(story_state.metadata, "plot_template")
    assert story_state.metadata.plot_template == "three_act"
    
    # Add a chapter with characters and settings
    story_state.add_chapter("Chapter 1 content", 
                           [{"name": "John", "description": "Protagonist"}], 
                           [{"name": "Spaceship", "description": "Main setting"}],
                           [{"description": "Discovery of alien artifact"}])
    
    # Check that metadata contains the added elements
    assert len(story_state.metadata.characters) == 1
    assert len(story_state.metadata.settings) == 1
    assert len(story_state.metadata.plot_points) == 1
    
    # Check character data
    assert story_state.metadata.characters[0]["name"] == "John"
    
    # Check full story content
    full_story = story_state.get_full_story()
    assert "Chapter 1 content" in full_story
    assert story_state.metadata.chapter_count == 1

@pytest.mark.integration
def test_story_serialization():
    """
    Test story serialization and deserialization.
    """
    # Create test story
    story_state = StoryState("western", "Gunslinger's Revenge")
    story_state.add_chapter("The dusty town was quiet as he rode in.", 
                           [{"name": "The Gunslinger", "description": "A mysterious figure"}],
                           [{"name": "Dusty Town", "description": "A frontier settlement"}],
                           [{"description": "Arrival of the gunslinger"}])
    
    # Serialize to dictionary
    serialized = story_state.to_dict()
    
    # Check serialized data
    assert serialized["metadata"]["genre"] == "western"
    assert serialized["metadata"]["title"] == "Gunslinger's Revenge"
    assert len(serialized["chapters"]) == 1
    assert len(serialized["metadata"]["characters"]) == 1
    assert serialized["metadata"]["characters"][0]["name"] == "The Gunslinger"
    
    # Create new story state from serialized data
    new_story = StoryState.from_dict(serialized)
    
    # Check deserialized story
    assert new_story.metadata.genre == "western"
    assert new_story.metadata.title == "Gunslinger's Revenge"
    assert new_story.metadata.chapter_count == 1
    assert len(new_story.metadata.characters) == 1
    assert new_story.metadata.characters[0]["name"] == "The Gunslinger"
    
    # Check that full content matches
    assert new_story.get_full_story() == story_state.get_full_story() 