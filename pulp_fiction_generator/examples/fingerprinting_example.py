"""
Example demonstrating the use of CrewAI fingerprinting functionality.

This example shows how to use the fingerprinting functionality to track
and monitor agents, crews, and tasks throughout their lifecycle.
"""

import os
import json
import time
from typing import Dict, Any

from crewai import Agent, Crew, Process, Task
from crewai.security import Fingerprint

from pulp_fiction_generator.models.model_service import ModelService
from pulp_fiction_generator.agents.agent_factory import AgentFactory
from pulp_fiction_generator.crews.crew_factory import CrewFactory
from pulp_fiction_generator.utils.config_loader import ConfigLoader
from pulp_fiction_generator.utils.errors import logger


def save_fingerprint_data(fingerprint_data: Dict[str, Any], filename: str):
    """
    Save fingerprint data to a JSON file.
    
    Args:
        fingerprint_data: The fingerprint data to save
        filename: The filename to save to
    """
    os.makedirs("logs/fingerprints", exist_ok=True)
    with open(f"logs/fingerprints/{filename}.json", "w") as f:
        json.dump(fingerprint_data, f, indent=2)
    logger.info(f"Saved fingerprint data to logs/fingerprints/{filename}.json")


def main():
    """Run the fingerprinting example."""
    # Load configuration
    config = ConfigLoader.load_config()
    
    # Initialize the model service
    model_service = ModelService(config)
    
    # Create an agent factory
    agent_factory = AgentFactory(model_service, verbose=True)

    # Create a crew factory
    crew_factory = CrewFactory(
        agent_factory=agent_factory,
        process=Process.sequential,
        verbose=True,
        enable_planning=True
    )
    
    # Example 1: Creating agents with deterministic fingerprints
    logger.info("Creating agents with deterministic fingerprints...")
    
    # Create a writer agent with a deterministic fingerprint
    writer_agent = agent_factory.create_agent(
        agent_type="writer",
        genre="noir",
        deterministic_id="noir_writer_example"
    )
    
    # Create a researcher agent with a deterministic fingerprint
    researcher_agent = agent_factory.create_agent(
        agent_type="researcher",
        genre="noir",
        deterministic_id="noir_researcher_example"
    )
    
    # Display the fingerprint information
    logger.info(f"Writer agent fingerprint: {writer_agent.fingerprint.uuid_str}")
    logger.info(f"Writer agent fingerprint metadata: {writer_agent.fingerprint.metadata}")
    
    logger.info(f"Researcher agent fingerprint: {researcher_agent.fingerprint.uuid_str}")
    logger.info(f"Researcher agent fingerprint metadata: {researcher_agent.fingerprint.metadata}")
    
    # Save the fingerprint data
    save_fingerprint_data(
        {
            "writer_agent": {
                "uuid": writer_agent.fingerprint.uuid_str,
                "metadata": writer_agent.fingerprint.metadata,
                "created_at": writer_agent.fingerprint.created_at.isoformat()
            },
            "researcher_agent": {
                "uuid": researcher_agent.fingerprint.uuid_str,
                "metadata": researcher_agent.fingerprint.metadata,
                "created_at": researcher_agent.fingerprint.created_at.isoformat()
            }
        },
        "agent_fingerprints"
    )
    
    # Example 2: Creating a crew with fingerprinting
    logger.info("\nCreating a crew with fingerprinting...")
    
    # Create a simple noir crew
    noir_crew = crew_factory.create_basic_crew(
        genre="noir",
        config={
            "verbose": True,
            "enable_planning": True
        }
    )
    
    # Display the crew fingerprint information
    logger.info(f"Noir crew fingerprint: {noir_crew.fingerprint.uuid_str}")
    logger.info(f"Noir crew fingerprint metadata: {noir_crew.fingerprint.metadata}")
    
    # Save the crew fingerprint data
    crew_fingerprint_data = {
        "crew": {
            "uuid": noir_crew.fingerprint.uuid_str,
            "metadata": noir_crew.fingerprint.metadata,
            "created_at": noir_crew.fingerprint.created_at.isoformat()
        },
        "agents": []
    }
    
    # Add agent fingerprint data
    for agent in noir_crew.agents:
        crew_fingerprint_data["agents"].append({
            "role": agent.role,
            "uuid": agent.fingerprint.uuid_str,
            "metadata": agent.fingerprint.metadata,
            "created_at": agent.fingerprint.created_at.isoformat()
        })
    
    save_fingerprint_data(crew_fingerprint_data, "crew_fingerprints")
    
    # Example 3: Tracking task execution with fingerprints
    logger.info("\nCreating and executing tasks with fingerprinting...")
    
    # Create a task for the writer agent
    writing_task = agent_factory.create_task(
        description="Write a short noir story about a detective investigating a mysterious disappearance.",
        agent=writer_agent,
        genre="noir",
        expected_output="A short noir story (500-1000 words)"
    )
    
    # Create a task for the researcher agent
    research_task = agent_factory.create_task(
        description="Research common tropes and themes in noir fiction from the 1940s and 1950s.",
        agent=researcher_agent,
        genre="noir",
        expected_output="A list of common noir tropes and themes with brief explanations"
    )
    
    # Display task fingerprint information
    logger.info(f"Writing task fingerprint: {writing_task.fingerprint.uuid_str}")
    logger.info(f"Writing task fingerprint metadata: {writing_task.fingerprint.metadata}")
    
    logger.info(f"Research task fingerprint: {research_task.fingerprint.uuid_str}")
    logger.info(f"Research task fingerprint metadata: {research_task.fingerprint.metadata}")
    
    # Create a small crew for the tasks
    task_crew = Crew(
        agents=[writer_agent, researcher_agent],
        tasks=[research_task, writing_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Execute the crew and tasks
    logger.info("\nExecuting the crew...")
    result = task_crew.kickoff()
    
    # The fingerprinting has captured the execution lifecycle
    logger.info("\nFingerprinting has captured the execution lifecycle.")
    logger.info("Check the logs/crewai_events directory for detailed event logs.")
    
    
if __name__ == "__main__":
    main() 