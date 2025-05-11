"""
Tests for process handling and validation.
"""

import pytest
from typing import Dict, Any

from crewai import Process
from pulp_fiction_generator.crews.process_utils import (
    ExtendedProcessType,
    validate_process_config,
    get_process_from_string,
    get_process_description
)
from pulp_fiction_generator.crews.config.crew_coordinator_config import CrewCoordinatorConfig


class TestProcessUtils:
    """Tests for process utility functions."""
    
    def test_process_validation_sequential(self):
        """Test validation of sequential process configuration."""
        # Sequential process doesn't require any special config
        config: Dict[str, Any] = {}
        is_valid, error_message = validate_process_config(Process.sequential, config)
        assert is_valid
        assert error_message is None
    
    def test_process_validation_hierarchical_invalid(self):
        """Test validation of invalid hierarchical process configuration."""
        # Hierarchical process without manager should be invalid
        config: Dict[str, Any] = {}
        is_valid, error_message = validate_process_config(Process.hierarchical, config)
        assert not is_valid
        assert "manager_llm" in error_message or "manager_agent" in error_message
    
    def test_process_validation_hierarchical_valid_llm(self):
        """Test validation of valid hierarchical process with manager_llm."""
        # Hierarchical process with manager_llm should be valid
        config: Dict[str, Any] = {"manager_llm": "gpt-4"}
        is_valid, error_message = validate_process_config(Process.hierarchical, config)
        assert is_valid
        assert error_message is None
    
    def test_process_validation_hierarchical_valid_agent(self):
        """Test validation of valid hierarchical process with manager_agent."""
        # Hierarchical process with manager_agent should be valid
        config: Dict[str, Any] = {"manager_agent": "dummy_agent"}
        is_valid, error_message = validate_process_config(Process.hierarchical, config)
        assert is_valid
        assert error_message is None
    
    def test_get_process_from_string_valid(self):
        """Test conversion of valid process strings to Process enum."""
        assert get_process_from_string("sequential") == Process.sequential
        assert get_process_from_string("hierarchical") == Process.hierarchical
        
        # Test with different cases and whitespace
        assert get_process_from_string("Sequential") == Process.sequential
        assert get_process_from_string(" hierarchical ") == Process.hierarchical
    
    def test_get_process_from_string_invalid(self):
        """Test conversion of invalid process strings."""
        with pytest.raises(ValueError):
            get_process_from_string("invalid_process")
    
    def test_get_process_from_string_consensual(self):
        """Test conversion of consensual process string (future support)."""
        # Should fall back to sequential for now
        assert get_process_from_string("consensual") == Process.sequential
    
    def test_extended_process_type_conversion(self):
        """Test conversion between ExtendedProcessType and Process."""
        # Test conversion from CrewAI Process to ExtendedProcessType
        assert ExtendedProcessType.from_crewai_process(Process.sequential) == ExtendedProcessType.SEQUENTIAL
        assert ExtendedProcessType.from_crewai_process(Process.hierarchical) == ExtendedProcessType.HIERARCHICAL
        
        # Test conversion from ExtendedProcessType to CrewAI Process
        assert ExtendedProcessType.SEQUENTIAL.to_crewai_process() == Process.sequential
        assert ExtendedProcessType.HIERARCHICAL.to_crewai_process() == Process.hierarchical
        assert ExtendedProcessType.CONSENSUAL.to_crewai_process() == Process.sequential  # Falls back to sequential
    
    def test_get_process_description(self):
        """Test getting process descriptions."""
        sequential_desc = get_process_description(Process.sequential)
        assert "Sequential" in sequential_desc
        assert "order" in sequential_desc
        
        hierarchical_desc = get_process_description(Process.hierarchical)
        assert "Hierarchical" in hierarchical_desc
        assert "manager" in hierarchical_desc


class TestCrewCoordinatorConfig:
    """Tests for CrewCoordinatorConfig process handling."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CrewCoordinatorConfig()
        assert config.process == Process.sequential
        assert config.extended_process is None  # Default doesn't set extended process
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        # Sequential process
        config = CrewCoordinatorConfig.from_dict({
            "process": "sequential",
            "verbose": False
        })
        assert config.process == Process.sequential
        assert config.extended_process == ExtendedProcessType.SEQUENTIAL
        assert not config.verbose
        
        # Hierarchical process
        config = CrewCoordinatorConfig.from_dict({
            "process": "hierarchical",
            "debug_mode": True
        })
        assert config.process == Process.hierarchical
        assert config.extended_process == ExtendedProcessType.HIERARCHICAL
        assert config.debug_mode
        
        # Invalid process falls back to sequential
        config = CrewCoordinatorConfig.from_dict({
            "process": "invalid_process"
        })
        assert config.process == Process.sequential
    
    def test_with_process(self):
        """Test updating process in config."""
        config = CrewCoordinatorConfig()
        
        # Update with Process enum
        updated = config.with_process(Process.hierarchical)
        assert updated.process == Process.hierarchical
        assert updated.extended_process == ExtendedProcessType.HIERARCHICAL
        
        # Update with ExtendedProcessType enum
        updated = config.with_process(ExtendedProcessType.SEQUENTIAL)
        assert updated.process == Process.sequential
        assert updated.extended_process == ExtendedProcessType.SEQUENTIAL
        
        # Update with string
        updated = config.with_process("hierarchical")
        assert updated.process == Process.hierarchical
        assert updated.extended_process == ExtendedProcessType.HIERARCHICAL
        
        # Update with consensual (falls back to sequential for now)
        updated = config.with_process("consensual")
        assert updated.process == Process.sequential
        # But the extended process should still be CONSENSUAL
        assert updated.extended_process == ExtendedProcessType.CONSENSUAL 