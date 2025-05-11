"""
CLI commands related to memory management.
"""

import typer
from typing import Optional
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from ...utils.memory_utils import reset_memory, export_memory, list_memory_contents

console = Console()
memory_app = typer.Typer(name="memory", help="Memory management commands")

@memory_app.command("reset")
def reset(
    memory_type: str = typer.Option(
        "all", 
        "--type", "-t", 
        help="Type of memory to reset (all, short, long, entities, knowledge, kickoff_outputs)"
    ),
    genre: Optional[str] = typer.Option(
        None, 
        "--genre", "-g", 
        help="Genre to reset memory for (optional)"
    ),
    storage_dir: str = typer.Option(
        "./.memory", 
        "--storage-dir", "-d", 
        help="Base storage directory"
    ),
    force: bool = typer.Option(
        False, 
        "--force", "-f", 
        help="Force reset without confirmation"
    )
):
    """Reset memory for all or specific types."""
    if not force:
        target = f"{memory_type} memory"
        if genre:
            target += f" for genre '{genre}'"
        else:
            target += " for all genres"
            
        proceed = typer.confirm(f"Reset {target}?")
        if not proceed:
            rprint("[yellow]Operation cancelled.[/yellow]")
            return
            
    success = reset_memory(memory_type, genre, storage_dir)
    
    if success:
        target = f"{memory_type} memory"
        if genre:
            target += f" for genre '{genre}'"
        else:
            target += " for all genres"
            
        rprint(f"[green]Successfully reset {target}[/green]")
    else:
        rprint("[red]Failed to reset memory[/red]")

@memory_app.command("export")
def export(
    output_dir: str = typer.Argument(
        ..., 
        help="Directory to export memory to"
    ),
    genre: Optional[str] = typer.Option(
        None, 
        "--genre", "-g", 
        help="Genre to export memory for (optional)"
    ),
    storage_dir: str = typer.Option(
        "./.memory", 
        "--storage-dir", "-d", 
        help="Base storage directory"
    )
):
    """Export memory to a directory."""
    success = export_memory(output_dir, genre, storage_dir)
    
    if success:
        target = "all memory"
        if genre:
            target = f"memory for genre '{genre}'"
            
        rprint(f"[green]Successfully exported {target} to {output_dir}[/green]")
    else:
        rprint("[red]Failed to export memory[/red]")

@memory_app.command("list")
def list_memory(
    genre: Optional[str] = typer.Option(
        None, 
        "--genre", "-g", 
        help="Genre to list memory for (optional)"
    ),
    storage_dir: str = typer.Option(
        "./.memory", 
        "--storage-dir", "-d", 
        help="Base storage directory"
    )
):
    """List memory contents."""
    memory_info = list_memory_contents(genre, storage_dir)
    
    if memory_info["status"] == "not_found":
        rprint(f"[yellow]{memory_info['message']}[/yellow]")
        return
    elif memory_info["status"] == "error":
        rprint(f"[red]Error: {memory_info['message']}[/red]")
        return
        
    if genre:
        # Display memory for the specific genre
        table = Table(title=f"Memory for Genre: {genre}")
        table.add_column("Memory Type", style="cyan")
        table.add_column("Available", style="green")
        
        for memory_type, available in memory_info["memory"].items():
            table.add_row(memory_type, "✅" if available else "❌")
            
        console.print(table)
    else:
        # Display all genres with memory
        if "genres" in memory_info and memory_info["genres"]:
            table = Table(title="Genres with Memory")
            table.add_column("Genre", style="cyan")
            
            for genre_name in memory_info["genres"]:
                table.add_row(genre_name)
                
            console.print(table)
        else:
            rprint("[yellow]No memory found for any genre[/yellow]") 