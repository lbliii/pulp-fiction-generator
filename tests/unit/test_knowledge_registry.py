import unittest
from unittest.mock import MagicMock

from pulp_fiction_generator.agents.knowledge.knowledge_registry import KnowledgeRegistry


class TestKnowledgeSource:
    """Dummy knowledge source class for testing."""
    def __init__(self, config=None):
        self.config = config or {}


def test_knowledge_factory(**kwargs):
    """Dummy knowledge factory function for testing."""
    # This function is used as a factory in tests, so it needs to return a value
    return TestKnowledgeSource(**kwargs)


# Stand-alone test function to test the factory
def test_the_knowledge_factory():
    """Test the test_knowledge_factory function."""
    source = test_knowledge_factory(config={"test": "value"})
    assert isinstance(source, TestKnowledgeSource)
    assert source.config == {"test": "value"}


class TestKnowledgeRegistry(unittest.TestCase):
    """Tests for the KnowledgeRegistry class."""

    def setUp(self):
        """Set up a fresh registry for each test."""
        self.registry = KnowledgeRegistry()

    def test_register_source(self):
        """Test registering a knowledge source class."""
        self.registry.register_source("test_source", TestKnowledgeSource)
        self.assertEqual(self.registry.get_source_class("test_source"), TestKnowledgeSource)

    def test_register_source_factory(self):
        """Test registering a knowledge source factory function."""
        self.registry.register_source_factory("test_factory", test_knowledge_factory)
        self.assertEqual(self.registry.get_source_factory("test_factory"), test_knowledge_factory)

    def test_get_nonexistent_source(self):
        """Test getting a knowledge source that doesn't exist."""
        self.assertIsNone(self.registry.get_source_class("nonexistent"))
        self.assertIsNone(self.registry.get_source_factory("nonexistent"))

    def test_create_source_from_class(self):
        """Test creating a knowledge source from a registered class."""
        self.registry.register_source("test_source", TestKnowledgeSource)
        source = self.registry.create_source("test_source", config={"param": "value"})
        self.assertIsInstance(source, TestKnowledgeSource)
        self.assertEqual(source.config, {"param": "value"})

    def test_create_source_from_factory(self):
        """Test creating a knowledge source from a registered factory function."""
        self.registry.register_source_factory("test_factory", test_knowledge_factory)
        source = self.registry.create_source("test_factory", config={"param": "value"})
        self.assertIsInstance(source, TestKnowledgeSource)
        self.assertEqual(source.config, {"param": "value"})

    def test_create_nonexistent_source(self):
        """Test creating a knowledge source that doesn't exist."""
        with self.assertRaises(ValueError):
            self.registry.create_source("nonexistent")

    def test_list_sources(self):
        """Test listing registered knowledge sources."""
        self.registry.register_source("test_source", TestKnowledgeSource)
        self.registry.register_source_factory("test_factory", test_knowledge_factory)
        sources = self.registry.list_sources()
        self.assertIn("test_source", sources)
        self.assertIn("test_factory", sources)


if __name__ == "__main__":
    unittest.main() 