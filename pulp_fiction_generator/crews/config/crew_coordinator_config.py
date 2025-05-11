"""
Configuration class for CrewCoordinator settings.
"""

from dataclasses import dataclass
from typing import Optional, Union

from crewai import Process

from ..process_utils import ExtendedProcessType, get_process_from_string


@dataclass
class CrewCoordinatorConfig:
    """
    Configuration settings for the CrewCoordinator.
    
    This class encapsulates all configuration parameters needed
    by the CrewCoordinator, following the Single Responsibility Principle
    by separating configuration concerns from coordination logic.
    """
    process: Process = Process.sequential
    verbose: bool = True
    debug_mode: bool = False
    debug_output_dir: Optional[str] = None
    extended_process: Optional[ExtendedProcessType] = None
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'CrewCoordinatorConfig':
        """
        Create a config from a dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            A new config instance
        """
        # Handle process conversion from string
        process = Process.sequential
        if "process" in config_dict and isinstance(config_dict["process"], str):
            try:
                process = get_process_from_string(config_dict["process"])
            except ValueError:
                # Default to sequential on error
                pass
                
        # Create the config
        return cls(
            process=process,
            verbose=config_dict.get("verbose", True),
            debug_mode=config_dict.get("debug_mode", False),
            debug_output_dir=config_dict.get("debug_output_dir"),
            extended_process=ExtendedProcessType.from_crewai_process(process)
        )
    
    def with_debug(self, enabled: bool = True, output_dir: Optional[str] = None) -> 'CrewCoordinatorConfig':
        """
        Create a new instance with updated debug settings.
        
        Args:
            enabled: Whether to enable debug mode
            output_dir: Directory for debug output
            
        Returns:
            A new config instance with updated debug settings
        """
        return CrewCoordinatorConfig(
            process=self.process,
            verbose=self.verbose,
            debug_mode=enabled,
            debug_output_dir=output_dir or self.debug_output_dir,
            extended_process=self.extended_process
        )
    
    def with_process(self, process: Union[Process, ExtendedProcessType, str]) -> 'CrewCoordinatorConfig':
        """
        Create a new instance with an updated process.
        
        Args:
            process: The new process to use (can be a Process enum, ExtendedProcessType enum, or string)
            
        Returns:
            A new config instance with the updated process
            
        Raises:
            ValueError: If the process string is invalid
        """
        # Handle different process types
        if isinstance(process, str):
            crewai_process = get_process_from_string(process)
            extended_process = ExtendedProcessType.from_crewai_process(crewai_process)
        elif isinstance(process, Process):
            crewai_process = process
            extended_process = ExtendedProcessType.from_crewai_process(process)
        elif isinstance(process, ExtendedProcessType):
            crewai_process = process.to_crewai_process()
            extended_process = process
        else:
            raise TypeError(f"Unsupported process type: {type(process)}")
            
        return CrewCoordinatorConfig(
            process=crewai_process,
            verbose=self.verbose,
            debug_mode=self.debug_mode,
            debug_output_dir=self.debug_output_dir,
            extended_process=extended_process
        ) 