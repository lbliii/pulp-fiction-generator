"""
Flow command implementation for visualization and story generation using CrewAI Flows.
"""

import os
import sys
import typer
from enum import Enum
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.markdown import Markdown

from ..base import BaseCommand
from ...agents.agent_factory import AgentFactory
from ...crews.crew_coordinator import CrewCoordinator
from ...crews.config.crew_coordinator_config import CrewCoordinatorConfig
from ...models.ollama_adapter import OllamaAdapter
from ...utils.story_persistence import StoryPersistence, StoryState
from ...story_model.state import StoryStateManager
from ...utils.errors import logger

app = typer.Typer(help="Flow commands for visualizing and running story generation")
console = Console()

class OutputFormat(str, Enum):
    """Output format for the generated story."""
    plain = "plain"
    markdown = "markdown"
    html = "html"
    pdf = "pdf"

def get_agent_factory(config):
    """Get the agent factory with the specified configuration."""
    return AgentFactory(
        model_service=get_model_service(config),
        verbose=config.get("verbose", True)
    )

def get_model_service(config):
    """Get the model service with the specified configuration."""
    # Get model name from config
    model_name = config.get("model", "llama3.2")
    
    # Create the OllamaAdapter with just the model name
    # The adapter will get other settings from environment variables
    return OllamaAdapter(model_name=model_name)

def get_crew_coordinator(config, agent_factory, model_service):
    """Get the crew coordinator with the specified configuration."""
    # Create coordinator config
    coordinator_config = CrewCoordinatorConfig(
        process=config.get("process", "sequential"),
        verbose=config.get("verbose", True),
        debug_mode=config.get("debug", False),
        debug_output_dir=config.get("output_dir", "./output")
    )
    
    # Create crew coordinator
    return CrewCoordinator(
        agent_factory=agent_factory,
        model_service=model_service,
        config=coordinator_config
    )

def create_execution_config(**kwargs):
    """Create an execution configuration with the specified parameters."""
    # Start with default values
    config = {
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "ollama_threads": os.getenv("OLLAMA_THREADS", None),
        "ollama_gpu_layers": os.getenv("OLLAMA_GPU_LAYERS", None),
        "ollama_ctx_size": os.getenv("OLLAMA_CTX_SIZE", None), 
        "ollama_batch_size": os.getenv("OLLAMA_BATCH_SIZE", None),
        "process": "sequential",
        "verbose": True,
        "debug": False,
        "output_dir": os.getenv("OUTPUT_DIR", "./output")
    }
    
    # Update with any provided kwargs
    config.update(kwargs)
    
    # Convert string values to integers where needed
    for param in ["ollama_threads", "ollama_gpu_layers", "ollama_ctx_size", "ollama_batch_size"]:
        if config[param] and isinstance(config[param], str):
            try:
                config[param] = int(config[param])
            except ValueError:
                # If not a valid integer, set to None
                config[param] = None
    
    return config

@app.command()
def visualize(
    genre: str = typer.Argument(..., help="The genre to visualize a story flow for"),
    output_file: str = typer.Option("story_flow.html", "--output", "-o", help="Output file for visualization"),
    theme: str = typer.Option(None, "--theme", help="Theme for the story"),
    setting: str = typer.Option(None, "--setting", help="Setting for the story"),
    character: str = typer.Option(None, "--character", "-c", help="Main character concept"),
):
    """Generate a visualization of the story generation flow."""
    
    # Create a configuration object
    config = create_execution_config()
    
    # Create model service
    model_service = get_model_service(config)
    
    # Create agent factory 
    agent_factory = get_agent_factory(config)
    
    # Create story generator components
    crew_coordinator = get_crew_coordinator(config, agent_factory, model_service)
    
    # Collect custom inputs
    custom_inputs = {}
    if theme:
        custom_inputs["theme"] = theme
    if setting:
        custom_inputs["setting"] = setting
    if character:
        custom_inputs["main_character"] = character
    
    console.print(f"[cyan]Generating flow visualization for {genre} genre...[/cyan]")
    
    try:
        # Import flow components
        from pulp_fiction_generator.flow.flow_factory import FlowFactory
        
        # Create flow factory
        flow_factory = FlowFactory(crew_coordinator.crew_factory)
        
        # Generate the visualization
        flow_output = flow_factory.visualize_story_flow(
            genre=genre, 
            output_file=output_file,
            custom_inputs=custom_inputs
        )
        
        console.print(f"[green]Flow visualization saved to {flow_output}[/green]")
        
        # Try to open the visualization in the browser
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(flow_output)}")
        except Exception as e:
            console.print(f"[yellow]Could not open visualization in browser: {str(e)}[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Error generating flow visualization: {str(e)}[/bold red]")
        if config.get("debug", False):
            import traceback
            console.print(traceback.format_exc())

