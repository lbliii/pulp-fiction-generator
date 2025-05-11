"""
Tests for the CrewFactory with custom inputs.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from pulp_fiction_generator.crews.crew_factory import CrewFactory
from crewai import Task, Crew

class TestCrewFactoryCustomInputs(unittest.TestCase):
    """Test case for the CrewFactory class with custom inputs handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock agent factory
        self.agent_factory = Mock()
        
        # Mock the agent creation methods
        self.agent_factory.create_researcher = Mock(return_value=Mock())
        self.agent_factory.create_worldbuilder = Mock(return_value=Mock())
        self.agent_factory.create_character_creator = Mock(return_value=Mock())
        self.agent_factory.create_plotter = Mock(return_value=Mock())
        self.agent_factory.create_writer = Mock(return_value=Mock())
        self.agent_factory.create_editor = Mock(return_value=Mock())
        
        # Create the factory
        self.crew_factory = CrewFactory(
            agent_factory=self.agent_factory,
            verbose=False
        )
    
    def test_create_basic_crew_with_inputs(self):
        """Test that create_basic_crew_with_inputs correctly attaches custom inputs."""
        # Define custom inputs
        custom_inputs = {
            "title": "Test Story",
            "protagonist_name": "Test Hero",
            "setting": "Test World"
        }
        
        # Create a crew with custom inputs
        crew = self.crew_factory.create_basic_crew_with_inputs(
            genre="scifi",
            custom_inputs=custom_inputs
        )
        
        # Assert that custom_inputs are attached to the crew
        self.assertTrue(hasattr(crew, 'custom_inputs'))
        self.assertEqual(crew.custom_inputs, custom_inputs)
    
    def test_create_basic_crew_without_inputs(self):
        """Test that create_basic_crew_with_inputs works without custom inputs."""
        # Create a crew without custom inputs
        crew = self.crew_factory.create_basic_crew_with_inputs(
            genre="fantasy",
            custom_inputs=None
        )
        
        # Assert that custom_inputs attribute is not set
        self.assertFalse(hasattr(crew, 'custom_inputs'))
    
    def test_create_continuation_crew_with_inputs(self):
        """Test that create_continuation_crew correctly handles custom inputs."""
        # Define custom inputs
        custom_inputs = {
            "title": "Test Story Continuation",
            "protagonist_name": "Test Hero",
            "setting": "Test World"
        }
        
        # Create a continuation crew with custom inputs
        crew = self.crew_factory.create_continuation_crew(
            genre="horror",
            previous_output="Previous story content here.",
            custom_inputs=custom_inputs
        )
        
        # Assert that custom_inputs are attached to the crew
        self.assertTrue(hasattr(crew, 'custom_inputs'))
        self.assertEqual(crew.custom_inputs, custom_inputs)
        
        # Assert that previous_output is stored in context
        self.assertTrue(hasattr(crew, 'context'))
        self.assertEqual(crew.context.get('previous_output'), "Previous story content here.")
    
    def test_create_custom_crew_with_inputs(self):
        """Test that create_custom_crew correctly handles custom inputs."""
        # Define custom inputs
        custom_inputs = {
            "title": "Custom Crew Story",
            "protagonist_name": "Custom Hero",
            "setting": "Custom World"
        }
        
        # Define agent types and task descriptions
        agent_types = ["researcher", "writer"]
        task_descriptions = [
            "Research custom elements",
            "Write the custom story"
        ]
        
        # Create a custom crew with custom inputs
        crew = self.crew_factory.create_custom_crew(
            genre="western",
            agent_types=agent_types,
            task_descriptions=task_descriptions,
            custom_inputs=custom_inputs
        )
        
        # Assert that custom_inputs are attached to the crew
        self.assertTrue(hasattr(crew, 'custom_inputs'))
        self.assertEqual(crew.custom_inputs, custom_inputs)
    
    @patch('pulp_fiction_generator.crews.crew_factory.Crew')
    def test_crew_kickoff_with_attached_inputs(self, mock_crew_class):
        """Test that the crew kickoff method is called with attached inputs."""
        # Create a mock crew instance
        mock_crew_instance = MagicMock()
        mock_crew_class.return_value = mock_crew_instance
        
        # Define custom inputs
        custom_inputs = {
            "title": "Test Story",
            "protagonist_name": "Test Hero"
        }
        
        # Create a crew with custom inputs
        crew = self.crew_factory.create_basic_crew_with_inputs(
            genre="mystery",
            custom_inputs=custom_inputs
        )
        
        # Simulate kickoff
        crew.kickoff()
        
        # Verify that kickoff was called with the inputs
        mock_crew_instance.kickoff.assert_called_once_with(inputs=custom_inputs)

if __name__ == '__main__':
    unittest.main() 