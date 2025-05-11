"""
Validation service for story generation.

Contains guardrails and validation functions for ensuring 
story content quality throughout the generation process.
"""

from typing import Tuple, Union, Callable, Dict, Any


class StoryValidator:
    """
    Provides validation functions for story content.
    
    This class encapsulates validation logic that can be used
    as guardrails in CrewAI tasks to ensure quality outputs.
    """
    
    @staticmethod
    def validate_story_content(result: str) -> Tuple[bool, Union[str, str]]:
        """
        Validate story content to ensure it meets quality standards.
        
        Args:
            result: The story content to validate
            
        Returns:
            Tuple of (success, content/error_message)
        """
        # Simple validation: check for minimum length
        if len(result) < 200:
            return (False, "Story content is too short (minimum 200 characters required)")
            
        # Check for common error indicators
        error_indicators = ["ERROR:", "FAILED:", "Unable to complete", "AI ASSISTANT:"]
        for indicator in error_indicators:
            if indicator in result:
                return (False, f"Story contains error indicator: {indicator}")
                
        # Success case
        return (True, result)
    
    @staticmethod
    def validate_research(result: str) -> Tuple[bool, Union[str, str]]:
        """
        Validate research content to ensure it has adequate information.
        
        Args:
            result: The research content to validate
            
        Returns:
            Tuple of (success, content/error_message)
        """
        # Check for minimum length
        if len(result) < 500:
            return (False, "Research content is too brief (minimum 500 characters required)")
            
        # Check for required sections
        required_topics = ["elements", "tropes", "conventions", "history"]
        found_topics = sum(1 for topic in required_topics if topic.lower() in result.lower())
        
        if found_topics < 2:
            return (False, f"Research must cover at least 2 of these topics: {', '.join(required_topics)}")
            
        return (True, result)
    
    @staticmethod
    def validate_characters(result: str) -> Tuple[bool, Union[str, str]]:
        """
        Validate character descriptions to ensure they have depth.
        
        Args:
            result: The character descriptions to validate
            
        Returns:
            Tuple of (success, content/error_message)
        """
        # Check for protagonist and antagonist
        if "protagonist" not in result.lower() or "antagonist" not in result.lower():
            return (False, "Character descriptions must include both protagonist and antagonist")
            
        # Check for character traits
        character_traits = ["motivation", "background", "personality", "appearance", "goal"]
        found_traits = sum(1 for trait in character_traits if trait.lower() in result.lower())
        
        if found_traits < 3:
            return (False, f"Characters must be described with at least 3 traits from: {', '.join(character_traits)}")
            
        return (True, result)
    
    @staticmethod
    def validate_plot(result: str) -> Tuple[bool, Union[str, str]]:
        """
        Validate plot outline to ensure it has structure and elements.
        
        Args:
            result: The plot outline to validate
            
        Returns:
            Tuple of (success, content/error_message)
        """
        # Check for plot structure
        plot_elements = ["beginning", "introduction", "conflict", "climax", "resolution", "ending"]
        found_elements = sum(1 for element in plot_elements if element.lower() in result.lower())
        
        if found_elements < 3:
            return (False, f"Plot must contain at least 3 structural elements from: {', '.join(plot_elements)}")
            
        # Check for minimum length
        if len(result) < 400:
            return (False, "Plot outline is too brief (minimum 400 characters required)")
            
        return (True, result)
    
    # Factory method to get the right validator for a task type
    @classmethod
    def get_validator_for_task(cls, task_type: str) -> Callable[[str], Tuple[bool, Union[str, str]]]:
        """
        Get the appropriate validator function for a specific task type.
        
        Args:
            task_type: The type of task to get a validator for
            
        Returns:
            A validator function appropriate for the task type
        """
        validators = {
            "research": cls.validate_research,
            "characters": cls.validate_characters,
            "plot": cls.validate_plot,
            "draft": cls.validate_story_content,
            "final_story": cls.validate_story_content
        }
        
        return validators.get(task_type, cls.validate_story_content) 