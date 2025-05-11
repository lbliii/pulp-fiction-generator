"""
Unit tests for the plugin system.
"""

import pytest
from typing import Dict, List, Any, Type
from unittest.mock import Mock, patch

from pulp_fiction_generator.plugins.base import BasePlugin, GenrePlugin, AgentPlugin, ModelPlugin
from pulp_fiction_generator.plugins.registry import PluginRegistry
from pulp_fiction_generator.plugins.exceptions import PluginRegistrationError, PluginNotFoundError


class TestPluginRegistry:
    """Tests for the PluginRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh plugin registry for each test."""
        return PluginRegistry()
    
    @pytest.fixture
    def mock_genre_plugin(self):
        """Create a mock genre plugin class."""
        class TestGenrePlugin(GenrePlugin):
            plugin_id = "test-genre"
            plugin_name = "Test Genre"
            plugin_description = "A test genre plugin"
            plugin_version = "1.0.0"
            
            def get_prompt_enhancers(self) -> Dict[str, str]:
                return {"writer": "Write in test genre style"}
            
            def get_character_templates(self) -> List[Dict[str, Any]]:
                return [{"name": "Test Character", "role": "Protagonist"}]
            
            def get_plot_templates(self) -> List[Dict[str, Any]]:
                return [{"title": "Test Plot", "synopsis": "A test plot"}]
            
            def get_example_passages(self) -> List[Dict[str, str]]:
                return [{"title": "Test Passage", "text": "This is a test passage."}]
        
        return TestGenrePlugin
    
    @pytest.fixture
    def mock_agent_plugin(self):
        """Create a mock agent plugin class."""
        class TestAgentPlugin(AgentPlugin):
            plugin_id = "test-agent"
            plugin_name = "Test Agent"
            plugin_description = "A test agent plugin"
            plugin_version = "1.0.0"
            
            def get_agent_class(self) -> Type:
                return Mock
            
            def get_default_config(self) -> Dict[str, Any]:
                return {"temperature": 0.7}
            
            def get_prompt_templates(self) -> Dict[str, str]:
                return {"default": "This is a test prompt template"}
        
        return TestAgentPlugin
    
    def test_register_plugin(self, registry, mock_genre_plugin):
        """Test registering a plugin."""
        registry.register_plugin(mock_genre_plugin)
        
        # Verify the plugin was registered
        assert "test-genre" in registry.plugins
        assert registry.plugins["test-genre"] == mock_genre_plugin
    
    def test_register_duplicate_plugin(self, registry, mock_genre_plugin):
        """Test that registering a duplicate plugin ID raises an error."""
        registry.register_plugin(mock_genre_plugin)
        
        # Create a plugin with the same ID
        class DuplicatePlugin(GenrePlugin):
            plugin_id = "test-genre"  # Same ID!
            plugin_name = "Duplicate Genre"
            plugin_description = "A duplicate plugin"
            
            def get_prompt_enhancers(self): pass
            def get_character_templates(self): pass
            def get_plot_templates(self): pass
            def get_example_passages(self): pass
        
        # Should raise an error
        with pytest.raises(PluginRegistrationError):
            registry.register_plugin(DuplicatePlugin)
    
    def test_get_plugins(self, registry, mock_genre_plugin, mock_agent_plugin):
        """Test getting all plugins."""
        registry.register_plugin(mock_genre_plugin)
        registry.register_plugin(mock_agent_plugin)
        
        plugins = registry.get_plugins()
        
        # Should return all registered plugins
        assert len(plugins) == 2
        assert mock_genre_plugin in plugins
        assert mock_agent_plugin in plugins
    
    def test_get_plugins_by_type(self, registry, mock_genre_plugin, mock_agent_plugin):
        """Test getting plugins filtered by type."""
        registry.register_plugin(mock_genre_plugin)
        registry.register_plugin(mock_agent_plugin)
        
        # Get only genre plugins
        genre_plugins = registry.get_plugins(GenrePlugin)
        
        assert len(genre_plugins) == 1
        assert mock_genre_plugin in genre_plugins
        assert mock_agent_plugin not in genre_plugins
    
    def test_get_plugin(self, registry, mock_genre_plugin):
        """Test getting a specific plugin by ID."""
        registry.register_plugin(mock_genre_plugin)
        
        plugin = registry.get_plugin("test-genre")
        
        assert plugin == mock_genre_plugin
    
    def test_get_plugin_not_found(self, registry):
        """Test that getting a non-existent plugin raises an error."""
        with pytest.raises(PluginNotFoundError):
            registry.get_plugin("nonexistent-plugin")
    
    def test_get_genre_plugins(self, registry, mock_genre_plugin, mock_agent_plugin):
        """Test getting all genre plugins."""
        registry.register_plugin(mock_genre_plugin)
        registry.register_plugin(mock_agent_plugin)
        
        genre_plugins = registry.get_genre_plugins()
        
        assert len(genre_plugins) == 1
        assert mock_genre_plugin in genre_plugins
    
    def test_get_agent_plugins(self, registry, mock_genre_plugin, mock_agent_plugin):
        """Test getting all agent plugins."""
        registry.register_plugin(mock_genre_plugin)
        registry.register_plugin(mock_agent_plugin)
        
        agent_plugins = registry.get_agent_plugins()
        
        assert len(agent_plugins) == 1
        assert mock_agent_plugin in agent_plugins


