#!/usr/bin/env python3
"""Entry point for the Pulp Fiction Generator CLI."""

import sys
import logging
from pulp_fiction_generator.cli.app import create_app
from pulp_fiction_generator.utils.directory_init import initialize_app_directories

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

def main():
    """Main entry point for the CLI application."""
    # Initialize directories needed by the application
    if not initialize_app_directories():
        logger.error("Failed to initialize directories. Some features may not work correctly.")
    
    # Create and run the CLI app
    logger.info("Starting Pulp Fiction Generator")
    app = create_app()
    app()

if __name__ == "__main__":
    main() 