"""
Main entry point for the Pulp Fiction Generator.
"""

import os
import sys
import subprocess
import tempfile
from typing import Optional, List
from datetime import datetime

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box
import difflib
import json
import functools
import platform
import importlib
import requests
from packaging import version

from .agents.agent_factory import AgentFactory
from .crews.crew_coordinator import CrewCoordinator
from .models.model_service import ModelService
from .models.ollama_adapter import OllamaAdapter
from .utils.story_persistence import StoryPersistence, StoryState
from .utils.consistency import ConsistencyChecker
from .plots import plot_registry
from crewai import Task, Agent, Crew
from .utils.error_handling import ErrorHandler, setup_error_handling, logger, DiagnosticInfo

# Create typer app
app = typer.Typer(help="Pulp Fiction Generator - Create serialized pulp fiction using AI agents")
console = Console()

# Initialize error handling
setup_error_handling()

# Helper function for improved error reporting in command callbacks
def with_error_handling(func):
    """Decorator to add consistent error handling to commands"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = ErrorHandler.handle_exception(
                e, 
                context={"command": func.__name__, "args": args, "kwargs": kwargs},
                show_traceback=kwargs.get("verbose", False)
            )
            
            # User-friendly error display
            console.print(f"\n[bold red]Error:[/bold red] {error_info['error_message']}")
            
            # Show detailed error location in verbose mode
            if kwargs.get("verbose", False):
                caller = error_info.get("caller", {})
                if caller:
                    console.print(f"[dim]Location: {caller.get('file')}:{caller.get('line')} in {caller.get('function')}[/dim]")
            
            # Show potential solutions for common errors
            if isinstance(e, NameError) and "Task" in str(e):
                console.print("[yellow]Hint: This might be due to a missing import. Make sure 'from crewai import Task' is properly imported.[/yellow]")
            elif "Failed to connect to Ollama" in str(e) or "Connection refused" in str(e):
                console.print("[yellow]Hint: Make sure Ollama is running with 'ollama serve' and the model is available.[/yellow]")
            
            # Always tell the user where to find more details
            if "log_file" in error_info:
                console.print(f"[dim]Detailed error information saved to {error_info['log_file']}[/dim]")
            
            sys.exit(1)
    
    return wrapper

@app.command(name="generate")
@with_error_handling
def generate(
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
    """
    Generate a pulp fiction story in the specified genre.
    """
    # Initialize story state
    story_state = None
    
    # Initialize story persistence
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    # Handle continuation if specified
    if continue_from:
        try:
            story_state = story_persistence.load_story(continue_from)
            console.print(f"[bold green]Continuing story: {story_state.metadata.title} ({story_state.metadata.genre})[/bold green]")
            console.print(f"[green]Already has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words[/green]")
            
            # Update genre from the story state
            genre = story_state.metadata.genre
            
            # If plot template is specified but different from saved, warn the user
            if (plot_template and hasattr(story_state.metadata, 'plot_template') and 
                story_state.metadata.plot_template != plot_template):
                console.print(f"[bold yellow]Warning: Continuing with plot template '{story_state.metadata.plot_template}' from saved story, ignoring specified '{plot_template}'[/bold yellow]")
                plot_template = story_state.metadata.plot_template
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[bold red]Error loading story: {e}[/bold red]")
            return
    else:
        # Create new story state
        story_state = StoryState(genre, title)
        
        # Add plot template to metadata if specified
        if plot_template:
            # Verify plot template exists
            if not plot_registry.has_template(plot_template):
                console.print(f"[bold red]Error: Plot template '{plot_template}' not found. Use 'list-plots' to see available templates.[/bold red]")
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
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print("[yellow]Make sure Ollama is running with 'ollama serve' and the model is pulled with 'ollama pull {model}'[/yellow]")
            sys.exit(1)
        
        # Set up agent factory and crew coordinator
        task = progress.add_task("[bold blue]Initializing agent system...", total=None)
        agent_factory = AgentFactory(model_service, verbose=verbose)
        crew_coordinator = CrewCoordinator(agent_factory, model_service, verbose=verbose)
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
        
        # Display AI agent configuration
        console.print("\n[bold]Agent Configuration:[/bold]")
        console.print("The following AI agents will collaborate to create your story:")
        
        # Create a table for the agents
        agent_table = Table(box=box.ROUNDED)
        agent_table.add_column("Agent", style="cyan")
        agent_table.add_column("Role", style="green")
        agent_table.add_column("Responsibility")
        
        # Add the agents that will be used in the crew
        agent_table.add_row("Editor", "Lead", "Coordinates the story creation, maintains quality and consistency")
        agent_table.add_row("Plotter", "Strategist", "Creates the narrative structure and plot points")
        agent_table.add_row("Character Designer", "Creator", "Develops complex, engaging characters")
        agent_table.add_row("Setting Designer", "World Builder", "Crafts vivid, immersive environments")
        agent_table.add_row("Prose Writer", "Wordsmith", "Writes engaging, genre-appropriate prose")
        
        console.print(agent_table)
        
        # Display generation workflow
        console.print("\n[bold]Generation Process:[/bold]")
        if chunked:
            console.print("1. [green]Research[/green] (divided into stages):")
            console.print("   1.1 [green]Core Tropes & Elements[/green]: Identifying key genre elements")
            console.print("   1.2 [green]Historical Context[/green]: Analyzing historical influences")
            console.print("   1.3 [green]Writing Style Guide[/green]: Defining genre-appropriate language patterns")
            console.print("2. [green]World Building[/green]: Creating the setting and atmosphere")
            console.print("3. [green]Character Creation[/green]: Developing main characters with clear motivations")
            console.print("4. [green]Plot Development[/green]: Crafting the narrative structure and events")
            console.print("5. [green]Writing[/green]: Drafting the actual story")
            console.print("6. [green]Editing[/green]: Final polish and consistency check")
        else:
            console.print("1. [green]Plot Development[/green]: Establishing the narrative structure")
            console.print("2. [green]Character Creation[/green]: Designing protagonists, antagonists, and supporting characters")
            console.print("3. [green]Setting Design[/green]: Building the story world and environments")
            console.print("4. [green]Prose Writing[/green]: Crafting the actual story text")
            console.print("5. [green]Editing & Revision[/green]: Ensuring consistency and coherence")
        
        console.print("\n[bold blue]Starting story generation process...[/bold blue]")
                
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
                            
                            # You could save these intermediate results to files if desired
                            
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
                
                # Extract characters, settings, and plot points (simplified for now)
                # In a real implementation, you would extract these from agent outputs
                characters = []
                settings = []
                plot_points = [{"description": f"Chapter {chapter_num} events"}]
                
                # Log the chapter content for debugging
                logger.info(f"Generated chapter {chapter_num} with {len(chapter)} characters")
                logger.info(f"Chapter begins with: {chapter[:100]}...")
                
                # Check for empty or error chapter content
                if not chapter or chapter.startswith("ERROR:"):
                    logger.error(f"Chapter generation failed: {chapter}")
                    progress.update(task, description=f"[bold red]Chapter {chapter_num} generation failed!")
                    console.print(f"[bold red]Error generating chapter {chapter_num}:[/bold red] {chapter}")
                    break
                
                # Add chapter to story state
                try:
                    story_state.add_chapter(chapter, characters, settings, plot_points)
                    logger.info(f"Successfully added chapter {chapter_num} to story state")
                    logger.info(f"Story now has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                except Exception as e:
                    logger.error(f"Failed to add chapter to story state: {e}")
                    progress.update(task, description=f"[bold red]Failed to add chapter {chapter_num} to story state!")
                    console.print(f"[bold red]Error:[/bold red] {e}")
                    break
                
                # Append to displayed story
                story_text += f"\n\n## Chapter {chapter_num}\n\n{chapter}"
                
                progress.update(task, description=f"[bold green]Chapter {chapter_num} generated!")
                
                # Save story state after each chapter if requested
                if save_state:
                    try:
                        story_path = story_persistence.save_story(story_state)
                        logger.info(f"Story state saved to {story_path}")
                        if verbose:
                            console.print(f"[dim]Story state saved to {story_path}[/dim]")
                    except Exception as e:
                        logger.error(f"Failed to save story state: {e}")
                        if verbose:
                            console.print(f"[dim]Failed to save story state: {e}[/dim]")
                
            except Exception as e:
                progress.update(task, description=f"[bold red]Failed to generate chapter {chapter_num}: {e}")
                if verbose:
                    console.print(f"[bold red]Error:[/bold red] {e}")
                    # Print traceback for debugging
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                break
            finally:
                progress.remove_task(task)
    
    # Output the story
    console.print(f"\n[bold green]Generated a {genre} pulp fiction story with {chapters} new chapter(s)![/bold green]")
    console.print(f"[green]Story now has {story_state.metadata.chapter_count} total chapters and {story_state.metadata.word_count} words[/green]\n")
    
    if output_file:
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_file, "w") as f:
                f.write(story_state.get_full_story())
            console.print(f"[bold green]Story saved to {output_file}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to save story to {output_file}: {e}[/bold red]")
    else:
        # Print story to console as Markdown
        console.print(Markdown(f"# {story_state.metadata.title}\n\n{story_text}"))
        
    # Print continuation information
    if save_state:
        console.print("\n[bold]To continue this story in the future, use:[/bold]")
        console.print(f"[cyan]pulp-fiction generate --continue {os.path.basename(story_persistence.save_story(story_state))} --chapters 1[/cyan]")

@app.command(name="generate-chunked", help="Generate a story with the chunked approach that produces intermediate outputs (deprecated, use generate --chunked instead)")
def generate_chunked(
    genre: str = typer.Option(
        "noir", "--genre", "-g", help="Pulp fiction genre to generate"
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
    verbose: bool = typer.Option(
        True, "--verbose", "-v", help="Enable verbose output"
    ),
    save_artifacts: bool = typer.Option(
        False, "--save-artifacts", help="Save intermediate artifacts to separate files"
    ),
):
    """
    Generate a story using the chunked approach with intermediate deliverables.
    """
    # Print deprecation warning
    console.print("[yellow]Note: This command is deprecated. Use 'generate --chunked' instead.[/yellow]")
    
    # Redirect to the main generate command with the chunked flag
    generate(
        genre=genre,
        chapters=1,
        output_file=output_file,
        model=model,
        title=title,
        verbose=verbose,
        chunked=True,
    )

@app.command(name="test-step")
@with_error_handling
def test_step(
    step: str = typer.Argument(..., help="The generation step to test: research, research1, research2, research3, world, character, plot, write, edit, or sequences like 'research-world'"),
    genre: str = typer.Option(
        "noir", "--genre", "-g", help="Pulp fiction genre to generate"
    ),
    model: str = typer.Option(
        "llama3.2", "--model", "-m", help="Ollama model to use"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="File to save the output to"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", help="File with input content from previous steps (JSON artifact file)"
    ),
    verbose: bool = typer.Option(
        True, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """
    Test a specific step of the story generation process.
    
    This command runs a single step or a sequence of steps in the generation process
    and outputs the result, allowing you to test and debug each component separately.
    
    You can test individual steps: 
    - research: The full research phase (combines all 3 research substeps)
    - research1: Core genre elements research
    - research2: Historical context research
    - research3: Writing style research
    - world: World building
    - character: Character creation
    - plot: Plot development
    - write: Draft writing
    - edit: Final editing
    
    Or test sequences with steps separated by hyphens:
    - research-world: Research followed by world building
    - world-character-plot: World building, then characters, then plot
    """
    # Initialize model service
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[bold blue]Initializing model service...", total=None)
        
        try:
            model_service = OllamaAdapter(model_name=model)
            # Test connection to Ollama
            model_service.get_model_info()
            progress.update(task, description=f"[bold green]Connected to Ollama using {model}!")
            progress.remove_task(task)
        except Exception as e:
            progress.update(task, description=f"[bold red]Failed to connect to Ollama: {e}")
            progress.remove_task(task)
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print("[yellow]Make sure Ollama is running with 'ollama serve' and the model is pulled with 'ollama pull {model}'[/yellow]")
            sys.exit(1)
    
    # Parse input file if provided
    input_data = {}
    if input_file:
        try:
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            console.print(f"[green]Loaded input data from {input_file}[/green]")
        except Exception as e:
            console.print(f"[bold red]Error loading input file: {e}[/bold red]")
            sys.exit(1)
    
    # Set up agent factory and crew coordinator
    agent_factory = AgentFactory(model_service, verbose=verbose)
    crew_coordinator = CrewCoordinator(agent_factory, model_service, verbose=verbose)
    
    # Parse the step sequence
    steps = step.lower().split('-')
    valid_steps = {"research", "research1", "research2", "research3", "world", "character", "plot", "write", "edit"}
    
    for s in steps:
        if s not in valid_steps:
            console.print(f"[bold red]Error: '{s}' is not a valid step. Valid steps are: {', '.join(valid_steps)}[/bold red]")
            sys.exit(1)
    
    console.print(f"[bold blue]Testing generation step(s): {', '.join(steps)}[/bold blue]")
    
    # Track results across steps
    results = {}
    
    # Process each step
    for current_step in steps:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=False,
        ) as progress:
            task = progress.add_task(f"[bold blue]Running {current_step}...", total=None)
            
            try:
                # Process individual steps
                if current_step == "research":
                    result = crew_coordinator._execute_research_phase(genre, input_data)
                    results["research"] = result
                
                elif current_step == "research1":
                    # Just run the first research substep
                    researcher = agent_factory.create_researcher(genre)
                    genre_research_task = Task(
                        description=f"Research the essential elements and history of {genre} pulp fiction. "
                                  f"Focus only on identifying the core tropes, themes, and conventions. "
                                  f"Keep this brief and focused on the most important elements.",
                        agent=researcher,
                        expected_output="A concise brief on the core elements of the genre",
                    )
                    result = crew_coordinator._execute_task(genre_research_task)
                    results["research1"] = result
                
                elif current_step == "research2":
                    # Need previous research1 output
                    if "research1" not in results and "research1" not in input_data:
                        console.print("[bold yellow]Warning: Running research2 without prior research1 output.[/bold yellow]")
                        # Create minimal research1 output if needed
                        genre_elements = input_data.get("research1", "Basic genre elements would be here.")
                    else:
                        genre_elements = results.get("research1") or input_data.get("research1")
                    
                    researcher = agent_factory.create_researcher(genre)
                    historical_context_task = Task(
                        description=f"Based on your initial research on {genre} pulp fiction elements, "
                                  f"provide historical context and key time periods or movements that "
                                  f"influenced this genre. Keep this brief and focused.",
                        agent=researcher,
                        expected_output="Historical context brief for the genre",
                        context=genre_elements
                    )
                    result = crew_coordinator._execute_task(historical_context_task)
                    results["research2"] = result
                
                elif current_step == "research3":
                    # Need previous research1 and research2 output
                    if "research1" not in results and "research1" not in input_data:
                        console.print("[bold yellow]Warning: Running research3 without prior research1 output.[/bold yellow]")
                        genre_elements = input_data.get("research1", "Basic genre elements would be here.")
                    else:
                        genre_elements = results.get("research1") or input_data.get("research1")
                    
                    if "research2" not in results and "research2" not in input_data:
                        console.print("[bold yellow]Warning: Running research3 without prior research2 output.[/bold yellow]")
                        historical_context = input_data.get("research2", "Historical context would be here.")
                    else:
                        historical_context = results.get("research2") or input_data.get("research2")
                    
                    researcher = agent_factory.create_researcher(genre)
                    style_research_task = Task(
                        description=f"Research the distinctive writing style, language patterns, and "
                                  f"vocabulary commonly found in {genre} pulp fiction. Include examples "
                                  f"of typical phrasing, dialogue patterns, and narrative voice.",
                        agent=researcher,
                        expected_output="Writing style guide for the genre",
                        context=f"Genre Elements: {genre_elements}\n\nHistorical Context: {historical_context}"
                    )
                    result = crew_coordinator._execute_task(style_research_task)
                    results["research3"] = result
                
                elif current_step == "world":
                    # Check if we have research results
                    if "research" not in results and "research" not in input_data:
                        console.print("[bold yellow]Warning: Running world building without research results.[/bold yellow]")
                        research_results = input_data.get("research", "Research results would be here.")
                    else:
                        research_results = results.get("research") or input_data.get("research")
                    
                    worldbuilding_agent = agent_factory.create_worldbuilder(genre)
                    worldbuilding_task = Task(
                        description=f"Based on the research brief, create a vivid and immersive {genre} world "
                                  f"with appropriate atmosphere, rules, and distinctive features. "
                                  f"Define the primary locations where the story will unfold.",
                        agent=worldbuilding_agent,
                        expected_output="A detailed world description with locations, atmosphere, and rules",
                        context=research_results
                    )
                    result = crew_coordinator._execute_task(worldbuilding_task)
                    results["world"] = result
                
                elif current_step == "character":
                    # Need research and world results
                    if "research" not in results and "research" not in input_data:
                        console.print("[bold yellow]Warning: Running character creation without research results.[/bold yellow]")
                        research_results = input_data.get("research", "Research results would be here.")
                    else:
                        research_results = results.get("research") or input_data.get("research")
                    
                    if "world" not in results and "world" not in input_data:
                        console.print("[bold yellow]Warning: Running character creation without world building results.[/bold yellow]")
                        world = input_data.get("world", "World building results would be here.")
                    else:
                        world = results.get("world") or input_data.get("world")
                    
                    char_agent = agent_factory.create_character_creator(genre)
                    char_task = Task(
                        description=f"Create compelling {genre} characters that fit the world. "
                                  f"Develop a protagonist, an antagonist, and key supporting characters "
                                  f"with clear motivations, backgrounds, and relationships.",
                        agent=char_agent,
                        expected_output="Character profiles for all main characters including motivations and relationships",
                        context=f"Research: {research_results}\n\nWorld: {world}"
                    )
                    result = crew_coordinator._execute_task(char_task)
                    results["character"] = result
                
                elif current_step == "plot":
                    # Need research, world, and character results
                    if "research" not in results and "research" not in input_data:
                        console.print("[bold yellow]Warning: Running plot development without research results.[/bold yellow]")
                        research_results = input_data.get("research", "Research results would be here.")
                    else:
                        research_results = results.get("research") or input_data.get("research")
                    
                    if "world" not in results and "world" not in input_data:
                        console.print("[bold yellow]Warning: Running plot development without world building results.[/bold yellow]")
                        world = input_data.get("world", "World building results would be here.")
                    else:
                        world = results.get("world") or input_data.get("world")
                    
                    if "character" not in results and "character" not in input_data:
                        console.print("[bold yellow]Warning: Running plot development without character creation results.[/bold yellow]")
                        characters = input_data.get("character", "Character creation results would be here.")
                    else:
                        characters = results.get("character") or input_data.get("character")
                    
                    plot_agent = agent_factory.create_plotter(genre)
                    plot_task = Task(
                        description=f"Using the established world and characters, develop a {genre} plot "
                                  f"with appropriate structure, pacing, and twists. Create an outline "
                                  f"of the main events and ensure it follows {genre} conventions while "
                                  f"remaining fresh and engaging.",
                        agent=plot_agent,
                        expected_output="A detailed plot outline with key events, conflicts, and resolution",
                        context=f"Research: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}"
                    )
                    result = crew_coordinator._execute_task(plot_task)
                    results["plot"] = result
                
                elif current_step == "write":
                    # Need research, world, character, and plot results
                    if "research" not in results and "research" not in input_data:
                        console.print("[bold yellow]Warning: Running writing without research results.[/bold yellow]")
                        research_results = input_data.get("research", "Research results would be here.")
                    else:
                        research_results = results.get("research") or input_data.get("research")
                    
                    if "world" not in results and "world" not in input_data:
                        console.print("[bold yellow]Warning: Running writing without world building results.[/bold yellow]")
                        world = input_data.get("world", "World building results would be here.")
                    else:
                        world = results.get("world") or input_data.get("world")
                    
                    if "character" not in results and "character" not in input_data:
                        console.print("[bold yellow]Warning: Running writing without character creation results.[/bold yellow]")
                        characters = input_data.get("character", "Character creation results would be here.")
                    else:
                        characters = results.get("character") or input_data.get("character")
                    
                    if "plot" not in results and "plot" not in input_data:
                        console.print("[bold yellow]Warning: Running writing without plot development results.[/bold yellow]")
                        plot = input_data.get("plot", "Plot development results would be here.")
                    else:
                        plot = results.get("plot") or input_data.get("plot")
                    
                    writer_agent = agent_factory.create_writer(genre)
                    writing_task = Task(
                        description=f"Write the {genre} story based on the world, characters, and plot outline. "
                                  f"Use appropriate style, voice, and dialogue for the genre. "
                                  f"Create vivid descriptions and engaging narrative.",
                        agent=writer_agent,
                        expected_output="A complete draft of the story with appropriate style and voice",
                        context=f"Research: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}\n\nPlot: {plot}"
                    )
                    result = crew_coordinator._execute_task(writing_task)
                    results["write"] = result
                
                elif current_step == "edit":
                    # Need draft results
                    if "write" not in results and "write" not in input_data:
                        console.print("[bold yellow]Warning: Running editing without writing results.[/bold yellow]")
                        draft = input_data.get("write", "Draft writing results would be here.")
                    else:
                        draft = results.get("write") or input_data.get("write")
                    
                    # Optional context from earlier steps
                    research_results = results.get("research") or input_data.get("research", "")
                    world = results.get("world") or input_data.get("world", "")
                    characters = results.get("character") or input_data.get("character", "")
                    plot = results.get("plot") or input_data.get("plot", "")
                    
                    editor_agent = agent_factory.create_editor(genre)
                    editing_task = Task(
                        description=f"Review and refine the {genre} story draft. Ensure consistency in "
                                  f"plot, characters, and setting. Polish the prose while maintaining "
                                  f"the appropriate {genre} style. Correct any errors or inconsistencies.",
                        agent=editor_agent,
                        expected_output="A polished, final version of the story",
                        context=f"Draft: {draft}\n\nResearch: {research_results}\n\nWorld: {world}\n\nCharacters: {characters}\n\nPlot: {plot}"
                    )
                    result = crew_coordinator._execute_task(editing_task)
                    results["edit"] = result
                
                # Update progress and show completion
                progress.update(task, description=f"[bold green]{current_step} completed!")
                
            except Exception as e:
                progress.update(task, description=f"[bold red]Failed during {current_step}: {e}")
                console.print(f"[bold red]Error:[/bold red] {e}")
                if verbose:
                    import traceback
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
                sys.exit(1)
            finally:
                progress.remove_task(task)
    
    # Display the final result (the last step executed)
    final_step = steps[-1]
    final_result = results[final_step]
    
    console.print(f"\n[bold green]Completed testing of step(s): {', '.join(steps)}[/bold green]\n")
    
    # Output results
    if output_file:
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Save all results to file
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
            console.print(f"[bold green]Results saved to {output_file}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to save results to {output_file}: {e}[/bold red]")
    
    # Print the final result to console
    if len(final_result) > 1000 and not verbose:
        console.print(f"\n{final_result[:1000]}...\n[dim](Output truncated. Use --verbose to see full output or save to file with --output)[/dim]")
    else:
        console.print(f"\n{final_result}")

@app.command(name="setup-model")
def setup_model(
    model: str = typer.Option(
        "llama3.2", "--model", "-m", help="Base Ollama model to configure"
    ),
    save_as: Optional[str] = typer.Option(
        None, "--save-as", "-s", help="Name to save the configured model as (default: model-optimized)"
    ),
    threads: Optional[int] = typer.Option(
        None, "--threads", help=f"Number of CPU threads (default: {os.environ.get('OLLAMA_THREADS', 4)})"
    ),
    gpu_layers: Optional[int] = typer.Option(
        None, "--gpu-layers", help=f"Number of layers to run on GPU (default: {os.environ.get('OLLAMA_GPU_LAYERS', 0)})"
    ),
    ctx_size: Optional[int] = typer.Option(
        None, "--ctx-size", help=f"Context window size (default: {os.environ.get('OLLAMA_CTX_SIZE', 4096)})"
    ),
    batch_size: Optional[int] = typer.Option(
        None, "--batch-size", help=f"Batch size for processing tokens (default: {os.environ.get('OLLAMA_BATCH_SIZE', 256)})"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """
    Create an optimized model configuration for Ollama.
    
    This command creates a custom Modelfile with optimal parameters for your system,
    then builds a new model that you can use for faster generation.
    """
    # If no save_as provided, use default name
    if not save_as:
        save_as = f"{model}-optimized"
    
    # Get default parameters from environment variables
    default_threads = int(os.environ.get("OLLAMA_THREADS", 4))
    default_gpu_layers = int(os.environ.get("OLLAMA_GPU_LAYERS", 0))
    default_ctx_size = int(os.environ.get("OLLAMA_CTX_SIZE", 4096))
    default_batch_size = int(os.environ.get("OLLAMA_BATCH_SIZE", 256))
    
    # Use provided values or defaults
    threads = threads if threads is not None else default_threads
    gpu_layers = gpu_layers if gpu_layers is not None else default_gpu_layers
    ctx_size = ctx_size if ctx_size is not None else default_ctx_size
    batch_size = batch_size if batch_size is not None else default_batch_size
    
    # Check if Ollama is running
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("[bold blue]Checking Ollama service...", total=None)
            
            # Try to connect to Ollama
            adapter = OllamaAdapter(model_name=model)
            adapter.get_model_info()
            
            progress.update(task, description="[bold green]Ollama service is running!")
            progress.remove_task(task)
    except Exception as e:
        console.print("[bold red]Error:[/bold red] Could not connect to Ollama service.")
        console.print("[yellow]Make sure Ollama is running with 'ollama serve'[/yellow]")
        return
    
    # Create temporary Modelfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.Modelfile') as f:
        modelfile_path = f.name
        f.write(f"FROM {model}\n")
        
        # Add parameter settings using correct Ollama parameter names
        f.write(f"PARAMETER num_thread {threads}\n")
        f.write(f"PARAMETER num_gpu {gpu_layers}\n")
        f.write(f"PARAMETER num_ctx {ctx_size}\n")
        f.write(f"PARAMETER num_batch {batch_size}\n")
    
    # Display model configuration
    console.print("\n[bold]Creating optimized model configuration:[/bold]")
    console.print(f"Base model: [cyan]{model}[/cyan]")
    console.print(f"New model name: [cyan]{save_as}[/cyan]")
    console.print(f"Configuration:")
    console.print(f"  - num_thread: [cyan]{threads}[/cyan]")
    console.print(f"  - num_gpu: [cyan]{gpu_layers}[/cyan]")
    console.print(f"  - num_ctx: [cyan]{ctx_size}[/cyan]")
    console.print(f"  - num_batch: [cyan]{batch_size}[/cyan]")
    
    try:
        # Create the model
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=False,
        ) as progress:
            task = progress.add_task(f"[bold blue]Creating optimized model {save_as}...", total=None)
            
            # Run the ollama create command
            create_cmd = ["ollama", "create", save_as, "-f", modelfile_path]
            if verbose:
                console.print(f"[dim]Running command: {' '.join(create_cmd)}[/dim]")
            
            process = subprocess.run(
                create_cmd,
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                progress.update(task, description=f"[bold red]Failed to create model!")
                progress.remove_task(task)
                console.print(f"[bold red]Error:[/bold red] {process.stderr}")
                return
            
            progress.update(task, description=f"[bold green]Model {save_as} created successfully!")
            progress.remove_task(task)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return
    finally:
        # Clean up the temporary file
        try:
            os.unlink(modelfile_path)
        except:
            pass
    
    # Success message
    console.print(f"\n[bold green]Model {save_as} has been optimized and is ready to use![/bold green]")
    console.print(f"[green]You can now generate stories with:[/green]")
    console.print(f"[cyan]pulp-fiction generate --model {save_as} --genre noir --chapters 1[/cyan]")
    
    # Suggest updating .env
    console.print(f"\n[bold]Tip:[/bold] To make {save_as} your default model, update your .env file with:")
    console.print(f"[cyan]OLLAMA_MODEL={save_as}[/cyan]")


@app.command(name="list-genres")
def list_genres():
    """
    List available pulp fiction genres.
    """
    genres = [
        ("noir", "Gritty crime fiction with tough, cynical characters"),
        ("sci-fi", "Space adventures with advanced technology and alien encounters"),
        ("weird", "Horror stories with supernatural or cosmic elements"),
        ("adventure", "Tales of exploration and discovery in exotic locations"),
        ("western", "Stories set in the American frontier with cowboys and outlaws"),
        ("espionage", "Tales of international intrigue and spycraft")
    ]
    
    console.print("[bold]Available Pulp Fiction Genres:[/bold]\n")
    
    for genre, description in genres:
        console.print(f"[bold cyan]{genre}[/bold cyan]: {description}")


@app.command(name="check-model")
def check_model(
    model: str = typer.Option(
        "llama3.2", "--model", "-m", help="Ollama model to check"
    )
):
    """
    Check if an Ollama model is available and fetch its details.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[bold blue]Checking model {model}...", total=None)
        
        try:
            model_service = OllamaAdapter(model_name=model)
            model_info = model_service.get_model_info()
            
            progress.update(task, description=f"[bold green]Model {model} is available!")
            progress.remove_task(task)
            
            console.print(f"\n[bold]Details for model [cyan]{model}[/cyan]:[/bold]\n")
            
            # Extract and display relevant model information
            if "details" in model_info:
                details = model_info["details"]
                if "parameter_size" in details:
                    console.print(f"Parameter Size: [cyan]{details['parameter_size']}[/cyan]")
                if "family" in details:
                    console.print(f"Model Family: [cyan]{details['family']}[/cyan]")
                if "quantization_level" in details:
                    console.print(f"Quantization: [cyan]{details['quantization_level']}[/cyan]")
            
            if "license" in model_info:
                # Truncate license text for display
                license_text = model_info["license"]
                if len(license_text) > 100:
                    license_text = license_text[:100] + "..."
                console.print(f"License: [dim]{license_text}[/dim]")
            
            if "modified_at" in model_info:
                console.print(f"Last Modified: [cyan]{model_info['modified_at']}[/cyan]")
                
        except Exception as e:
            progress.update(task, description=f"[bold red]Model {model} check failed!")
            progress.remove_task(task)
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print("[yellow]Make sure Ollama is running with 'ollama serve' and the model is pulled with 'ollama pull {model}'[/yellow]")


