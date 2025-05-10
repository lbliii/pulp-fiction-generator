#!/usr/bin/env python3

"""
Test script for the CrewAIModelAdapter with CrewAI.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
if os.path.exists(".env"):
    load_dotenv()

# Try importing the necessary components
try:
    from crewai import Agent, Task, Crew
except ImportError as e:
    print(f"Failed to import CrewAI: {e}")
    sys.exit(1)

# Import our adapters
try:
    from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
    from pulp_fiction_generator.models.crewai_adapter import CrewAIModelAdapter
except ImportError as e:
    print(f"Failed to import model components: {e}")
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

    print("\nCreating CrewAIModelAdapter...")
    try:
        # Create the CrewAIModelAdapter
        crewai_adapter = CrewAIModelAdapter(ollama_adapter=ollama_adapter)
        print("CrewAIModelAdapter created successfully")
    except Exception as e:
        print(f"Failed to create CrewAIModelAdapter: {e}")
        sys.exit(1)

    print("\nTesting direct generation with OllamaAdapter...")
    try:
        response = ollama_adapter.generate(
            prompt="Write a one-sentence description of noir fiction.",
            temperature=0.7,
            max_tokens=30
        )
        print(f"Direct generation test result: {response.strip()}")
    except Exception as e:
        print(f"Direct generation test failed: {e}")
        sys.exit(1)

    print("\nCreating test agent with CrewAIModelAdapter...")
    try:
        test_agent = Agent(
            role="Tester",
            goal="Test the system",
            backstory="I am a test agent",
            llm=crewai_adapter,
            verbose=True
        )
        print("Test agent created successfully")
    except Exception as e:
        print(f"Failed to create test agent: {e}")
        sys.exit(1)

    print("\nCreating test task...")
    try:
        test_task = Task(
            description="Write 'hello world'",
            agent=test_agent,
            expected_output="A simple hello world message"
        )
        print("Test task created successfully")
        print(f"Task description: {test_task.description}")
        print(f"Task agent: {test_agent.name if hasattr(test_agent, 'name') else 'Unknown'}")
    except Exception as e:
        print(f"Failed to create test task: {e}")
        sys.exit(1)

    print("\nCreating test crew...")
    try:
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=True
        )
        print("Test crew created successfully")
    except Exception as e:
        print(f"Failed to create test crew: {e}")
        sys.exit(1)

    print("\nTrying to execute the crew...")
    try:
        print("Setting timeout to 120 seconds to ensure enough time")
        from pulp_fiction_generator.utils.error_handling import timeout
        with timeout(120):
            print("Starting kickoff...")
            result = test_crew.kickoff()
            print(f"Task result: {result}")
    except Exception as e:
        print(f"Failed to execute the crew: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 