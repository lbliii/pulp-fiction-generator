"""
Condition functions for conditional tasks.

This module provides predefined condition functions that can be used
with conditional tasks to create dynamic story generation workflows.
"""

from typing import Any, Dict, Optional, Union
from crewai.tasks.task_output import TaskOutput


def text_contains(output: TaskOutput, text: str, case_sensitive: bool = False) -> bool:
    """
    Check if the output text contains a specific substring.
    
    Args:
        output: The task output
        text: The text to search for
        case_sensitive: Whether the search should be case sensitive
        
    Returns:
        True if the text is found, False otherwise
    """
    output_text = get_output_text(output)
    if not case_sensitive:
        return text.lower() in output_text.lower()
    return text in output_text


def text_length_below(output: TaskOutput, threshold: int) -> bool:
    """
    Check if the output text length is below a threshold.
    
    Args:
        output: The task output
        threshold: The length threshold
        
    Returns:
        True if the text length is below the threshold, False otherwise
    """
    output_text = get_output_text(output)
    return len(output_text) < threshold


def text_length_above(output: TaskOutput, threshold: int) -> bool:
    """
    Check if the output text length is above a threshold.
    
    Args:
        output: The task output
        threshold: The length threshold
        
    Returns:
        True if the text length is above the threshold, False otherwise
    """
    output_text = get_output_text(output)
    return len(output_text) > threshold


def pydantic_field_contains(output: TaskOutput, field_name: str, text: str) -> bool:
    """
    Check if a field in the pydantic model output contains specific text.
    
    Args:
        output: The task output
        field_name: The name of the field to check
        text: The text to search for
        
    Returns:
        True if the field contains the text, False otherwise
    """
    if not hasattr(output, 'pydantic') or not output.pydantic:
        return False
    
    if not hasattr(output.pydantic, field_name):
        return False
    
    field_value = getattr(output.pydantic, field_name)
    if isinstance(field_value, str):
        return text in field_value
    elif isinstance(field_value, list):
        return any(text in str(item) for item in field_value)
    
    return False


def list_field_length_below(output: TaskOutput, field_name: str, threshold: int) -> bool:
    """
    Check if a list field in the pydantic model has fewer items than the threshold.
    
    Args:
        output: The task output
        field_name: The name of the field to check
        threshold: The length threshold
        
    Returns:
        True if the list length is below the threshold, False otherwise
    """
    if not hasattr(output, 'pydantic') or not output.pydantic:
        return False
    
    if not hasattr(output.pydantic, field_name):
        return False
    
    field_value = getattr(output.pydantic, field_name)
    if isinstance(field_value, list):
        return len(field_value) < threshold
    
    return False


def get_output_text(output: TaskOutput) -> str:
    """
    Safely extract text from a TaskOutput object.
    
    Args:
        output: The task output
        
    Returns:
        The output text as a string
    """
    if output is None:
        return ""
    
    if isinstance(output, str):
        return output
    
    if hasattr(output, 'output') and isinstance(output.output, str):
        return output.output
    
    if hasattr(output, 'pydantic'):
        if hasattr(output.pydantic, 'content') and isinstance(output.pydantic.content, str):
            return output.pydantic.content
            
    # Fall back to string representation
    return str(output)


# Story-specific conditions
def needs_research_expansion(output: TaskOutput) -> bool:
    """
    Check if the research needs expansion.
    
    Args:
        output: The research task output
        
    Returns:
        True if the research needs more detail, False otherwise
    """
    output_text = get_output_text(output)
    
    # Check for indicators that research is shallow
    indicators = [
        "requires additional research",
        "needs more depth",
        "insufficient information",
        "further research needed",
        "more details required"
    ]
    
    return any(indicator.lower() in output_text.lower() for indicator in indicators)


def needs_character_development(output: TaskOutput) -> bool:
    """
    Check if the characters need more development.
    
    Args:
        output: The character development task output
        
    Returns:
        True if characters need more development, False otherwise
    """
    output_text = get_output_text(output)
    
    # Check text length as a basic heuristic
    if len(output_text) < 800:  # Arbitrary threshold
        return True
    
    # Check for indicators of shallow character development
    indicators = [
        "needs more depth",
        "character motivations unclear",
        "personality not well defined",
        "flat character",
        "one-dimensional"
    ]
    
    return any(indicator.lower() in output_text.lower() for indicator in indicators)


def needs_plot_twist(output: TaskOutput) -> bool:
    """
    Check if the plot needs a twist to make it more engaging.
    
    Args:
        output: The plot development task output
        
    Returns:
        True if a plot twist would improve the story, False otherwise
    """
    output_text = get_output_text(output)
    
    # Check for indicators that suggest a plot twist would help
    indicators = [
        "predictable plot",
        "straightforward storyline",
        "needs more tension",
        "plot too simple",
        "needs more excitement",
        "could use a twist"
    ]
    
    return any(indicator.lower() in output_text.lower() for indicator in indicators)


def needs_style_improvement(output: TaskOutput) -> bool:
    """
    Check if the writing style needs improvement.
    
    Args:
        output: The draft task output
        
    Returns:
        True if the style needs improvement, False otherwise
    """
    output_text = get_output_text(output)
    
    # Check for indicators of style issues
    indicators = [
        "prose needs work",
        "writing style is weak",
        "needs more vivid descriptions",
        "style inconsistent",
        "dialogue needs improvement"
    ]
    
    return any(indicator.lower() in output_text.lower() for indicator in indicators)


def has_inconsistencies(output: TaskOutput) -> bool:
    """
    Check if the story has inconsistencies that need fixing.
    
    Args:
        output: The draft task output
        
    Returns:
        True if inconsistencies are detected, False otherwise
    """
    output_text = get_output_text(output)
    
    # Check for indicators of inconsistencies
    indicators = [
        "plot hole",
        "inconsistent character",
        "timeline issue",
        "contradiction in",
        "continuity error"
    ]
    
    return any(indicator.lower() in output_text.lower() for indicator in indicators) 