@app.command(name="list-stories")
def list_stories():
    """
    List all saved stories.
    """
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    stories = story_persistence.list_stories()
    
    if not stories:
        console.print("[yellow]No saved stories found.[/yellow]")
        return
        
    table = Table(title="Saved Stories")
    table.add_column("Title", style="cyan")
    table.add_column("Genre", style="green")
    table.add_column("Chapters", justify="right")
    table.add_column("Filename", style="dim")
    table.add_column("Last Modified", style="dim")
    
    for story in stories:
        table.add_row(
            story["title"],
            story["genre"],
            str(story["chapters"]),
            story["filename"],
            story["modified"].split("T")[0] if "T" in story["modified"] else story["modified"]
        )
        
    console.print(table)
    console.print("\n[bold]To continue a story, use:[/bold]")
    console.print("[cyan]python -m pulp_fiction_generator --continue FILENAME --chapters 1[/cyan]")


@app.command(name="search-stories")
def search_stories(
    query: str = typer.Argument(..., help="Search term to look for in stories")
):
    """
    Search for stories by title, character names, or other metadata.
    """
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    results = story_persistence.search_stories(query)
    
    if not results:
        console.print(f"[yellow]No stories found matching '{query}'.[/yellow]")
        return
        
    table = Table(title=f"Search Results for '{query}'")
    table.add_column("Title", style="cyan")
    table.add_column("Genre", style="green")
    table.add_column("Chapters", justify="right")
    table.add_column("Words", justify="right")
    table.add_column("Filename", style="dim")
    
    for story in results:
        table.add_row(
            story["title"],
            story["genre"],
            str(story["chapters"]),
            str(story["word_count"]),
            story["filename"]
        )
        
    console.print(table)


