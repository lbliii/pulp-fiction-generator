"""
Unit tests for the ContextVisualizer class.
"""

import os
import tempfile
import json
import pytest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.utils.context_visualizer import ContextVisualizer


class TestContextVisualizer:
    """Test the ContextVisualizer class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname
    
    @pytest.fixture
    def visualizer(self, temp_dir):
        """Create a ContextVisualizer instance with a temporary output directory."""
        return ContextVisualizer(output_dir=temp_dir)
    
    @pytest.fixture
    def disabled_visualizer(self, temp_dir):
        """Create a disabled ContextVisualizer instance."""
        return ContextVisualizer(output_dir=temp_dir, enabled=False)
    
    @pytest.fixture
    def sample_context(self):
        """Create a sample context for testing."""
        return {
            "genre": "noir",
            "title": "The Long Goodbye",
            "characters": [
                {"name": "Philip Marlowe", "role": "Detective"},
                {"name": "Terry Lennox", "role": "Client"}
            ],
            "setting": {
                "time": "1950s",
                "location": "Los Angeles",
                "mood": "Dark and rainy"
            },
            "plot": {
                "act_1": "Marlowe meets Lennox",
                "act_2": "Lennox disappears",
                "act_3": "Marlowe solves the case"
            }
        }
    
    def test_init(self, temp_dir):
        """Test initialization of the visualizer."""
        visualizer = ContextVisualizer(output_dir=temp_dir)
        
        assert visualizer.enabled is True
        assert visualizer.output_dir == temp_dir
        assert visualizer.context_history == []
        assert visualizer.agent_interactions == []
    
    def test_init_creates_output_dir(self):
        """Test that initialization creates the output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as base_dir:
            output_dir = os.path.join(base_dir, "nonexistent_dir")
            visualizer = ContextVisualizer(output_dir=output_dir)
            
            assert os.path.exists(output_dir)
    
    def test_visualize_context(self, visualizer, sample_context, temp_dir):
        """Test visualizing a context."""
        with patch.object(visualizer, 'console') as mock_console:
            visualizer.visualize_context(sample_context, stage="test_stage")
            
            # Check that console output was called
            assert mock_console.print.call_count >= 2
            
            # Check that the context was saved to history
            assert len(visualizer.context_history) == 1
            assert visualizer.context_history[0]['stage'] == "test_stage"
            assert visualizer.context_history[0]['context'] == sample_context
            
            # Check that a JSON file was created
            files = os.listdir(temp_dir)
            assert any(f.startswith("context_test_stage_") for f in files)
    
    def test_disabled_visualizer(self, disabled_visualizer, sample_context, temp_dir):
        """Test that disabled visualizer doesn't create output."""
        disabled_visualizer.visualize_context(sample_context, stage="test_stage")
        
        # Check that nothing was saved to history
        assert len(disabled_visualizer.context_history) == 0
        
        # Check that no files were created
        files = os.listdir(temp_dir)
        assert not any(f.startswith("context_") for f in files)
    
    def test_track_agent_interaction(self, visualizer, sample_context, temp_dir):
        """Test tracking an agent interaction."""
        input_context = sample_context.copy()
        output_context = sample_context.copy()
        output_context['title'] = "The Modified Goodbye"
        output_context['plot']['act_3'] = "Marlowe solves the mystery"
        
        with patch.object(visualizer, 'console') as mock_console:
            visualizer.track_agent_interaction(
                agent_name="test_agent",
                input_context=input_context,
                output_context=output_context,
                prompt="Generate a modified story",
                response="I have modified the story"
            )
            
            # Check that console output was called
            assert mock_console.print.call_count >= 2
            
            # Check that the interaction was saved
            assert len(visualizer.agent_interactions) == 1
            interaction = visualizer.agent_interactions[0]
            assert interaction['agent'] == "test_agent"
            assert interaction['input_context'] == input_context
            assert interaction['output_context'] == output_context
            assert interaction['prompt'] == "Generate a modified story"
            assert interaction['response'] == "I have modified the story"
            
            # Check that a JSON file was created
            files = os.listdir(temp_dir)
            assert any(f.startswith("interaction_test_agent_") for f in files)
    
    def test_calculate_context_diff(self, visualizer):
        """Test calculating context differences."""
        before = {
            "title": "Original Title",
            "characters": ["Alice", "Bob"],
            "setting": "New York",
            "to_remove": "This will be removed"
        }
        
        after = {
            "title": "Modified Title",
            "characters": ["Alice", "Bob", "Charlie"],
            "setting": "New York",
            "new_field": "This is new"
        }
        
        diff = visualizer._calculate_context_diff(before, after)
        
        assert "title" in diff
        assert diff["title"] == ("Original Title", "Modified Title")
        
        assert "characters" in diff
        assert diff["characters"] == (["Alice", "Bob"], ["Alice", "Bob", "Charlie"])
        
        assert "to_remove" in diff
        assert diff["to_remove"] == ("This will be removed", None)
        
        assert "new_field" in diff
        assert diff["new_field"] == (None, "This is new")
        
        assert "setting" not in diff  # Unchanged field should not be in diff
    
    def test_export_visualization_html(self, visualizer, sample_context, temp_dir):
        """Test exporting visualization to HTML."""
        # Add some data to the visualizer
        visualizer.visualize_context(sample_context, stage="initial")
        
        # Modify the context and track an interaction
        modified_context = sample_context.copy()
        modified_context['title'] = "The Modified Goodbye"
        
        visualizer.track_agent_interaction(
            agent_name="editor",
            input_context=sample_context,
            output_context=modified_context,
            prompt="Modify the title",
            response="Title modified"
        )
        
        # Export to HTML
        with patch.object(visualizer, 'console') as mock_console:
            output_path = visualizer.export_visualization_html()
            
            # Check that the file was created
            assert os.path.exists(output_path)
            
            # Check that the file contains expected content
            with open(output_path, 'r') as f:
                content = f.read()
                assert "Story Generation Debug Visualization" in content
                assert "Context History" in content
                assert "Agent Interactions" in content
                assert "The Long Goodbye" in content
                assert "The Modified Goodbye" in content
                assert "editor" in content
                
            # Check that console output was called
            mock_console.print.assert_called_once()
    
    def test_no_export_when_empty(self, visualizer, temp_dir):
        """Test that no HTML is exported when there's no history."""
        # Export without adding any data
        output_path = visualizer.export_visualization_html()
        
        # Check that no file was created
        assert output_path is None
        files = os.listdir(temp_dir)
        assert not any(f.endswith(".html") for f in files) 