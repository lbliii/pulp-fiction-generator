#!/usr/bin/env python3
"""
Simple test script to verify that custom_inputs are properly handled in the CrewFactory.
"""

import sys
import logging
import time
import os

# Configure balanced logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduce verbosity of noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("crewai").setLevel(logging.INFO)  # Keep CrewAI events at INFO

# Import necessary components
from pulp_fiction_generator.agents import AgentFactory
from pulp_fiction_generator.models.ollama_adapter import OllamaAdapter
from pulp_fiction_generator.crews import CrewCoordinator
from pulp_fiction_generator.utils.story_persistence import StoryPersistence, StoryState, StoryMetadata
from pulp_fiction_generator.story_model.models import StoryArtifacts  # Keep this import as it might be used elsewhere

def main():
    """Main test function."""
    try:
        # Set necessary environment variables for Crew validation
        os.environ["CHROMA_OPENAI_API_KEY"] = "dummy-api-key-for-testing"
        
        # Initialize the model service
        logger.info("Initializing OllamaAdapter...")
        model_service = OllamaAdapter(model_name="llama3.2")
        
        # Initialize the agent factory
        logger.info("Initializing agent factory...")
        agent_factory = AgentFactory(model_service)
        
        # Initialize the crew coordinator
        logger.info("Initializing crew coordinator...")
        coordinator = CrewCoordinator(agent_factory, model_service)
        
        # Initialize the story persistence service
        logger.info("Initializing story persistence...")
        story_persistence = StoryPersistence(output_dir="./output")
        
        # Define custom inputs
        custom_inputs = {
            "title": "The Mars Conspiracy",
            "protagonist_name": "Commander Alex Reyes",
            "setting": "Mars Colony Alpha in the year 2157",
            "antagonist": "Dr. Elias Blackwood, head of the Mars Science Division"
        }
        
        # Log our test plans
        logger.info(f"Testing with custom inputs: {custom_inputs}")
        
        # Generate a story with custom inputs
        try:
            logger.info("Generating a sci-fi story with custom inputs...")
            logger.info("This may take several minutes as the agents work on your story...")
            
            story = coordinator.generate_story(
                genre="sci-fi",
                custom_inputs=custom_inputs,
                timeout_seconds=300,  # 5 minutes
                use_yaml_crew=False  # Disable YAML crew to avoid validation issues
            )
            
            # Check if we got a valid result
            if story and len(story) > 100:
                logger.info("SUCCESS: Generated a story with custom inputs!")
                logger.info(f"Story length: {len(story)} characters")
                logger.info(f"Story preview:\n{story[:200]}...")
                
                # Save the story using StoryPersistence
                # Create a StoryState object with the correct genre and title
                story_state = StoryState(
                    genre="sci-fi", 
                    title=custom_inputs["title"]
                )
                
                # Add the generated story as the first chapter
                story_state.add_chapter(story)
                
                # Add any other metadata we have from custom inputs
                if "protagonist_name" in custom_inputs:
                    story_state.metadata.add_character({
                        "name": custom_inputs["protagonist_name"],
                        "role": "protagonist",
                        "description": f"Main character of the story. {custom_inputs.get('setting', '')}"
                    })
                
                if "antagonist" in custom_inputs:
                    story_state.metadata.add_character({
                        "name": custom_inputs["antagonist"],
                        "role": "antagonist",
                        "description": "Main antagonist of the story."
                    })
                
                if "setting" in custom_inputs:
                    story_state.metadata.add_setting({
                        "name": "Main Setting",
                        "description": custom_inputs["setting"]
                    })
                
                # Add tags
                story_state.metadata.add_tag("sci-fi")
                story_state.metadata.add_tag("custom_inputs")
                story_state.metadata.add_tag("test")
                
                # Save using the StoryPersistence service
                saved_path = story_persistence.save_story(story_state)
                logger.info(f"Story saved to project folder: {saved_path}")
                
                # Show the project directory path for clarity
                project_dir = story_persistence.get_project_dir(story_state)
                logger.info(f"Project directory: {project_dir}")
                
                # Also save a simple copy for easier testing
                with open("test_custom_inputs_result.md", "w") as f:
                    f.write(story)
                logger.info("Story also saved to test_custom_inputs_result.md")
                
                return 0
            else:
                logger.error(f"Generated story is too short or empty: {story}")
                return 1
        except Exception as e:
            logger.error(f"Error during story generation: {e}", exc_info=True)
            return 1
    except Exception as e:
        logger.error(f"Setup error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    start_time = time.time()
    exit_code = main()
    elapsed_time = time.time() - start_time
    logger.info(f"Script completed in {elapsed_time:.2f} seconds with exit code {exit_code}")
    sys.exit(exit_code) 