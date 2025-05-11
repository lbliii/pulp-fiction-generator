"""
Example demonstrating how to use forced tool outputs in the pulp fiction generator.

This script shows how to capture raw tool outputs during story generation.
"""

import os
import sys
from typing import Dict, Any, Optional

# Add the parent directory to the path so we can import our package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import required modules
from pulp_fiction_generator.models.model_service import ModelService
from pulp_fiction_generator.agents.agent_factory import AgentFactory
from pulp_fiction_generator.crews.crew_factory import CrewFactory
from pulp_fiction_generator.crews.crew_coordinator import CrewCoordinator
from pulp_fiction_generator.story_generation.story_generator import StoryGenerator
from pulp_fiction_generator.story_model.models import StoryArtifacts

# Try to import CrewAI tools
try:
    from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool, FileWriteTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    print("CrewAI tools not available. Please install with `pip install crewai_tools`")
    CREWAI_TOOLS_AVAILABLE = False


def create_tools() -> Dict[str, Any]:
    """
    Create tools for the story generation.
    
    Returns:
        Dictionary of tools to use
    """
    tools = {}
    
    if CREWAI_TOOLS_AVAILABLE:
        # Add search tool if API key is available
        if "SERPER_API_KEY" in os.environ:
            tools["search_tool"] = SerperDevTool()
            print("Added SerperDevTool for genre research")
        else:
            print("SERPER_API_KEY not found in environment, search tool will not be available")
            
        # Add file read tool
        tools["file_tool"] = FileReadTool()
        print("Added FileReadTool for reference data")
        
        # Add website search tool (no API key required)
        tools["website_tool"] = WebsiteSearchTool()
        print("Added WebsiteSearchTool for style examples")
    
    return tools


def callback(task_name: str, task_output: Optional[str]) -> None:
    """
    Callback for story generation progress.
    
    Args:
        task_name: Name of the completed task
        task_output: Output of the task
    """
    if task_output:
        output_preview = task_output[:100] + "..." if len(task_output) > 100 else task_output
        print(f"Task '{task_name}' completed with output: {output_preview}")
    else:
        print(f"Task '{task_name}' completed without output")


def generate_story_with_tool_outputs(
    genre: str = "noir",
    title: str = "The Case of the Missing Alibi"
) -> StoryArtifacts:
    """
    Generate a story with tool outputs.
    
    Args:
        genre: Genre of the story
        title: Title of the story
        
    Returns:
        Story artifacts
    """
    print(f"Generating {genre} story: '{title}'")
    
    # Create the necessary components
    model_service = ModelService()
    agent_factory = AgentFactory(model_service)
    crew_factory = CrewFactory(agent_factory)
    crew_coordinator = CrewCoordinator(agent_factory, model_service)
    
    # Create story generator
    story_generator = StoryGenerator(
        crew_factory=crew_factory,
        debug_mode=True
    )
    
    # Create tools
    tools = create_tools()
    
    if not tools:
        print("No tools available. Please install crewai_tools.")
        return None
    
    # Generate story with raw tool outputs
    custom_inputs = {
        "title": title,
        "character_names": ["Detective Smith", "Lola Nightingale", "Boss Marconi"],
        "location": "Rain City",
        "time_period": "1940s"
    }
    
    print("Starting story generation with raw tool outputs...")
    artifacts = story_generator.generate_story_chunked_with_raw_tools(
        genre=genre,
        tools=tools,
        custom_inputs=custom_inputs,
        chunk_callback=callback,
        timeout_seconds=120  # Reduced timeout for example purposes
    )
    
    print("\nStory generation complete!")
    
    # Check which artifacts were generated
    print("\nBasic artifacts:")
    for name in ["research", "worldbuilding", "characters", "plot", "draft", "final_story"]:
        if hasattr(artifacts, name) and getattr(artifacts, name):
            print(f" - {name}: ✓")
        else:
            print(f" - {name}: ✗")
    
    print("\nConditional artifacts:")
    if artifacts.has_conditional_content():
        for name, content in artifacts.get_conditional_artifacts().items():
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f" - {name}: {content_preview}")
    else:
        print(" - No conditional artifacts were generated")
    
    print("\nRaw tool outputs:")
    if artifacts.has_raw_tool_outputs():
        for name, content in artifacts.get_raw_tool_outputs().items():
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f" - {name}: {content_preview}")
    else:
        print(" - No raw tool outputs were captured")
    
    # Save the final story to a file
    if artifacts and artifacts.final_story:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{title.lower().replace(' ', '_')}.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(artifacts.final_story)
        
        print(f"\nFinal story saved to {output_path}")
    
    return artifacts


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a story with forced tool outputs")
    parser.add_argument("--genre", type=str, default="noir", help="Genre of the story")
    parser.add_argument("--title", type=str, default="The Case of the Missing Alibi", help="Title of the story")
    
    args = parser.parse_args()
    
    # Generate the story
    generate_story_with_tool_outputs(genre=args.genre, title=args.title) 