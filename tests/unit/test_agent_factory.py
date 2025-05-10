#!/usr/bin/env python3

"""
Test script for the updated AgentFactory with the CrewAIModelAdapter.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()

# Try importing the necessary components
try:
    from crewai import Crew, Task
except ImportError as e:
    print(f"Failed to import CrewAI: {e}")
    sys.exit(1)

# Import our agents and adapters
try:
    from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
    from pulp_fiction_generator.agents.agent_factory import AgentFactory
except ImportError as e:
    print(f"Failed to import agent components: {e}")
    sys.exit(1)

def main():
    print("Creating OllamaAdapter...")
    try:
        # Create the OllamaAdapter
        ollama_adapter = OllamaAdapter(
            model_name=os.environ.get("OLLAMA_MODEL", "llama3.2"),
            api_base=os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        )
        print("OllamaAdapter created successfully")
    except Exception as e:
        print(f"Failed to create OllamaAdapter: {e}")
        sys.exit(1)

    print("\nCreating AgentFactory...")
    try:
        # Create the AgentFactory
        agent_factory = AgentFactory(
            model_service=ollama_adapter,
            verbose=True
        )
        print("AgentFactory created successfully")
    except Exception as e:
        print(f"Failed to create AgentFactory: {e}")
        sys.exit(1)

    print("\nCreating a researcher agent...")
    try:
        # Create a researcher agent
        researcher = agent_factory.create_researcher(genre="noir")
        print(f"Agent created successfully")
        print(f"Agent role: {researcher.role}")
        print(f"Agent goal: {researcher.goal}")
    except Exception as e:
        print(f"Failed to create researcher agent: {e}")
        sys.exit(1)

    print("\nCreating a simple task...")
    try:
        task = Task(
            description="Research the essential elements of noir fiction",
            agent=researcher,
            expected_output="A brief summary of noir fiction tropes and elements"
        )
        print("Task created successfully")
    except Exception as e:
        print(f"Failed to create task: {e}")
        sys.exit(1)

    print("\nCreating a crew...")
    try:
        crew = Crew(
            agents=[researcher],
            tasks=[task],
            verbose=True
        )
        print("Crew created successfully")
    except Exception as e:
        print(f"Failed to create crew: {e}")
        sys.exit(1)

    print("\nTrying to execute the crew...")
    try:
        print("Setting timeout to 120 seconds to ensure enough time")
        from pulp_fiction_generator.utils.error_handling import timeout
        with timeout(120):
            print("Starting kickoff...")
            result = crew.kickoff()
            print(f"\nTask result: {result}")
    except Exception as e:
        print(f"Failed to execute the crew: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 