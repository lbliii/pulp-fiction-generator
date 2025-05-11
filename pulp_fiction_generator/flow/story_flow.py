"""
Story Flow implementation for orchestrating the story generation process.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

class StoryState(BaseModel):
    """Structured state model for story generation flow."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Generate a UUID by default
    genre: str = "scifi"  # Default genre
    title: str = "Untitled Story"
    research: str = ""
    worldbuilding: str = ""
    characters: str = ""
    plot: str = ""
    draft: str = ""
    final_story: str = ""
    custom_inputs: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "arbitrary_types_allowed": True
    }

class StoryGenerationFlow(Flow[StoryState]):
    """
    Flow for generating stories with a structured, phased approach.
    
    This flow organizes story generation into discrete phases:
    1. Research
    2. Worldbuilding
    3. Character development
    4. Plot creation
    5. Initial draft
    6. Final story
    
    Each phase builds on the outputs of previous phases and all results
    are stored in the structured state.
    """
    
    # Will be injected by the flow factory
    crew_factory = None
    
    def __init__(self, initial_state: StoryState):
        """Initialize the flow with the given initial state."""
        # Make sure the state has the proper typing
        super().__init__(initial_state=initial_state)
        print(f"Initialized StoryGenerationFlow with genre: {self.state.genre}")
        
        # Set up state persistence directory
        self.persistence_dir = os.getenv("OUTPUT_DIR", "./output")
        os.makedirs(self.persistence_dir, exist_ok=True)
        
        # Create a subdirectory for this specific flow
        self.flow_dir = os.path.join(
            self.persistence_dir,
            f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.state.genre}"
        )
        os.makedirs(self.flow_dir, exist_ok=True)
        
        # Save initial state
        self._save_state("initial_state")
    
    def _save_state(self, phase_name: str):
        """Save the current state to disk."""
        # Convert state to dict
        state_dict = self.state.model_dump()
        
        # Save to JSON file
        state_file = os.path.join(self.flow_dir, f"{phase_name}.json")
        with open(state_file, "w") as f:
            json.dump(state_dict, f, indent=2)
        
        # Also save the current phase output as a text file for easy viewing
        current_phase_output = getattr(self.state, phase_name, None)
        if current_phase_output and isinstance(current_phase_output, str):
            output_file = os.path.join(self.flow_dir, f"{phase_name}.txt")
            with open(output_file, "w") as f:
                f.write(current_phase_output)
    
    @start()
    def initialize_story(self):
        """Initialize story state and set up initial parameters."""
        print(f"Starting story generation flow for genre: {self.state.genre}")
        print(f"Flow State ID: {self.state.id}")
        
        # Save state after initialization
        self._save_state("initialize_story")
        
        # Return genre to pass to the next phase
        return self.state.genre
    
    @listen(initialize_story)
    def generate_research(self, genre):
        """Generate research for the story."""
        print(f"Generating research for {genre} genre")
        
        # Create a research-focused crew
        research_crew = self._create_specialized_crew(
            "research", 
            genre, 
            self.state.custom_inputs
        )
        
        # Execute the research crew
        result = research_crew.kickoff(inputs=self.state.custom_inputs)
        
        # Store the result in state
        self.state.research = result
        print(f"Research phase complete: {len(result)} characters")
        
        # Save state after research
        self._save_state("research")
        
        return result
    
    @listen(generate_research)
    def generate_worldbuilding(self, research):
        """Generate worldbuilding based on research."""
        print(f"Generating worldbuilding based on research")
        
        # Create a worldbuilding crew
        worldbuilding_crew = self._create_specialized_crew(
            "worldbuilding", 
            self.state.genre, 
            {
                **self.state.custom_inputs,
                "research": research
            }
        )
        
        # Execute the worldbuilding crew
        result = worldbuilding_crew.kickoff(inputs={
            **self.state.custom_inputs,
            "research": research
        })
        
        # Store the result in state
        self.state.worldbuilding = result
        print(f"Worldbuilding phase complete: {len(result)} characters")
        
        # Save state after worldbuilding
        self._save_state("worldbuilding")
        
        return result
    
    @listen(generate_worldbuilding)
    def generate_characters(self, worldbuilding):
        """Generate characters based on worldbuilding."""
        print("Generating characters based on worldbuilding")
        
        # Create a character development crew
        character_crew = self._create_specialized_crew(
            "characters", 
            self.state.genre, 
            {
                **self.state.custom_inputs,
                "research": self.state.research,
                "worldbuilding": worldbuilding
            }
        )
        
        # Execute the character crew
        result = character_crew.kickoff(inputs={
            **self.state.custom_inputs,
            "research": self.state.research,
            "worldbuilding": worldbuilding
        })
        
        # Store the result in state
        self.state.characters = result
        print(f"Character phase complete: {len(result)} characters")
        
        # Save state after character generation
        self._save_state("characters")
        
        return result
    
    @listen(generate_characters)
    def generate_plot(self, characters):
        """Generate plot based on characters."""
        print("Generating plot based on characters")
        
        # Create a plot development crew
        plot_crew = self._create_specialized_crew(
            "plot", 
            self.state.genre, 
            {
                **self.state.custom_inputs,
                "research": self.state.research,
                "worldbuilding": self.state.worldbuilding,
                "characters": characters
            }
        )
        
        # Execute the plot crew
        result = plot_crew.kickoff(inputs={
            **self.state.custom_inputs,
            "research": self.state.research,
            "worldbuilding": self.state.worldbuilding,
            "characters": characters
        })
        
        # Store the result in state
        self.state.plot = result
        print(f"Plot phase complete: {len(result)} characters")
        
        # Save state after plot generation
        self._save_state("plot")
        
        return result
    
    @listen(generate_plot)
    def generate_draft(self, plot):
        """Generate draft based on plot."""
        print("Generating draft based on plot")
        
        # Create a draft writing crew
        draft_crew = self._create_specialized_crew(
            "draft", 
            self.state.genre, 
            {
                **self.state.custom_inputs,
                "research": self.state.research,
                "worldbuilding": self.state.worldbuilding,
                "characters": self.state.characters,
                "plot": plot
            }
        )
        
        # Execute the draft crew
        result = draft_crew.kickoff(inputs={
            **self.state.custom_inputs,
            "research": self.state.research,
            "worldbuilding": self.state.worldbuilding,
            "characters": self.state.characters,
            "plot": plot
        })
        
        # Store the result in state
        self.state.draft = result
        print(f"Draft phase complete: {len(result)} characters")
        
        # Save state after draft generation
        self._save_state("draft")
        
        return result
    
    @listen(generate_draft)
    def generate_final_story(self, draft):
        """Generate final story based on draft."""
        print("Generating final story based on draft")
        
        # Create a final story editing crew
        final_crew = self._create_specialized_crew(
            "final", 
            self.state.genre, 
            {
                **self.state.custom_inputs,
                "research": self.state.research,
                "worldbuilding": self.state.worldbuilding,
                "characters": self.state.characters,
                "plot": self.state.plot,
                "draft": draft
            }
        )
        
        # Execute the final crew
        result = final_crew.kickoff(inputs={
            **self.state.custom_inputs,
            "research": self.state.research,
            "worldbuilding": self.state.worldbuilding,
            "characters": self.state.characters,
            "plot": self.state.plot,
            "draft": draft
        })
        
        # Store the result in state
        self.state.final_story = result
        print(f"Final story phase complete: {len(result)} characters")
        
        # Set the title if provided in custom inputs
        if "title" in self.state.custom_inputs:
            self.state.title = self.state.custom_inputs["title"]
        
        # Save the final state
        self._save_state("final_story")
        
        # Save the complete story as a single file
        story_file = os.path.join(self.flow_dir, f"{self.state.title.replace(' ', '_')}.txt")
        with open(story_file, "w") as f:
            f.write(result)
        
        print(f"Completed story saved to {story_file}")
        
        return result
    
    def _create_specialized_crew(self, phase_type, genre, inputs=None):
        """
        Create a specialized crew for a specific story generation phase.
        
        Args:
            phase_type: The type of crew to create (research, worldbuilding, etc.)
            genre: The genre for the story
            inputs: Any inputs to provide to the crew
            
        Returns:
            A configured crew for the specified phase
        """
        # Check if the crew factory is available
        if not self.crew_factory:
            raise ValueError("Crew factory is not available")
        
        # Create and return a specialized crew
        return self.crew_factory.create_specialized_crew(phase_type, genre, inputs or {}) 