"""
File utility functions for the Pulp Fiction Generator.

This module provides utilities for reading and writing files, loading templates,
and other file-related operations.
"""

import os
import yaml
from typing import Dict, Any, List, Optional
import importlib.resources
import glob
from pathlib import Path

# Import crewai tools for file operations
try:
    from crewai_tools import FileReadTool
    has_crewai_tools = True
except ImportError:
    has_crewai_tools = False

def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary containing the parsed YAML content
    """
    if has_crewai_tools:
        # Use CrewAI's FileReadTool if available
        file_tool = FileReadTool()
        content = file_tool.file_read(file_path)
        return yaml.safe_load(content)
    else:
        # Fallback to standard file reading
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error reading YAML file {file_path}: {str(e)}")
            return {}

def load_templates(template_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Load template files from a directory.
    
    Args:
        template_dir: Directory containing template files. If None, uses a default directory.
        
    Returns:
        Dictionary mapping template names to template contents
    """
    # Use default directory if none specified
    if template_dir is None:
        template_dir = "pulp_fiction_generator/prompts/templates"
    
    # Get all YAML files in the directory
    templates = {}
    template_files = glob.glob(os.path.join(template_dir, "*.yaml"))
    
    for file_path in template_files:
        # Get the template name (filename without extension)
        template_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Load the template
        template_content = read_yaml_file(file_path)
        templates[template_name] = template_content
    
    return templates

def write_file(file_path: str, content: str) -> bool:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {str(e)}")
        return False

def read_file(file_path: str) -> Optional[str]:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as a string, or None if the file could not be read
    """
    if has_crewai_tools:
        # Use CrewAI's FileReadTool if available
        try:
            file_tool = FileReadTool()
            return file_tool.file_read(file_path)
        except Exception as e:
            print(f"Error reading file with CrewAI tools {file_path}: {str(e)}")
            return None
    else:
        # Fallback to standard file reading
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return None 