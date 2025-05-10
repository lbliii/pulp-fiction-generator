"""
CLI command implementations for Pulp Fiction Generator.
"""

from pulp_fiction_generator.cli.commands.generate import Generate
from pulp_fiction_generator.cli.commands.list_genres import list_genres
from pulp_fiction_generator.cli.commands.list_plugins import list_plugins
from pulp_fiction_generator.cli.commands.config import ConfigCommand

__all__ = [
    'Generate',
    'list_genres',
    'list_plugins',
    'ConfigCommand',
] 