"""
Generate command implementation.
"""

import os
import sys
from typing import Optional, List, Tuple, Any
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

from ..base import GenerateCommand
from ...agents.agent_factory import AgentFactory
from ...crews.crew_coordinator import CrewCoordinator
from ...crews.config.crew_coordinator_config import CrewCoordinatorConfig
from ...crews.crew_executor import CrewExecutor
from ...models.ollama_adapter import OllamaAdapter
from ...utils.story_persistence import StoryPersistence, StoryState
from ...story.state import StoryStateManager
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
            "plain", "--format", case_sensitive=False, help="Output format (plain, markdown, html, pdf)"
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
        
        # Initialize story state and state manager
        story_state = None
        story_state_manager = None
        
        # Initialize story persistence
        output_dir = os.getenv("OUTPUT_DIR", "./output")
        story_persistence = StoryPersistence(output_dir)
        
        # Both continue and resume options can't be used together
        if continue_from and resume:
            cls.error("Cannot use both --continue and --resume options at the same time.")
            return
        
        # Handle project resume if specified
        if resume:
            try:
                story_state = story_persistence.load_story(resume)
                # Create a story state manager from the loaded state
                story_state_manager = story_state.to_story_state_manager()
                cls.success(f"Resuming project: {story_state.metadata.title} ({story_state.metadata.genre})")
                cls.info(f"Project has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                
                # Update genre from the story state
                genre = story_state.metadata.genre
                
                # If plot template is specified but different from saved, warn the user
                if (plot_template and hasattr(story_state.metadata, 'plot_template') and 
                    story_state.metadata.plot_template != plot_template):
                    console.print(f"[bold yellow]Warning: Resuming with plot template '{story_state.metadata.plot_template}' from saved project, ignoring specified '{plot_template}'[/bold yellow]")
                    plot_template = story_state.metadata.plot_template
            except (FileNotFoundError, ValueError) as e:
                cls.error(f"Error loading project: {e}")
                return
        # Handle continuation if specified
        elif continue_from:
            try:
                story_state = story_persistence.load_story(continue_from)
                # Create a story state manager from the loaded state
                story_state_manager = story_state.to_story_state_manager()
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
            # Create a corresponding StoryStateManager
            story_state_manager = StoryStateManager()
            if title:
                story_state_manager.set_project_directory(title)
            
            # Add plot template to metadata if specified
            if plot_template:
                # Verify plot template exists
                if not plot_registry.has_template(plot_template):
                    cls.error(f"Plot template '{plot_template}' not found. Use 'list-plots' to see available templates.")
                    return
                story_state.metadata.plot_template = plot_template
        
        # Initialize Ollama model
        ollama_adapter = OllamaAdapter.from_env(
            model=model,
            num_ctx=ollama_ctx_size,
            num_gpu=ollama_gpu_layers,
            num_thread=ollama_threads,
            batch_size=ollama_batch_size,
        )
        
        # Initialize CrewExecutor for events
        crew_executor = CrewExecutor(debug_mode=verbose)
        
        # Create a progress display with Rich
        progress_display = None
        execution_task = None
        token_count = 0
        
        # Set up progress callback for CrewAI events
        def progress_callback(completed_tasks, total_tasks, progress, remaining):
            nonlocal progress_display, execution_task
            
            if progress_display and execution_task:
                # Update progress bar
                if progress is not None:
                    progress_display.update(execution_task, completed=int(progress))
                    
                    # Update description with estimated time
                    if remaining:
                        minutes = int(remaining / 60)
                        seconds = int(remaining % 60)
                        time_str = f"{minutes}m {seconds}s"
                        progress_display.update(
                            execution_task, 
                            description=f"Generating story... {completed_tasks}/{total_tasks} tasks ({progress:.1f}%, ~{time_str} remaining)"
                        )
                    else:
                        progress_display.update(
                            execution_task, 
                            description=f"Generating story... {completed_tasks}/{total_tasks} tasks ({progress:.1f}%)"
                        )
        
        # Set up token tracking for CrewAI events
        def token_callback(source, event):
            nonlocal token_count
            if hasattr(event, 'tokens_used'):
                token_count += event.tokens_used
                if progress_display and execution_task:
                    progress_display.update(
                        execution_task,
                        description=f"Generating story... (tokens: {token_count:,})"
                    )
        
        # Register event listeners
        progress_listener = crew_executor.create_custom_event_listener(callback=progress_callback)
        token_listener = crew_executor.add_token_tracking_listener()
        
        # Initialize crew coordinator
        crew_coordinator_config = CrewCoordinatorConfig(
            debug_mode=verbose,
            verbose=verbose,
            process="sequential",
        )
        
        agent_factory = AgentFactory(ollama_adapter)
        crew_coordinator = CrewCoordinator(
            agent_factory=agent_factory,
            model_service=ollama_adapter,
            config=crew_coordinator_config
        )
        
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
        
        try:
            # Start a progress display
            with Progress() as progress_display:
                # Add a task for the current chapter
                execution_task = progress_display.add_task(
                    f"Generating story...", 
                    total=100
                )
                
                # Function to generate a single chapter
                if chunked:
                    # Chunked generation process
                    cls.info(f"Generating {genre} story using chunked method...")
                    
                    # Define a callback for chunked progress updates
                    def chunk_callback(stage, result):
                        # Update the progress display with the current stage
                        progress_display.update(
                            execution_task, 
                            description=f"Generating {stage}..."
                        )
                        if verbose and result:
                            cls.info(f"Completed {stage}")
                    
                    # Generate using chunked approach
                    try:
                        results = crew_coordinator.generate_story_chunked(
                            genre,
                            custom_inputs=custom_inputs,
                            chunk_callback=chunk_callback,
                            story_state=story_state_manager,
                            timeout_seconds=timeout
                        )
                        
                        # Process results
                        if isinstance(results, dict):
                            result = results.get("final_story", "")
                        elif hasattr(results, 'final_story'):
                            result = results.final_story
                        else:
                            result = str(results)
                            
                        # Update progress to complete
                        progress_display.update(execution_task, completed=100)
                        
                        # Finalize the story
                        chapter_title = title or f"Chapter {story_state_manager.get_chapter_count() + 1}"
                        final_content, word_count, char_count = finalize_story(
                            genre, 
                            result, 
                            chapter_title,
                            story_state_manager.get_chapter_count() + 1,
                            story_state_manager,
                            save_state
                        )
                        
                        # Output the story
                        if output_format.lower() == "markdown":
                            console.print(Markdown(final_content))
                        else:
                            console.print(final_content)
                            
                        # Save to file if requested
                        if output_file:
                            file_path = os.path.expanduser(output_file)
                            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(final_content)
                            cls.success(f"Story saved to: {file_path}")
                    except Exception as e:
                        cls.error(f"Error during chunked generation: {str(e)}")
                        if verbose:
                            import traceback
                            traceback.print_exc()
                else:
                    # Regular generation (non-chunked)
                    # Title suffix for display
                    title_suffix = f" ({title})" if title else ""
                    cls.info(f"Generating {genre} story{title_suffix}...")
                    
                    try:
                        # Add a fake task for token counting in regular generation
                        token_task = progress_display.add_task(
                            f"LLM token usage: 0", 
                            total=None,
                            visible=verbose
                        )
                        
                        # Prepare any custom inputs from plot template
                        custom_inputs = {}
                        if plot_template:
                            plot_data = plot_registry.get_template(plot_template)
                            if plot_data:
                                custom_inputs = plot_data.get("inputs", {})
                                if verbose:
                                    cls.info(f"Using plot template: {plot_template}")
                        
                        # Add state if we're continuing a story
                        if story_state_manager and (resume or continue_from):
                            custom_inputs["previous_content"] = "\n\n".join(story_state_manager.get_chapters())
                            
                        start_time = time.time()
                        
                        # Generate the story
                        if use_flow:
                            result = "Flow-based generation is not implemented yet"
                        elif use_yaml_crew:
                            result = crew_coordinator.generate_story(
                                genre, 
                                custom_inputs=custom_inputs,
                                debug_mode=verbose,
                                timeout_seconds=timeout,
                                use_yaml_crew=True
                            )
                        else:
                            result = crew_coordinator.generate_story(
                                genre, 
                                custom_inputs=custom_inputs,
                                debug_mode=verbose,
                                timeout_seconds=timeout,
                                use_yaml_crew=False
                            )
                            
                        generation_time = time.time() - start_time
                        
                        # Update progress to complete
                        progress_display.update(execution_task, completed=100)
                        
                        # Output the generated story
                        if result:
                            # Finalize the story and store the content
                            chapter_title = title or f"Chapter {story_state_manager.get_chapter_count() + 1}"
                            final_content, word_count, char_count = finalize_story(
                                genre, 
                                result, 
                                chapter_title,
                                story_state_manager.get_chapter_count() + 1,
                                story_state_manager,
                                save_state
                            )
                            
                            # Calculate stats
                            tokens_per_second = token_count / generation_time if token_count > 0 and generation_time > 0 else 0
                            words_per_second = word_count / generation_time
                            
                            # Print stats
                            cls.success(f"Generated {word_count} words ({char_count} characters)")
                            cls.info(f"Generation time: {generation_time:.2f} seconds")
                            cls.info(f"Speed: {words_per_second:.2f} words/sec")
                            if token_count > 0:
                                cls.info(f"Token usage: {token_count:,} tokens ({tokens_per_second:.2f} tokens/sec)")
                            
                            # Output format handling
                            if output_format.lower() == "markdown":
                                console.print(Markdown(final_content))
                            else:
                                console.print(final_content)
                                
                            # Save to file if requested
                            if output_file:
                                file_path = os.path.expanduser(output_file)
                                
                                # Ensure the directory exists
                                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
                                
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(final_content)
                                    
                                cls.success(f"Story saved to: {file_path}")
                                
                            # Save state if requested
                            if save_state:
                                # Update story state
                                story_state.add_chapter(
                                    chapter_num=story_state_manager.get_chapter_count(),
                                    content=result,
                                    title=chapter_title
                                )
                                
                                # Save the story state
                                story_id = story_persistence.save_story(story_state)
                                cls.success(f"Story state saved with ID: {story_id}")
                                
                                # Also save in the story state manager's project directory
                                story_state_manager.save_chapter(result, chapter_title)
                        else:
                            cls.error("Failed to generate story.")
                    except Exception as e:
                        cls.error(f"Error generating story: {str(e)}")
                        if verbose:
                            import traceback
                            traceback.print_exc()
        except KeyboardInterrupt:
            cls.info("Story generation interrupted.")
            sys.exit(1)
        
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
            # Always save to the project directory in markdown format
            try:
                project_dir = story_persistence.get_project_dir(story_state)
                title_slug = story_state.get_project_dirname()
                markdown_file = project_dir / f"{title_slug}.md"
                
                with open(markdown_file, "w") as f:
                    f.write(story_state.get_full_story())
                cls.success(f"Story saved to {markdown_file}")
                
                # Print story to console as Markdown
                console.print(Markdown(f"# {story_state.metadata.title}\n\n{story_text}"))
            except Exception as e:
                cls.error(f"Failed to save story to project directory: {e}")
                # Print story to console as Markdown
                console.print(Markdown(f"# {story_state.metadata.title}\n\n{story_text}"))
            
        # Print continuation information
        if save_state:
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

def finalize_story(
    genre: str,
    chapter_content: str,
    title: str,
    chapter_num: int,
    state_manager: Any,
    save_state: bool = True
) -> Tuple[str, int, int]:
    """
    Finalize and save a generated story.
    
    Args:
        genre: The genre of the story
        chapter_content: The content of the chapter
        title: The title of the story
        chapter_num: The chapter number
        state_manager: The state manager to use
        save_state: Whether to save the state
        
    Returns:
        Tuple of (output_file, chapter_count, word_count)
    """
    from rich.console import Console
    
    # Make sure we have some content, even if just a fallback message
    if not chapter_content or not chapter_content.strip():
        chapter_content = f"Your {genre} story titled '{title}' could not be generated due to technical issues. The CrewFactory is experiencing problems with the 'custom_inputs' parameter. Please check the code and fix the issue."
        
    # Save the chapter to state manager
    if state_manager:
        # Add chapter to state
        state_manager.add_chapter(chapter_num, chapter_content)
        
        # Save state if requested
        if save_state:
            from time import strftime
            timestamp = strftime("%Y%m%d%H%M%S")
            state_file = f"{title.lower().replace(' ', '_')}_{timestamp}.json"
            state_manager.save_state(state_file)
    
    # Calculate chapter count and word count
    chapter_count = 1  # Assuming one chapter
    word_count = len(chapter_content.split())  # Simple word count
    
    # Construct output file path
    output_file = f"{title.lower().replace(' ', '_')}_{chapter_num}.txt"
    
    return output_file, chapter_count, word_count 