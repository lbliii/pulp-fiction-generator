"""
Unit tests for the ModelService abstract class and implementations.
"""

import pytest
from unittest.mock import MagicMock
from pulp_fiction_generator.models.model_service import ModelService


class TestModelServiceImplementation(ModelService):
    """A concrete implementation of ModelService for testing."""
    
    def __init__(self):
        self.mock_generate = MagicMock(return_value="Test generated text")
        self.mock_chat = MagicMock(return_value="Test chat response")
        self.mock_get_model_info = MagicMock(return_value={"name": "Test Model", "version": "1.0"})
        self.mock_tokenize = MagicMock(return_value=[1, 2, 3, 4, 5])
    
    def generate(self, prompt, parameters=None):
        return self.mock_generate(prompt, parameters)
    
    def chat(self, messages, parameters=None):
        return self.mock_chat(messages, parameters)
    
    def get_model_info(self):
        return self.mock_get_model_info()
    
    def tokenize(self, text):
        return self.mock_tokenize(text)


class TestModelService:
    """Test the ModelService class and its implementations."""
    
    @pytest.fixture
    def model_service(self):
        return TestModelServiceImplementation()
    
    def test_generate(self, model_service):
        """Test the generate method."""
        result = model_service.generate("Test prompt")
        assert result == "Test generated text"
        model_service.mock_generate.assert_called_once_with("Test prompt", None)
    
    def test_generate_with_parameters(self, model_service):
        """Test the generate method with parameters."""
        params = {"temperature": 0.7}
        result = model_service.generate("Test prompt", params)
        assert result == "Test generated text"
        model_service.mock_generate.assert_called_once_with("Test prompt", params)
    
    def test_chat(self, model_service):
        """Test the chat method."""
        messages = [{"role": "user", "content": "Hello"}]
        result = model_service.chat(messages)
        assert result == "Test chat response"
        model_service.mock_chat.assert_called_once_with(messages, None)
    
    def test_get_model_info(self, model_service):
        """Test the get_model_info method."""
        info = model_service.get_model_info()
        assert info == {"name": "Test Model", "version": "1.0"}
        model_service.mock_get_model_info.assert_called_once()
    
    def test_count_tokens(self, model_service):
        """Test the count_tokens method."""
        count = model_service.count_tokens("Test text")
        assert count == 5
        model_service.mock_tokenize.assert_called_once_with("Test text")
    
    def test_batch_generate(self, model_service):
        """Test the batch_generate method."""
        prompts = ["Prompt 1", "Prompt 2"]
        results = model_service.batch_generate(prompts)
        assert results == ["Test generated text", "Test generated text"]
        assert model_service.mock_generate.call_count == 2 