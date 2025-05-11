"""
CLI command registry for Pulp Fiction Generator.
"""

from typing import Dict, List, Optional, Type, Union, Callable, Any
import typer
import inspect
import importlib
import importlib.util
import pkgutil
import sys
import os
from pathlib import Path

from .base import BaseCommand, command_callback, GenerateCommand
from .commands import __all__ as command_modules
from .commands import *

# Type for command functions that have name and help attributes
CommandFunction = Callable[..., Any]

# Define aliases for common commands
COMMAND_ALIASES = {
    "g": "generate",
    "gen": "generate",
    "t": "templates",
    "tpl": "templates",
    "st": "stats",
    "stat": "stats",
    "ls": "list-projects",
    "projects": "list-projects",
    "genres": "list-genres",
    "plugins": "list-plugins",
    "c": "config",
    "conf": "config",
    "m": "memory",
    "f": "flow",
}

class CommandRegistry:
    """Registry for CLI commands in the Pulp Fiction Generator."""
    
    def __init__(self):
        """Initialize the command registry."""
        # Create the main application
        self.app = typer.Typer(help="Pulp Fiction Generator CLI")
        self.commands: Dict[str, Union[BaseCommand, typer.Typer]] = {}
        
        # Set to keep track of registered commands to avoid duplicates
        self._registered_modules = set()
    
    def register(self, command: Union[BaseCommand, typer.Typer, CommandFunction], name: Optional[str] = None) -> None:
        """
        Register a command with the CLI application.
        
        Args:
            command: The command to register
            name: Optional name for the command
        """
        # If it's a BaseCommand subclass (not instance), instantiate it
        if inspect.isclass(command) and issubclass(command, BaseCommand):
            if hasattr(command, 'name'):
                name = name or command.name
                
            if not name:
                # Skip commands without a name
                return
            
            # Convert underscore name to hyphenated format
            if "_" in name:
                name = name.replace("_", "-")
                
            # Special handling for GenerateCommand which has its own run method
            if issubclass(command, GenerateCommand):
                # Use direct registration with the original signature
                run_method = command._run_impl
                
                # Register with Typer using the command name
                @self.app.command(name=name, help=command.help)
                def command_wrapper(**kwargs):
                    return command.run(**kwargs)
                    
                self.commands[name] = command
            else:
                # For other BaseCommand classes, call their run method
                self.app.command(name=name, help=command.help)(command.run)
                self.commands[name] = command
                
        # If it's a Typer application
        elif isinstance(command, typer.Typer):
            if name:
                # Convert underscore name to hyphenated format
                if "_" in name:
                    name = name.replace("_", "-")
                self.app.add_typer(command, name=name)
                self.commands[name] = command
        # If it's a function with name and help attributes
        elif callable(command) and hasattr(command, "name") and hasattr(command, "help"):
            cmd_name = name or command.name
            # Convert underscore name to hyphenated format
            if "_" in cmd_name:
                cmd_name = cmd_name.replace("_", "-")
            self.app.command(name=cmd_name, help=command.help)(command)
            self.commands[cmd_name] = command
        else:
            raise TypeError("Command must be a BaseCommand subclass, a Typer app, or a function with name and help attributes")

    def register_alias(self, alias: str, target_command: str) -> None:
        """
        Register an alias for an existing command.
        
        Args:
            alias: The alias name
            target_command: The target command name
        """
        if target_command not in self.commands:
            # Skip if target command doesn't exist
            return
            
        target = self.commands[target_command]
        
        # Handle different types of commands
        if inspect.isclass(target) and issubclass(target, BaseCommand):
            # For BaseCommand subclasses, create a function to call run
            @self.app.command(name=alias, help=f"Alias for '{target_command}' - {target.help}")
            def alias_wrapper(**kwargs):
                return target.run(**kwargs)
        elif isinstance(target, typer.Typer):
            # For Typer apps, add a callback to forward to the target app
            self.app.add_typer(target, name=alias)
        elif callable(target) and not inspect.isclass(target):
            # For function commands, create a wrapper function
            @self.app.command(name=alias, help=f"Alias for '{target_command}'")
            def alias_wrapper(**kwargs):
                return target(**kwargs)
                
        self.commands[alias] = target

    def discover_commands(self) -> None:
        """Discover and register commands from the commands package."""
        # Register the commands from the command_modules
        for cmd_name in command_modules:
            # Get the module or class
            cmd = globals().get(cmd_name)
            
            # Handle different types of commands
            if cmd:
                # If it's a Typer app
                if isinstance(cmd, typer.Typer):
                    # Convert underscore name to hyphenated format
                    display_name = cmd_name.lower()
                    if "_" in display_name:
                        display_name = display_name.replace("_", "-")
                    self.register(cmd, name=display_name)
                # If it's a BaseCommand subclass
                elif inspect.isclass(cmd) and issubclass(cmd, BaseCommand):
                    self.register(cmd)
                # If it's a function (for simpler commands)
                elif callable(cmd) and not inspect.isclass(cmd):
                    # For simple function commands, add them directly to the app
                    display_name = cmd_name.lower()
                    if "_" in display_name:
                        display_name = display_name.replace("_", "-")
                    self.app.command(name=display_name)(cmd)
        
        # Register the flow command
        if "flow_command" in globals():
            self.app.add_typer(
                globals()["flow_command"], 
                name="flow",
                help="Flow-based story generation commands"
            )

        # Register command aliases
        self._register_aliases()

        # Discover plugins
        self._discover_plugin_commands()
    
    def _register_aliases(self) -> None:
        """Register aliases for commonly used commands."""
        for alias, target in COMMAND_ALIASES.items():
            if target in self.commands:
                self.register_alias(alias, target)
    
    def _discover_plugin_commands(self) -> None:
        """
        Discover commands from plugins.
        
        This looks for plugins that might provide additional commands
        to extend the CLI functionality.
        """
        # Get the plugins directory
        plugins_dir = os.getenv("PLUGINS_DIR", "./plugins")
        
        # Skip if the directory doesn't exist
        if not os.path.isdir(plugins_dir):
            return
        
        # Import commands from plugins
        sys.path.append(plugins_dir)
        
        # Look for plugin modules with commands
        for plugin_file in Path(plugins_dir).glob("*/commands.py"):
            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(
                    f"plugin_commands_{plugin_file.parent.name}",
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Register any commands in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Register BaseCommand subclasses
                    if inspect.isclass(attr) and issubclass(attr, BaseCommand) and attr is not BaseCommand:
                        self.register(attr)
                    
                    # Register Typer apps
                    elif isinstance(attr, typer.Typer):
                        # Use the module name as a namespace
                        namespace = plugin_file.parent.name
                        self.register(attr, name=f"{namespace}_{attr_name}")
            
            except Exception as e:
                # Skip problematic plugins
                print(f"Error loading plugin commands from {plugin_file}: {e}")
                continue
                
    
    def get_app(self) -> typer.Typer:
        """
        Get the configured application.
        
        Returns:
            The configured typer application
        """
        return self.app 