@app.command(name="check-consistency")
def check_consistency(
    story_file: str = typer.Argument(..., help="Path to the story file to check"),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="File to save the consistency report to"
    ),
    model: str = typer.Option(
        "llama3.2", "--model", "-m", help="Ollama model to use for AI-assisted checks"
    ),
    ai_checks: bool = typer.Option(
        True, "--ai-checks/--no-ai-checks", help="Enable/disable AI-assisted consistency checks"
    ),
):
    """
    Check a story for character and plot consistency issues.
    """
    # Initialize story persistence
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    # Load the story
    try:
        story_state = story_persistence.load_story(story_file)
        console.print(f"[bold green]Checking consistency for: {story_state.metadata.title} ({story_state.metadata.genre})[/bold green]")
        console.print(f"[green]Story has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words[/green]")
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error loading story: {e}[/bold red]")
        return
    
    # Set up model service if AI checks are enabled
    model_service = None
    if ai_checks:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("[bold blue]Initializing model service for AI checks...", total=None)
            
            try:
                model_service = OllamaAdapter(model_name=model)
                # Test connection to Ollama
                model_service.get_model_info()
                progress.update(task, description=f"[bold green]Connected to Ollama using {model}!")
                progress.remove_task(task)
            except Exception as e:
                progress.update(task, description=f"[bold red]Failed to connect to Ollama: {e}")
                progress.remove_task(task)
                console.print(f"[bold red]Error:[/bold red] {e}")
                console.print("[yellow]AI-assisted checks will be disabled. Make sure Ollama is running with 'ollama serve'.[/yellow]")
                ai_checks = False
    
    # Initialize consistency checker
    consistency_checker = ConsistencyChecker(model_service)
    
    # Run consistency check
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[bold blue]Checking story consistency...", total=None)
        
        try:
            # Generate consistency report
            report = consistency_checker.generate_consistency_report(story_state)
            progress.update(task, description="[bold green]Consistency check complete!")
            progress.remove_task(task)
            
            # Output the report
            if output_file:
                try:
                    # Create output directory if it doesn't exist
                    report_dir = os.path.dirname(output_file)
                    if report_dir and not os.path.exists(report_dir):
                        os.makedirs(report_dir)
                        
                    with open(output_file, "w") as f:
                        f.write(report)
                    console.print(f"[bold green]Consistency report saved to {output_file}[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]Failed to save report to {output_file}: {e}[/bold red]")
            
            # Display report to console
            console.print(Markdown(report))
                
        except Exception as e:
            progress.update(task, description=f"[bold red]Consistency check failed: {e}")
            progress.remove_task(task)
            console.print(f"[bold red]Error:[/bold red] {e}")


