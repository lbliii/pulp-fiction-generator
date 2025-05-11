"""
Export commands for Pulp Fiction Generator.
"""

import os
import typer
from enum import Enum
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from typing import List, Optional

from ..base import BaseCommand
from ...utils.story_persistence import StoryPersistence
from ...utils.errors import logger
from ...exporters.factory import ExporterFactory
from ...exporters.exceptions import ExporterDependencyError

# Create a Typer app for export commands
export_app = typer.Typer(help="Export stories in various formats")
console = Console()

class OutputFormat(str, Enum):
    """Output formats for story export."""
    plain = "plain"
    markdown = "md"
    html = "html"
    pdf = "pdf"
    docx = "docx"
    epub = "epub"
    terminal = "terminal"
    all = "all"


@export_app.command("story")
def export_story_cmd(
    project: str = typer.Argument(..., help="Project name to export"),
    format: List[OutputFormat] = typer.Option(
        [OutputFormat.markdown], "--format", "-f", 
        help="Output format(s) to export to"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", 
        help="Output directory (defaults to ./exports/PROJECT_NAME)"
    ),
    include_metadata: bool = typer.Option(
        False, "--metadata", "-m",
        help="Include story metadata in exported files"
    ),
):
    """Export a story to various formats."""
    # Initialize story persistence to access stories
    story_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(story_dir)
    
    # Set up output directory
    if not output_dir:
        output_dir = f"./exports/{project}"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load the story
    try:
        story = story_persistence.load_story(project)
        console.print(f"[green]Loaded project: {project}[/green]")
    except Exception as e:
        console.print(f"[bold red]Error loading project '{project}': {str(e)}[/bold red]")
        return
    
    # Get content
    content = story.content
    
    # Add metadata if requested
    if include_metadata:
        metadata = story.metadata
        metadata_text = f"""
# Story Metadata

- **Title**: {metadata.title}
- **Genre**: {metadata.genre}
- **Chapters**: {metadata.chapter_count}
- **Word Count**: {metadata.word_count:,}
- **Generated with**: {metadata.model if hasattr(metadata, "model") else "Unknown model"}
"""
        content = metadata_text + "\n\n" + content
    
    # Process all formats
    formats_to_export = []
    if OutputFormat.all in format:
        formats_to_export = [f for f in OutputFormat if f != OutputFormat.all]
    else:
        formats_to_export = format
    
    # Export to each format
    with Progress() as progress:
        task = progress.add_task("[green]Exporting...", total=len(formats_to_export))
        
        for fmt in formats_to_export:
            try:
                progress.update(task, description=f"[green]Exporting to {fmt}...")
                output_file = output_path / f"{project}.{fmt}"
                
                # Get exporter from factory
                exporter = ExporterFactory.create_exporter(fmt)
                if not exporter:
                    console.print(f"[yellow]No exporter available for format: {fmt}[/yellow]")
                    continue
                
                # Export the content
                result_path = exporter.export(content, str(output_file))
                console.print(f"[green]Exported to {fmt}: {result_path}[/green]")
                
            except ExporterDependencyError as e:
                console.print(f"[yellow]Missing dependency for {fmt} format: {e}[/yellow]")
                continue
            except Exception as e:
                console.print(f"[bold red]Error exporting to {fmt}: {str(e)}[/bold red]")
                continue
            finally:
                progress.update(task, advance=1)
    
    console.print(f"[bold green]Export complete![/bold green] Files saved to: {output_path}")


