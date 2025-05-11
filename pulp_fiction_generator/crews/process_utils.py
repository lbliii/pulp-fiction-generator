"""
Process utilities for CrewAI process management.

This module provides utilities for working with CrewAI processes,
including validation, configuration, and future support for new process types.
"""

from typing import Dict, Any, Optional, Tuple, Union
from enum import Enum, auto

from crewai import Process


# Define our extended process types for future use
class ExtendedProcessType(Enum):
    """
    Extended process types including planned future processes.
    """
    SEQUENTIAL = auto()
    HIERARCHICAL = auto()
    CONSENSUAL = auto()  # Planned for future CrewAI releases
    
    @classmethod
    def from_crewai_process(cls, process: Process) -> 'ExtendedProcessType':
        """Convert a CrewAI Process to our extended process type."""
        if process == Process.sequential:
            return cls.SEQUENTIAL
        elif process == Process.hierarchical:
            return cls.HIERARCHICAL
        else:
            raise ValueError(f"Unknown CrewAI process type: {process}")
    
    def to_crewai_process(self) -> Process:
        """Convert our extended process type to a CrewAI Process."""
        if self == self.SEQUENTIAL:
            return Process.sequential
        elif self == self.HIERARCHICAL:
            return Process.hierarchical
        elif self == self.CONSENSUAL:
            # Currently not supported in CrewAI, fallback to sequential
            return Process.sequential
        else:
            raise ValueError(f"Cannot convert {self} to CrewAI process")


def validate_process_config(
    process: Union[Process, ExtendedProcessType], 
    config: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Validate process configuration.
    
    Args:
        process: The process to validate
        config: The configuration to validate
        
    Returns:
        A tuple of (is_valid, error_message)
    """
    # Convert ExtendedProcessType to Process if needed
    if isinstance(process, ExtendedProcessType):
        process = process.to_crewai_process()
    
    # Validate hierarchical process
    if process == Process.hierarchical:
        has_manager_llm = config.get("manager_llm") is not None
        has_manager_agent = config.get("manager_agent") is not None
        
        if not (has_manager_llm or has_manager_agent):
            return False, (
                "Hierarchical process requires either 'manager_llm' or 'manager_agent' "
                "to be specified in the configuration."
            )
    
    # When consensual process is added to CrewAI, add validation here
    
    return True, None


def get_process_from_string(process_name: str) -> Process:
    """
    Convert a process name string to a Process enum value.
    
    Args:
        process_name: The name of the process
        
    Returns:
        The corresponding Process enum value
        
    Raises:
        ValueError: If the process name is invalid
    """
    process_name = process_name.lower().strip()
    
    if process_name == "sequential":
        return Process.sequential
    elif process_name == "hierarchical":
        return Process.hierarchical
    elif process_name == "consensual":
        # Placeholder for future consensual process
        # For now, log a warning and fallback to sequential
        import logging
        logging.warning(
            "Consensual process is not yet available in CrewAI. "
            "Falling back to sequential process."
        )
        return Process.sequential
    else:
        raise ValueError(f"Unknown process type: {process_name}")


def get_process_description(process: Process) -> str:
    """
    Get a description of a process.
    
    Args:
        process: The process to describe
        
    Returns:
        A description of the process
    """
    if process == Process.sequential:
        return (
            "Sequential process: Tasks are executed in order, with each task's output "
            "serving as context for subsequent tasks."
        )
    elif process == Process.hierarchical:
        return (
            "Hierarchical process: A manager agent oversees task execution, including planning, "
            "delegation, and validation. Tasks are allocated dynamically based on agent capabilities."
        )
    else:
        return f"Unknown process type: {process}" 