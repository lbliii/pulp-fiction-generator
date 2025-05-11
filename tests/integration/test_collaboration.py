"""
Integration test for CrewAI collaboration features.

This test verifies that the implementation of CrewAI collaboration features
works correctly within the Pulp Fiction Generator system.
"""

import os
import sys
import logging
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pulp_fiction_generator.models.model_service import ModelService
from pulp_fiction_generator.agents.agent_factory import AgentFactory
from pulp_fiction_generator.crews.crew_factory import CrewFactory
from pulp_fiction_generator.utils.collaborative_memory import CollaborativeMemory
from pulp_fiction_generator.flow.flow_factory import FlowFactory
from pulp_fiction_generator.flow.story_flow import StoryState


# Create a mock ModelService for testing
class MockModelService(ModelService):
    """Mock model service for testing."""
    
    def __init__(self):
        """Initialize the mock model service."""
        self.provider = "mock_provider"
        self.model_name = "mock_model"
    
    def chat(self, messages, **kwargs):
        """Mock chat method."""
        return "This is a mock response"
    
    def generate(self, prompt, **kwargs):
        """Mock generate method."""
        return "This is a mock generated text"
    
    def get_model_info(self):
        """Mock get_model_info method."""
        return {"name": self.model_name, "provider": self.provider}
    
    def get_planning_llm(self):
        """Mock get_planning_llm method."""
        return self


