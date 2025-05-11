"""
FlowFactory handles the creation and configuration of story generation flows.
"""

from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import time

from ..utils.errors import TimeoutError, logger
from ..utils.collaborative_memory import CollaborativeMemory
from .story_flow import StoryGenerationFlow, StoryState

class FlowFactory:
    """
    Factory for creating and configuring story generation flows.
    
    This class is responsible for assembling flows with the proper
    dependencies and configuration for story generation.
    """
    
    def __init__(self, crew_factory):
        """
        Initialize the flow factory.
        
        Args:
            crew_factory: The factory for creating crews that the flow will use
        """
        self.crew_factory = crew_factory
        
        # Configure crew factory to use hierarchical process by default
        # This is set in the constructor now, but we ensure it here as well
        self.crew_factory.process = "hierarchical"
        self.crew_factory.enable_planning = True
    
    def create_story_flow(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        use_collaboration: bool = True
    ) -> StoryGenerationFlow:
        """
        Create a flow for generating a story.
        
        Args:
            genre: The genre of the story
            custom_inputs: Optional custom inputs for the flow
            title: Optional title for the story
            use_collaboration: Whether to use collaborative features
            
        Returns:
            A configured story generation flow
        """
        # Create the initial state
        initial_state = StoryState(
            genre=genre,
            custom_inputs=custom_inputs or {},
            title=title or custom_inputs.get("title", "Untitled Story") if custom_inputs else "Untitled Story"
        )
        
        # Initialize collaborative memory if enabled
        if use_collaboration:
            # Set up a collaborative memory for this genre
            self.collaborative_memory = CollaborativeMemory(
                genre=genre,
                storage_dir="./.memory"
            )
            
            # Add collaborative memory to custom inputs so it can be accessed in the flow
            if not initial_state.custom_inputs:
                initial_state.custom_inputs = {}
                
            initial_state.custom_inputs["collaborative_memory"] = self.collaborative_memory
        
        print(f"Created initial state with genre: {initial_state.genre}")
        
        # Create the flow with the initial state
        flow = StoryGenerationFlow(initial_state=initial_state)
        
        # Inject the crew factory
        flow.crew_factory = self.crew_factory
        
        return flow
    
    def execute_flow(
        self, 
        flow: StoryGenerationFlow,
        timeout_seconds: int = 300,
        track_delegations: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a flow with timeout protection.
        
        Args:
            flow: The flow to execute
            timeout_seconds: Maximum time to allow for execution
            track_delegations: Whether to track delegations between agents
            
        Returns:
            The flow state after execution
            
        Raises:
            TimeoutError: If execution exceeds the timeout
        """
        logger.info(f"Executing flow with timeout of {timeout_seconds} seconds")
        
        if track_delegations and hasattr(self, 'collaborative_memory'):
            # Initialize the collaborative memory for this flow
            logger.info("Initializing collaborative memory for delegation tracking")
            self.collaborative_memory.update_shared_context(
                "flow_started", 
                {"timestamp": time.time(), "genre": flow.state.genre},
                "Flow System"
            )
        
        # Execute the flow with timeout
        with ThreadPoolExecutor() as executor:
            future = executor.submit(flow.kickoff)
            try:
                result = future.result(timeout=timeout_seconds)
                logger.info(f"Flow execution completed successfully")
                
                if track_delegations and hasattr(self, 'collaborative_memory'):
                    # Record flow completion in collaborative memory
                    self.collaborative_memory.update_shared_context(
                        "flow_completed", 
                        {"timestamp": time.time(), "genre": flow.state.genre},
                        "Flow System"
                    )
                    
                    # Store insights about the collaboration
                    delegations = self.collaborative_memory._get_delegations_for_agent(
                        agent_name="*", 
                        as_delegatee=True
                    )
                    
                    if delegations:
                        self.collaborative_memory.add_collaborative_insight(
                            f"Flow completed with {len(delegations)} delegations between agents",
                            ["Flow System"]
                        )
                
                return flow.state.dict()
            except FutureTimeoutError:
                logger.error(f"Flow execution timed out after {timeout_seconds} seconds")
                raise TimeoutError(f"Story generation timed out after {timeout_seconds} seconds")
            except Exception as e:
                logger.error(f"Error during flow execution: {str(e)}")
                raise
    
    def generate_story(
        self, 
        genre: str, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 300,
        use_collaboration: bool = True
    ) -> str:
        """
        Generate a story using a flow.
        
        Args:
            genre: The genre of the story
            custom_inputs: Optional custom inputs
            timeout_seconds: Maximum time for generation
            use_collaboration: Whether to use collaborative features
            
        Returns:
            The generated story
        """
        # Create the flow with collaboration if enabled
        flow = self.create_story_flow(
            genre, 
            custom_inputs,
            use_collaboration=use_collaboration
        )
        
        # Execute the flow and get the result
        result = self.execute_flow(
            flow, 
            timeout_seconds,
            track_delegations=use_collaboration
        )
        
        # Return the final story from the flow state
        return result.get("final_story", "")
    
    def visualize_story_flow(
        self, 
        genre: str, 
        output_file: str = "story_flow.html",
        custom_inputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a visualization of the story generation flow.
        
        Args:
            genre: The genre for visualization
            output_file: The output file path for the visualization
            custom_inputs: Optional custom inputs for the flow
            
        Returns:
            Path to the saved visualization
        """
        # Create a flow for visualization
        flow = self.create_story_flow(genre, custom_inputs)
        
        # Use CrewAI's built-in plot functionality
        try:
            # flow.plot() creates the file but returns None
            # Strip any .html extension as flow.plot will add it
            base_filename = output_file.replace(".html", "")
            flow.plot(filename=base_filename)
            
            # Since flow.plot() returns None, we'll construct the expected path
            output_path = f"{base_filename}.html"
            
            return output_path
        except Exception as e:
            # Fallback to simple HTML visualization
            print(f"Could not generate CrewAI plot: {str(e)}. Falling back to simple visualization.")

            # Create a simple HTML visualization instead
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Pulp Fiction Generator Flow for {genre}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #444;
                        border-bottom: 1px solid #ddd;
                        padding-bottom: 10px;
                    }}
                    .flow-node {{
                        background-color: #f1f8ff;
                        border: 1px solid #c8e1ff;
                        border-radius: 5px;
                        padding: 10px;
                        margin: 10px 0;
                        position: relative;
                    }}
                    .flow-node::after {{
                        content: "";
                        position: absolute;
                        bottom: -15px;
                        left: 50%;
                        width: 2px;
                        height: 15px;
                        background-color: #c8e1ff;
                    }}
                    .flow-node:last-child::after {{
                        display: none;
                    }}
                    .flow-node h3 {{
                        margin-top: 0;
                        color: #0366d6;
                    }}
                    .parameters {{
                        margin-top: 20px;
                        padding: 10px;
                        background-color: #f6f8fa;
                        border-radius: 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Pulp Fiction Generator Flow for {genre}</h1>
                    
                    <div class="parameters">
                        <h2>Input Parameters</h2>
                        <ul>
                            <li><strong>Genre:</strong> {genre}</li>
                            {"".join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in (custom_inputs or {}).items()])}
                        </ul>
                    </div>
                    
                    <h2>Flow Stages</h2>
                    
                    <div class="flow-node">
                        <h3>1. Initialize Story</h3>
                        <p>Set up the initial story parameters and prepare for generation.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>2. Research Phase</h3>
                        <p>Research the genre, tropes, and key elements of a pulp fiction story in the specified genre.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>3. Worldbuilding Phase</h3>
                        <p>Create a detailed world for the story based on the research.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>4. Character Development Phase</h3>
                        <p>Create detailed characters for the story based on the world and research.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>5. Plot Creation Phase</h3>
                        <p>Develop a compelling plot based on the characters, world, and research.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>6. Draft Writing Phase</h3>
                        <p>Write a draft of the story based on the plot, characters, world, and research.</p>
                    </div>
                    
                    <div class="flow-node">
                        <h3>7. Final Editing Phase</h3>
                        <p>Edit and finalize the story draft into a polished final story.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Write HTML to output file
            with open(output_file, "w") as f:
                f.write(html_content)
            
            return output_file 