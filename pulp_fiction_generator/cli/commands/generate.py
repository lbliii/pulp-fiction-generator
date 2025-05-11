"""
Generate command implementation.
"""

import os
import sys
from typing import Optional, List, Tuple, Any
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn, TimeElapsedColumn

from ..base import GenerateCommand
from ...agents.agent_factory import AgentFactory
from ...crews.crew_coordinator import CrewCoordinator
from ...crews.config.crew_coordinator_config import CrewCoordinatorConfig
from ...crews.crew_executor import CrewExecutor
from ...models.ollama_adapter import OllamaAdapter
from ...utils.story_persistence import StoryPersistence, StoryState
from ...story_model.state import StoryStateManager
from ...plots import plot_registry
from ...plugins.manager import PluginManager
from ...plugins.base import GenrePlugin
from ...story_generation.story_generator import StoryGenerator
from ...story_generation.generation_config import GenerationConfig

console = Console()

class Generate(GenerateCommand):
    """Generate a pulp fiction story"""
    
    name = "generate"
    help = "Generate a pulp fiction story in the specified genre"
    
    @classmethod
    def _run_impl(
        cls,
        genre: str = typer.Option(
            "noir", "--genre", "-g", help="Pulp fiction genre to generate"
        ),
        chapters: int = typer.Option(
            1, "--chapters", "-c", help="Number of chapters to generate"
        ),
        output_file: Optional[str] = typer.Option(
            None, "--output", "-o", help="File to save the generated story to"
        ),
        model: str = typer.Option(
            "llama3.2", "--model", "-m", help="Ollama model to use"
        ),
        title: Optional[str] = typer.Option(
            None, "--title", "-t", help="Title for the story"
        ),
        save_state: bool = typer.Option(
            True, "--save-state/--no-save-state", help="Save the story state for future continuation"
        ),
        continue_from: Optional[str] = typer.Option(
            None, "--continue", "-C", help="Continue from an existing story file"
        ),
        resume: Optional[str] = typer.Option(
            None, "--resume", "-R", help="Resume a project by name"
        ),
        plot_template: Optional[str] = typer.Option(
            None, "--plot", "-p", help="Plot template to use for the story"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Enable verbose output"
        ),
        chunked: bool = typer.Option(
            False, "--chunked/--no-chunked", help="Use chunked generation process with checkpoints"
        ),
        timeout: int = typer.Option(
            120, "--timeout", "-T", help="Maximum time in seconds to wait for each generation stage (default: 120)"
        ),
        use_yaml_crew: bool = typer.Option(
            False, "--yaml-crew/--no-yaml-crew", help="Use YAML-based crew approach (experimental)"
        ),
        # Ollama resource configuration options
        ollama_threads: Optional[int] = typer.Option(
            None, "--ollama-threads", help=f"Number of CPU threads for Ollama to use (default: {os.environ.get('OLLAMA_THREADS', 4)})"
        ),
        ollama_gpu_layers: Optional[int] = typer.Option(
            None, "--ollama-gpu-layers", help=f"Number of layers to run on GPU (default: {os.environ.get('OLLAMA_GPU_LAYERS', 0)})"
        ),
        ollama_ctx_size: Optional[int] = typer.Option(
            None, "--ollama-ctx-size", help=f"Context window size (default: {os.environ.get('OLLAMA_CTX_SIZE', 4096)})"
        ),
        ollama_batch_size: Optional[int] = typer.Option(
            None, "--ollama-batch-size", help=f"Batch size for processing tokens (default: {os.environ.get('OLLAMA_BATCH_SIZE', 256)})"
        ),
        use_flow: bool = typer.Option(
            False, "--flow", "-f", help="Use CrewAI Flow for generation"
        ),
        plot_flow: bool = typer.Option(
            False, "--plot-flow", help="Generate a visualization of the flow (only used with --flow)"
        ),
        output_format: str = typer.Option(
            "plain", "--format", case_sensitive=False, help="Output format (plain, markdown, html, pdf, terminal)"
        ),
        interactive_display: bool = typer.Option(
            False, "--interactive/--no-interactive", help="Display interactive progress and story chunks during generation"
        ),
    ):
        """Generate a pulp fiction story in the specified genre"""
        try:
            # Create configuration object from CLI arguments
            config = GenerationConfig(
                genre=genre,
                chapters=chapters,
                output_file=output_file,
                model=model,
                title=title,
                save_state=save_state,
                continue_from=continue_from,
                resume=resume,
                plot_template=plot_template,
                verbose=verbose,
                chunked=chunked,
                timeout=timeout,
                use_yaml_crew=use_yaml_crew,
                ollama_threads=ollama_threads,
                ollama_gpu_layers=ollama_gpu_layers,
                ollama_ctx_size=ollama_ctx_size,
                ollama_batch_size=ollama_batch_size,
                use_flow=use_flow,
                plot_flow=plot_flow,
                output_format=output_format,
                interactive_display=interactive_display
            )
            
            # Validate configuration
            cls._validate_config(config)
            
            # Initialize components
            story_persistence = StoryPersistence(os.getenv("OUTPUT_DIR", "./output"))
            
            # Handle project resume or continuation
            story_state, story_state_manager = cls._initialize_state(
                config, story_persistence
            )
            
            # Check for plugin genre
            plugin_genre = cls._get_plugin_genre(config.genre, config.verbose)
            
            # Show fancy title banner if interactive mode
            if config.interactive_display:
                cls._display_title_banner(config, story_state)
                
            # Create and run the story generator
            generator = StoryGenerator(
                config=config,
                story_state=story_state,
                story_state_manager=story_state_manager,
                story_persistence=story_persistence,
                plugin_genre=plugin_genre
            )
            
            # Register progress callbacks if in interactive mode
            if config.interactive_display:
                generator.register_progress_callback(cls._progress_callback)
                generator.register_chunk_callback(cls._chunk_callback)
                
            # Display generation plan
            cls._display_generation_plan(config, story_state)
            
            # Generate the story
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold]{task.fields[status]}"),
                TimeElapsedColumn(),
                console=console,
                transient=True if config.interactive_display else False,
                expand=True
            ) as progress:
                # Create main task for tracking overall progress
                main_task_id = progress.add_task(
                    f"[bold]Generating {config.genre} story...", 
                    total=100,
                    status="Planning story"
                )
                
                # Start generation with progress update callback
                def update_progress(stage, percent, status):
                    progress.update(
                        main_task_id, 
                        completed=percent,
                        status=status
                    )
                
                # Configure the callbacks
                generator.register_progress_callback(update_progress)
                
                # Generate the story
                result = generator.generate()
                
                # Complete the progress bar
                progress.update(main_task_id, completed=100, status="Complete!")
            
            # Handle the generation result
            cls._handle_generation_result(
                result, config, story_state, story_state_manager, story_persistence
            )
            
            # Print continuation information
            if config.save_state:
                cls._print_continuation_info(story_state, story_persistence)
                
        except KeyboardInterrupt:
            cls.info("Story generation interrupted.")
            sys.exit(1)
        except Exception as e:
            cls.error(f"Error generating story: {str(e)}")
            if config.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    @classmethod
    def _validate_config(cls, config):
        """Validate the generation configuration"""
        if config.continue_from and config.resume:
            cls.error("Cannot use both --continue and --resume options at the same time.")
            sys.exit(1)
            
        if config.plot_template and not plot_registry.has_template(config.plot_template):
            cls.error(f"Plot template '{config.plot_template}' not found. Use 'list-plots' to see available templates.")
            sys.exit(1)
    
    @classmethod
    def _initialize_state(cls, config, story_persistence):
        """Initialize story state and state manager"""
        story_state = None
        story_state_manager = None
        
        # Handle project resume if specified
        if config.resume:
            try:
                story_state = story_persistence.load_story(config.resume)
                story_state_manager = story_state.to_story_state_manager()
                cls.success(f"Resuming project: {story_state.metadata.title} ({story_state.metadata.genre})")
                cls.info(f"Project has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                
                # Update genre from the story state
                config.genre = story_state.metadata.genre
                
                # If plot template is specified but different from saved, warn the user
                if (config.plot_template and hasattr(story_state.metadata, 'plot_template') and 
                    story_state.metadata.plot_template != config.plot_template):
                    console.print(f"[bold yellow]Warning: Resuming with plot template '{story_state.metadata.plot_template}' from saved project, ignoring specified '{config.plot_template}'[/bold yellow]")
                    config.plot_template = story_state.metadata.plot_template
            except (FileNotFoundError, ValueError) as e:
                cls.error(f"Error loading project: {e}")
                sys.exit(1)
        # Handle continuation if specified
        elif config.continue_from:
            try:
                story_state = story_persistence.load_story(config.continue_from)
                story_state_manager = story_state.to_story_state_manager()
                cls.success(f"Continuing story: {story_state.metadata.title} ({story_state.metadata.genre})")
                cls.info(f"Already has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                
                # Update genre from the story state
                config.genre = story_state.metadata.genre
                
                # If plot template is specified but different from saved, warn the user
                if (config.plot_template and hasattr(story_state.metadata, 'plot_template') and 
                    story_state.metadata.plot_template != config.plot_template):
                    console.print(f"[bold yellow]Warning: Continuing with plot template '{story_state.metadata.plot_template}' from saved story, ignoring specified '{config.plot_template}'[/bold yellow]")
                    config.plot_template = story_state.metadata.plot_template
            except (FileNotFoundError, ValueError) as e:
                cls.error(f"Error loading story: {e}")
                sys.exit(1)
        else:
            # Create new story state
            story_state = StoryState(config.genre, config.title)
            # Create a corresponding StoryStateManager
            story_state_manager = StoryStateManager()
            if config.title:
                story_state_manager.set_project_directory(config.title)
            
            # Add plot template to metadata if specified
            if config.plot_template:
                story_state.metadata.plot_template = config.plot_template
        
        return story_state, story_state_manager
    
    @classmethod
    def _get_plugin_genre(cls, genre, verbose):
        """Check if the genre is from a plugin and return the plugin class if it is"""
        # Only check for plugin genres if it's not one of the built-in genres
        if genre in ["noir", "sci-fi", "adventure"]:
            return None
            
        # Check if it's a plugin genre
        plugin_manager = PluginManager()
        plugin_manager.discover_plugins()
        
        # Try to find a genre plugin with the given ID
        for plugin_class in plugin_manager.get_plugins(GenrePlugin):
            if plugin_class.plugin_id == genre:
                if verbose:
                    cls.info(f"Using genre plugin: {plugin_class.plugin_name}")
                return plugin_class
        
        cls.error(f"Unknown genre: {genre}. Use 'list-genres' to see available genres.")
        sys.exit(1)
    
    @classmethod
    def _display_generation_plan(cls, config, story_state):
        """Display generation plan to user"""
        console.print("\n[bold]Story Generation Plan:[/bold]")
        console.print(f"Generation method: [cyan]{'Chunked with checkpoints' if config.chunked else 'Standard'}")
        console.print(f"Genre: [cyan]{config.genre}[/cyan]")
        if config.title:
            console.print(f"Title: [cyan]{config.title}[/cyan]")
        if config.plot_template and hasattr(story_state.metadata, 'plot_template'):
            console.print(f"Plot template: [cyan]{story_state.metadata.plot_template}[/cyan]")
        console.print(f"Model: [cyan]{config.model}[/cyan]")
        console.print(f"Chapters to generate: [cyan]{config.chapters}[/cyan]")
    
    @classmethod
    def _handle_generation_result(cls, result, config, story_state, story_state_manager, story_persistence):
        """Handle the generation result"""
        if not result.success:
            cls.error(f"Failed to generate story: {result.error}")
            return
            
        # Output the story
        cls.success(f"Generated a {config.genre} pulp fiction story with {config.chapters} new chapter(s)!")
        cls.info(f"Story now has {story_state.metadata.chapter_count} total chapters and {story_state.metadata.word_count} words\n")
        
        # Save to file if requested
        if config.output_file:
            try:
                # Create output directory if it doesn't exist
                output_dir = os.path.dirname(config.output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(config.output_file, "w") as f:
                    f.write(story_state.get_full_story())
                cls.success(f"Story saved to {config.output_file}")
            except Exception as e:
                cls.error(f"Failed to save story to {config.output_file}: {e}")
        else:
            # Always save to the project directory in markdown format
            try:
                project_dir = story_persistence.get_project_dir(story_state)
                title_slug = story_state.get_project_dirname()
                markdown_file = project_dir / f"{title_slug}.md"
                
                with open(markdown_file, "w") as f:
                    f.write(story_state.get_full_story())
                cls.success(f"Story saved to {markdown_file}")
                
                # Print story to console as Markdown
                console.print(Markdown(f"# {story_state.metadata.title}\n\n{result.story_text}"))
            except Exception as e:
                cls.error(f"Failed to save story to project directory: {e}")
                # Print story to console as Markdown
                console.print(Markdown(f"# {story_state.metadata.title}\n\n{result.story_text}"))
    
    @classmethod
    def _print_continuation_info(cls, story_state, story_persistence):
        """Print information about how to continue the story"""
        console.print("\n[bold]To continue this story in the future, use:[/bold]")
        
        # Get the project name from the story title
        project_name = story_state.get_project_dirname()
        
        # Show both project resume option and specific file continue option
        console.print(f"[cyan]pulp-fiction generate --resume {project_name} --chapters 1[/cyan]")
        
        # Also show the specific file option for backward compatibility
        saved_file_path = story_persistence.save_story(story_state)
        saved_file_name = os.path.basename(saved_file_path)
        console.print(f"[dim]Or using the specific story file:[/dim]")
        console.print(f"[cyan]pulp-fiction generate --continue {saved_file_name} --chapters 1[/cyan]")
    
    @classmethod
    def _display_title_banner(cls, config, story_state):
        """Display a fancy title banner for the story generation"""
        if story_state and story_state.metadata.title:
            title = story_state.metadata.title
        else:
            title = config.title or f"New {config.genre.capitalize()} Story"
            
        genre = config.genre.upper()
        
        # Create a fancy banner
        banner = Panel(
            Align.center(
                f"[bold red]{title}[/bold red]\n\n"
                f"[yellow]Genre:[/yellow] [bold yellow]{genre}[/bold yellow]\n"
                f"[blue]Chapters:[/blue] [bold blue]{config.chapters}[/bold blue]\n"
                f"[green]Model:[/green] [bold green]{config.model}[/bold green]"
            ),
            border_style="red",
            title="[bold]PULP FICTION GENERATOR[/bold]",
            subtitle="[italic]Creating your story...[/italic]"
        )
        
        console.print("\n")
        console.print(Align.center(banner))
        console.print("\n")
    
    @classmethod
    def _progress_callback(cls, stage, percent, status):
        """Progress callback for interactive mode"""
        # The actual progress tracking is handled by the Progress context manager
        pass
    
    @classmethod
    def _chunk_callback(cls, chunk_type, chunk_content):
        """Callback for displaying generated content chunks in real-time"""
        if chunk_type == "chapter_title":
            console.print("\n")
            console.print(Panel(
                Align.center(f"[bold yellow]{chunk_content}[/bold yellow]"),
                border_style="yellow",
                expand=False
            ))
            console.print("\n")
        elif chunk_type == "paragraph":
            # Display new paragraphs as they're generated
            console.print(Markdown(chunk_content))
            console.print("\n")
        elif chunk_type == "planning":
            # Display planning notes in a subtle panel
            console.print(Panel(
                Markdown(chunk_content),
                border_style="dim blue",
                title="[bold blue]Planning[/bold blue]",
                expand=False
            )) 