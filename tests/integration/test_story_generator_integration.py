"""
Integration tests for the StoryGenerator with real components.
"""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch

from pulp_fiction_generator.story import StoryGenerator, StoryArtifacts
from pulp_fiction_generator.story.tasks import TaskFactory
from pulp_fiction_generator.crews import CrewFactory
from pulp_fiction_generator.agents import AgentFactory


@pytest.mark.integration
class TestStoryGeneratorIntegration:
    """Integration tests for StoryGenerator."""
    
    @pytest.fixture
    def agent_factory(self):
        """Create a mock agent factory."""
        mock_factory = Mock()
        mock_factory.create_researcher = Mock(return_value=Mock())
        mock_factory.create_worldbuilder = Mock(return_value=Mock())
        mock_factory.create_character_creator = Mock(return_value=Mock())
        mock_factory.create_plotter = Mock(return_value=Mock())
        mock_factory.create_writer = Mock(return_value=Mock())
        mock_factory.create_editor = Mock(return_value=Mock())
        return mock_factory
    
    @pytest.fixture
    def crew_factory(self, agent_factory):
        """Create a real CrewFactory with mocked methods."""
        mock_factory = Mock(spec=CrewFactory)
        mock_factory.agent_factory = agent_factory
        
        # Create a mock crew
        mock_crew = MagicMock()
        mock_crew.kickoff = Mock(return_value="This is a complete story.")
        
        # Set create_basic_crew to return the mock crew
        mock_factory.create_basic_crew = Mock(return_value=mock_crew)
        
        return mock_factory
    
    @pytest.fixture
    def task_factory(self, agent_factory):
        """Create a mock task factory."""
        mock_factory = Mock(spec=TaskFactory)
        mock_factory.agent_factory = agent_factory
        
        # Create a mock task
        mock_task = MagicMock()
        mock_task.name = "mock_task"
        
        # Configure all task creation methods to return the mock task
        mock_factory.create_research_task = Mock(return_value=mock_task)
        mock_factory.create_worldbuilding_task = Mock(return_value=mock_task)
        mock_factory.create_character_task = Mock(return_value=mock_task)
        mock_factory.create_plot_task = Mock(return_value=mock_task)
        mock_factory.create_writing_task = Mock(return_value=mock_task)
        mock_factory.create_editing_task = Mock(return_value=mock_task)
        mock_factory.create_research_subtasks = Mock(return_value=[mock_task, mock_task, mock_task])
        
        return mock_factory
    
    @pytest.fixture
    def story_generator(self, crew_factory, task_factory):
        """Create a real StoryGenerator with mocked components."""
        generator = StoryGenerator(
            crew_factory=crew_factory,
            task_factory=task_factory
        )
        
        # Replace the execute methods with mocks to avoid actual LLM calls
        generator.execution_engine.execute_crew = Mock(return_value="This is a complete story.")
        generator.execution_engine.execute_task = Mock(return_value="This is task output.")
        
        return generator
    
    def test_story_artifacts_creation(self):
        """Test that StoryArtifacts can be created and manipulated."""
        artifacts = StoryArtifacts(
            genre="noir",
            title="The Long Goodbye"
        )
        
        # Test artifact property setting
        artifacts.research = "Research on noir detective fiction"
        artifacts.worldbuilding = "Description of the seedy underworld"
        artifacts.characters = "Detective, femme fatale, villain"
        artifacts.plot = "Murder mystery with twists"
        artifacts.draft = "Initial draft of the story"
        artifacts.final_story = "Polished final story"
        
        # Test is_complete property
        assert artifacts.is_complete is True
        
        # Test what happens when a field is missing
        artifacts.plot = None
        assert artifacts.is_complete is False
    
    def test_story_generator_with_real_components(self, story_generator, crew_factory):
        """Test that the StoryGenerator works with real components."""
        # Generate a story using the simple approach
        result = story_generator.generate_story(genre="noir")
        assert result == "This is a complete story."
        
        # Verify the crew factory was called correctly
        crew_factory.create_basic_crew.assert_called_once_with(genre="noir", config=None, custom_inputs=None)
        
        # Test chunked story generation with patches to avoid process methods
        with patch.object(story_generator, '_process_research_phase') as mock_research:
            with patch.object(story_generator, '_process_worldbuilding_phase') as mock_worldbuilding:
                with patch.object(story_generator, '_process_character_phase') as mock_character:
                    with patch.object(story_generator, '_process_plot_phase') as mock_plot:
                        with patch.object(story_generator, '_process_draft_phase') as mock_draft:
                            with patch.object(story_generator, '_process_final_phase') as mock_final:
                                
                                # Set up side effects to modify artifacts
                                def add_to_artifacts(genre, chapter_num, project_dir, callback, state, artifacts, timeout_seconds, field_name):
                                    setattr(artifacts, field_name, "This is test output.")
                                    # Create a mock task with the right properties instead of calling callback directly
                                    mock_task = MagicMock()
                                    mock_task.name = field_name
                                    mock_task.output = MagicMock()
                                    mock_task.output.raw = "This is test output."
                                    callback(mock_task)
                                
                                # Configure side effects
                                mock_research.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="research")
                                mock_worldbuilding.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="worldbuilding")
                                mock_character.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="characters")
                                mock_plot.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="plot")
                                mock_draft.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="draft")
                                mock_final.side_effect = lambda *args, **kwargs: add_to_artifacts(*args, **kwargs, field_name="final_story")
                                
                                # Collect callback results
                                chunks = []
                                def callback(task_type, content):
                                    chunks.append((task_type, content))
                                
                                # Generate chunked story
                                artifacts = story_generator.generate_story_chunked(
                                    genre="noir",
                                    custom_inputs={"title": "The Big Sleep"},
                                    chunk_callback=callback
                                )
                                
                                # Verify the artifacts
                                assert isinstance(artifacts, StoryArtifacts)
                                assert artifacts.genre == "noir"
                                assert artifacts.title == "The Big Sleep"
                                assert artifacts.research == "This is test output."
                                
                                # Verify all phases were processed
                                assert mock_research.call_count == 1
                                assert mock_worldbuilding.call_count == 1
                                assert mock_character.call_count == 1
                                assert mock_plot.call_count == 1
                                assert mock_draft.call_count == 1
                                assert mock_final.call_count == 1
                                
                                # Verify the callbacks were called
                                assert len(chunks) == 6  # One for each phase
                                phase_names = [chunk[0] for chunk in chunks]
                                assert "research" in phase_names
                                assert "worldbuilding" in phase_names
                                assert "characters" in phase_names
                                assert "plot" in phase_names
                                assert "draft" in phase_names
                                assert "final_story" in phase_names
    
    def test_story_state_persistence(self, story_generator, tmpdir):
        """Test that story state can be persisted and retrieved."""
        # Configure the state manager to use the temporary directory
        story_generator.state_manager.base_dir = str(tmpdir)
        
        # Set up a test task output
        story_generator.state_manager.add_task_output("research", 1, "Test research content")
        
        # Verify it was saved
        assert os.path.exists(os.path.join(str(tmpdir), "default_project", "chapter_1", "research.txt"))
        
        # Verify it can be retrieved
        assert story_generator.state_manager.has_completed_task("research", 1) is True
        assert story_generator.state_manager.get_task_output("research", 1) == "Test research content"
        
        # Test setting project directory
        story_generator.state_manager.set_project_directory("Test Story")
        assert story_generator.state_manager.project_dir == "test_story" 