@app.command(name="list-plots")
def list_plots():
    """
    List available plot templates.
    """
    try:
        templates = plot_registry.list_templates()
        
        if not templates:
            console.print("[yellow]No plot templates available.[/yellow]")
            return
        
        console.print("[bold]Available Plot Templates:[/bold]\n")
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Narrative Arc", style="green")
        table.add_column("Suitable Genres", style="yellow")
        
        for template_info in templates:
            # Get full template to access genre affinities
            template = plot_registry.get_template(template_info["name"])
            genre_affinities = template.get_suitable_genres()
            
            # Get suitable genres with affinity above 0.7
            suitable_genres = [genre for genre, affinity in genre_affinities.items() if affinity >= 0.7]
            genre_text = ", ".join(suitable_genres) if suitable_genres else "All"
            
            table.add_row(
                template_info["name"],
                template_info["description"][:80] + ("..." if len(template_info["description"]) > 80 else ""),
                template_info["narrative_arc"] or "Custom",
                genre_text
            )
            
        console.print(table)
        console.print("\n[bold]To use a plot template, add the --plot option to the generate command:[/bold]")
        console.print("[cyan]python -m pulp_fiction_generator --genre noir --plot three_act[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error listing plot templates: {e}[/bold red]")


@app.command(name="interactive")
def interactive():
    """
    Launch an interactive mode for running and testing the Pulp Fiction Generator.
    """
    console.print("[bold]Pulp Fiction Generator - Interactive Mode[/bold]")
    console.print("[dim]This mode allows you to easily set up and run story generation.[/dim]\n")
    
    # Initialize story persistence
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    story_persistence = StoryPersistence(output_dir)
    
    # Set up model service
    console.print("[bold]Model Setup[/bold]")
    default_model = "llama3.2"
    model_name = Prompt.ask("Model to use", default=default_model)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[bold blue]Connecting to Ollama with {model_name}...", total=None)
        
        try:
            model_service = OllamaAdapter(model_name=model_name)
            model_info = model_service.get_model_info()
            progress.update(task, description=f"[bold green]Connected to Ollama using {model_name}!")
            progress.remove_task(task)
        except Exception as e:
            progress.update(task, description=f"[bold red]Failed to connect to Ollama: {e}")
            progress.remove_task(task)
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print("[yellow]Make sure Ollama is running with 'ollama serve' and the model is pulled with 'ollama pull {model_name}'[/yellow]")
            return
    
    # Set up agent factory and crew coordinator
    agent_factory = AgentFactory(model_service, verbose=False)
    crew_coordinator = CrewCoordinator(agent_factory, model_service, verbose=False)
    
    # Genre selection
    console.print("\n[bold]Genre Selection[/bold]")
    genres = {
        "noir": "Gritty crime fiction with tough, cynical characters",
        "sci-fi": "Space adventures with advanced technology and alien encounters",
        "weird": "Horror stories with supernatural or cosmic elements",
        "adventure": "Tales of exploration and discovery in exotic locations",
        "western": "Stories set in the American frontier with cowboys and outlaws",
        "espionage": "Tales of international intrigue and spycraft"
    }
    
    # Display genres table
    table = Table(title="Available Genres", box=box.ROUNDED)
    table.add_column("Genre", style="cyan")
    table.add_column("Description")
    
    for genre, description in genres.items():
        table.add_row(genre, description)
    
    console.print(table)
    
    # Get genre choice
    genre = Prompt.ask("Select a genre", choices=list(genres.keys()), default="noir")
    
    # Plot template selection
    console.print("\n[bold]Plot Template Selection[/bold]")
    use_plot = Confirm.ask("Use a plot template?", default=True)
    
    plot_template = None
    if use_plot:
        templates = plot_registry.list_templates()
        
        # Display plot templates table
        plot_table = Table(title="Available Plot Templates", box=box.ROUNDED)
        plot_table.add_column("Name", style="cyan")
        plot_table.add_column("Description")
        plot_table.add_column("Narrative Arc", style="green")
        
        template_names = []
        for template_info in templates:
            plot_table.add_row(
                template_info["name"],
                template_info["description"][:80] + ("..." if len(template_info["description"]) > 80 else ""),
                template_info["narrative_arc"] or "Custom"
            )
            template_names.append(template_info["name"])
        
        console.print(plot_table)
        
        # Get plot template choice
        if template_names:
            plot_template = Prompt.ask("Select a plot template", choices=template_names, default=template_names[0])
        else:
            console.print("[yellow]No plot templates available.[/yellow]")
    
    # Story configuration
    console.print("\n[bold]Story Configuration[/bold]")
    
    # Title (optional)
    title = Prompt.ask("Story title (leave empty for auto-generated)", default="")
    title = None if not title else title
    
    # Number of chapters
    chapters = IntPrompt.ask("Number of chapters to generate", default=1)
    
    # Continue from existing story?
    continue_story = Confirm.ask("Continue from existing story?", default=False)
    continue_from = None
    
    if continue_story:
        stories = story_persistence.list_stories()
        
        if not stories:
            console.print("[yellow]No saved stories found. Starting a new story.[/yellow]")
        else:
            # Display stories table
            stories_table = Table(title="Saved Stories", box=box.ROUNDED)
            stories_table.add_column("ID", style="dim")
            stories_table.add_column("Title", style="cyan")
            stories_table.add_column("Genre", style="green")
            stories_table.add_column("Chapters", justify="right")
            
            for i, story in enumerate(stories):
                stories_table.add_row(
                    str(i+1),
                    story["title"],
                    story["genre"],
                    str(story["chapters"])
                )
            
            console.print(stories_table)
            
            # Get story choice
            story_id = IntPrompt.ask("Select a story ID", default=1)
            if 1 <= story_id <= len(stories):
                continue_from = stories[story_id-1]["filename"]
            else:
                console.print("[yellow]Invalid story ID. Starting a new story.[/yellow]")
    
    # Output configuration
    console.print("\n[bold]Output Configuration[/bold]")
    
    save_to_file = Confirm.ask("Save story to file?", default=True)
    output_file = None
    
    if save_to_file:
        default_filename = f"{genre}_story.md"
        output_file = Prompt.ask("Output filename", default=default_filename)
    
    save_state = Confirm.ask("Save story state for future continuation?", default=True)
    
    verbose = Confirm.ask("Enable verbose output?", default=False)
    
    # Confirmation
    console.print("\n[bold]Story Generation Configuration:[/bold]")
    console.print(f"Genre: [cyan]{genre}[/cyan]")
    if plot_template:
        console.print(f"Plot template: [cyan]{plot_template}[/cyan]")
    if title:
        console.print(f"Title: [cyan]{title}[/cyan]")
    console.print(f"Chapters: [cyan]{chapters}[/cyan]")
    if continue_from:
        console.print(f"Continuing from: [cyan]{continue_from}[/cyan]")
    if output_file:
        console.print(f"Output file: [cyan]{output_file}[/cyan]")
    console.print(f"Save state: [cyan]{save_state}[/cyan]")
    console.print(f"Verbose: [cyan]{verbose}[/cyan]")
    
    proceed = Confirm.ask("\nGenerate story with these settings?", default=True)
    
    if not proceed:
        console.print("[yellow]Story generation cancelled.[/yellow]")
        return
    
    # Run generation with the selected parameters
    console.print("\n[bold]Generating Story[/bold]")
    
    # Initialize story state
    story_state = None
    
    # Handle continuation if specified
    if continue_from:
        try:
            story_state = story_persistence.load_story(continue_from)
            console.print(f"[bold green]Continuing story: {story_state.metadata.title} ({story_state.metadata.genre})[/bold green]")
            console.print(f"[green]Already has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words[/green]")
            
            # Update genre from the story state
            genre = story_state.metadata.genre
            
            # If plot template is specified but different from saved, warn the user
            if (plot_template and hasattr(story_state.metadata, 'plot_template') and 
                story_state.metadata.plot_template != plot_template):
                console.print(f"[bold yellow]Warning: Continuing with plot template '{story_state.metadata.plot_template}' from saved story, ignoring specified '{plot_template}'[/bold yellow]")
                plot_template = story_state.metadata.plot_template
        except (FileNotFoundError, ValueError) as e:
            console.print(f"[bold red]Error loading story: {e}[/bold red]")
            return
    else:
        # Create new story state
        story_state = StoryState(genre, title)
        
        # Add plot template to metadata if specified
        if plot_template:
            # Verify plot template exists
            if not plot_registry.has_template(plot_template):
                console.print(f"[bold red]Error: Plot template '{plot_template}' not found.[/bold red]")
                return
            story_state.metadata.plot_template = plot_template
    
    # Generate story chapters
    story_text = ""
    starting_chapter = story_state.metadata.chapter_count + 1
    
    console.print("\n[bold]Starting generation. Press Ctrl+C at any time to abort.[/bold]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=False,
        ) as progress:
            for chapter_num in range(starting_chapter, starting_chapter + chapters):
                task = progress.add_task(f"[bold blue]Generating chapter {chapter_num}...", total=None)
                
                try:
                    # Prepare custom inputs including plot template if available
                    custom_inputs = {"chapter_number": chapter_num, "title": title}
                    
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
                        
                        continuation_crew = crew_coordinator.create_continuation_crew(
                            genre, 
                            previous_content,
                            config=custom_inputs
                        )
                        chapter = crew_coordinator.kickoff_crew(
                            continuation_crew, 
                            inputs=custom_inputs
                        )
                    
                    # Extract characters, settings, and plot points (simplified for now)
                    characters = []
                    settings = []
                    plot_points = [{"description": f"Chapter {chapter_num} events"}]
                    
                    # Log the chapter content for debugging
                    logger.info(f"Generated chapter {chapter_num} with {len(chapter)} characters")
                    logger.info(f"Chapter begins with: {chapter[:100]}...")
                    
                    # Check for empty or error chapter content
                    if not chapter or chapter.startswith("ERROR:"):
                        logger.error(f"Chapter generation failed: {chapter}")
                        progress.update(task, description=f"[bold red]Chapter {chapter_num} generation failed!")
                        console.print(f"[bold red]Error generating chapter {chapter_num}:[/bold red] {chapter}")
                        break
                    
                    # Add chapter to story state
                    try:
                        story_state.add_chapter(chapter, characters, settings, plot_points)
                        logger.info(f"Successfully added chapter {chapter_num} to story state")
                        logger.info(f"Story now has {story_state.metadata.chapter_count} chapters and {story_state.metadata.word_count} words")
                    except Exception as e:
                        logger.error(f"Failed to add chapter to story state: {e}")
                        progress.update(task, description=f"[bold red]Failed to add chapter {chapter_num} to story state!")
                        console.print(f"[bold red]Error:[/bold red] {e}")
                        break
                    
                    # Append to displayed story
                    story_text += f"\n\n## Chapter {chapter_num}\n\n{chapter}"
                    
                    progress.update(task, description=f"[bold green]Chapter {chapter_num} generated!")
                    
                    # Save story state after each chapter if requested
                    if save_state:
                        try:
                            story_path = story_persistence.save_story(story_state)
                            logger.info(f"Story state saved to {story_path}")
                            if verbose:
                                console.print(f"[dim]Story state saved to {story_path}[/dim]")
                        except Exception as e:
                            logger.error(f"Failed to save story state: {e}")
                            if verbose:
                                console.print(f"[dim]Failed to save story state: {e}[/dim]")
                
                except Exception as e:
                    progress.update(task, description=f"[bold red]Failed to generate chapter {chapter_num}: {e}")
                    if verbose:
                        console.print(f"[bold red]Error:[/bold red] {e}")
                    break
                finally:
                    progress.remove_task(task)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Generation aborted by user.[/bold yellow]")
        if story_state.metadata.chapter_count > 0:
            console.print(f"[yellow]The story has {story_state.metadata.chapter_count} completed chapters.[/yellow]")
            if save_state:
                try:
                    story_path = story_persistence.save_story(story_state)
                    console.print(f"[green]Partial story saved to {story_path}[/green]")
                except Exception as e:
                    console.print(f"[bold red]Failed to save partial story: {e}[/bold red]")
        return
    
    # Output the story
    console.print(f"\n[bold green]Generated a {genre} pulp fiction story with {chapters} new chapter(s)![/bold green]")
    console.print(f"[green]Story now has {story_state.metadata.chapter_count} total chapters and {story_state.metadata.word_count} words[/green]\n")
    
    if output_file:
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_file, "w") as f:
                f.write(story_state.get_full_story())
            console.print(f"[bold green]Story saved to {output_file}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Failed to save story to {output_file}: {e}[/bold red]")
    else:
        # Print story to console as Markdown
        console.print(Markdown(f"# {story_state.metadata.title}\n\n{story_text}"))
        
    # Print continuation information
    if save_state:
        console.print("\n[bold]To continue this story in the future, use:[/bold]")
        console.print(f"[cyan]pulp-fiction generate --continue {os.path.basename(story_persistence.save_story(story_state))} --chapters 1[/cyan]")
        
    # Ask what to do next
    console.print("\n[bold]What would you like to do next?[/bold]")
    next_action = Prompt.ask(
        "Select an option",
        choices=["generate", "continue", "edit", "menu", "exit"],
        default="exit"
    )
    
    if next_action == "generate":
        # Run interactive again to generate a new story
        interactive()
    elif next_action == "continue":
        # Run interactive with continuation flag
        console.print("[green]Launching interactive mode to continue this story...[/green]")
        # We would need to restart the interactive mode with continue_from set
        interactive()
    elif next_action == "edit":
        console.print("[yellow]Edit functionality not yet implemented.[/yellow]")
    elif next_action == "menu":
        console.print("[green]Returning to main menu...[/green]")
        # In a more complex application, this would show the main menu
        pass
    else:
        console.print("[green]Exiting interactive mode. Goodbye![/green]")