class TestCollaboration:
    """Test suite for CrewAI collaboration features."""
    
    @classmethod
    def setup_class(cls):
        """Setup test suite."""
        # Initialize mock model service
        cls.model_service = MockModelService()
        
        # Initialize agent factory
        cls.agent_factory = AgentFactory(
            model_service=cls.model_service, 
            verbose=True
        )
        
        # Initialize crew factory with hierarchical process
        cls.crew_factory = CrewFactory(
            agent_factory=cls.agent_factory,
            verbose=True, 
            enable_planning=True
        )
        
        # Initialize collaborative memory
        cls.memory = CollaborativeMemory(genre="test_genre")
        
        # Initialize flow factory
        cls.flow_factory = FlowFactory(cls.crew_factory)
    
    def test_manager_agent_creation(self):
        """Test that a manager agent can be created."""
        # Create a manager agent directly
        manager_agent = self.crew_factory.story_manager_agent.create_agent(genre="noir")
        
        # Assert that the manager agent is created correctly
        assert manager_agent is not None
        assert "Noir Story Manager" in manager_agent.role
        assert manager_agent.goal is not None
        assert manager_agent.backstory is not None
    
    def test_collaborative_memory_initialization(self):
        """Test that collaborative memory is properly initialized."""
        # Initialize a new memory instance
        memory = CollaborativeMemory(genre="noir")
        
        # Get shared context
        context = memory.get_shared_context()
        
        # Assert that the context has the expected structure
        assert "shared_knowledge" in context
        assert "agent_contributions" in context
        assert "collaborative_insights" in context
        assert "context_version" in context
        assert "created_at" in context
        assert "last_updated" in context
    
    def test_flow_custom_inputs(self):
        """Test that a flow can have custom inputs with collaborative memory."""
        # Create a state with custom inputs
        state = StoryState(
            genre="scifi",
            custom_inputs={"prompt": "A test prompt"}
        )
        
        # Add collaborative memory to the state
        state.custom_inputs["collaborative_memory"] = self.memory
        
        # Assert that the custom inputs contain the collaborative memory
        assert "collaborative_memory" in state.custom_inputs
        assert state.custom_inputs["collaborative_memory"] == self.memory
    
    def test_memory_delegation_recording(self):
        """Test that delegations can be recorded in memory."""
        # Create a fresh memory instance for this test
        test_memory = CollaborativeMemory(genre="test_delegations")
        
        # Record a test delegation
        result = test_memory.record_delegation(
            delegator="Writer",
            delegatee="Researcher",
            task_description="Research the history of noir fiction",
            context={"importance": "high"}
        )
        
        # Assert that the delegation was recorded successfully
        assert result == True
        
        # Get delegations for the researcher
        delegations = test_memory._get_delegations_for_agent("Researcher", as_delegatee=True)
        
        # Assert that at least one delegation exists
        assert len(delegations) > 0
        
        # Assert that the delegation has the expected properties
        delegation = delegations[0]
        assert delegation["delegator"] == "Writer"
        assert delegation["delegatee"] == "Researcher"
        assert delegation["status"] == "delegated"
        assert "Research the history of noir fiction" in delegation["task_description"]
    
    def test_collaborative_insights(self):
        """Test that collaborative insights can be added to memory."""
        # Add a test insight
        result = self.memory.add_collaborative_insight(
            insight="Writers and researchers work better together on noir fiction",
            agents_involved=["Writer", "Researcher"]
        )
        
        # Assert that the insight was added successfully
        assert result == True
        
        # Get shared context
        context = self.memory.get_shared_context()
        
        # Assert that the insight exists in the context
        assert len(context["collaborative_insights"]) > 0
        
        # Assert that the insight has the expected properties
        insight = context["collaborative_insights"][0]
        assert "Writers and researchers work better together" in insight["insight"]
        assert "Writer" in insight["agents_involved"]
        assert "Researcher" in insight["agents_involved"]
    
    def test_agent_specific_context(self):
        """Test that agent-specific context can be retrieved."""
        # Add some test data
        self.memory.update_shared_context(
            key="noir_elements",
            value=["shadows", "rain", "detective"],
            agent_name="Researcher"
        )
        
        # Record a delegation
        self.memory.record_delegation(
            delegator="Writer",
            delegatee="Researcher",
            task_description="Find more noir elements"
        )
        
        # Get agent-specific context
        context = self.memory.get_agent_specific_context(agent_name="Researcher")
        
        # Assert that the context has the expected structure
        assert "shared_knowledge" in context
        assert "your_contributions" in context
        assert "delegations" in context
        assert "delegated_to_you" in context["delegations"]
        
        # Assert that the agent's contributions are included
        assert len(context["your_contributions"]) > 0
        
        # Assert that delegations to this agent are included
        assert len(context["delegations"]["delegated_to_you"]) > 0
    
    @pytest.mark.skip
    def test_create_hierarchical_crew(self):
        """Test the creation of a hierarchical crew (skipped for now)."""
        # Create a simple manager agent
        manager_agent = self.crew_factory.story_manager_agent.create_agent(genre="noir")
        
        # Mock the story manager's create_agent method to prevent it from trying to create a real agent
        with patch.object(self.crew_factory, 'validate_process_configuration', return_value=True):
            # Create a crew with a provided manager agent
            crew = self.crew_factory.create_basic_crew(
                genre="noir",
                config={
                    "enable_planning": True,
                    "process": "hierarchical",
                    "memory": True,
                    "manager_agent": manager_agent  # Pass the manager agent directly
                }
            )
            
            # Assert the crew was created with the manager agent
            assert crew is not None
            assert hasattr(crew, 'name')
            assert crew.name == "NoirStoryGenerationCrew"
    
    def test_flow_factory_collaboration(self):
        """Test the flow factory's collaboration-specific methods."""
        # Create a collaborative memory instance
        memory = CollaborativeMemory(genre="test")
        
        # Test the update_shared_context method
        result = memory.update_shared_context(
            "test_key", 
            {"value": "test_value"}, 
            "Flow System"
        )
        assert result == True
        
        # Get the updated context
        context = memory.get_shared_context()
        assert "test_key" in context["shared_knowledge"]
        assert context["shared_knowledge"]["test_key"]["value"] == "test_value"
        
        # Check that the flow factory can be initialized with correct process settings
        assert self.flow_factory.crew_factory.process == "hierarchical"
        assert self.flow_factory.crew_factory.enable_planning == True
        
        # Create a partial mock of the flow factory to avoid actual execution
        with patch.object(self.flow_factory, 'execute_flow') as mock_execute:
            # Set up the mock to return a simple result
            mock_execute.return_value = {"final_story": "A test story"}
            
            # Test the generate_story method with collaboration enabled
            story = self.flow_factory.generate_story(
                genre="noir",
                custom_inputs={"prompt": "A test prompt"},
                timeout_seconds=10,
                use_collaboration=True
            )
            
            # Assert that the mock was called with the expected arguments
            mock_execute.assert_called_once()
            # Get the actual arguments passed to execute_flow
            args, kwargs = mock_execute.call_args
            # Check that track_delegations=True was passed to execute_flow
            assert kwargs.get('track_delegations') == True 