"""
Custom templates for the Pulp Fiction Generator.

This module provides utilities for creating and registering custom prompt templates
for different genres and agent types beyond the predefined ones.
"""

from typing import Dict, Optional

from pulp_fiction_generator.prompts.templates import PromptLibrary, PromptTemplate


def create_custom_genre(
    name: str,
    instructions: str,
    library: Optional[PromptLibrary] = None
) -> Dict[str, str]:
    """
    Create a custom genre context for use with prompt templates.
    
    Args:
        name: The name of the genre
        instructions: Specific instructions for this genre
        library: Optional prompt library to register with
        
    Returns:
        A context dictionary for the genre
    """
    context = {
        "genre": name,
        "genre_specific_instructions": instructions
    }
    
    # Register templates if a library was provided
    if library:
        register_custom_genre(library, name, context)
        
    return context


def register_custom_genre(
    library: PromptLibrary,
    genre_name: str,
    context: Dict[str, str]
) -> None:
    """
    Register a custom genre with the prompt library.
    
    Args:
        library: The prompt library to register with
        genre_name: The name of the genre
        context: The genre context dictionary
    """
    # Agent types to create templates for
    agent_types = [
        "researcher",
        "worldbuilder",
        "character_creator",
        "plotter",
        "writer",
        "editor"
    ]
    
    # Create and register templates for each agent type
    for agent_type in agent_types:
        try:
            # Get the base template
            base_template = library.get_template(agent_type, "base")
            
            # Create a new template with the same template string but with default variables
            genre_template = PromptTemplate(base_template.template_str, context)
            
            # Add the genre-specific template
            library.add_template(agent_type, genre_name, genre_template)
        except ValueError as e:
            # Skip if base template doesn't exist
            print(f"Warning: Couldn't create template for {agent_type}: {e}")


def create_custom_template(
    library: PromptLibrary,
    agent_type: str,
    template_name: str,
    template_str: str,
    variables: Optional[Dict[str, str]] = None
) -> PromptTemplate:
    """
    Create and register a completely custom template.
    
    Args:
        library: The prompt library to register with
        agent_type: The type of agent this template is for
        template_name: The name of the template
        template_str: The template string
        variables: Optional default variables
        
    Returns:
        The created template
    """
    # Create the template
    template = PromptTemplate(template_str, variables)
    
    # Register it with the library
    library.add_template(agent_type, template_name, template)
    
    return template


def create_custom_agent_type(
    library: PromptLibrary,
    agent_type: str,
    base_template: str,
    default_variables: Optional[Dict[str, str]] = None
) -> PromptTemplate:
    """
    Create a new agent type with a base template.
    
    Args:
        library: The prompt library to register with
        agent_type: The name of the new agent type
        base_template: The template string for this agent type
        default_variables: Optional default variables
        
    Returns:
        The created template
    """
    return create_custom_template(library, agent_type, "base", base_template, default_variables)


# Example custom genre creation
example_cyberpunk = {
    "name": "cyberpunk",
    "instructions": """
    Create high-tech, low-life cyberpunk pulp fiction. Emphasize:
    - Near-future dystopian urban settings
    - Advanced technology alongside social decay
    - Corporate power vs. individual rebellion
    - Gritty, noir-influenced atmosphere
    - Digital and physical realities blurring
    - Anti-hero protagonists operating in moral gray areas
    
    Focus on the street-level impact of technology and power structures.
    Include vivid sensory descriptions of the neon-lit, overcrowded,
    technologically saturated world.
    """
} 