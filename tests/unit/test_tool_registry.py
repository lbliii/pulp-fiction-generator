import unittest
from unittest.mock import MagicMock

from pulp_fiction_generator.agents.tools.tool_registry import ToolRegistry


class TestToolClass:
    """Dummy tool class for testing."""
    def __init__(self, config=None):
        self.config = config or {}


def test_tool_factory(**kwargs):
    """Dummy tool factory function for testing."""
    # This function is used as a factory in tests, so it needs to return a value
    return TestToolClass(**kwargs)


# Stand-alone test function to test the factory
def test_the_tool_factory():
    """Test the test_tool_factory function."""
    tool = test_tool_factory(config={"test": "value"})
    assert isinstance(tool, TestToolClass)
    assert tool.config == {"test": "value"}


class TestToolRegistry(unittest.TestCase):
    """Tests for the ToolRegistry class."""

    def setUp(self):
        """Set up a fresh registry for each test."""
        self.registry = ToolRegistry()

    def test_register_tool(self):
        """Test registering a tool class."""
        self.registry.register_tool("test_tool", TestToolClass)
        self.assertEqual(self.registry.get_tool_class("test_tool"), TestToolClass)

    def test_register_tool_factory(self):
        """Test registering a tool factory function."""
        self.registry.register_tool_factory("test_factory", test_tool_factory)
        self.assertEqual(self.registry.get_tool_factory("test_factory"), test_tool_factory)

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        self.assertIsNone(self.registry.get_tool_class("nonexistent"))
        self.assertIsNone(self.registry.get_tool_factory("nonexistent"))

    def test_create_tool_from_class(self):
        """Test creating a tool from a registered class."""
        self.registry.register_tool("test_tool", TestToolClass)
        tool = self.registry.create_tool("test_tool", config={"param": "value"})
        self.assertIsInstance(tool, TestToolClass)
        self.assertEqual(tool.config, {"param": "value"})

    def test_create_tool_from_factory(self):
        """Test creating a tool from a registered factory function."""
        self.registry.register_tool_factory("test_factory", test_tool_factory)
        tool = self.registry.create_tool("test_factory", config={"param": "value"})
        self.assertIsInstance(tool, TestToolClass)
        self.assertEqual(tool.config, {"param": "value"})

    def test_create_nonexistent_tool(self):
        """Test creating a tool that doesn't exist."""
        with self.assertRaises(ValueError):
            self.registry.create_tool("nonexistent")

    def test_list_tools(self):
        """Test listing registered tools."""
        self.registry.register_tool("test_tool", TestToolClass)
        self.registry.register_tool_factory("test_factory", test_tool_factory)
        tools = self.registry.list_tools()
        self.assertIn("test_tool", tools)
        self.assertIn("test_factory", tools)


if __name__ == "__main__":
    unittest.main() 