import unittest
from unittest.mock import patch, MagicMock

from pulp_fiction_generator.agents.knowledge.genre_database import GenreDatabaseKnowledge
from pulp_fiction_generator.agents.tools.web_search import WebSearchTool
from pulp_fiction_generator.agents.knowledge.knowledge_registry import registry as knowledge_registry
from pulp_fiction_generator.agents.tools.tool_registry import registry as tool_registry
from pulp_fiction_generator.agents.knowledge.default_sources import register_default_sources
from pulp_fiction_generator.agents.tools.default_tools import register_default_tools
from pulp_fiction_generator.agents.knowledge.knowledge_loader import KnowledgeLoader
from pulp_fiction_generator.agents.tools.tool_loader import ToolLoader


class TestAgentKnowledgeToolsIntegration(unittest.TestCase):
    """Integration tests for agent knowledge sources and tools working together."""

    def setUp(self):
        """Set up the test environment."""
        # Clear the registries
        knowledge_registry._sources = {}
        knowledge_registry._factories = {}
        tool_registry._tools = {}
        tool_registry._factories = {}
        
        # Register default sources and tools
        register_default_sources()
        register_default_tools()
        
        # Create a mock agent that will use both knowledge sources and tools
        self.agent = MagicMock()

    def test_agent_with_knowledge_and_tools(self):
        """Test an agent using both knowledge sources and tools."""
        # Load knowledge sources
        knowledge_sources = KnowledgeLoader.load_sources([
            {"name": "genre_database", "config": {"genre": "noir"}}
        ])
        
        # Load tools
        tools = ToolLoader.load_tools([
            {"name": "web_search", "config": {"search_engine": "bing"}}
        ])
        
        # Verify knowledge sources were loaded correctly
        self.assertEqual(len(knowledge_sources), 1)
        self.assertIsInstance(knowledge_sources[0], GenreDatabaseKnowledge)
        self.assertEqual(knowledge_sources[0].genre, "noir")
        
        # Verify tools were loaded correctly
        self.assertEqual(len(tools), 1)
        self.assertIsInstance(tools[0], WebSearchTool)
        self.assertEqual(tools[0].search_engine, "bing")
        
        # Assign knowledge sources and tools to the agent
        self.agent.knowledge_sources = knowledge_sources
        self.agent.tools = tools
        
        # Verify agent has access to the correct knowledge sources and tools
        self.assertEqual(len(self.agent.knowledge_sources), 1)
        self.assertEqual(len(self.agent.tools), 1)
        self.assertIsInstance(self.agent.knowledge_sources[0], GenreDatabaseKnowledge)
        self.assertIsInstance(self.agent.tools[0], WebSearchTool)

    def test_load_from_config(self):
        """Test loading both knowledge sources and tools from a combined configuration."""
        # Define a combined configuration
        config = {
            "knowledge_sources": [
                {"name": "genre_database", "config": {"genre": "sci-fi"}}
            ],
            "tools": [
                {"name": "web_search", "config": {"search_engine": "google"}}
            ]
        }
        
        # Load knowledge sources and tools from the configuration
        knowledge_sources = KnowledgeLoader.load_sources(config.get("knowledge_sources", []))
        tools = ToolLoader.load_tools(config.get("tools", []))
        
        # Verify knowledge sources were loaded correctly
        self.assertEqual(len(knowledge_sources), 1)
        self.assertIsInstance(knowledge_sources[0], GenreDatabaseKnowledge)
        self.assertEqual(knowledge_sources[0].genre, "sci-fi")
        
        # Verify tools were loaded correctly
        self.assertEqual(len(tools), 1)
        self.assertIsInstance(tools[0], WebSearchTool)
        self.assertEqual(tools[0].search_engine, "google")

    def test_tool_with_knowledge_interaction(self):
        """Test the interaction between a tool and a knowledge source."""
        # Create a mock web search tool directly
        mock_tool = MagicMock()
        mock_tool._run.return_value = "Search results for: noir fiction tropes"
        
        # Create knowledge source
        knowledge = GenreDatabaseKnowledge(genre="noir")
        
        # Knowledge source provides content
        content = knowledge.load_content()
        genre_info = content[f"genre_{knowledge.genre}"]
        
        # Use the mock tool with knowledge from the knowledge source
        search_query = f"Find more information about: {genre_info}"
        search_result = mock_tool._run(search_query)
        
        # Verify the tool was called with the correct query
        mock_tool._run.assert_called_once_with(search_query)
        self.assertEqual(search_result, "Search results for: noir fiction tropes")
        self.assertIn("Noir", search_query)
        self.assertIn("cynicism", search_query)


if __name__ == "__main__":
    unittest.main() 