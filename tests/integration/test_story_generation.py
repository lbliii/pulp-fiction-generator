"""
Integration tests for story generation.
"""

import os
import pytest
from unittest.mock import patch

from pulp_fiction_generator.models.model_service import ModelService
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter


# Skip tests if the SKIP_INTEGRATION_TESTS environment variable is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION_TESTS", "False").lower() == "true",
    reason="Integration tests skipped via environment variable"
)


class TestStoryGeneration:
    """Integration tests for the story generation functionality."""
    
    @pytest.fixture
    def model_service(self):
        """Return a mocked model service for testing."""
        # This could be replaced with a real model service for true integration testing
        # But for now, we'll mock it to avoid external dependencies
        
        class MockModelService(ModelService):
            def generate(self, prompt, parameters=None):
                return "This is a test story generated from a prompt."
            
            def chat(self, messages, parameters=None):
                return "This is a test chat response."
            
            def get_model_info(self):
                return {"name": "Test Model", "version": "1.0"}
        
        return MockModelService()
    
    @pytest.mark.xfail(reason="This test requires a running Ollama instance")
    def test_real_model_connection(self):
        """Test connecting to a real Ollama instance (if available)."""
        try:
            adapter = OllamaAdapter()
            info = adapter.get_model_info()
            assert isinstance(info, dict)
            assert "license" in info or "modelfile" in info or "parameters" in info
        except Exception as e:
            pytest.xfail(f"Failed to connect to Ollama: {str(e)}")
    
    def test_basic_story_generation(self, model_service):
        """
        Test basic story generation functionality.
        
        Note: This is a simplified integration test that only tests
        the model service connection. A full integration test would need
        to test the entire pipeline from user input to story output.
        """
        # For a true integration test, this would use the actual story generation pipeline
        # But for this example, we're just testing the model service integration
        prompt = "Generate a short detective story set in 1930s Chicago."
        result = model_service.generate(prompt)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter.generate")
    def test_noir_genre_story(self, mock_generate):
        """Test generating a noir genre story."""
        # Set up the mock to return a simple noir story
        mock_generate.return_value = """
        The rain fell like tears from a jilted lover, washing the neon reflections across the wet pavement.
        Detective Jack Morgan pulled his collar up against the damp chill, watching the entrance to the Starlight Lounge.
        His informant had promised information on the Callahan case - a case that had already cost two good men their lives.
        """
        
        # TODO: In a full integration test, we would:
        # 1. Initialize the actual story generation pipeline
        # 2. Set up the noir genre parameters
        # 3. Generate a story
        # 4. Validate the output meets noir genre conventions
        
        # For now, we'll just verify our mock works
        adapter = OllamaAdapter()
        result = adapter.generate("Generate a noir story")
        
        assert "Detective Jack Morgan" in result
        assert "rain fell" in result
        assert "Starlight Lounge" in result 