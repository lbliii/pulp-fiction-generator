"""
Prompt templates and management for the Pulp Fiction Generator.
"""

from pulp_fiction_generator.prompts.templates import (
    PromptTemplate,
    PromptLibrary,
    prompt_library
)
from pulp_fiction_generator.prompts.genre_templates import (
    register_genre_templates,
    register_noir_templates,
    register_hardboiled_templates,
    register_scifi_templates,
    register_western_templates,
    register_horror_templates
)
from pulp_fiction_generator.prompts.custom_templates import (
    create_custom_genre,
    register_custom_genre,
    create_custom_template,
    create_custom_agent_type,
    example_cyberpunk
)
from pulp_fiction_generator.prompts.utility import (
    save_prompt_context,
    load_prompt_context,
    save_template,
    load_template,
    save_library,
    load_library,
    merge_contexts,
    extract_placeholders,
    validate_context
)

# Initialize genre templates
register_genre_templates(prompt_library)

__all__ = [
    # Core prompt template system
    "PromptTemplate", 
    "PromptLibrary", 
    "prompt_library",
    
    # Genre template registration functions
    "register_genre_templates",
    "register_noir_templates",
    "register_hardboiled_templates",
    "register_scifi_templates",
    "register_western_templates",
    "register_horror_templates",
    
    # Custom template utilities
    "create_custom_genre",
    "register_custom_genre",
    "create_custom_template",
    "create_custom_agent_type",
    "example_cyberpunk",
    
    # Utility functions
    "save_prompt_context",
    "load_prompt_context",
    "save_template",
    "load_template",
    "save_library",
    "load_library",
    "merge_contexts",
    "extract_placeholders",
    "validate_context"
] 