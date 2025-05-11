"""
Unit tests for model plugins.
"""

import pytest
from typing import Dict, List, Any, Type
from unittest.mock import Mock, patch

# Import only the required components
from pulp_fiction_generator.plugins.base import ModelPlugin
from pulp_fiction_generator.plugins.registry import PluginRegistry


class MockModelService:
    """Mock model service for testing."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def generate_text(self, prompt, **kwargs):
        """Mock text generation."""
        return f"Generated text for: {prompt[:20]}..."
    
    def get_embeddings(self, texts):
        """Mock embedding generation."""
        return [[0.1, 0.2, 0.3] for _ in texts]


class TestModelPlugin(ModelPlugin):
    """Test implementation of ModelPlugin for testing."""
    
    plugin_id = "test-model"
    plugin_name = "Test Model"
    plugin_description = "A test model plugin"
    plugin_version = "1.0.0"
    
    def get_model_service(self) -> Type:
        """Get the model service class."""
        return MockModelService
    
    def get_supported_features(self) -> List[str]:
        """Get a list of features supported by this model."""
        return ["text_generation", "embeddings"]
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this model."""
        return {
            "api_key": {"type": "string", "required": True},
            "temperature": {"type": "float", "default": 0.7},
            "max_tokens": {"type": "integer", "default": 1000}
        }


class TestModelPluginImplementation:
    """Tests for model plugin implementation."""
    
    @pytest.fixture
    def model_plugin(self):
        """Create a model plugin instance."""
        return TestModelPlugin()
    
    @pytest.fixture
    def registry(self):
        """Create a plugin registry with the test model plugin registered."""
        registry = PluginRegistry()
        registry.register_plugin(TestModelPlugin)
        return registry
    
    def test_plugin_info(self, model_plugin):
        """Test the plugin info is correctly reported."""
        info = model_plugin.get_plugin_info()
        
        assert info["id"] == "test-model"
        assert info["name"] == "Test Model"
        assert info["description"] == "A test model plugin"
        assert info["version"] == "1.0.0"
        assert info["type"] == "TestModelPlugin"
    
    def test_get_model_service(self, model_plugin):
        """Test getting the model service class."""
        service_class = model_plugin.get_model_service()
        
        assert service_class == MockModelService
        
        # Test instantiating the service
        service = service_class({"api_key": "test-key"})
        assert service.config["api_key"] == "test-key"
    
    def test_get_supported_features(self, model_plugin):
        """Test getting supported features."""
        features = model_plugin.get_supported_features()
        
        assert "text_generation" in features
        assert "embeddings" in features
        assert len(features) == 2
    
    def test_get_configuration_schema(self, model_plugin):
        """Test getting the configuration schema."""
        schema = model_plugin.get_configuration_schema()
        
        assert "api_key" in schema
        assert schema["api_key"]["required"] is True
        
        assert "temperature" in schema
        assert schema["temperature"]["default"] == 0.7
        
        assert "max_tokens" in schema
        assert schema["max_tokens"]["default"] == 1000
    
    def test_registry_integration(self, registry):
        """Test integration with the plugin registry."""
        # Check plugin is registered
        assert "test-model" in registry.plugins
        
        # Get the plugin by ID
        plugin_class = registry.get_plugin("test-model")
        assert plugin_class == TestModelPlugin
        
        # Get all model plugins
        model_plugins = registry.get_model_plugins()
        assert TestModelPlugin in model_plugins
        assert len(model_plugins) == 1


class TestModelPluginUsage:
    """Tests for using model plugins in the application."""
    
    def test_model_service_integration(self):
        """Test integration of model service with the application."""
        plugin = TestModelPlugin()
        model_service_class = plugin.get_model_service()
        
        # Create a model service instance
        model_service = model_service_class({
            "api_key": "test-key",
            "temperature": 0.5
        })
        
        # Test generating text
        generated_text = model_service.generate_text("Create a story about a detective")
        assert "Generated text for:" in generated_text
        
        # Test generating embeddings
        embeddings = model_service.get_embeddings(["text1", "text2"])
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 3  # 3D embeddings in our mock 