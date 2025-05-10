"""
List plugins command implementation.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import box

from ..base import with_error_handling
from ...plugins.manager import PluginManager
from ...plugins.base import GenrePlugin, AgentPlugin, ModelPlugin

console = Console()

@with_error_handling
def list_plugins(
    genre_only: bool = typer.Option(
        False, "--genre", "-g", help="Only show genre plugins"
    ),
    agent_only: bool = typer.Option(
        False, "--agent", "-a", help="Only show agent plugins"
    ),
    model_only: bool = typer.Option(
        False, "--model", "-m", help="Only show model plugins"
    ),
):
    """List installed plugins"""
    console.print("[bold blue]Discovering plugins...[/bold blue]")
    
    # Create the plugin manager and discover plugins
    manager = PluginManager()
    manager.discover_plugins()
    
    # Get plugins according to filter
    if genre_only:
        plugins = manager.get_plugins(GenrePlugin)
        plugin_type = "Genre"
    elif agent_only:
        plugins = manager.get_plugins(AgentPlugin)
        plugin_type = "Agent"
    elif model_only:
        plugins = manager.get_plugins(ModelPlugin)
        plugin_type = "Model"
    else:
        plugins = manager.get_plugins()
        plugin_type = "All"
    
    # Create a table
    table = Table(title=f"{plugin_type} Plugins", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Type")
    table.add_column("Version")
    table.add_column("Description")
    
    if not plugins:
        console.print("[yellow]No plugins found. You can create and install custom plugins to extend the system.[/yellow]")
        
        # Print example usage
        console.print("\n[bold]How to create a plugin:[/bold]")
        console.print("1. Create a Python class that inherits from one of the plugin base classes")
        console.print("2. Place the file in ~/.pulp-fiction/plugins/ or ./plugins/")
        console.print("3. Run 'pulp-fiction plugins' to see your plugin listed")
    else:
        # Add each plugin to the table
        for plugin_class in plugins:
            try:
                info = plugin_class.get_plugin_info()
                table.add_row(
                    info["id"],
                    info["name"],
                    info["type"],
                    info["version"],
                    info["description"]
                )
            except Exception as e:
                console.print(f"[red]Error getting info for plugin {plugin_class.__name__}: {e}[/red]")
        
        # Display the table
        console.print(table)
        
        # Print usage example if we have genre plugins
        if not genre_only and not agent_only and not model_only:
            genre_plugins = manager.get_plugins(GenrePlugin)
            if genre_plugins:
                plugin = genre_plugins[0]
                console.print("\n[bold]Example usage with genre plugin:[/bold]")
                console.print(f"pulp-fiction generate --genre {plugin.plugin_id} --chapters 1")

# The command registry will pick up this name and function directly
list_plugins.name = "plugins"
list_plugins.help = "List installed plugins" 