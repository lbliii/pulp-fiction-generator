"""
Genre-specific templates for the Pulp Fiction Generator.

This module contains specialized template extensions for different
pulp fiction genres, extending the base templates with genre-specific
instructions and details.
"""

from typing import Dict

from pulp_fiction_generator.prompts.templates import PromptLibrary, PromptTemplate


def register_genre_templates(library: PromptLibrary) -> None:
    """
    Register genre-specific templates with the prompt library.
    
    Args:
        library: The prompt library to register templates with
    """
    # Register noir templates
    register_noir_templates(library)
    
    # Register hardboiled detective templates
    register_hardboiled_templates(library)
    
    # Register sci-fi templates
    register_scifi_templates(library)
    
    # Register western templates 
    register_western_templates(library)
    
    # Register horror templates
    register_horror_templates(library)


def register_noir_templates(library: PromptLibrary) -> None:
    """Register noir-specific templates."""
    noir_context = {
        "genre": "noir",
        "genre_specific_instructions": """
        Focus on the dark, cynical atmosphere of noir fiction. Emphasize:
        - Moral ambiguity and corruption
        - Urban settings, often at night or in rain
        - Fatalistic themes and existential despair
        - Hard-edged dialogue with metaphors and similes
        - First-person or limited third-person narration
        - Visual elements like shadows, light contrast, and smoke
        
        Classic noir stories often involve crime, betrayal, and doomed romance.
        Authenticity is critical - don't sanitize the grim realities of the noir world.
        """
    }
    
    # Add genre-specific templates for each agent role
    _add_genre_template(library, "researcher", "noir", noir_context)
    _add_genre_template(library, "worldbuilder", "noir", noir_context)
    _add_genre_template(library, "character_creator", "noir", noir_context)
    _add_genre_template(library, "plotter", "noir", noir_context)
    _add_genre_template(library, "writer", "noir", noir_context)
    _add_genre_template(library, "editor", "noir", noir_context)


def register_hardboiled_templates(library: PromptLibrary) -> None:
    """Register hardboiled detective-specific templates."""
    hardboiled_context = {
        "genre": "hardboiled detective",
        "genre_specific_instructions": """
        Capture the tough, unsentimental style of hardboiled detective fiction. Focus on:
        - A cynical, world-weary detective protagonist
        - Violence and crime in urban settings
        - Terse, clipped dialogue with slang of the era
        - Straightforward, unflinching descriptions
        - Complex mysteries with twists and red herrings
        - Social commentary on corruption and moral decay
        
        The detective should be flawed but principled in their own way, operating 
        in a world where justice and the law don't always align.
        """
    }
    
    # Add genre-specific templates for each agent role
    _add_genre_template(library, "researcher", "hardboiled", hardboiled_context)
    _add_genre_template(library, "worldbuilder", "hardboiled", hardboiled_context)
    _add_genre_template(library, "character_creator", "hardboiled", hardboiled_context)
    _add_genre_template(library, "plotter", "hardboiled", hardboiled_context)
    _add_genre_template(library, "writer", "hardboiled", hardboiled_context)
    _add_genre_template(library, "editor", "hardboiled", hardboiled_context)


def register_scifi_templates(library: PromptLibrary) -> None:
    """Register science fiction-specific templates."""
    scifi_context = {
        "genre": "science fiction",
        "genre_specific_instructions": """
        Create pulp sci-fi in the tradition of the golden age magazines. Emphasize:
        - Bold, adventurous storylines with clear heroes
        - Fantastical technology that drives the plot
        - Alien worlds, space travel, or future Earth settings
        - Action-oriented narratives with wonder and discovery
        - Big ideas presented in accessible ways
        - Visual spectacle and sense of awe
        
        Focus on the adventure and excitement rather than hard scientific accuracy.
        Embrace the optimism or cautionary themes common in classic pulp sci-fi.
        """
    }
    
    # Add genre-specific templates for each agent role
    _add_genre_template(library, "researcher", "scifi", scifi_context)
    _add_genre_template(library, "worldbuilder", "scifi", scifi_context)
    _add_genre_template(library, "character_creator", "scifi", scifi_context)
    _add_genre_template(library, "plotter", "scifi", scifi_context)
    _add_genre_template(library, "writer", "scifi", scifi_context)
    _add_genre_template(library, "editor", "scifi", scifi_context)


def register_western_templates(library: PromptLibrary) -> None:
    """Register western-specific templates."""
    western_context = {
        "genre": "western",
        "genre_specific_instructions": """
        Capture the rugged frontier spirit of pulp westerns. Focus on:
        - The American frontier, typically 1865-1900
        - Moral conflicts between lawfulness and frontier justice
        - Stark landscapes as a character in themselves
        - Action sequences like shootouts, chases, and standoffs
        - Archetypal characters with clear motivations
        - Terse dialogue with period-appropriate speech
        
        Embrace the mythology of the Old West while avoiding simplistic 
        good vs. evil narratives. Characters should have clear motivations
        shaped by the harsh realities of frontier life.
        """
    }
    
    # Add genre-specific templates for each agent role
    _add_genre_template(library, "researcher", "western", western_context)
    _add_genre_template(library, "worldbuilder", "western", western_context)
    _add_genre_template(library, "character_creator", "western", western_context)
    _add_genre_template(library, "plotter", "western", western_context)
    _add_genre_template(library, "writer", "western", western_context)
    _add_genre_template(library, "editor", "western", western_context)


def register_horror_templates(library: PromptLibrary) -> None:
    """Register horror-specific templates."""
    horror_context = {
        "genre": "horror",
        "genre_specific_instructions": """
        Create unsettling, atmospheric horror in the pulp tradition. Focus on:
        - Building suspense and dread through pacing
        - Vivid, sensory descriptions of the horrific elements
        - Psychological or supernatural threats
        - Vulnerable characters facing overwhelming forces
        - Confined or isolated settings
        - Moments of shock and revelation
        
        The horror should feel visceral and immediate. Draw on primal fears
        and the unknown, using suggestion and atmosphere as much as explicit
        descriptions of horror elements.
        """
    }
    
    # Add genre-specific templates for each agent role
    _add_genre_template(library, "researcher", "horror", horror_context)
    _add_genre_template(library, "worldbuilder", "horror", horror_context)
    _add_genre_template(library, "character_creator", "horror", horror_context)
    _add_genre_template(library, "plotter", "horror", horror_context)
    _add_genre_template(library, "writer", "horror", horror_context)
    _add_genre_template(library, "editor", "horror", horror_context)


def _add_genre_template(
    library: PromptLibrary, 
    agent_type: str, 
    genre_name: str, 
    context: Dict[str, str]
) -> None:
    """
    Add a genre-specific template based on the base template.
    
    Args:
        library: The prompt library to add to
        agent_type: The agent type to add a template for
        genre_name: The name of the genre
        context: The context to initialize the template with
    """
    # Get the base template
    base_template = library.get_template(agent_type, "base")
    
    # Create a new template with the same template string but with default variables
    genre_template = PromptTemplate(base_template.template_str, context)
    
    # Add the genre-specific template
    library.add_template(agent_type, genre_name, genre_template) 