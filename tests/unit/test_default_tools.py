import unittest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.agents.tools.default_tools import register_default_tools
from pulp_fiction_generator.agents.tools.web_search import WebSearchTool, create_web_search_tool


class TestDefaultTools(unittest.TestCase):
    """Tests for the default tools functionality."""

    @patch('pulp_fiction_generator.agents.tools.default_tools.registry')
    def test_register_default_tools(self, mock_registry):
        """Test registration of default tools."""
        # Call the function to register default tools
        register_default_tools()
        
        # Verify that the registry's register_tool method was called for web_search
        mock_registry.register_tool.assert_any_call("web_search", WebSearchTool)
        
        # Verify that the registry's register_tool_factory method was called for web_search
        mock_registry.register_tool_factory.assert_any_call("web_search", create_web_search_tool)


if __name__ == "__main__":
    unittest.main() 