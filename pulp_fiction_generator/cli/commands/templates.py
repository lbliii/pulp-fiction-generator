"""
Template management commands for Pulp Fiction Generator.
"""

import os
import json
import typer
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path

from ..base import BaseCommand
from ...utils.errors import logger

# Create a Typer app for template commands
templates_app = typer.Typer(help="Manage project templates")
console = Console()

# Default location for storing templates
DEFAULT_TEMPLATES_DIR = os.path.expanduser(os.getenv("TEMPLATES_DIR", "~/.pulp_fiction/templates"))


def get_templates_dir() -> Path:
    """Get the templates directory, creating it if it doesn't exist."""
    templates_dir = Path(DEFAULT_TEMPLATES_DIR)
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


def list_templates() -> Dict[str, Dict]:
    """List all available templates."""
    templates_dir = get_templates_dir()
    templates = {}
    
    for file in templates_dir.glob("*.json"):
        try:
            with open(file, "r") as f:
                template = json.load(f)
                templates[file.stem] = template
        except Exception as e:
            logger.warning(f"Error loading template {file}: {e}")
    
    return templates


@templates_app.command("list")
def list_templates_cmd():
    """List all available project templates."""
    templates = list_templates()
    
    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        console.print(f"Create templates with '[bold]pulp-fiction templates save[/bold]'")
        return
        
    table = Table(title="Project Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Genre", style="green")
    table.add_column("Description", style="white")
    table.add_column("Parameters", style="yellow")
    
    for name, template in templates.items():
        # Extract key parameters for display
        params = []
        for key, value in template.get("parameters", {}).items():
            if key not in ["genre", "description"] and value is not None:
                params.append(f"{key}={value}")
        
        table.add_row(
            name,
            template.get("genre", "N/A"),
            template.get("description", "No description"),
            ", ".join(params[:3]) + ("..." if len(params) > 3 else "")
        )
    
    console.print(table)


@templates_app.command("save")
def save_template_cmd(
    name: str = typer.Argument(..., help="Name for the template"),
    genre: str = typer.Option(..., "--genre", "-g", help="Pulp fiction genre"),
    description: str = typer.Option("", "--description", "-d", help="Template description"),
    chapters: int = typer.Option(1, "--chapters", "-c", help="Number of chapters"),
    model: str = typer.Option("llama3.2", "--model", "-m", help="Ollama model to use"),
    plot_template: Optional[str] = typer.Option(None, "--plot", "-p", help="Plot template"),
    output_format: str = typer.Option("markdown", "--format", help="Output format"),
):
    """Save current parameters as a template for reuse."""
    templates_dir = get_templates_dir()
    template_path = templates_dir / f"{name}.json"
    
    # Create template data structure
    template = {
        "name": name,
        "genre": genre,
        "description": description,
        "parameters": {
            "genre": genre,
            "chapters": chapters,
            "model": model,
            "plot_template": plot_template,
            "output_format": output_format,
        }
    }
    
    # Save to file
    try:
        with open(template_path, "w") as f:
            json.dump(template, f, indent=2)
        console.print(f"[green]Template '{name}' saved successfully.[/green]")
    except Exception as e:
        console.print(f"[bold red]Error saving template: {e}[/bold red]")


@templates_app.command("delete")
def delete_template_cmd(
    name: str = typer.Argument(..., help="Name of the template to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete without confirmation"),
):
    """Delete a project template."""
    templates_dir = get_templates_dir()
    template_path = templates_dir / f"{name}.json"
    
    if not template_path.exists():
        console.print(f"[bold red]Template '{name}' not found.[/bold red]")
        return
    
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete template '{name}'?")
        if not confirm:
            console.print("Aborted.")
            return
    
    try:
        template_path.unlink()
        console.print(f"[green]Template '{name}' deleted successfully.[/green]")
    except Exception as e:
        console.print(f"[bold red]Error deleting template: {e}[/bold red]")


@templates_app.command("use")
def use_template_cmd(
    name: str = typer.Argument(..., help="Name of the template to use"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Override title"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Override output file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show command without executing"),
):
    """Generate a story using a saved template."""
    templates = list_templates()
    
    if name not in templates:
        console.print(f"[bold red]Template '{name}' not found.[/bold red]")
        return
    
    template = templates[name]
    parameters = template.get("parameters", {})
    
    # Override parameters if provided
    if title:
        parameters["title"] = title
    if output_file:
        parameters["output_file"] = output_file
    
    # Build the command
    command = ["pulp-fiction", "generate"]
    
    for key, value in parameters.items():
        if value is None:
            continue
            
        if isinstance(value, bool):
            if value:
                command.append(f"--{key}")
        else:
            command.append(f"--{key}")
            command.append(str(value))
    
    command_str = " ".join(command)
    
    if dry_run:
        console.print("[bold]Command:[/bold]")
        console.print(f"[green]{command_str}[/green]")
        return
    
    # Execute the command
    console.print(f"[cyan]Executing template '{name}'...[/cyan]")
    console.print(f"[dim]{command_str}[/dim]")
    
    # Import and run main generate command
    try:
        from pulp_fiction_generator.cli.commands.generate import Generate
        
        # Filter out None values and convert parameters
        filtered_params = {}
        for key, value in parameters.items():
            if value is not None:
                # Convert string values to appropriate types if needed
                if key == "chapters" and isinstance(value, str):
                    value = int(value)
                filtered_params[key] = value
                
        # Add overrides
        if title:
            filtered_params["title"] = title
        if output_file:
            filtered_params["output_file"] = output_file
            
        # Run the command
        Generate.run(**filtered_params)
    except Exception as e:
        console.print(f"[bold red]Error executing template: {e}[/bold red]") 