class TestPluginBaseClasses:
    """Tests for the plugin base classes."""
    
    def test_base_plugin_info(self):
        """Test the get_plugin_info method of BasePlugin."""
        class TestPlugin(GenrePlugin):
            plugin_id = "test-plugin"
            plugin_name = "Test Plugin"
            plugin_description = "A test plugin"
            plugin_version = "1.2.3"
            
            # Abstract methods implementation
            def get_prompt_enhancers(self): return {}
            def get_character_templates(self): return []
            def get_plot_templates(self): return []
            def get_example_passages(self): return []
        
        # Get the plugin info
        info = TestPlugin.get_plugin_info()
        
        assert info["id"] == "test-plugin"
        assert info["name"] == "Test Plugin"
        assert info["description"] == "A test plugin"
        assert info["version"] == "1.2.3"
        assert info["type"] == "TestPlugin"
    
    def test_plugin_metaclass_validation(self):
        """Test that the plugin metaclass validates required attributes."""
        # Should raise TypeError for missing required attributes
        with pytest.raises(TypeError):
            class InvalidPlugin(GenrePlugin):
                # Missing plugin_id, plugin_name, plugin_description
                
                def get_prompt_enhancers(self): pass
                def get_character_templates(self): pass
                def get_plot_templates(self): pass
                def get_example_passages(self): pass


class TestPluginManager:
    """Tests for plugin manager functionality (loading plugins)."""
    
    @patch('pulp_fiction_generator.plugins.manager.importlib.import_module')
    def test_plugin_discovery(self, mock_import_module):
        """Test discovering plugins from directories."""
        from pulp_fiction_generator.plugins.manager import discover_plugins
        
        # Mock the imported module
        mock_module = Mock()
        mock_import_module.return_value = mock_module
        
        # Create a mock plugin class
        class MockPlugin(GenrePlugin):
            plugin_id = "mock-plugin"
            plugin_name = "Mock Plugin"
            plugin_description = "A mock plugin"
            
            def get_prompt_enhancers(self): return {}
            def get_character_templates(self): return []
            def get_plot_templates(self): return []
            def get_example_passages(self): return []
        
        # Add the plugin to the mocked module
        mock_module.MockPlugin = MockPlugin
        
        # Mock the file search results
        with patch('os.listdir', return_value=['plugin_module.py']):
            with patch('os.path.isfile', return_value=True):
                registry = PluginRegistry()
                discover_plugins(['test_dir'], registry)
        
        # Check that the plugin was registered
        assert len(registry.plugins) == 1
        assert "mock-plugin" in registry.plugins 