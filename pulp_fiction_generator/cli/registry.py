"""
Command registry for Pulp Fiction Generator CLI.
"""

from typing import Dict, List, Type, Optional, Union, Callable, Any
import inspect
import importlib
import pkgutil
import typer
from typer.models import CommandInfo

from .base import BaseCommand, command_callback, GenerateCommand

# Type for command functions that have name and help attributes
CommandFunction = Callable[..., Any]

class CommandRegistry:
    """Registry for CLI commands"""
    
    def __init__(self):
        self.commands: Dict[str, Union[Type[BaseCommand], typer.Typer, CommandFunction]] = {}
        self.app = typer.Typer(help="Pulp Fiction Generator")
        
        # Set to keep track of registered commands to avoid duplicates
        self._registered_modules = set()
    
    def register(self, command: Union[Type[BaseCommand], typer.Typer, CommandFunction], name: Optional[str] = None) -> None:
        """Register a command class, Typer app, or function with name/help attributes"""
        if isinstance(command, type) and issubclass(command, BaseCommand):
            # Register a class-based command
            command_name = command.name
            
            # Skip if already registered
            if command_name in self.commands:
                return
            
            self.commands[command_name] = command
            
            # Special handling for GenerateCommand which needs parameter preservation
            if issubclass(command, GenerateCommand):
                # Use direct registration with the original signature
                run_method = command._run_impl
                # Get the signature and preserve parameter defaults and annotations
                sig = inspect.signature(run_method)
                
                # Define a wrapper function that preserves the signature
                # This is actually registered with typer
                @self.app.command(name=command_name, help=command.help)
                def generate_wrapper(**kwargs):
                    return command.run(**kwargs)
                
                # Try to copy signature metadata
                generate_wrapper.__signature__ = sig
                generate_wrapper.__annotations__ = getattr(run_method, "__annotations__", {})
                generate_wrapper.__defaults__ = getattr(run_method, "__defaults__", None)
                
            else:
                # Standard command handling
                # Create a callback for the command
                callback = command_callback(command)
                
                # Set properties on the callback for documentation
                callback.__name__ = command.name
                callback.__doc__ = command.help
                
                # Register with Typer
                self.app.command(name=command_name, help=command.help)(callback)
            
        elif isinstance(command, typer.Typer):
            # Register a sub-Typer app
            command_name = name or getattr(command, "name", None)
            if not command_name:
                raise ValueError("Command name is required for Typer app registration")
            
            # Skip if already registered
            if command_name in self.commands:
                return
                
            self.commands[command_name] = command
            
            # Register sub-app with main app
            self.app.add_typer(command, name=command_name)
            
        elif callable(command) and hasattr(command, "name") and hasattr(command, "help"):
            # Register a function with name and help attributes
            command_name = command.name
            command_help = command.help
            
            # Skip if already registered
            if command_name in self.commands:
                return
                
            self.commands[command_name] = command
            
            # Register the function directly
            self.app.command(name=command_name, help=command_help)(command)
            
        else:
            raise TypeError("Command must be a BaseCommand subclass, a Typer app, or a function with name and help attributes")
    
    def discover_commands(self, package_name: str = "pulp_fiction_generator.cli.commands") -> None:
        """Discover and register commands in the specified package"""
        # Skip if this package has already been processed
        if package_name in self._registered_modules:
            return
            
        # Add to tracked modules
        self._registered_modules.add(package_name)
        
        try:
            package = importlib.import_module(package_name)
            
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                if is_pkg:
                    self.discover_commands(name)
                else:
                    # Skip if this module has already been processed
                    if name in self._registered_modules:
                        continue
                        
                    # Add to tracked modules
                    self._registered_modules.add(name)
                    
                    module = importlib.import_module(name)
                    
                    # Check for direct command functions in the module
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if callable(item) and hasattr(item, "name") and hasattr(item, "help"):
                            self.register(item)
                    
                    # Check for Typer apps in the module
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if isinstance(item, typer.Typer):
                            # Get the command name from attributes, the callback, or the module name
                            app_name = getattr(item, "name", None)
                            
                            if not app_name and hasattr(item, "registered_callback") and item.registered_callback:
                                for callback in item.registered_callback:
                                    if hasattr(callback, "name"):
                                        app_name = callback.name
                                        break
                            
                            if not app_name:
                                # Try to get the name from module name (turn list_genres into list-genres)
                                module_parts = name.split('.')
                                module_name = module_parts[-1]
                                app_name = module_name.replace('_', '-')
                                
                            # Register the Typer app
                            self.register(item, app_name)
                            
                    # Also check for BaseCommand classes
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (inspect.isclass(item) and 
                            issubclass(item, BaseCommand) and 
                            item is not BaseCommand and
                            hasattr(item, 'name') and
                            item.name):
                            self.register(item)
        except (ImportError, AttributeError) as e:
            print(f"Error discovering commands in {package_name}: {e}")
    
    def get_app(self) -> typer.Typer:
        """Get the configured Typer app"""
        return self.app 