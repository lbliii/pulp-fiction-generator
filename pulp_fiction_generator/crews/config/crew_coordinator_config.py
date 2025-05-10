"""
Configuration class for CrewCoordinator settings.
"""

from dataclasses import dataclass
from typing import Optional

from crewai import Process


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
            debug_output_dir=output_dir or self.debug_output_dir
        )
    
    def with_process(self, process: Process) -> 'CrewCoordinatorConfig':
        """
        Create a new instance with an updated process.
        
        Args:
            process: The new process to use
            
        Returns:
            A new config instance with the updated process
        """
        return CrewCoordinatorConfig(
            process=process,
            verbose=self.verbose,
            debug_mode=self.debug_mode,
            debug_output_dir=self.debug_output_dir
        ) 