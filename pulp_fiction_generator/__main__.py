#!/usr/bin/env python3
"""Entry point for the Pulp Fiction Generator CLI."""

import sys
from pulp_fiction_generator.cli.app import create_app

def main():
    """Main entry point for the CLI application."""
    app = create_app()
    app()

if __name__ == "__main__":
    main() 