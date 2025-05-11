#!/usr/bin/env python3
"""Entry point for the Pulp Fiction Generator CLI."""

import sys
import logging
import importlib.metadata
from packaging import version
from pulp_fiction_generator.cli.app import create_app
from pulp_fiction_generator.utils.directory_init import initialize_app_directories
from rich.console import Console

# Create console for startup messages
console = Console()

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/pulp_fiction_generator.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check that required dependencies are installed with compatible versions"""
    try:
        # Check CrewAI version
        crewai_version = importlib.metadata.version("crewai")
        min_crewai_version = "0.28.0"  # Minimum required version with delegation support
        
        if version.parse(crewai_version) < version.parse(min_crewai_version):
            console.print(f"[bold yellow]Warning:[/bold yellow] CrewAI version {crewai_version} detected. Some features may not work correctly.")
            console.print(f"[bold yellow]Recommended:[/bold yellow] CrewAI version {min_crewai_version} or higher for full functionality.")
            return False
        
        # Check for other critical dependencies as needed
        return True
    except Exception as e:
        logger.warning(f"Error checking dependencies: {e}")
        return False

def main():
    """Main entry point for the CLI application."""
    # Display a welcome message
    console.print("[bold]Pulp Fiction Generator[/bold] - AI-powered story creation")
    
    # Check dependencies
    dependency_check = check_dependencies()
    if not dependency_check:
        logger.warning("Dependency check failed. Some features may not work correctly.")
    
    # Initialize directories needed by the application
    if not initialize_app_directories():
        logger.error("Failed to initialize directories. Some features may not work correctly.")
    
    # Create and run the CLI app
    logger.info("Starting Pulp Fiction Generator")
    app = create_app()
    app()

if __name__ == "__main__":
    main() 