@app.command(name="health-check")
@with_error_handling
def health_check(
    check_model: bool = typer.Option(
        True, "--check-model/--no-check-model", help="Check Ollama model connection"
    ),
    model: str = typer.Option(
        "llama3.2", "--model", "-m", help="Ollama model to check"
    ),
    check_tasks: bool = typer.Option(
        True, "--check-tasks/--no-check-tasks", help="Test basic task execution"
    ),
    check_filesystem: bool = typer.Option(
        True, "--check-filesystem/--no-check-filesystem", help="Check filesystem access"
    ),
    fix_issues: bool = typer.Option(
        False, "--fix/--no-fix", help="Attempt to fix common issues"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed output"
    ),
):
    """
    Run a health check on the system.
    
    This command tests critical components of the system to ensure they are
    working properly, including imports, file access, and LLM connectivity.
    """
    console.print("Pulp Fiction Generator Health Check")
    console.print("This command verifies critical components are working properly")
    
    # Store test results for summary
    test_results = {}
    
    # 1. Check for imports and environment
    console.print("\nChecking environment...")
    
    # Check Python version
    python_version = platform.python_version()
    console.print(f"Python version: {python_version}")
    if version.parse(python_version) >= version.parse("3.10.0"):
        test_results["python_version"] = {"status": True, "value": python_version}
    else:
        test_results["python_version"] = {"status": False, "value": python_version}
        console.print("[yellow]⚠ Python version is below 3.10.0 which may cause issues[/yellow]")
        
    # Check for required packages
    all_imports_ok = True
    for package in ["crewai", "typer", "dotenv", "rich"]:
        try:
            importlib.import_module(package)
            console.print(f"✓ Found {package}")
            test_results[f"import_{package}"] = {"status": True}
        except ImportError:
            console.print(f"✗ [red]Could not import {package}. Please install it with pip install {package}[/red]")
            test_results[f"import_{package}"] = {"status": False}
            all_imports_ok = False
    
    # 2. Check filesystem access if requested
    if check_filesystem:
        console.print("\nChecking filesystem access...")
        
        # Check if output directory exists and is writable
        output_dir = "output"
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                console.print(f"✓ Created output directory: ./{output_dir}")
                test_results["output_dir"] = {"status": True}
            except Exception as e:
                console.print(f"✗ [red]Failed to create output directory: {e}[/red]")
                test_results["output_dir"] = {"status": False}
        else:
            console.print(f"✓ Created/accessed output directory: ./{output_dir}")
            test_results["output_dir"] = {"status": True}
        
        # Test file operations
        try:
            test_file = os.path.join(output_dir, f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(test_file, "w") as f:
                f.write("Test file for health check")
            console.print(f"✓ Created test file: {test_file}")
            
            with open(test_file, "r") as f:
                content = f.read()
            console.print(f"✓ Read test file successfully")
            
            os.remove(test_file)
            console.print(f"✓ Deleted test file successfully")
            
            test_results["file_operations"] = {"status": True}
        except Exception as e:
            console.print(f"✗ [red]File operations failed: {e}[/red]")
            test_results["file_operations"] = {"status": False}
    
    # 3. Check Ollama API connectivity if requested
    if check_model:
        console.print("\nChecking Ollama connection...")
        
        # First check if Ollama is running
        ollama_status = "not running"
        try:
            ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_status = "running"
                models = response.json().get("models", [])
                console.print("\n✓ Ollama service is running")
                test_results["ollama_service"] = {"status": True}
                
                # Check if the specified model is available
                model_found = False
                model_details = None
                
                for m in models:
                    if m.get("name") == model:
                        model_found = True
                        model_details = m.get("details", {})
                        break
                
                if model_found:
                    console.print(f"✓ Model '{model}' is available")
                    
                    # Display model details if available
                    if model_details:
                        if "parameter_size" in model_details:
                            console.print(f"  - Parameter Size: {model_details['parameter_size']}")
                        if "family" in model_details:
                            console.print(f"  - Family: {model_details['family']}")
                            
                    test_results["model"] = {"status": True, "details": model_details}
                else:
                    console.print(f"[yellow]⚠ Model '{model}' not found. Available models:[/yellow]")
                    for m in models:
                        console.print(f"  - {m.get('name')}")
                        
                    if fix_issues and len(models) > 0:
                        # Suggest using an available model
                        fixed_model = models[0].get("name")
                        console.print(f"[yellow]Suggesting to use available model: {fixed_model}[/yellow]")
                        model = fixed_model
                        test_results["model"] = {"status": True, "details": {"name": fixed_model}}
                    else:
                        test_results["model"] = {"status": False}
                
                # If Ollama is running and model is found/fixed, try to create ModelService
                if model_found or (fix_issues and len(models) > 0):
                    try:
                        # Initialize the OllamaAdapter
                        from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
                        model_service = OllamaAdapter(
                            model_name=model,
                            api_base=ollama_url
                        )
                        
                        # Try a simple generation to check if model works
                        try:
                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[bold blue]{task.description}"),
                                transient=True,
                            ) as progress:
                                task = progress.add_task(f"[bold blue]Testing generation with {model}...", total=None)
                                
                                response = model_service.generate(
                                    prompt="Write a one-sentence description of noir fiction.",
                                    max_tokens=30,
                                    temperature=0.7
                                )
                                
                                progress.update(task, description=f"[bold green]Generation test successful!")
                                progress.remove_task(task)
                            
                            console.print(f"✓ Model generated response: \"{response.strip()}\"")
                            test_results["generation"] = {"status": True}
                        except Exception as e:
                            console.print(f"✗ Model generation test failed: {e}")
                            test_results["generation"] = {"status": False, "error": str(e)}
                            
                    except Exception as e:
                        console.print(f"✗ Failed to initialize model service: {e}")
                        test_results["model_service"] = {"status": False, "error": str(e)}
            else:
                console.print(f"✗ [red]Ollama API returned status code {response.status_code}[/red]")
                test_results["ollama_service"] = {"status": False, "status_code": response.status_code}
                
        except requests.exceptions.ConnectionError:
            console.print(f"✗ [red]Ollama service is not running or cannot be reached at {ollama_url}[/red]")
            test_results["ollama_service"] = {"status": False, "error": "connection_error"}
            
            if fix_issues:
                console.print("[yellow]Attempting to start Ollama service...[/yellow]")
                try:
                    subprocess.Popen(["ollama", "serve"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   start_new_session=True)
                    console.print("[yellow]Ollama service start initiated.[/yellow]")
                    console.print("[yellow]Run health-check again after 5-10 seconds.[/yellow]")
                except Exception as e:
                    console.print(f"[red]Failed to start Ollama service: {e}[/red]")
    
    # 4. Check basic task execution
    if check_tasks and all_imports_ok and test_results.get("ollama_service", {}).get("status", False):
        console.print("\nTesting basic task execution...")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(f"[bold blue]Testing simple direct task...", total=None)
                
                # Create a very simple direct task using our already imported objects
                from crewai import Agent, Task, Crew
                
                # Use our adapter from earlier
                from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
                from pulp_fiction_generator.models.crewai_adapter import CrewAIModelAdapter
                
                # Create the OllamaAdapter
                ollama_adapter = OllamaAdapter(
                    model_name=model,
                    api_base=os.environ.get("OLLAMA_HOST", "http://localhost:11434")
                )
                
                # Create the CrewAIModelAdapter
                crewai_adapter = CrewAIModelAdapter(
                    ollama_adapter=ollama_adapter
                )
                
                # Create a super simple direct test of the basic task interface
                test_agent = Agent(
                    role="Tester",
                    goal="Test the system",
                    backstory="I am a test agent",
                    llm=crewai_adapter  # Use the CrewAI-compatible adapter
                )
                
                # Define a very simple task
                test_task = Task(
                    description="Write 'hello world'",
                    agent=test_agent,
                    expected_output="A simple hello world message"
                )
                
                # Create a minimal crew
                test_crew = Crew(
                    agents=[test_agent],
                    tasks=[test_task],
                    verbose=verbose
                )
                
                # Set up a 30-second timeout
                from pulp_fiction_generator.utils.error_handling import timeout
                
                # Execute with a timeout of 30 seconds
                with timeout(30):
                    progress.update(task, description=f"[bold blue]Executing simple task...")
                    result = test_crew.kickoff()
                
                progress.update(task, description=f"[bold green]Task execution successful!")
                progress.remove_task(task)
            
            console.print(f"✓ Basic task execution works")
            
            # Convert result to string if it's not already
            if result:
                if hasattr(result, "raw_output"):
                    # Handle CrewOutput object
                    result_str = str(result.raw_output)
                    console.print(f"  Result: \"{result_str[:50]}\"{'...' if len(result_str) > 50 else ''}")
                elif hasattr(result, "__str__"):
                    # Handle other objects with string representation
                    result_str = str(result)
                    console.print(f"  Result: \"{result_str[:50]}\"{'...' if len(result_str) > 50 else ''}")
                
            test_results["task_execution"] = {"status": True}
            
        except Exception as e:
            console.print(f"✗ Basic task execution failed: {e}")
            test_results["task_execution"] = {"status": False, "error": str(e)}
    
    # Display summary
    console.print("\n[bold]Health Check Summary:[/bold]")
    
    all_passed = all(result.get("status", False) for result in test_results.values())
    
    if all_passed:
        console.print("[bold green]✓ All checks passed! Your system is ready to generate stories.[/bold green]")
    else:
        console.print("[bold yellow]⚠ Some checks failed. Review issues above before generating stories.[/bold yellow]")
        
        # Summarize failures
        failures = [name for name, result in test_results.items() if not result.get("status", False)]
        console.print(f"Failed checks: {', '.join(failures)}")
    
    # Save diagnostic information
    diagnostic_info = DiagnosticInfo.collect()
    diagnostic_info["health_check"] = {
        "timestamp": datetime.now().isoformat(),
        "results": test_results,
        "all_passed": all_passed
    }
    
    try:
        log_file = DiagnosticInfo.save_to_file(diagnostic_info)
        console.print(f"\n[dim]Health check details saved to {log_file}[/dim]")
    except Exception as e:
        console.print(f"[yellow]Failed to save health check details: {e}[/yellow]")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    # Load environment variables if .env file exists
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
    
    try:
        app()
    except Exception as e:
        error_info = ErrorHandler.handle_exception(e, context={"source": "main_entry"}, show_traceback=True)
        console.print(f"\n[bold red]Unhandled application error:[/bold red] {error_info['error_message']}")
        if "log_file" in error_info:
            console.print(f"[dim]Error details saved to {error_info['log_file']}[/dim]")
        sys.exit(1) 