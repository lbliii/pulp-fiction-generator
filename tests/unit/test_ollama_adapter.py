"""
Unit tests for the OllamaAdapter class.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter


class TestOllamaAdapter:
    """Test the OllamaAdapter implementation."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Clear OLLAMA environment variables for consistent testing."""
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
    
    @pytest.fixture
    def adapter(self, mock_env):
        """Return a test adapter with environment variables cleared."""
        with patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True):
            return OllamaAdapter(model_name="test-model", api_base="http://test-ollama:11434")
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    def test_init(self, mock_verify, mock_env):
        """Test initialization with default and custom parameters."""
        # Default initialization
        adapter = OllamaAdapter()
        assert adapter.model_name == "llama3.2"
        assert adapter.api_base == "http://localhost:11434"
        assert adapter.timeout == 120
        
        # Custom initialization
        adapter = OllamaAdapter(
            model_name="custom-model",
            api_base="http://custom-ollama:11434",
            timeout=60
        )
        assert adapter.model_name == "custom-model"
        assert adapter.api_base == "http://custom-ollama:11434" 
        assert adapter.timeout == 60
        
        # Verify that _verify_connection was called
        assert mock_verify.call_count == 2
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    def test_init_env_vars(self, mock_verify, monkeypatch):
        """Test initialization with environment variables."""
        monkeypatch.setenv("OLLAMA_HOST", "http://env-ollama:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "env-model")
        
        adapter = OllamaAdapter()
        assert adapter.model_name == "env-model"
        assert adapter.api_base == "http://env-ollama:11434"
        assert mock_verify.call_count == 1
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    @patch("requests.post")
    def test_generate(self, mock_post, mock_verify, adapter):
        """Test the generate method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Generated text"}
        mock_post.return_value = mock_response
        
        # Test generate
        result = adapter.generate("Test prompt")
        
        # Assertions
        assert result == "Generated text"
        mock_post.assert_called_once()
        
        # Check the request payload
        call_args = mock_post.call_args[1]
        payload = call_args["json"]
        assert payload["model"] == "test-model"
        assert payload["prompt"] == "Test prompt"
        assert payload["stream"] is False
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    @patch("requests.post")
    def test_generate_with_parameters(self, mock_post, mock_verify, adapter):
        """Test the generate method with parameters."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Generated text with params"}
        mock_post.return_value = mock_response
        
        # Test generate with parameters
        result = adapter.generate(
            "Test prompt", 
            parameters={"temperature": 0.7, "max_tokens": 100}
        )
        
        # Assertions
        assert result == "Generated text with params"
        
        # Check the request payload
        call_args = mock_post.call_args[1]
        payload = call_args["json"]
        assert payload["model"] == "test-model"
        assert payload["prompt"] == "Test prompt"
        assert payload["options"].get("temperature") == 0.7
        assert payload["options"].get("num_predict") == 100
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    @patch("requests.post")
    def test_chat(self, mock_post, mock_verify, adapter):
        """Test the chat method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Chat response"}}
        mock_post.return_value = mock_response
        
        # Test chat
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        result = adapter.chat(messages)
        
        # Assertions
        assert result == "Chat response"
        mock_post.assert_called_once()
        
        # Check the request payload
        call_args = mock_post.call_args[1]
        payload = call_args["json"]
        assert payload["model"] == "test-model"
        assert payload["messages"] == messages
        assert payload["stream"] is False
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    @patch("requests.post")
    @patch("requests.get")
    def test_get_model_info(self, mock_get, mock_post, mock_verify):
        """Test the get_model_info method."""
        # Create adapter
        adapter = OllamaAdapter(model_name="test-model", api_base="http://test-ollama:11434")
        
        # Mock GET response for model list
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "models": [
                {"name": "test-model"},
                {"name": "another-model"}
            ]
        }
        mock_get.return_value = mock_get_response
        
        # Mock POST response for model details
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_info = {
            "license": "MIT",
            "modelfile": "FROM llama3.2",
            "parameters": "7B",
            "template": "{{ .Prompt}}",
            "context": 4096
        }
        mock_post_response.json.return_value = mock_info
        mock_post.return_value = mock_post_response
        
        # Test get_model_info
        result = adapter.get_model_info()
        
        # Assertions
        assert result == mock_info
        
        # Check that requests were made correctly - match the actual implementation
        mock_get.assert_called_once_with("http://test-ollama:11434/api/tags")
        mock_post.assert_called_once()
        
        # Check the POST request payload
        call_args = mock_post.call_args[1]
        payload = call_args["json"]
        assert payload["name"] == "test-model"
    
    @patch("pulp_fiction_generator.models.ollama_adapter.OllamaAdapter._verify_connection", return_value=True)
    @patch("requests.post")
    def test_api_error(self, mock_post, mock_verify, adapter):
        """Test handling of API errors."""
        # Mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"
        mock_post.return_value = mock_response
        
        # Test API error
        with pytest.raises(Exception) as excinfo:
            adapter.generate("Test prompt")
        
        # Check error message contains status code and response text
        error_message = str(excinfo.value)
        assert "404" in error_message
        assert "Model not found" in error_message 