@app.command()
def generate(
    genre: str = typer.Argument(..., help="The genre to generate a story for"),
    title: str = typer.Option(None, "--title", "-t", help="Title for the story"),
    theme: str = typer.Option(None, "--theme", help="Theme for the story"),
    setting: str = typer.Option(None, "--setting", help="Setting for the story"),
    character: str = typer.Option(None, "--character", "-c", help="Main character concept"),
    protagonist: str = typer.Option(None, "--protagonist", help="Protagonist details"),
    antagonist: str = typer.Option(None, "--antagonist", help="Antagonist details"),
    conflict: str = typer.Option(None, "--conflict", help="Main conflict"),
    tone: str = typer.Option(None, "--tone", help="Tone of the story"),
    style: str = typer.Option(None, "--style", help="Writing style"),
    length: str = typer.Option(None, "--length", "-l", help="Target length (short, medium, long)"),
    custom_prompt: str = typer.Option(None, "--custom-prompt", help="Custom instructions"),
    output_file: str = typer.Option(None, "--output", "-o", help="File to save the story to"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Generate a visualization of the flow"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    output_format: OutputFormat = typer.Option(
        OutputFormat.plain, "--format", case_sensitive=False, 
        help="Output format (plain, markdown, html, pdf)"
    ),
):
    """Generate a story using CrewAI Flow."""
    
    # Create a configuration object
    config = create_execution_config(debug=debug)
    
    # Create model service
    model_service = get_model_service(config)
    
    # Create agent factory 
    agent_factory = get_agent_factory(config)
    
    # Create story generator components
    crew_coordinator = get_crew_coordinator(config, agent_factory, model_service)
    
    # Collect custom inputs
    custom_inputs = {}
    if title:
        custom_inputs["title"] = title
    if theme:
        custom_inputs["theme"] = theme
    if setting:
        custom_inputs["setting"] = setting
    if character:
        custom_inputs["main_character"] = character
    if protagonist:
        custom_inputs["protagonist"] = protagonist
    if antagonist:
        custom_inputs["antagonist"] = antagonist
    if conflict:
        custom_inputs["conflict"] = conflict
    if tone:
        custom_inputs["tone"] = tone
    if style:
        custom_inputs["style"] = style
    if length:
        custom_inputs["length"] = length
    if custom_prompt:
        custom_inputs["custom_prompt"] = custom_prompt
    
    # Determine the output directory and file
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    
    if output_file and not os.path.isabs(output_file):
        output_file = os.path.join(output_dir, output_file)
    
    if visualize:
        flow_output = os.path.join(output_dir, "story_flow.html")
        console.print(f"[cyan]Generating flow visualization for {genre} genre...[/cyan]")
        
        try:
            crew_coordinator.story_generator.visualize_story_flow(
                genre=genre, 
                output_file=flow_output,
                custom_inputs=custom_inputs
            )
            console.print(f"[green]Flow visualization saved to {flow_output}[/green]")
        except Exception as e:
            console.print(f"[yellow]Could not generate flow visualization: {str(e)}[/yellow]")
    
    console.print(f"[cyan]Generating {genre} story using CrewAI Flow...[/cyan]")
    
    try:
        # Use flow-based generation
        story_text = crew_coordinator.story_generator.generate_story_with_flow(
            genre=genre,
            custom_inputs=custom_inputs,
            debug_mode=debug
        )
        
        # Format the output
        if output_format == OutputFormat.markdown:
            console.print(Markdown(story_text))
        elif output_format == OutputFormat.html:
            html_output = f"<html><body><div style='font-family: serif; max-width: 800px; margin: 0 auto; padding: 20px;'>{story_text.replace('\n', '<br>')}</div></body></html>"
            
            if output_file:
                with open(output_file, "w") as f:
                    f.write(html_output)
                console.print(f"[green]HTML story saved to {output_file}[/green]")
            else:
                # Just save to a default file since direct console output wouldn't be helpful
                default_file = os.path.join(output_dir, f"{genre.lower().replace(' ', '_')}_story.html")
                with open(default_file, "w") as f:
                    f.write(html_output)
                console.print(f"[green]HTML story saved to {default_file}[/green]")
        elif output_format == OutputFormat.pdf:
            try:
                from weasyprint import HTML
                import tempfile
                
                # Create HTML version first
                html_content = f"<html><body><div style='font-family: serif; max-width: 800px; margin: 0 auto; padding: 20px;'>{story_text.replace('\n', '<br>')}</div></body></html>"
                
                # Use a temporary file if no output specified
                if not output_file:
                    output_file = os.path.join(output_dir, f"{genre.lower().replace(' ', '_')}_story.pdf")
                
                # Generate PDF
                HTML(string=html_content).write_pdf(output_file)
                console.print(f"[green]PDF story saved to {output_file}[/green]")
            except ImportError:
                console.print("[bold red]PDF generation requires weasyprint. Install with: pip install weasyprint[/bold red]")
                
                # Fall back to plain text
                if output_file:
                    with open(output_file, "w") as f:
                        f.write(story_text)
                    console.print(f"[yellow]Saved as plain text instead to {output_file}[/yellow]")
        else:  # Plain text
            if output_file:
                with open(output_file, "w") as f:
                    f.write(story_text)
                console.print(f"[green]Story saved to {output_file}[/green]")
            else:
                # Output to console
                console.print("\n" + "="*40 + " GENERATED STORY " + "="*40 + "\n")
                console.print(story_text)
                console.print("\n" + "="*90 + "\n")
                
                # Also save to default file
                default_file = os.path.join(output_dir, f"{genre.lower().replace(' ', '_')}_story.txt")
                with open(default_file, "w") as f:
                    f.write(story_text)
                console.print(f"[green]Story also saved to {default_file}[/green]")
                
    except Exception as e:
        console.print(f"[bold red]Error generating story: {str(e)}[/bold red]")
        if debug:
            import traceback
            console.print(traceback.format_exc()) 

