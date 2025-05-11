#!/usr/bin/env python
"""
Script to measure code coverage for the plugin system.
This avoids the dependency issues in the test framework.
"""

import sys
from typing import Dict, List, Any, Type

print("Starting plugin system coverage measurement...")

# Direct imports of the plugin system
try:
    from pulp_fiction_generator.plugins.base import BasePlugin, GenrePlugin, AgentPlugin, ModelPlugin
    from pulp_fiction_generator.plugins.registry import PluginRegistry
    from pulp_fiction_generator.plugins.exceptions import PluginRegistrationError, PluginNotFoundError
    print("Successfully imported plugin modules")
except ImportError as e:
    print(f"Error importing plugin modules: {e}")
    sys.exit(1)


# Create a mock model service
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


# Create a test plugin implementation
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


class TestGenrePlugin(GenrePlugin):
    """Test implementation of GenrePlugin for testing."""
    
    plugin_id = "test-genre"
    plugin_name = "Test Genre"
    plugin_description = "A test genre plugin"
    plugin_version = "1.0.0"
    
    def get_prompt_enhancers(self) -> Dict[str, str]:
        """Get prompt enhancers for different agent types."""
        return {"writer": "Write in test genre style"}
    
    def get_character_templates(self) -> List[Dict[str, Any]]:
        """Get character templates for this genre."""
        return [{"name": "Test Character", "role": "Protagonist"}]
    
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        """Get plot templates for this genre."""
        return [{"title": "Test Plot", "synopsis": "A test plot"}]
    
    def get_example_passages(self) -> List[Dict[str, str]]:
        """Get example passages for this genre."""
        return [{"title": "Test Passage", "text": "This is a test passage."}]


def test_plugin_registry():
    """Test the plugin registry functionality."""
    print("Testing plugin registry...")
    
    registry = PluginRegistry()
    print("  Created registry")
    
    # Register plugins
    registry.register_plugin(TestModelPlugin)
    registry.register_plugin(TestGenrePlugin)
    print("  Registered plugins")
    
    # Get all plugins
    all_plugins = registry.get_plugins()
    assert len(all_plugins) == 2
    print("  Retrieved all plugins")
    
    # Get plugins by type
    model_plugins = registry.get_model_plugins()
    genre_plugins = registry.get_genre_plugins()
    assert len(model_plugins) == 1
    assert len(genre_plugins) == 1
    print("  Retrieved plugins by type")
    
    # Get a specific plugin
    model_plugin = registry.get_plugin("test-model")
    assert model_plugin == TestModelPlugin
    print("  Retrieved specific plugin")
    
    # Get plugin info
    plugin_info = model_plugin.get_plugin_info()
    assert plugin_info["id"] == "test-model"
    assert plugin_info["name"] == "Test Model"
    print("  Retrieved plugin info")
    
    # Test registry error handling
    try:
        registry.get_plugin("nonexistent-plugin")
        assert False, "Should have raised PluginNotFoundError"
    except PluginNotFoundError:
        print("  Error handling for missing plugin works")
    
    # Test duplicate registration
    try:
        class DuplicatePlugin(ModelPlugin):
            plugin_id = "test-model"  # Same ID!
            plugin_name = "Duplicate Model"
            plugin_description = "A duplicate plugin"
            
            def get_model_service(self): pass
            def get_supported_features(self): pass
            def get_configuration_schema(self): pass
        
        registry.register_plugin(DuplicatePlugin)
        assert False, "Should have raised PluginRegistrationError"
    except PluginRegistrationError:
        print("  Error handling for duplicate registration works")
    
    print("Plugin registry tests passed!")


def test_model_plugin():
    """Test the model plugin functionality."""
    print("Testing model plugin...")
    
    # Create plugin instance
    plugin = TestModelPlugin()
    print("  Created plugin instance")
    
    # Test plugin API
    service_class = plugin.get_model_service()
    assert service_class == MockModelService
    print("  Retrieved model service class")
    
    features = plugin.get_supported_features()
    assert "text_generation" in features
    assert "embeddings" in features
    print("  Retrieved supported features")
    
    schema = plugin.get_configuration_schema()
    assert "api_key" in schema
    assert schema["api_key"]["required"] is True
    print("  Retrieved configuration schema")
    
    # Test service instantiation
    service = service_class({"api_key": "test-key"})
    assert service.config["api_key"] == "test-key"
    print("  Instantiated service")
    
    # Test service usage
    generated_text = service.generate_text("Create a story about a detective")
    assert "Generated text for:" in generated_text
    print("  Generated text")
    
    embeddings = service.get_embeddings(["text1", "text2"])
    assert len(embeddings) == 2
    print("  Generated embeddings")
    
    print("Model plugin tests passed!")


if __name__ == "__main__":
    print("Testing plugin system functionality...")
    test_plugin_registry()
    test_model_plugin()
    print("All plugin system tests passed!") 