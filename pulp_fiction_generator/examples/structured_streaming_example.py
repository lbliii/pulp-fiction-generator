"""
Example demonstrating structured LLM output and streaming responses.

This example shows how to use the enhanced OllamaAdapter and CrewAIModelAdapter
to get structured responses using Pydantic models and streaming responses.
"""

import sys
import os
import time
from typing import List, Optional
from pydantic import BaseModel, Field

# Add the parent directory to the path to allow importing from the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from crewai import Agent, Task, Crew
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
from pulp_fiction_generator.models.crewai_adapter import CrewAIModelAdapter
from pulp_fiction_generator.models.story_output import Character, Location, PlotPoint, StoryOutput


def demonstrate_streaming():
    """Demonstrate streaming responses with the Ollama adapter."""
    print("\n\n--- STREAMING EXAMPLE ---\n")
    
    # Create an Ollama adapter
    ollama = OllamaAdapter()
    
    # Simple streaming example
    prompt = "Tell me a short story about a detective in a noir setting. Make it 5 sentences long."
    
    print("Streaming response directly from OllamaAdapter:\n")
    
    # Get a streaming response
    for chunk in ollama.generate_with_system(prompt=prompt, stream=True):
        print(chunk, end="", flush=True)
        time.sleep(0.01)  # Small delay to simulate real-time typing
    
    print("\n\nDone streaming!")


def demonstrate_structured_response():
    """Demonstrate structured responses with Pydantic models."""
    print("\n\n--- STRUCTURED RESPONSE EXAMPLE ---\n")
    
    # Create an Ollama adapter
    ollama = OllamaAdapter()
    
    # Create a CrewAI model adapter with the StoryOutput Pydantic model
    crewai_llm = CrewAIModelAdapter(
        ollama_adapter=ollama,
        response_format=StoryOutput
    )
    
    # Define a system prompt that asks for a structured story
    system_prompt = """You are a creative fiction writer that specializes in pulp noir stories.
    Create a short story with characters, locations, and plot points.
    Your response must strictly follow the structured format requested."""
    
    # Create a user prompt
    user_prompt = """Create a very short pulp noir detective story with one protagonist, 
    one antagonist, two locations, and three brief plot points. 
    The story should have the title "Shadows in the Rain" and fit the noir genre.
    Keep the full text under 250 words."""
    
    # Create a CrewAI agent
    writer_agent = Agent(
        role="Noir Fiction Writer",
        goal="Create engaging noir fiction stories",
        backstory="An experienced writer specializing in pulp noir stories with a keen eye for atmosphere and character development.",
        verbose=True,
        llm=crewai_llm,
        allow_delegation=False
    )
    
    # Create a task
    writing_task = Task(
        description=user_prompt,
        agent=writer_agent,
        expected_output="A complete structured noir story"
    )
    
    # Display the structured output
    print("Generating structured story output...\n")
    
    # Execute the task directly to get the result
    result = writer_agent.execute_task(writing_task)
    
    try:
        # Try to parse the result as a StoryOutput model
        story_dict = result
        if isinstance(result, str):
            import json
            # Find JSON in the result
            import re
            json_match = re.search(r'{.*}', result, re.DOTALL)
            if json_match:
                story_dict = json.loads(json_match.group(0))
        
        # Parse the story
        story = StoryOutput.model_validate(story_dict)
        
        # Display the structured story
        print("\n--- STRUCTURED STORY OUTPUT ---\n")
        print(f"Title: {story.title}")
        print(f"Genre: {story.genre}")
        print(f"Summary: {story.summary}")
        
        print("\nCharacters:")
        for character in story.characters:
            print(f"- {character.name} ({character.role}): {character.description}")
        
        print("\nLocations:")
        for location in story.locations:
            print(f"- {location.name}: {location.description}")
        
        print("\nPlot Points:")
        for i, plot_point in enumerate(story.plot_points, 1):
            print(f"{i}. {plot_point.title}: {plot_point.description}")
        
        print("\nFull Story Text:")
        print(story.full_text)
        
    except Exception as e:
        print(f"Error parsing structured output: {e}")
        print("\nRaw output:")
        print(result)


def demonstrate_streaming_with_crewai():
    """Demonstrate streaming with CrewAI."""
    print("\n\n--- CREWAI STREAMING EXAMPLE ---\n")
    
    # Create an Ollama adapter
    ollama = OllamaAdapter()
    
    # Create a CrewAI model adapter with streaming enabled
    crewai_llm = CrewAIModelAdapter(
        ollama_adapter=ollama,
        stream=True  # Enable streaming by default
    )
    
    # Create a CrewAI agent
    writer_agent = Agent(
        role="Noir Fiction Writer",
        goal="Create engaging noir fiction stories",
        backstory="An experienced writer specializing in pulp noir stories with a keen eye for atmosphere and character development.",
        verbose=True,
        llm=crewai_llm,
        allow_delegation=False
    )
    
    # Create a task
    writing_task = Task(
        description="Write a short paragraph describing a rainy street scene in a noir setting.",
        agent=writer_agent,
        expected_output="A descriptive paragraph about a rainy street scene."
    )
    
    # Create a crew
    noir_crew = Crew(
        agents=[writer_agent],
        tasks=[writing_task],
        verbose=2  # Verbose to see streaming output
    )
    
    # Run the crew
    print("Running CrewAI with streaming output...\n")
    result = noir_crew.kickoff()
    
    print("\nDone streaming with CrewAI!")


if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_streaming()
    demonstrate_structured_response()
    demonstrate_streaming_with_crewai() 