@app.command()
def run(
    genre: str = typer.Argument(..., help="The genre to generate a story for"),
    title: str = typer.Option(None, "--title", "-t", help="Title for the story"),
    theme: str = typer.Option(None, "--theme", help="Theme for the story"),
    setting: str = typer.Option(None, "--setting", help="Setting for the story"),
    character: str = typer.Option(None, "--character", "-c", help="Main character concept"),
    protagonist: str = typer.Option(None, "--protagonist", help="Protagonist details"),
    antagonist: str = typer.Option(None, "--antagonist", help="Antagonist details"),
    conflict: str = typer.Option(None, "--conflict", help="Main conflict"),
    tone: str = typer.Option(None, "--tone", help="Tone of the story"),
    style: str = typer.Option(None, "--style", help="Writing style"),
    length: str = typer.Option(None, "--length", "-l", help="Target length (short, medium, long)"),
    custom_prompt: str = typer.Option(None, "--custom-prompt", help="Custom instructions"),
    output_file: str = typer.Option(None, "--output", "-o", help="File to save the story to"),
    timeout: int = typer.Option(300, "--timeout", help="Maximum execution time in seconds"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
):
    """Run the story generation flow using the CrewAI CLI."""
    
    # Create a configuration object
    config = create_execution_config(debug=debug)
    
    # Collect custom inputs
    custom_inputs = {}
    if title:
        custom_inputs["title"] = title
    if theme:
        custom_inputs["theme"] = theme
    if setting:
        custom_inputs["setting"] = setting
    if character:
        custom_inputs["main_character"] = character
    if protagonist:
        custom_inputs["protagonist"] = protagonist
    if antagonist:
        custom_inputs["antagonist"] = antagonist
    if conflict:
        custom_inputs["conflict"] = conflict
    if tone:
        custom_inputs["tone"] = tone
    if style:
        custom_inputs["style"] = style
    if length:
        custom_inputs["length"] = length
    if custom_prompt:
        custom_inputs["custom_prompt"] = custom_prompt
    
    # Determine the output directory and file
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    
    if output_file and not os.path.isabs(output_file):
        output_file = os.path.join(output_dir, output_file)
    
    console.print(f"[cyan]Running {genre} story flow...[/cyan]")
    
    try:
        # Import flow components
        from pulp_fiction_generator.flow.flow_factory import FlowFactory
        from ...models.model_factory import ModelFactory
        from ...crews.crew_factory import CrewFactory
        
        # Create model and agent factories
        model_factory = ModelFactory()
        model_service = model_factory.create_model_service()
        agent_factory = get_agent_factory(config)
        
        # Create crew factory
        crew_factory = CrewFactory(agent_factory=agent_factory, model_service=model_service)
        
        # Create flow factory
        flow_factory = FlowFactory(crew_factory)
        
        # Create the flow
        flow = flow_factory.create_story_flow(genre=genre, custom_inputs=custom_inputs, title=title)
        
        # Execute the flow with timeout protection
        result = flow_factory.execute_flow(flow, timeout_seconds=timeout)
        
        # Get the final story from the flow state
        story_text = result.get("final_story", "")
        
        if not story_text:
            console.print("[bold red]No story was generated.[/bold red]")
            return
        
        # Save the story to file if specified
        if output_file:
            with open(output_file, "w") as f:
                f.write(story_text)
            console.print(f"[green]Story saved to {output_file}[/green]")
        
        # Print the story to console
        console.print("\n[bold cyan]Generated Story:[/bold cyan]\n")
        console.print(story_text)
        
        return story_text
        
    except Exception as e:
        console.print(f"[bold red]Error running flow: {str(e)}[/bold red]")
        if config.get("debug", False):
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1) 

