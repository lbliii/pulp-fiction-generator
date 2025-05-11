import unittest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.agents.tools.tool_loader import ToolLoader


class TestToolLoader(unittest.TestCase):
    """Tests for the ToolLoader class."""

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_empty_config(self, mock_registry):
        """Test loading tools with an empty configuration."""
        tools = ToolLoader.load_tools([])
        self.assertEqual(tools, [])
        mock_registry.create_tool.assert_not_called()

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_none_config(self, mock_registry):
        """Test loading tools with None configuration."""
        tools = ToolLoader.load_tools(None)
        self.assertEqual(tools, [])
        mock_registry.create_tool.assert_not_called()

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_string_config(self, mock_registry):
        """Test loading tools with string configurations."""
        mock_tool = MagicMock()
        mock_registry.create_tool.return_value = mock_tool
        
        tools = ToolLoader.load_tools(["tool1", "tool2"])
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools, [mock_tool, mock_tool])
        mock_registry.create_tool.assert_any_call("tool1")
        mock_registry.create_tool.assert_any_call("tool2")

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_dict_config(self, mock_registry):
        """Test loading tools with dictionary configurations."""
        mock_tool = MagicMock()
        mock_registry.create_tool.return_value = mock_tool
        
        tools = ToolLoader.load_tools([
            {"name": "tool1", "config": {"param1": "value1"}},
            {"name": "tool2", "config": {"param2": "value2"}}
        ])
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools, [mock_tool, mock_tool])
        mock_registry.create_tool.assert_any_call("tool1", param1="value1")
        mock_registry.create_tool.assert_any_call("tool2", param2="value2")

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_dict_no_config(self, mock_registry):
        """Test loading tools with dictionary configurations without config field."""
        mock_tool = MagicMock()
        mock_registry.create_tool.return_value = mock_tool
        
        tools = ToolLoader.load_tools([{"name": "tool1"}])
        
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools, [mock_tool])
        mock_registry.create_tool.assert_called_once_with("tool1")

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_dict_no_name(self, mock_registry):
        """Test loading tools with dictionary configurations without name field."""
        with self.assertRaises(ValueError):
            ToolLoader.load_tools([{"config": {"param": "value"}}])

    @patch('pulp_fiction_generator.agents.tools.tool_loader.registry')
    def test_load_tools_invalid_type(self, mock_registry):
        """Test loading tools with invalid configuration type."""
        with self.assertRaises(ValueError):
            ToolLoader.load_tools([123])  # Integer is not a valid config type


if __name__ == "__main__":
    unittest.main() 