"""
Handler for crew visualization and debug output.
"""

from typing import Optional

from ..utils.context_visualizer import ContextVisualizer


class VisualizationHandler:
    """
    Handles visualization and debug output for crews.
    
    This class encapsulates visualization logic, separating it from
    coordination concerns to follow the Single Responsibility Principle.
    """
    
    def __init__(self, debug_mode: bool = False, output_dir: Optional[str] = None):
        """
        Initialize the visualization handler.
        
        Args:
            debug_mode: Whether visualization is enabled
            output_dir: Directory for debug output
        """
        self.debug_mode = debug_mode
        self.visualizer = ContextVisualizer(
            output_dir=output_dir,
            enabled=debug_mode
        ) if debug_mode else None
    
    def is_enabled(self) -> bool:
        """
        Check if visualization is enabled.
        
        Returns:
            True if visualization is enabled, False otherwise
        """
        return self.debug_mode and self.visualizer is not None
    
    def visualize_crew_execution(self, crew_name: str, inputs: dict, output: str) -> None:
        """
        Visualize the execution of a crew.
        
        Args:
            crew_name: Name of the crew
            inputs: Inputs to the crew
            output: Output from the crew
        """
        if not self.is_enabled() or self.visualizer is None:
            return
            
        self.visualizer.visualize_execution(
            component=f"crew_{crew_name}",
            inputs=inputs,
            output=output
        )
    
    def visualize_story_generation(self, genre: str, inputs: dict, output: str) -> None:
        """
        Visualize a story generation process.
        
        Args:
            genre: The genre of the story
            inputs: Inputs to the generation process
            output: The generated story
        """
        if not self.is_enabled() or self.visualizer is None:
            return
            
        self.visualizer.visualize_execution(
            component=f"story_generation_{genre}",
            inputs=inputs,
            output=output
        ) 