import unittest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.agents.knowledge.knowledge_loader import KnowledgeLoader


class TestKnowledgeLoader(unittest.TestCase):
    """Tests for the KnowledgeLoader class."""

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_empty_config(self, mock_registry):
        """Test loading knowledge sources with an empty configuration."""
        sources = KnowledgeLoader.load_sources([])
        self.assertEqual(sources, [])
        mock_registry.create_source.assert_not_called()

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_none_config(self, mock_registry):
        """Test loading knowledge sources with None configuration."""
        sources = KnowledgeLoader.load_sources(None)
        self.assertEqual(sources, [])
        mock_registry.create_source.assert_not_called()

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_string_config(self, mock_registry):
        """Test loading knowledge sources with string configurations."""
        mock_source = MagicMock()
        mock_registry.create_source.return_value = mock_source
        
        sources = KnowledgeLoader.load_sources(["source1", "source2"])
        
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources, [mock_source, mock_source])
        mock_registry.create_source.assert_any_call("source1")
        mock_registry.create_source.assert_any_call("source2")

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_dict_config(self, mock_registry):
        """Test loading knowledge sources with dictionary configurations."""
        mock_source = MagicMock()
        mock_registry.create_source.return_value = mock_source
        
        sources = KnowledgeLoader.load_sources([
            {"name": "source1", "config": {"param1": "value1"}},
            {"name": "source2", "config": {"param2": "value2"}}
        ])
        
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources, [mock_source, mock_source])
        mock_registry.create_source.assert_any_call("source1", param1="value1")
        mock_registry.create_source.assert_any_call("source2", param2="value2")

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_dict_no_config(self, mock_registry):
        """Test loading knowledge sources with dictionary configurations without config field."""
        mock_source = MagicMock()
        mock_registry.create_source.return_value = mock_source
        
        sources = KnowledgeLoader.load_sources([{"name": "source1"}])
        
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources, [mock_source])
        mock_registry.create_source.assert_called_once_with("source1")

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_dict_no_name(self, mock_registry):
        """Test loading knowledge sources with dictionary configurations without name field."""
        with self.assertRaises(ValueError):
            KnowledgeLoader.load_sources([{"config": {"param": "value"}}])

    @patch('pulp_fiction_generator.agents.knowledge.knowledge_loader.registry')
    def test_load_sources_invalid_type(self, mock_registry):
        """Test loading knowledge sources with invalid configuration type."""
        with self.assertRaises(ValueError):
            KnowledgeLoader.load_sources([123])  # Integer is not a valid config type


if __name__ == "__main__":
    unittest.main() 