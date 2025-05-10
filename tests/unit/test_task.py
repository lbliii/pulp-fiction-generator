#!/usr/bin/env python3

"""
Simple test script to diagnose CrewAI task execution problems
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

# Import the model service
try:
    from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
except ImportError as e:
    print(f"Failed to import model components: {e}")
    sys.exit(1)

def main():
    print("Creating OllamaAdapter...")
    try:
        # Create the OllamaAdapter directly
        ollama_adapter = OllamaAdapter(
            model_name=os.environ.get("OLLAMA_MODEL", "llama3.2"),
            api_base=os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        )
        print("OllamaAdapter created successfully")
    except Exception as e:
        print(f"Failed to create OllamaAdapter: {e}")
        sys.exit(1)

    print("\nTesting direct generation...")
    try:
        response = ollama_adapter.generate(
            prompt="Write a one-sentence description of noir fiction.",
            max_tokens=30,
            temperature=0.7
        )
        print(f"Direct generation test result: {response.strip()}")
    except Exception as e:
        print(f"Direct generation test failed: {e}")
        sys.exit(1)

    print("\nCreating test agent...")
    try:
        test_agent = Agent(
            role="Tester",
            goal="Test the system",
            backstory="I am a test agent",
            llm=ollama_adapter,
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
        print(f"Task agent: {test_task.agent.name if hasattr(test_task.agent, 'name') else 'Unknown'}")
        
        # Check if the task has an execute method
        if hasattr(test_task, 'execute'):
            print("Task has an execute method")
        else:
            print("WARNING: Task does not have an execute method")
        
        # Inspect task attributes
        print("Task attributes:")
        for attr in dir(test_task):
            if not attr.startswith('__'):
                print(f"  - {attr}")
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
        
        # Inspect crew attributes
        print("Crew attributes:")
        for attr in dir(test_crew):
            if not attr.startswith('__'):
                print(f"  - {attr}")
    except Exception as e:
        print(f"Failed to create test crew: {e}")
        sys.exit(1)

    print("\nTrying to execute the crew...")
    try:
        print("Setting timeout to 120 seconds to ensure enough time")
        from pulp_fiction_generator.utils.errors import timeout
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