@export_app.command("bulk")
def bulk_export_cmd(
    format: List[OutputFormat] = typer.Option(
        [OutputFormat.markdown], "--format", "-f", 
        help="Output format(s) to export to"
    ),
    output_dir: str = typer.Option(
        "./exports", "--output", "-o", 
        help="Output directory"
    ),
    include_metadata: bool = typer.Option(
        False, "--metadata", "-m",
        help="Include story metadata in exported files"
    ),
    recent: Optional[int] = typer.Option(
        None, "--recent", "-r",
        help="Export only the most recent N projects"
    ),
):
    """Bulk export multiple stories to various formats."""
    # Initialize story persistence to access stories
    story_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(story_dir)
    
    # Set up output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all projects
    try:
        projects = story_persistence.list_stories()
        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return
            
        # Sort by modification time if recent flag is set
        if recent is not None:
            # Get metadata for all projects to sort by date
            project_data = []
            for proj in projects:
                try:
                    story = story_persistence.load_story(proj)
                    if hasattr(story.metadata, "last_modified"):
                        project_data.append((proj, story.metadata.last_modified))
                    else:
                        project_data.append((proj, ""))
                except Exception:
                    project_data.append((proj, ""))
            
            # Sort by last_modified (most recent first)
            project_data.sort(key=lambda x: x[1], reverse=True)
            
            # Limit to the most recent N projects
            projects = [p[0] for p in project_data[:recent]]
        
        console.print(f"[green]Found {len(projects)} projects to export[/green]")
    except Exception as e:
        console.print(f"[bold red]Error listing projects: {str(e)}[/bold red]")
        return
    
    # Process all formats
    formats_to_export = []
    if OutputFormat.all in format:
        formats_to_export = [f for f in OutputFormat if f != OutputFormat.all]
    else:
        formats_to_export = format
    
    # Export each project in each format
    with Progress() as progress:
        task = progress.add_task("[green]Exporting projects...", total=len(projects))
        
        for project in projects:
            try:
                progress.update(task, description=f"[green]Exporting project: {project}...")
                
                # Create project directory
                project_dir = output_path / project
                project_dir.mkdir(parents=True, exist_ok=True)
                
                # Load the story
                story = story_persistence.load_story(project)
                
                # Get content
                content = story.content
                
                # Add metadata if requested
                if include_metadata:
                    metadata = story.metadata
                    metadata_text = f"""
# Story Metadata

- **Title**: {metadata.title}
- **Genre**: {metadata.genre}
- **Chapters**: {metadata.chapter_count}
- **Word Count**: {metadata.word_count:,}
- **Generated with**: {metadata.model if hasattr(metadata, "model") else "Unknown model"}
"""
                    content = metadata_text + "\n\n" + content
                
                # Export to each format
                for fmt in formats_to_export:
                    try:
                        output_file = project_dir / f"{project}.{fmt}"
                        
                        # Get exporter from factory
                        exporter = ExporterFactory.create_exporter(fmt)
                        if not exporter:
                            console.print(f"[yellow]No exporter available for format: {fmt}[/yellow]")
                            continue
                        
                        # Export the content
                        exporter.export(content, str(output_file))
                        
                    except ExporterDependencyError:
                        # Skip formats with missing dependencies in bulk mode
                        continue
                    except Exception as e:
                        console.print(f"[yellow]Error exporting {project} to {fmt}: {str(e)}[/yellow]")
                        continue
                
            except Exception as e:
                console.print(f"[yellow]Error processing project '{project}': {str(e)}[/yellow]")
                continue
            finally:
                progress.update(task, advance=1)
    
    console.print(f"[bold green]Bulk export complete![/bold green] Files saved to: {output_path}")


class ExportCommand(BaseCommand):
    """Command to export stories to various formats"""
    
    name = "export"
    help = "Export stories to various formats"
    
    @classmethod
    def _run_impl(
        cls,
        project: str = typer.Argument(..., help="Project name to export"),
        format: str = typer.Option(
            "markdown", "--format", "-f", 
            help="Output format to export to (plain, md, html, pdf, docx, epub, all)"
        ),
        output_file: Optional[str] = typer.Option(
            None, "--output", "-o", 
            help="Output file path (defaults to ./exports/PROJECT_NAME.FORMAT)"
        ),
        include_metadata: bool = typer.Option(
            False, "--metadata", "-m",
            help="Include story metadata in exported file"
        ),
    ):
        """Export a story to a specific format."""
        # Initialize story persistence to access stories
        story_dir = os.getenv("OUTPUT_DIR", "./output")
        story_persistence = StoryPersistence(story_dir)
        
        # Set up output file
        if not output_file:
            # Create exports directory if it doesn't exist
            exports_dir = Path("./exports")
            exports_dir.mkdir(parents=True, exist_ok=True)
            output_file = f"./exports/{project}.{format}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Load the story
        try:
            story = story_persistence.load_story(project)
            cls.success(f"Loaded project: {project}")
        except Exception as e:
            cls.error(f"Error loading project '{project}': {str(e)}")
            return
        
        # Get content
        content = story.content
        
        # Add metadata if requested
        if include_metadata:
            metadata = story.metadata
            metadata_text = f"""
# Story Metadata

- **Title**: {metadata.title}
- **Genre**: {metadata.genre}
- **Chapters**: {metadata.chapter_count}
- **Word Count**: {metadata.word_count:,}
- **Generated with**: {metadata.model if hasattr(metadata, "model") else "Unknown model"}
"""
            content = metadata_text + "\n\n" + content
        
        # Export based on format
        try:
            if format.lower() == "all":
                # Export to all available formats
                formats = ["plain", "md", "html", "pdf", "docx", "epub"]
                output_base = os.path.splitext(output_file)[0]
                
                for fmt in formats:
                    try:
                        fmt_output = f"{output_base}.{fmt}"
                        exporter = ExporterFactory.create_exporter(fmt)
                        if exporter:
                            exporter.export(content, fmt_output)
                            cls.info(f"Exported to {fmt}: {fmt_output}")
                    except ExporterDependencyError:
                        cls.warning(f"Missing dependency for {fmt} format")
                    except Exception as e:
                        cls.warning(f"Error exporting to {fmt}: {str(e)}")
                
                cls.success("Export complete!")
            else:
                # Export to a single format
                exporter = ExporterFactory.create_exporter(format.lower())
                if not exporter:
                    cls.error(f"Unsupported format: {format}")
                    return
                
                result_path = exporter.export(content, output_file)
                cls.success(f"Exported to {format}: {result_path}")
        
        except ExporterDependencyError as e:
            cls.error(f"Missing dependency: {e}")
        except Exception as e:
            cls.error(f"Export error: {str(e)}") 