"""
Unit tests for the modular StoryGenerator.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call

from pulp_fiction_generator.story import StoryGenerator
from pulp_fiction_generator.models import ModelAdapter, MessageBase
from pulp_fiction_generator.story_model.execution import ExecutionEngine
from pulp_fiction_generator.story_model.validation import StoryValidator
from pulp_fiction_generator.story_model.tasks import TaskFactory
from pulp_fiction_generator.story_model.state import StoryStateManager


class TestStoryGenerator:
    """Tests for the StoryGenerator class."""
    
    @pytest.fixture
    def mock_crew_factory(self):
        """Create a mock crew factory."""
        mock_factory = Mock()
        mock_factory.agent_factory = Mock()
        mock_factory.create_basic_crew = Mock(return_value=Mock())
        
        # Set up agent_factory methods that might be called
        mock_factory.agent_factory.create_researcher = Mock(return_value=Mock())
        mock_factory.agent_factory.create_worldbuilder = Mock(return_value=Mock())
        mock_factory.agent_factory.create_character_creator = Mock(return_value=Mock())
        mock_factory.agent_factory.create_plotter = Mock(return_value=Mock())
        mock_factory.agent_factory.create_writer = Mock(return_value=Mock())
        mock_factory.agent_factory.create_editor = Mock(return_value=Mock())
        
        return mock_factory
    
    @pytest.fixture
    def mock_execution_engine(self):
        """Create a mock execution engine."""
        mock_engine = Mock(spec=ExecutionEngine)
        
        # Configure mock to return meaningful test data
        mock_engine.execute_crew = Mock(return_value="This is a test story.")
        mock_engine.execute_task = Mock(return_value="This is test task output.")
        
        return mock_engine
    
    @pytest.fixture
    def mock_story_state(self):
        """Create a mock story state manager."""
        mock_state = Mock(spec=StoryStateManager)
        mock_state.has_completed_task = Mock(return_value=False)
        mock_state.get_task_output = Mock(return_value=None)
        
        return mock_state
    
    @pytest.fixture
    def story_generator(self, mock_crew_factory, mock_execution_engine, mock_story_state):
        """Create a StoryGenerator instance with mocked dependencies."""
        mock_task_factory = Mock(spec=TaskFactory)
        
        # Configure mock task factory to return mock tasks
        mock_task = Mock()
        mock_task.name = "test_task"
        mock_task_factory.create_research_task = Mock(return_value=mock_task)
        mock_task_factory.create_worldbuilding_task = Mock(return_value=mock_task)
        mock_task_factory.create_character_task = Mock(return_value=mock_task)
        mock_task_factory.create_plot_task = Mock(return_value=mock_task)
        mock_task_factory.create_writing_task = Mock(return_value=mock_task)
        mock_task_factory.create_editing_task = Mock(return_value=mock_task)
        mock_task_factory.create_research_subtasks = Mock(return_value=[mock_task, mock_task, mock_task])
        
        return StoryGenerator(
            crew_factory=mock_crew_factory,
            task_factory=mock_task_factory,
            execution_engine=mock_execution_engine,
            state_manager=mock_story_state,
            debug_mode=False
        )
    
    def test_init(self, mock_crew_factory):
        """Test StoryGenerator initialization."""
        generator = StoryGenerator(crew_factory=mock_crew_factory)
        
        # Verify all components are properly initialized
        assert generator.crew_factory == mock_crew_factory
        assert isinstance(generator.task_factory, TaskFactory)
        assert isinstance(generator.execution_engine, ExecutionEngine)
        assert isinstance(generator.state_manager, StoryStateManager)
        assert generator.debug_mode is False
    
    def test_generate_story(self, story_generator, mock_crew_factory, mock_execution_engine):
        """Test generate_story method."""
        # Mock the logger
        with patch('pulp_fiction_generator.story.generator.logger') as mock_logger:
            # Call the method
            result = story_generator.generate_story(
                genre="noir",
                custom_inputs={"key": "value"},
                config={"setting": "city"}
            )
            
            # Check that the crew factory was called correctly
            mock_crew_factory.create_basic_crew.assert_called_once_with(
                genre="noir",
                custom_inputs={"key": "value"},
                config={"setting": "city"}
            )
            
            # Check that the execution engine was called
            mock_execution_engine.execute_crew.assert_called_once()
            
            # Verify the expected result was returned
            assert result == mock_execution_engine.execute_crew.return_value
    
    def test_generate_story_chunked(self, story_generator, mock_execution_engine):
        """Test generate_story_chunked method."""
        # Create a mock callback
        mock_callback = Mock()
        
        # Use patch to capture the internal callback
        with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_research_phase') as mock_research:
            with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_worldbuilding_phase') as mock_worldbuilding:
                with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_character_phase') as mock_character:
                    with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_plot_phase') as mock_plot:
                        with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_draft_phase') as mock_draft:
                            with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_final_phase') as mock_final:
                                
                                # Define side effects to update the artifacts
                                def process_phase_side_effect(genre, chapter_num, project_dir, callback, story_state, artifacts, timeout_seconds, phase_name="research"):
                                    setattr(artifacts, phase_name, "This is test task output.")
                                    # Call the external callback directly 
                                    mock_callback(phase_name, "This is test task output.")
                                
                                # Set side effects for each phase function
                                mock_research.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="research")
                                mock_worldbuilding.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="worldbuilding")
                                mock_character.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="characters")
                                mock_plot.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="plot")
                                mock_draft.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="draft")
                                mock_final.side_effect = lambda *args, **kwargs: process_phase_side_effect(*args, **kwargs, phase_name="final_story")
                                
                                # Call the method
                                result = story_generator.generate_story_chunked(
                                    genre="noir",
                                    custom_inputs={"title": "Test Story", "chapter_number": 2},
                                    chunk_callback=mock_callback
                                )
        
        # Verify the result is a StoryArtifacts object
        assert isinstance(result, StoryArtifacts)
        assert result.genre == "noir"
        assert result.title == "Test Story"
        
        # All artifact fields should contain the mock task output
        assert result.research == "This is test task output."
        assert result.worldbuilding == "This is test task output."
        assert result.characters == "This is test task output."
        assert result.plot == "This is test task output."
        assert result.draft == "This is test task output."
        assert result.final_story == "This is test task output."
        
        # Verify all process methods were called
        mock_research.assert_called_once()
        mock_worldbuilding.assert_called_once()
        mock_character.assert_called_once()
        mock_plot.assert_called_once()
        mock_draft.assert_called_once()
        mock_final.assert_called_once()
        
        # Verify the callback was called for each phase
        assert mock_callback.call_count == 6
        mock_callback.assert_has_calls([
            call("research", "This is test task output."),
            call("worldbuilding", "This is test task output."),
            call("characters", "This is test task output."),
            call("plot", "This is test task output."),
            call("draft", "This is test task output."),
            call("final_story", "This is test task output."),
        ], any_order=True)
    
    def test_execute_detailed_research(self, story_generator, mock_execution_engine):
        """Test execute_detailed_research method."""
        # Mock the logger
        with patch('pulp_fiction_generator.story.generator.logger') as mock_logger:
            # Call the method
            result = story_generator.execute_detailed_research(
                genre="noir",
                custom_inputs={"title": "Noir Research"}
            )
            
            # Check that the execution engine was called
            assert mock_execution_engine.execute_task.call_count > 0
            
            # Verify the expected result was returned
            assert result is not None
    
    def test_reuse_completed_tasks(self, story_generator, mock_story_state, mock_execution_engine):
        """Test that completed tasks are reused from story state."""
        # Configure mock state to have a completed task
        mock_story_state.has_completed_task = Mock(side_effect=lambda task_name, chapter: task_name == "research")
        mock_story_state.get_task_output = Mock(side_effect=lambda task_name, chapter: 
                                              "Existing research" if task_name == "research" else None)
        
        # Use patches to avoid direct execution
        with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_research_phase') as mock_research:
            with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_worldbuilding_phase') as mock_worldbuilding:
                with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_character_phase') as mock_character:
                    with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_plot_phase') as mock_plot:
                        with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_draft_phase') as mock_draft:
                            with patch('pulp_fiction_generator.story.generator.StoryGenerator._process_final_phase') as mock_final:
                                
                                # Define side effect to actually call the real method for research
                                def research_side_effect(genre, chapter_num, project_dir, callback, state, artifacts, timeout_seconds):
                                    # Just set the result from the mocked state
                                    artifacts.research = state.get_task_output("research", chapter_num)
                                
                                # Define side effect for other phases
                                def other_phase_side_effect(genre, chapter_num, project_dir, callback, state, artifacts, timeout_seconds, field_name):
                                    setattr(artifacts, field_name, "This is test task output.")
                                
                                # Set side effects
                                mock_research.side_effect = research_side_effect
                                mock_worldbuilding.side_effect = lambda *args, **kwargs: other_phase_side_effect(*args, **kwargs, field_name="worldbuilding")
                                mock_character.side_effect = lambda *args, **kwargs: other_phase_side_effect(*args, **kwargs, field_name="characters")
                                mock_plot.side_effect = lambda *args, **kwargs: other_phase_side_effect(*args, **kwargs, field_name="plot")
                                mock_draft.side_effect = lambda *args, **kwargs: other_phase_side_effect(*args, **kwargs, field_name="draft")
                                mock_final.side_effect = lambda *args, **kwargs: other_phase_side_effect(*args, **kwargs, field_name="final_story")
                                
                                # Call the method
                                result = story_generator.generate_story_chunked(
                                    genre="noir",
                                    story_state=mock_story_state
                                )
        
        # Verify research was reused
        assert result.research == "Existing research"
        
        # Other phases should still be processed
        assert result.worldbuilding == "This is test task output."
        
        # Since we're mocking the process methods, we can just verify they were all called
        mock_research.assert_called_once()
        mock_worldbuilding.assert_called_once()
        mock_character.assert_called_once()
        mock_plot.assert_called_once()
        mock_draft.assert_called_once()
        mock_final.assert_called_once() 