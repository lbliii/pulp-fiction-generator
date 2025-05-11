"""
List genres command implementation.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from ..base import with_error_handling
from ...plugins.manager import PluginManager
from ...plugins.base import GenrePlugin

console = Console()

@with_error_handling
def list_genres():
    """List available pulp fiction genres"""
    # Use a hardcoded list for built-in genres
    built_in_genres = [
        {"name": "noir", "display_name": "Noir", "description": "Dark crime fiction featuring cynical characters and moral ambiguity"},
        {"name": "sci-fi", "display_name": "Science Fiction", "description": "Futuristic settings with advanced technology and space exploration"},
        {"name": "adventure", "display_name": "Adventure", "description": "Action-packed stories of exploration and daring feats"}
    ]
    
    # Get genre plugins if any
    plugin_manager = PluginManager()
    plugin_manager.discover_plugins()
    
    genre_plugins = plugin_manager.get_plugins(GenrePlugin)
    plugin_genres = []
    
    # Add plugin genres to the list
    for plugin_class in genre_plugins:
        try:
            plugin_info = plugin_class.get_plugin_info()
            plugin_genres.append({
                "name": plugin_info["id"],
                "display_name": plugin_info["name"],
                "description": plugin_info["description"],
                "is_plugin": True,
                "version": plugin_info["version"],
            })
        except Exception as e:
            console.print(f"[red]Error loading plugin genre {plugin_class.__name__}: {e}[/red]")
    
    # Create a table
    table = Table(title="Available Genres", box=box.ROUNDED)
    table.add_column("Genre", style="cyan")
    table.add_column("Description")
    table.add_column("Source", style="dim")
    
    # Add each genre to the table
    for genre_info in built_in_genres:
        name = genre_info.get("display_name", genre_info.get("name", "Unknown").capitalize())
        description = genre_info.get("description", "No description available")
        table.add_row(name, description, "Built-in")
    
    # Add plugin genres
    for genre_info in plugin_genres:
        name = genre_info.get("display_name", genre_info.get("name", "Unknown").capitalize())
        description = genre_info.get("description", "No description available")
        source = f"Plugin (v{genre_info.get('version', '?')})"
        table.add_row(name, description, source)
    
    # Display the table
    console.print(table)
    
    # Print example usage
    console.print("\n[bold]Example usage:[/bold]")
    console.print("pulp-fiction generate --genre noir --chapters 1")
    
    # If we have plugin genres, show an example with the first one
    if plugin_genres:
        console.print(f"pulp-fiction generate --genre {plugin_genres[0]['name']} --chapters 1")

# Add basic commandline help
console.print("\n[bold]Common commands:[/bold]")
console.print("pulp-fiction generate --help           # Show all generation options")
console.print("pulp-fiction list-genres               # List available genres")
console.print("pulp-fiction list-plugins              # List installed plugins")
console.print("pulp-fiction list-projects             # List saved story projects")
console.print("pulp-fiction flow generate --genre sci-fi # Generate using flow architecture")

# The command registry will pick up this name and function directly
list_genres.name = "list-genres"
list_genres.help = "List available pulp fiction genres" 