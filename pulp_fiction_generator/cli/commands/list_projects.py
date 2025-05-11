"""
List projects command implementation.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text
from typing import Optional
import os
from datetime import datetime
import humanize

from ..base import BaseCommand
from ...utils.story_persistence import StoryPersistence

console = Console()

def list_projects(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show additional details for each project"
    ),
    limit: Optional[int] = typer.Option(
        None, "--limit", "-n", help="Maximum number of projects to display"
    ),
    project_tasks: Optional[str] = typer.Option(
        None, "--tasks", "-t", help="Show completed tasks for a specific project"
    )
):
    """List all available story projects"""
    
    # Initialize story persistence
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    # If requesting tasks for a specific project
    if project_tasks:
        try:
            # Load the story state
            story_state = story_persistence.load_story(project_tasks)
            
            # Check if it has completed tasks
            if hasattr(story_state.metadata, 'completed_tasks') and story_state.metadata.completed_tasks:
                console.print(f"\n[bold]Completed tasks for project:[/bold] [cyan]{project_tasks}[/cyan]\n")
                
                # Create a table for tasks
                task_table = Table(show_header=True, header_style="bold magenta")
                task_table.add_column("Chapter", style="cyan", justify="center")
                task_table.add_column("Task Type", style="green")
                task_table.add_column("Completed", style="blue")
                task_table.add_column("Output Length", justify="right")
                
                # Sort chapters numerically
                chapters = sorted(story_state.metadata.completed_tasks.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
                
                # Add rows for each task
                for chapter in chapters:
                    tasks = story_state.metadata.completed_tasks[chapter]
                    for task_type, task_data in tasks.items():
                        # Get completion timestamp
                        if "timestamp" in task_data:
                            try:
                                timestamp = datetime.fromisoformat(task_data["timestamp"])
                                completed_time = humanize.naturaltime(datetime.now() - timestamp)
                            except (ValueError, TypeError):
                                completed_time = "unknown"
                        else:
                            completed_time = "unknown"
                        
                        # Get output length
                        output_length = len(task_data.get("output", "")) if "output" in task_data else 0
                        
                        task_table.add_row(
                            chapter,
                            task_type,
                            completed_time,
                            f"{output_length} chars"
                        )
                
                console.print(task_table)
                
                # Show which chapter outputs are saved
                console.print("\n[bold]Chapter contents:[/bold]")
                for i, chapter in enumerate(story_state.chapters, 1):
                    console.print(f"  Chapter {i}: [green]{len(chapter)} chars[/green]")
                
                # Print a hint for resuming
                console.print("\n[dim]To resume this project:[/dim]")
                console.print(f"[cyan]pulp-fiction generate --resume {project_tasks} --chapters 1[/cyan]")
                
                return
            else:
                console.print(f"\n[yellow]No task tracking information available for project: {project_tasks}[/yellow]")
                console.print("[dim]This could be because the project was created before task tracking was implemented.[/dim]")
                return
                
        except (FileNotFoundError, ValueError) as e:
            console.print(f"\n[bold red]Error loading project:[/bold red] {e}")
            return
    
    # Get all projects
    projects = story_persistence.list_projects()
    
    # Sort by last modified date (newest first)
    projects.sort(key=lambda p: p.get("modified", ""), reverse=True)
    
    # Apply limit if specified
    if limit is not None and limit > 0:
        projects = projects[:limit]
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project Name", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Genre", style="yellow")
    table.add_column("Chapters", justify="right")
    
    if verbose:
        table.add_column("Last Modified", style="blue")
        table.add_column("Latest File", style="dim")
    else:
        table.add_column("Last Modified", style="blue")
    
    # Add rows
    for project in projects:
        row = []
        # Project name
        row.append(project["name"])
        
        # Title
        row.append(project["title"])
        
        # Genre
        row.append(project.get("genre", "unknown"))
        
        # Chapters
        row.append(str(project.get("chapters", 0)))
        
        # Last modified
        if "modified" in project:
            try:
                # Parse ISO formatted date
                modified_date = datetime.fromisoformat(project["modified"])
                # Format as relative time
                modified_str = humanize.naturaltime(datetime.now() - modified_date)
                row.append(modified_str)
            except (ValueError, TypeError):
                row.append("unknown")
        else:
            row.append("unknown")
        
        # Add latest file if verbose
        if verbose and "latest_file" in project:
            row.append(project["latest_file"])
        
        table.add_row(*row)
    
    # Print results
    console.print("\n[bold]Available Story Projects:[/bold]\n")
    
    if not projects:
        console.print("[italic]No projects found.[/italic]")
    else:
        console.print(table)
        
        # Print usage hint
        console.print("\n[dim]To continue a project:[/dim]")
        console.print("[cyan]pulp-fiction generate --resume PROJECT_NAME --chapters 1[/cyan]")

list_projects.name = "list-projects"
list_projects.help = "List all available story projects" 