"""
Unit tests for the configuration system.
"""

import os
import pytest
from pathlib import Path
import tempfile
import yaml

from pulp_fiction_generator.utils.config import Config, OllamaConfig, AppConfig


class TestConfig:
    """Tests for the configuration system."""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Clear environment variables for testing."""
        env_vars = [
            "OLLAMA_HOST", "OLLAMA_MODEL", "OLLAMA_THREADS", "OLLAMA_GPU_LAYERS",
            "OLLAMA_CTX_SIZE", "OLLAMA_BATCH_SIZE", "DEBUG", "LOG_LEVEL",
            "OUTPUT_DIR", "GENRES_DIR", "MAX_RETRY_COUNT", "GENERATION_TIMEOUT",
            "TEMPERATURE", "TOP_P", "ENABLE_AGENT_DELEGATION", "AGENT_VERBOSE",
            "ENABLE_CACHE", "CACHE_DIR", "MAX_CACHE_SIZE"
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary configuration file."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            config_data = {
                "ollama": {
                    "model": "test-model",
                    "threads": 16
                },
                "app": {
                    "debug": True,
                    "log_level": "debug"
                }
            }
            tmp.write(yaml.dump(config_data).encode('utf-8'))
            tmp.flush()
            yield Path(tmp.name)
            os.unlink(tmp.name)
    
    def test_default_config(self, mock_env):
        """Test that default configuration is loaded correctly."""
        config = Config()
        
        # Check default values
        assert config.ollama.host == "http://localhost:11434"
        assert config.ollama.model == "llama3.2"
        assert config.ollama.threads == 8
        assert config.app.debug is False
        assert config.app.log_level == "info"
        assert config.generation.temperature == 0.7
    
    def test_env_override(self, mock_env, monkeypatch):
        """Test that environment variables override defaults."""
        # Set environment variables
        monkeypatch.setenv("OLLAMA_MODEL", "env-model")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("TEMPERATURE", "0.9")
        
        config = Config()
        
        # Check overridden values
        assert config.ollama.model == "env-model"
        assert config.app.debug is True
        assert config.generation.temperature == 0.9
        
        # Check that other values are still defaults
        assert config.ollama.host == "http://localhost:11434"
        assert config.ollama.threads == 8
    
    def test_config_file(self, mock_env, temp_config_file):
        """Test loading configuration from a file."""
        # Create a config that will use our temp file
        config = Config()
        config._config_paths = [temp_config_file]
        config.load_from_file()
        
        # Check values from the file
        assert config.ollama.model == "test-model"
        assert config.ollama.threads == 16
        assert config.app.debug is True
        assert config.app.log_level == "debug"
        
        # Check that other values are still defaults
        assert config.ollama.host == "http://localhost:11434"
        assert config.generation.temperature == 0.7
    
    def test_config_validation(self, monkeypatch):
        """Test configuration validation."""
        # Mock Path.exists to always return True for directory checks
        original_exists = Path.exists
        def mock_exists(self):
            return True
        monkeypatch.setattr(Path, "exists", mock_exists)
        
        config = Config()
        
        # Valid configuration should have no errors
        assert not config.validate()
        
        # Test invalid log level
        config.app.log_level = "invalid"
        errors = config.validate()
        assert errors
        assert any("log level" in error.lower() for error in errors)
        
        # Test invalid temperature
        config.app.log_level = "info"  # Reset to valid
        config.generation.temperature = 3.0
        errors = config.validate()
        assert errors
        assert any("temperature" in error.lower() for error in errors)
    
    def test_get_ollama_params(self):
        """Test getting Ollama parameters."""
        config = Config()
        config.ollama.threads = 12
        config.ollama.gpu_layers = 24
        
        params = config.get_ollama_params()
        assert params["num_thread"] == 12
        assert params["num_gpu"] == 24
        assert params["num_ctx"] == 8192
        assert params["num_batch"] == 512
    
    def test_plugin_config(self):
        """Test plugin configuration."""
        config = Config()
        
        # Add plugin config
        plugin_config = {
            "test-plugin": {
                "option1": "value1",
                "option2": 123
            }
        }
        config._additional = plugin_config
        
        # Get plugin config
        plugin = config.get_plugin_config("test-plugin")
        assert plugin["option1"] == "value1"
        assert plugin["option2"] == 123
        
        # Non-existent plugin should return empty dict
        assert config.get_plugin_config("non-existent") == {}
    
    def test_save_and_load(self, mock_env, tmp_path):
        """Test saving and loading configuration."""
        config_path = tmp_path / "test_config.yaml"
        
        # Create and modify a config
        config = Config()
        config.ollama.model = "saved-model"
        config.app.debug = True
        
        # Save it
        config.save_to_file(config_path)
        
        # Create a new config and load from the file
        new_config = Config()
        new_config._config_paths = [config_path]
        new_config.load_from_file()
        
        # Check that values were loaded correctly
        assert new_config.ollama.model == "saved-model"
        assert new_config.app.debug is True 