"""
Statistics commands for Pulp Fiction Generator.
"""

import os
import json
import typer
import datetime
from typing import Dict, List, Optional, Union, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from pathlib import Path

from ..base import BaseCommand
from ...utils.story_persistence import StoryPersistence
from ...utils.errors import logger

# Create a Typer app for stats commands
stats_app = typer.Typer(help="Show statistics for generated stories")
console = Console()


class StatsCommand(BaseCommand):
    """Command to show statistics about generated stories"""
    
    name = "stats"
    help = "Show statistics about generated stories"
    
    @classmethod
    def _run_impl(
        cls,
        project: Optional[str] = typer.Argument(None, help="Specific project to show stats for"),
        all_projects: bool = typer.Option(False, "--all", "-a", help="Show stats for all projects"),
        format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
        sort_by: str = typer.Option(
            "date", "--sort", "-s", 
            help="Sort by (date, words, chapters)"
        ),
    ):
        """Show statistics about generated stories"""
        # Initialize story persistence to access stories
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        story_persistence = StoryPersistence(output_dir)
        
        try:
            # Get story data
            if project:
                # Get a specific project
                try:
                    story = story_persistence.load_story(project)
                    stats = cls._compile_project_stats(story)
                    cls._display_project_stats(stats, format)
                except Exception as e:
                    console.print(f"[bold red]Error loading project '{project}': {str(e)}[/bold red]")
                    return
            else:
                # Get all projects
                projects = story_persistence.list_stories()
                if not projects:
                    console.print("[yellow]No projects found.[/yellow]")
                    return
                
                all_stats = []
                for proj in projects:
                    try:
                        story = story_persistence.load_story(proj)
                        stats = cls._compile_project_stats(story)
                        all_stats.append(stats)
                    except Exception as e:
                        logger.warning(f"Error loading project '{proj}': {str(e)}")
                
                # Sort the stats
                if sort_by == "date":
                    all_stats.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
                elif sort_by == "words":
                    all_stats.sort(key=lambda x: x.get("word_count", 0), reverse=True)
                elif sort_by == "chapters":
                    all_stats.sort(key=lambda x: x.get("chapter_count", 0), reverse=True)
                
                cls._display_all_stats(all_stats, format)
        
        except Exception as e:
            console.print(f"[bold red]Error retrieving statistics: {str(e)}[/bold red]")
    
    @staticmethod
    def _compile_project_stats(story) -> Dict[str, Any]:
        """Compile statistics for a single project"""
        metadata = story.metadata
        
        # Calculate time spent
        time_spent = 0
        if hasattr(metadata, "generation_time"):
            time_spent = metadata.generation_time
        
        # Get additional metadata
        genres = [metadata.genre]
        if hasattr(metadata, "subgenres") and metadata.subgenres:
            genres.extend(metadata.subgenres)
        
        # Calculate words per minute
        words_per_minute = 0
        if time_spent > 0:
            words_per_minute = int((metadata.word_count / time_spent) * 60)
        
        # Get last modified date
        last_modified = metadata.last_modified if hasattr(metadata, "last_modified") else ""
        created_date = metadata.created if hasattr(metadata, "created") else ""
        
        return {
            "project_name": metadata.name if hasattr(metadata, "name") else "Unknown",
            "title": metadata.title,
            "genre": ", ".join(genres),
            "chapter_count": metadata.chapter_count,
            "word_count": metadata.word_count,
            "generation_time": time_spent,
            "words_per_minute": words_per_minute,
            "last_modified": last_modified,
            "created_date": created_date,
            "model": metadata.model if hasattr(metadata, "model") else "Unknown",
        }
    
    @staticmethod
    def _display_project_stats(stats: Dict[str, Any], format: str):
        """Display statistics for a single project"""
        if format.lower() == "json":
            console.print_json(json.dumps(stats, indent=2))
            return
        
        # Format times
        gen_time = stats.get("generation_time", 0)
        gen_time_str = f"{int(gen_time // 60)}m {int(gen_time % 60)}s" if gen_time else "N/A"
        
        # Create a rich panel with the stats
        content = [
            f"[bold cyan]Title:[/bold cyan] {stats.get('title', 'Untitled')}",
            f"[bold cyan]Genre:[/bold cyan] {stats.get('genre', 'Unknown')}",
            f"[bold cyan]Chapters:[/bold cyan] {stats.get('chapter_count', 0)}",
            f"[bold cyan]Word Count:[/bold cyan] {stats.get('word_count', 0):,}",
            f"[bold cyan]Generation Time:[/bold cyan] {gen_time_str}",
            f"[bold cyan]Words per Minute:[/bold cyan] {stats.get('words_per_minute', 0):,}",
            f"[bold cyan]Model:[/bold cyan] {stats.get('model', 'Unknown')}",
        ]
        
        # Add dates if available
        if stats.get("created_date"):
            content.append(f"[bold cyan]Created:[/bold cyan] {stats.get('created_date')}")
        if stats.get("last_modified"):
            content.append(f"[bold cyan]Last Modified:[/bold cyan] {stats.get('last_modified')}")
        
        panel = Panel(
            "\n".join(content),
            title=f"[bold]Project: {stats.get('project_name', 'Unknown')}[/bold]",
            expand=False,
            border_style="blue",
            box=box.ROUNDED
        )
        console.print(panel)
    
    @staticmethod
    def _display_all_stats(all_stats: List[Dict[str, Any]], format: str):
        """Display statistics for all projects"""
        if format.lower() == "json":
            console.print_json(json.dumps(all_stats, indent=2))
            return
        
        # Create a table for all stats
        table = Table(title="Project Statistics", box=box.ROUNDED)
        table.add_column("Project", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Genre", style="green")
        table.add_column("Chapters", justify="right", style="yellow")
        table.add_column("Words", justify="right", style="yellow")
        table.add_column("Gen Time", justify="right", style="magenta")
        table.add_column("WPM", justify="right", style="magenta")
        table.add_column("Last Modified", style="blue")
        
        # Total stats
        total_words = 0
        total_chapters = 0
        total_time = 0
        
        for stats in all_stats:
            # Format times
            gen_time = stats.get("generation_time", 0)
            gen_time_str = f"{int(gen_time // 60)}m {int(gen_time % 60)}s" if gen_time else "N/A"
            
            # Add row
            table.add_row(
                stats.get("project_name", "Unknown"),
                stats.get("title", "Untitled"),
                stats.get("genre", "Unknown"),
                str(stats.get("chapter_count", 0)),
                f"{stats.get('word_count', 0):,}",
                gen_time_str,
                f"{stats.get('words_per_minute', 0):,}",
                stats.get("last_modified", "Unknown"),
            )
            
            # Update totals
            total_words += stats.get("word_count", 0)
            total_chapters += stats.get("chapter_count", 0)
            total_time += stats.get("generation_time", 0)
        
        # Add summary row
        avg_wpm = int((total_words / total_time) * 60) if total_time > 0 else 0
        total_time_str = f"{int(total_time // 60)}m {int(total_time % 60)}s" if total_time else "N/A"
        
        table.add_section()
        table.add_row(
            f"[bold]TOTAL ({len(all_stats)})[/bold]",
            "",
            "",
            f"[bold]{total_chapters}[/bold]",
            f"[bold]{total_words:,}[/bold]",
            f"[bold]{total_time_str}[/bold]",
            f"[bold]{avg_wpm:,}[/bold]",
            "",
        )
        
        console.print(table)


# Register the command with the app
@stats_app.callback(invoke_without_command=True)
def main(
    project: Optional[str] = typer.Argument(None, help="Specific project to show stats for"),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Show stats for all projects"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
    sort_by: str = typer.Option(
        "date", "--sort", "-s", 
        help="Sort by (date, words, chapters)"
    ),
):
    """Show statistics about generated stories"""
    if typer.Context.get_current().invoked_subcommand is None:
        StatsCommand.run(project=project, all_projects=all_projects, format=format, sort_by=sort_by)
        
        
@stats_app.command("summary")
def summary_cmd():
    """Show a summary of all story generation statistics"""
    # Initialize story persistence to access stories
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    try:
        # Get all projects
        projects = story_persistence.list_stories()
        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return
        
        # Collect stats
        all_stats = []
        for proj in projects:
            try:
                story = story_persistence.load_story(proj)
                stats = StatsCommand._compile_project_stats(story)
                all_stats.append(stats)
            except Exception as e:
                logger.warning(f"Error loading project '{proj}': {str(e)}")
        
        # Calculate summary stats
        total_projects = len(all_stats)
        total_words = sum(s.get("word_count", 0) for s in all_stats)
        total_chapters = sum(s.get("chapter_count", 0) for s in all_stats)
        total_time = sum(s.get("generation_time", 0) for s in all_stats)
        
        # Genre distribution
        genres = {}
        for stats in all_stats:
            genre = stats.get("genre", "Unknown")
            for g in genre.split(", "):
                if g in genres:
                    genres[g] += 1
                else:
                    genres[g] = 1
        
        # Sort genres by count
        sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
        
        # Display summary stats
        console.print("\n[bold]Story Generation Summary[/bold]\n")
        
        console.print(f"[cyan]Total Projects:[/cyan] {total_projects}")
        console.print(f"[cyan]Total Chapters:[/cyan] {total_chapters}")
        console.print(f"[cyan]Total Words:[/cyan] {total_words:,}")
        
        # Format time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        time_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        console.print(f"[cyan]Total Generation Time:[/cyan] {time_str}")
        
        # Words per minute
        avg_wpm = int((total_words / total_time) * 60) if total_time > 0 else 0
        console.print(f"[cyan]Average Words per Minute:[/cyan] {avg_wpm:,}")
        
        # Genre distribution
        console.print("\n[bold]Genre Distribution:[/bold]")
        for genre, count in sorted_genres:
            percentage = (count / total_projects) * 100
            console.print(f"[green]{genre}:[/green] {count} projects ({percentage:.1f}%)")
        
    except Exception as e:
        console.print(f"[bold red]Error generating summary: {str(e)}[/bold red]") 