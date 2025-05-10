"""
CLI application creation for Pulp Fiction Generator.
"""

import typer
from rich.console import Console

from .registry import CommandRegistry

def create_app() -> typer.Typer:
    """Create and configure the CLI application"""
    
    # Create the command registry
    registry = CommandRegistry()
    
    # Discover and register commands
    registry.discover_commands()
    
    # Get the configured app
    app = registry.get_app()
    
    return app 