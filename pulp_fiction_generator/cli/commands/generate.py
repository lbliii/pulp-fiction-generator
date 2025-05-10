"""
Generate command implementation.
"""

import os
import sys
from typing import Optional, List
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..base import GenerateCommand
from ...agents.agent_factory import AgentFactory
from ...crews.crew_coordinator import CrewCoordinator
from ...crews.config.crew_coordinator_config import CrewCoordinatorConfig
from ...models.ollama_adapter import OllamaAdapter
from ...utils.story_persistence import StoryPersistence, StoryState
from ...plots import plot_registry
from ...plugins.manager import PluginManager
from ...plugins.base import GenrePlugin

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
        plot_template: Optional[str] = typer.Option(
            None, "--plot", "-p", help="Plot template to use for the story"
        ),
        verbose: bool = typer.Option(
            False, "--verbose", "-v", help="Enable verbose output"
        ),
        chunked: bool = typer.Option(
            False, "--chunked/--no-chunked", help="Use chunked generation process with checkpoints"
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
    ):
        """Generate a pulp fiction story in the specified genre"""
        # Check if the genre is from a plugin
        plugin_genre = None
        if genre not in ["noir", "sci-fi", "adventure"]:  # Standard built-in genres
            # Check if it's a plugin genre
            plugin_manager = PluginManager()
            plugin_manager.discover_plugins()
            
            # Try to find a genre plugin with the given ID
            genre_plugins = plugin_manager.get_plugins(GenrePlugin)
            for plugin_class in genre_plugins:
                if plugin_class.plugin_id == genre:
                    plugin_genre = plugin_class
                    if verbose:
                        cls.info(f"Using genre plugin: {plugin_class.plugin_name}")
                    break
            
            if not plugin_genre:
                cls.error(f"Unknown genre: {genre}. Use 'list-genres' to see available genres.")
                return
        
        # Initialize story state
        story_state = None
        
        # Initialize story persistence
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        story_persistence = StoryPersistence(output_dir)
        
        # Handle continuation if specified
        if continue_from:
            try:
                story_state = story_persistence.load_story(continue_from)
                cls.success(f"Continuing story: {story_state.metadata.title} ({story_state.metadata.genre})")
                cls.info(f"Already has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                
                # Update genre from the story state
                genre = story_state.metadata.genre
                
                # If plot template is specified but different from saved, warn the user
                if (plot_template and hasattr(story_state.metadata, 'plot_template') and 
                    story_state.metadata.plot_template != plot_template):
                    console.print(f"[bold yellow]Warning: Continuing with plot template '{story_state.metadata.plot_template}' from saved story, ignoring specified '{plot_template}'[/bold yellow]")
                    plot_template = story_state.metadata.plot_template
            except (FileNotFoundError, ValueError) as e:
                cls.error(f"Error loading story: {e}")
                return
        else:
            # Create new story state
            story_state = StoryState(genre, title)
            
            # Add plot template to metadata if specified
            if plot_template:
                # Verify plot template exists
                if not plot_registry.has_template(plot_template):
                    cls.error(f"Plot template '{plot_template}' not found. Use 'list-plots' to see available templates.")
                    return
                story_state.metadata.plot_template = plot_template
        
        # Initialize progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=True,
        ) as progress:
            # Show initializing task
            task = progress.add_task("[bold blue]Initializing model service...", total=None)
            
            # Set up model service
            try:
                # Prepare Ollama parameters if provided
                ollama_params = {}
                if ollama_threads is not None:
                    ollama_params["num_thread"] = ollama_threads
                if ollama_gpu_layers is not None:
                    ollama_params["num_gpu"] = ollama_gpu_layers
                if ollama_ctx_size is not None:
                    ollama_params["num_ctx"] = ollama_ctx_size
                if ollama_batch_size is not None:
                    ollama_params["num_batch"] = ollama_batch_size
                    
                model_service = OllamaAdapter(model_name=model)
                
                # Display configured parameters if any
                if verbose:
                    console.print("[dim]Using Ollama parameters:[/dim]")
                    # Get defaults from adapter if not overridden
                    params = model_service.get_default_ollama_params()
                    # Override with any specified parameters
                    params.update(ollama_params)
                    for param, value in params.items():
                        source = "from command line" if param in ollama_params else "from .env"
                        console.print(f"[dim] - {param}: {value} ({source})[/dim]")
                
                # Test connection to Ollama
                model_info = model_service.get_model_info()
                progress.update(task, description=f"[bold green]Connected to Ollama using {model}!")
                progress.remove_task(task)
            except Exception as e:
                progress.update(task, description=f"[bold red]Failed to connect to Ollama: {e}")
                progress.remove_task(task)
                cls.error(f"{e}")
                console.print("[yellow]Make sure Ollama is running with 'ollama serve' and the model is pulled with 'ollama pull {model}'[/yellow]")
                sys.exit(1)
            
            # Set up agent factory and crew coordinator
            task = progress.add_task("[bold blue]Initializing agent system...", total=None)
            agent_factory = AgentFactory(model_service, verbose=verbose)
            
            # Create a config object for crew coordinator
            coordinator_config = CrewCoordinatorConfig(verbose=verbose)
            crew_coordinator = CrewCoordinator(agent_factory, model_service, config=coordinator_config)
            
            progress.update(task, description="[bold green]Agent system initialized!")
            progress.remove_task(task)
            
            # Load plot template if specified
            plot_prompt_enhancement = None
            if hasattr(story_state.metadata, 'plot_template') and story_state.metadata.plot_template:
                try:
                    plot_template_obj = plot_registry.get_template(story_state.metadata.plot_template)
                    if verbose:
                        console.print(f"[dim]Using plot template: {plot_template_obj.name} - {plot_template_obj.description}[/dim]")
                except ValueError as e:
                    console.print(f"[bold yellow]Warning: {e}. Proceeding without plot template.[/bold yellow]")
            
            # Handle plugin genre prompt enhancements if applicable
            if plugin_genre:
                try:
                    # Instantiate the plugin
                    genre_plugin_instance = plugin_genre()
                    
                    # Get prompt enhancers for each agent type
                    prompt_enhancers = genre_plugin_instance.get_prompt_enhancers()
                    
                    # Apply prompt enhancers to crew coordinator or agent factory as needed
                    if hasattr(crew_coordinator, 'set_prompt_enhancers'):
                        crew_coordinator.set_prompt_enhancers(prompt_enhancers)
                    
                    if verbose:
                        console.print(f"[dim]Applied prompt enhancers from {plugin_genre.plugin_name} plugin[/dim]")
                except Exception as e:
                    console.print(f"[bold yellow]Warning: Error applying plugin enhancements: {e}[/bold yellow]")
            
            # Display generation plan to user
            console.print("\n[bold]Story Generation Plan:[/bold]")
            console.print(f"Generation method: [cyan]{'Chunked with checkpoints' if chunked else 'Standard'}")
            console.print(f"Genre: [cyan]{genre}[/cyan]")
            if title:
                console.print(f"Title: [cyan]{title}[/cyan]")
            if plot_template and hasattr(story_state.metadata, 'plot_template'):
                console.print(f"Plot template: [cyan]{story_state.metadata.plot_template}[/cyan]")
            console.print(f"Model: [cyan]{model}[/cyan]")
            console.print(f"Chapters to generate: [cyan]{chapters}[/cyan]")
            
            # Generate story chapters
            story_text = ""
            starting_chapter = story_state.metadata.chapter_count + 1
            
            for chapter_num in range(starting_chapter, starting_chapter + chapters):
                task = progress.add_task(f"[bold blue]Generating chapter {chapter_num}...", total=None)
                
                try:
                    # Prepare custom inputs including plot template if available
                    custom_inputs = {"chapter_number": chapter_num, "title": title}
                    
                    # Apply Ollama parameters to custom inputs if specified
                    if ollama_params:
                        custom_inputs["ollama_params"] = ollama_params
                    
                    # Add plot template guidance if available
                    if hasattr(story_state.metadata, 'plot_template') and story_state.metadata.plot_template:
                        try:
                            template = plot_registry.get_template(story_state.metadata.plot_template)
                            # Add plot structure to the inputs
                            custom_inputs["plot_structure"] = template.get_plot_structure().to_dict()
                            # For continuation, figure out which plot point we're at based on chapter number
                            if chapter_num > 1:
                                total_plot_points = len(template.get_plot_structure().plot_points)
                                # Simple mapping of chapters to plot points
                                current_plot_point_index = min(chapter_num - 1, total_plot_points - 1)
                                custom_inputs["current_plot_point"] = template.get_plot_structure().plot_points[current_plot_point_index].to_dict()
                        except Exception as e:
                            if verbose:
                                console.print(f"[dim]Error loading plot template: {e}[/dim]")
                    
                    # For first chapter of a new story, create a new story
                    if chapter_num == 1 and not continue_from:
                        # Use chunked generation if specified, otherwise use the regular crew
                        if chunked:
                            # Define a callback for chunked progress updates
                            def chunk_callback(stage, result):
                                # Update the progress spinner with the current stage
                                progress.update(task, description=f"[bold blue]Generating chapter {chapter_num} - {stage}...")
                                
                                # Save intermediate artifacts if needed
                                if verbose:
                                    console.print(f"[dim]Completed stage: {stage}[/dim]")
                            
                            # Generate using the chunked approach
                            results = crew_coordinator.generate_story_chunked(
                                genre, 
                                custom_inputs=custom_inputs,
                                chunk_callback=chunk_callback
                            )
                            
                            # Get the final story from the results
                            chapter = results["final_story"]
                            
                            # Extract artifacts for future reference
                            story_state.metadata.artifacts = {
                                "research": results["research"],
                                "world": results["worldbuilding"],
                                "characters": results["characters"],
                                "plot": results["plot"]
                            }
                        else:
                            # Use the standard approach
                            chapter = crew_coordinator.generate_story(
                                genre, 
                                custom_inputs=custom_inputs
                            )
                        
                        # Extract title if not provided
                        if not title and ":" in chapter[:100]:
                            title_line = chapter.split("\n")[0]
                            story_state.metadata.title = title_line.strip("# ")
                            
                    # For subsequent chapters, continue the story
                    else:
                        # Prepare context from previous chapters
                        previous_content = story_state.get_full_story() if story_state else ""
                        
                        # Use chunked or standard approach for continuation
                        if chunked:
                            # Define a callback for chunked progress updates
                            def chunk_callback(stage, result):
                                progress.update(task, description=f"[bold blue]Continuing chapter {chapter_num} - {stage}...")
                                if verbose:
                                    console.print(f"[dim]Completed continuation stage: {stage}[/dim]")
                            
                            # Create inputs that include the artifacts from previous generation
                            combined_inputs = custom_inputs.copy()
                            if hasattr(story_state.metadata, "artifacts"):
                                combined_inputs.update(story_state.metadata.artifacts)
                            
                            # Generate continuation using chunked approach
                            results = crew_coordinator.generate_story_chunked(
                                genre, 
                                custom_inputs=combined_inputs,
                                chunk_callback=chunk_callback
                            )
                            
                            chapter = results["final_story"]
                        else:
                            # Use standard approach for continuation
                            continuation_crew = crew_coordinator.create_continuation_crew(
                                genre, 
                                previous_content,
                                config=custom_inputs
                            )
                            chapter = crew_coordinator.kickoff_crew(
                                continuation_crew, 
                                inputs=custom_inputs
                            )
                    
                    # Check for empty or error chapter content
                    if not chapter or chapter.startswith("ERROR:"):
                        progress.update(task, description=f"[bold red]Chapter {chapter_num} generation failed!")
                        cls.error(f"Error generating chapter {chapter_num}: {chapter}")
                        break
                    
                    # Add chapter to story state
                    try:
                        # Simplified for extraction - in actual implementation extract characters, settings, plot points from agent outputs
                        characters = []
                        settings = []
                        plot_points = [{"description": f"Chapter {chapter_num} events"}]
                        
                        story_state.add_chapter(chapter, characters, settings, plot_points)
                    except Exception as e:
                        progress.update(task, description=f"[bold red]Failed to add chapter {chapter_num} to story state!")
                        cls.error(f"{e}")
                        break
                    
                    # Append to displayed story
                    story_text += f"\n\n## Chapter {chapter_num}\n\n{chapter}"
                    
                    progress.update(task, description=f"[bold green]Chapter {chapter_num} generated!")
                    
                    # Save story state after each chapter if requested
                    if save_state:
                        try:
                            story_path = story_persistence.save_story(story_state)
                            if verbose:
                                console.print(f"[dim]Story state saved to {story_path}[/dim]")
                        except Exception as e:
                            if verbose:
                                console.print(f"[dim]Failed to save story state: {e}[/dim]")
                    
                except Exception as e:
                    progress.update(task, description=f"[bold red]Failed to generate chapter {chapter_num}: {e}")
                    if verbose:
                        cls.error(f"{e}")
                        # Print traceback for debugging
                        import traceback
                        console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    break
                finally:
                    progress.remove_task(task)
        
        # Output the story
        cls.success(f"Generated a {genre} pulp fiction story with {chapters} new chapter(s)!")
        cls.info(f"Story now has {story_state.metadata.chapter_count} total chapters and {story_state.metadata.word_count} words\n")
        
        if output_file:
            try:
                # Create output directory if it doesn't exist
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(output_file, "w") as f:
                    f.write(story_state.get_full_story())
                cls.success(f"Story saved to {output_file}")
            except Exception as e:
                cls.error(f"Failed to save story to {output_file}: {e}")
        else:
            # Print story to console as Markdown
            console.print(Markdown(f"# {story_state.metadata.title}\n\n{story_text}"))
            
        # Print continuation information
        if save_state:
            console.print("\n[bold]To continue this story in the future, use:[/bold]")
            console.print(f"[cyan]pulp-fiction generate --continue {os.path.basename(story_persistence.save_story(story_state))} --chapters 1[/cyan]") 