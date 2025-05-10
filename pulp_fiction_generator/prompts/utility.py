"""
Utility functions for working with prompts in the Pulp Fiction Generator.

This module provides helper functions for loading, saving, and manipulating
prompt templates and context data.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pulp_fiction_generator.prompts.templates import PromptLibrary, PromptTemplate


def save_prompt_context(
    context: Dict[str, Any], 
    filepath: Union[str, Path],
    pretty: bool = True
) -> None:
    """
    Save prompt context (variables) to a JSON file.
    
    Args:
        context: The context dictionary to save
        filepath: The path to save to
        pretty: Whether to format the JSON with indentation
    """
    # Ensure directory exists
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    with open(path, 'w') as f:
        if pretty:
            json.dump(context, f, indent=2)
        else:
            json.dump(context, f)


def load_prompt_context(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Load prompt context from a JSON file.
    
    Args:
        filepath: The path to load from
        
    Returns:
        The loaded context dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_template(
    template: PromptTemplate,
    filepath: Union[str, Path],
    include_variables: bool = True
) -> None:
    """
    Save a template to a file.
    
    Args:
        template: The template to save
        filepath: The path to save to
        include_variables: Whether to include default variables
    """
    data = {
        "template": template.template_str,
        "variables": template.variables if include_variables else {}
    }
    
    save_prompt_context(data, filepath)


def load_template(filepath: Union[str, Path]) -> PromptTemplate:
    """
    Load a template from a file.
    
    Args:
        filepath: The path to load from
        
    Returns:
        The loaded template
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        KeyError: If the file doesn't contain required keys
    """
    data = load_prompt_context(filepath)
    
    if "template" not in data:
        raise KeyError("Template file must contain a 'template' key")
    
    return PromptTemplate(
        data["template"],
        data.get("variables", {})
    )


def save_library(
    library: PromptLibrary,
    directory: Union[str, Path],
    pretty: bool = True
) -> None:
    """
    Save all templates in a library to a directory.
    
    Args:
        library: The library to save
        directory: The directory to save to
        pretty: Whether to format the JSON with indentation
    """
    # Ensure directory exists
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    
    # Save templates by agent type and template name
    for agent_type, templates in library.templates.items():
        # Create agent type directory
        agent_dir = path / agent_type
        agent_dir.mkdir(exist_ok=True)
        
        # Save each template
        for template_name, template in templates.items():
            template_path = agent_dir / f"{template_name}.json"
            save_template(template, template_path, pretty)


def load_library(
    directory: Union[str, Path],
    existing_library: Optional[PromptLibrary] = None
) -> PromptLibrary:
    """
    Load templates from a directory into a library.
    
    Args:
        directory: The directory to load from
        existing_library: Optional existing library to load into
        
    Returns:
        The loaded library
    """
    # Create a new library or use the existing one
    library = existing_library or PromptLibrary()
    
    # Load templates from each agent type directory
    path = Path(directory)
    
    for agent_dir in path.iterdir():
        if not agent_dir.is_dir():
            continue
            
        agent_type = agent_dir.name
        
        # Load each template file in the agent directory
        for template_file in agent_dir.glob("*.json"):
            template_name = template_file.stem
            template = load_template(template_file)
            
            # Add to library
            library.add_template(agent_type, template_name, template)
    
    return library


def merge_contexts(*contexts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple context dictionaries.
    
    Later contexts override earlier ones for duplicate keys.
    
    Args:
        *contexts: Context dictionaries to merge
        
    Returns:
        Merged context dictionary
    """
    result: Dict[str, Any] = {}
    
    for context in contexts:
        result.update(context)
        
    return result


def extract_placeholders(template_str: str) -> List[str]:
    """
    Extract all placeholder variables from a template string.
    
    Args:
        template_str: The template string to analyze
        
    Returns:
        List of unique placeholder names
    """
    import re
    
    # Find all $placeholders, including those with braces like ${placeholder}
    matches = re.findall(r'\$\{?([a-zA-Z0-9_]+)\}?', template_str)
    
    # Return unique placeholder names
    return list(set(matches))


def validate_context(
    template: PromptTemplate, 
    context: Dict[str, Any]
) -> List[str]:
    """
    Validate that a context contains all required placeholders for a template.
    
    Args:
        template: The template to validate against
        context: The context to validate
        
    Returns:
        List of missing placeholder names
    """
    # Extract all placeholders from the template
    placeholders = extract_placeholders(template.template_str)
    
    # Combine with template variables
    combined_context = {**template.variables}
    combined_context.update(context)
    
    # Find missing placeholders
    missing = [p for p in placeholders if p not in combined_context]
    
    return missing 