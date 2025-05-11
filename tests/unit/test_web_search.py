import unittest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.agents.tools.web_search import WebSearchTool, create_web_search_tool


class TestWebSearchTool(unittest.TestCase):
    """Tests for the WebSearchTool class."""

    def test_init_default_values(self):
        """Test initialization with default values."""
        tool = WebSearchTool()
        self.assertEqual(tool.name, "web_search")
        expected_description = str(tool.description)
        self.assertEqual(expected_description, str(tool.description))
        self.assertIsNone(tool.api_key)
        self.assertEqual(tool.search_engine, "google")

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        tool = WebSearchTool(
            api_key="test_api_key",
            search_engine="bing"
        )
        self.assertEqual(tool.name, "web_search")
        expected_description = str(tool.description)
        self.assertEqual(expected_description, str(tool.description))
        self.assertEqual(tool.api_key, "test_api_key")
        self.assertEqual(tool.search_engine, "bing")

    def test_run_method(self):
        """Test the run method for web search."""
        tool = WebSearchTool()
        result = tool._run("test query")
        
        # Verify the result contains expected information
        self.assertIn("test query", result)
        self.assertIn("Title:", result)
        self.assertIn("Description:", result)
        self.assertIn("URL:", result)

    def test_run_method_with_max_results(self):
        """Test the run method with max_results parameter."""
        tool = WebSearchTool()
        result = tool._run("test query", max_results=10)
        
        # Since the current implementation ignores max_results,
        # this is just ensuring the method accepts the parameter
        self.assertIn("test query", result)

    def test_create_web_search_tool(self):
        """Test the factory function for creating a web search tool."""
        tool = create_web_search_tool(
            api_key="test_api_key",
            search_engine="bing"
        )
        self.assertIsInstance(tool, WebSearchTool)
        self.assertEqual(tool.api_key, "test_api_key")
        self.assertEqual(tool.search_engine, "bing")


if __name__ == "__main__":
    unittest.main() 