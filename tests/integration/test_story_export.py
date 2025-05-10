"""
Integration tests for story export functionality.
"""

import os
import shutil
import tempfile
import pytest
from unittest.mock import patch

from pulp_fiction_generator.models.model_service import ModelService
from pulp_fiction_generator.utils.story_exporter import StoryExporter
from pulp_fiction_generator.utils.story_persistence import StoryPersistence


# Skip tests if the SKIP_INTEGRATION_TESTS environment variable is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "False").lower() == "true",
    reason="Integration tests skipped via environment variable"
)


class TestStoryExportIntegration:
    """Integration tests for the story export functionality."""
    
    @pytest.fixture
    def model_service(self):
        """Return a mocked model service for testing."""
        class MockModelService(ModelService):
            def generate(self, prompt, parameters=None):
                return "This is a test story generated from a prompt."
            
            def chat(self, messages, parameters=None):
                return "This is a test chat response."
            
            def get_model_info(self):
                return {"name": "Test Model", "version": "1.0"}
        
        return MockModelService()
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for story exports."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_story(self):
        """Return a sample story for testing."""
        return {
            "title": "The Dark Alley",
            "content": """The neon sign flickered overhead, casting an eerie blue glow on the wet pavement.
            
Detective Mike Hammer pulled his coat tighter against the chill night air. This was the third murder this month with the same M.O. - body found in an alley, single gunshot wound to the chest, no shell casings.
            
"Who's our victim?" he asked, approaching the coroner who was hunched over the body.
            
"Male, early forties. ID says his name is Frank Delano, works at the shipyard. Been dead about six hours."
            
Mike nodded, jotting notes in his small pad. The rain was starting again, washing away what little evidence might have remained. This killer was smart, careful. But everyone makes mistakes eventually.
            
"I'll find you," he whispered, looking up at the narrow gap between buildings where the killer must have stood. "It's just a matter of time."
            """,
            "metadata": {
                "genre": "Noir",
                "date_created": "2024-06-15",
                "author": "AI Crime Writer",
                "word_count": 148,
                "tags": ["detective", "murder", "noir", "crime"],
                "characters": [
                    {"name": "Mike Hammer", "description": "Hard-boiled detective"},
                    {"name": "Frank Delano", "description": "Murder victim, works at shipyard"}
                ]
            }
        }
    
    def test_export_to_all_formats(self, temp_output_dir, sample_story):
        """Test exporting a story to all available formats."""
        # Initialize exporter
        exporter = StoryExporter(output_dir=temp_output_dir)
        
        # Export to all text-based formats
        formats = ["markdown", "html", "text"]
        results = exporter.export_story(sample_story, formats)
        
        # Verify all requested formats were exported
        assert len(results) == len(formats), f"Expected {len(formats)} export results, got {len(results)}"
        
        # Verify all files exist
        for fmt, filepath in results.items():
            assert os.path.exists(filepath), f"Export file for {fmt} format not found"
            
        # Verify content of each format
        for fmt, filepath in results.items():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for title, handling uppercase in text format
                if fmt == "text":
                    assert "THE DARK ALLEY" in content, f"Title not found in {fmt} export"
                else:
                    assert "The Dark Alley" in content, f"Title not found in {fmt} export"
                    
                assert "Detective Mike Hammer" in content, f"Content not found in {fmt} export"
                assert "Noir" in content, f"Metadata not found in {fmt} export"
    
    @patch("pulp_fiction_generator.utils.story_persistence.StoryPersistence.load_story")
    def test_export_from_persistence(self, mock_load_story, temp_output_dir, sample_story):
        """Test exporting a story loaded from persistence."""
        # Mock the story persistence to return our sample story
        mock_load_story.return_value = sample_story
        
        # Create persistence and exporter
        persistence = StoryPersistence()
        exporter = StoryExporter(output_dir=temp_output_dir)
        
        # Load story and export to markdown
        story_id = "test_story_123"
        loaded_story = persistence.load_story(story_id)
        result = exporter.export_to_markdown(loaded_story)
        
        # Verify the export
        assert os.path.exists(result), "Exported markdown file not found"
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "The Dark Alley" in content
            assert "Detective Mike Hammer" in content
    
    def test_exports_folder_creation(self, sample_story):
        """Test that the exports folder is created if it doesn't exist."""
        # Create a path that doesn't exist yet
        export_path = os.path.join(tempfile.gettempdir(), f"pulp_test_exports_{os.getpid()}")
        
        # Ensure the directory doesn't exist
        if os.path.exists(export_path):
            shutil.rmtree(export_path)
        
        try:
            # Initialize exporter - should create the directory
            exporter = StoryExporter(output_dir=export_path)
            
            # Verify directory was created
            assert os.path.exists(export_path), "Exports directory was not created"
            assert os.path.isdir(export_path), "Exports path is not a directory"
            
            # Test export works in this directory
            result = exporter.export_to_text(sample_story)
            assert os.path.exists(result), "Export file was not created"
            
        finally:
            # Cleanup
            if os.path.exists(export_path):
                shutil.rmtree(export_path) 