@app.command()
def plot(
    genre: str = typer.Argument(..., help="The genre to visualize a story flow for"),
    output_file: str = typer.Option("story_flow", "--output", "-o", help="Output filename (without extension)"),
    theme: str = typer.Option(None, "--theme", help="Theme for the story"),
    setting: str = typer.Option(None, "--setting", help="Setting for the story"),
    character: str = typer.Option(None, "--character", "-c", help="Main character concept"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open the visualization in a browser"),
):
    """Generate a CrewAI Flow visualization plot for the story generation flow."""
    
    # Create a configuration object
    config = create_execution_config()
    
    # Create model service
    model_service = get_model_service(config)
    
    # Create agent factory 
    agent_factory = get_agent_factory(config)
    
    # Create story generator components
    crew_coordinator = get_crew_coordinator(config, agent_factory, model_service)
    
    # Collect custom inputs
    custom_inputs = {}
    if theme:
        custom_inputs["theme"] = theme
    if setting:
        custom_inputs["setting"] = setting
    if character:
        custom_inputs["main_character"] = character
    
    console.print(f"[cyan]Generating CrewAI Flow plot for {genre} genre...[/cyan]")
    
    try:
        # Import flow components
        from pulp_fiction_generator.flow.flow_factory import FlowFactory
        
        # Create flow factory
        flow_factory = FlowFactory(crew_coordinator.crew_factory)
        
        # Create a flow instance
        flow = flow_factory.create_story_flow(
            genre=genre,
            custom_inputs=custom_inputs
        )
        
        # Generate the plot directly using flow.plot
        # Note: flow.plot doesn't return the path, even though it creates the file
        flow.plot(filename=output_file)
        
        # Use the expected output filename directly
        output_path = f"{output_file}.html"
        
        console.print(f"[green]Plot saved as {output_path}[/green]")
        
        # Try to open the visualization in the browser if requested
        if open_browser:
            try:
                import webbrowser
                full_path = os.path.abspath(output_path)
                webbrowser.open(f"file://{full_path}")
                console.print(f"[green]Opened visualization in browser[/green]")
            except Exception as e:
                console.print(f"[yellow]Could not open visualization in browser: {str(e)}[/yellow]")
                
    except Exception as e:
        console.print(f"[bold red]Error generating flow plot: {str(e)}[/bold red]")
        if config.get("debug", False):
            import traceback
            console.print(traceback.format_exc()) 