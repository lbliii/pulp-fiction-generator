"""
Template system for generating prompts.
"""

from string import Template
from typing import Any, Dict, Optional


class PromptTemplate:
    """
    Template for generating prompts with variable substitution.
    
    This class provides a simple template system for creating prompts
    with variable substitution using Python's string.Template.
    """
    
    def __init__(self, template: str, variables: Optional[Dict[str, str]] = None):
        """
        Initialize a prompt template.
        
        Args:
            template: The template string with $variable placeholders
            variables: Optional default values for variables
        """
        self.template_str = template
        self.template = Template(template)
        self.variables = variables or {}
        
    def render(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render the template with the provided context.
        
        Args:
            context: Dictionary of variables to substitute in the template
            
        Returns:
            The rendered template with variables substituted
        """
        # Combine default variables with context
        combined_context = {**self.variables}
        if context:
            combined_context.update(context)
            
        # Substitute variables in the template
        return self.template.safe_substitute(combined_context)
    
    def __str__(self) -> str:
        """
        Return the template string representation.
        
        Returns:
            The template string
        """
        return self.template_str


class PromptLibrary:
    """
    Library of prompt templates for different agent types and genres.
    """
    
    def __init__(self):
        """Initialize the prompt library with base templates."""
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {}
        
        # Initialize with base templates for each agent type
        self._initialize_base_templates()
        
    def _initialize_base_templates(self) -> None:
        """Initialize base templates for each agent type."""
        # Researcher agent
        self.add_template(
            "researcher",
            "base",
            PromptTemplate(
                """
                You are a $role focused on researching $genre pulp fiction.
                
                Your goal is to $goal to help create an authentic and engaging pulp fiction story.
                
                $backstory
                
                Research the following aspects of $genre pulp fiction:
                1. Historical context and era-appropriate details
                2. Common tropes, themes, and conventions
                3. Typical character archetypes and their traits
                4. Setting elements and atmosphere
                5. Storytelling techniques and narrative structures
                6. Language style, dialogue patterns, and vocabulary
                
                $genre_specific_instructions
                
                Format your research in a comprehensive brief that will be used by other agents
                to create the story. Include concrete examples, reference works, and specific
                details that will make the story authentic to the genre.
                """
            )
        )
        
        # WorldBuilder agent
        self.add_template(
            "worldbuilder",
            "base",
            PromptTemplate(
                """
                You are a $role responsible for creating the world for a $genre pulp fiction story.
                
                Your goal is to $goal based on the research provided.
                
                $backstory
                
                Using the research brief, design a world with the following elements:
                1. Primary locations where the story will unfold
                2. The time period and its significant characteristics
                3. Social, political, or supernatural rules governing this world
                4. Atmosphere and mood descriptions
                5. Sensory details that make the world vivid and immersive
                
                $genre_specific_instructions
                
                Create a detailed world description that other agents can use to develop
                characters and plot within this setting. Focus on what makes this world
                unique while remaining authentic to $genre pulp fiction conventions.
                
                Research Brief:
                $research_brief
                """
            )
        )
        
        # Character Creator agent
        self.add_template(
            "character_creator",
            "base",
            PromptTemplate(
                """
                You are a $role tasked with creating characters for a $genre pulp fiction story.
                
                Your goal is to $goal that fit within the established world.
                
                $backstory
                
                Based on the research brief and world description, create the following characters:
                1. A protagonist with clear motivations, flaws, and strengths
                2. An antagonist who provides meaningful opposition
                3. 2-3 supporting characters who enhance the story
                
                For each character, include:
                - Name and physical description
                - Background and history
                - Motivations and goals
                - Personality traits and quirks
                - Speech patterns and notable phrases
                - Relationships with other characters
                
                $genre_specific_instructions
                
                Ensure that the characters are consistent with $genre pulp fiction conventions
                while avoiding clichés. Each character should have depth and internal consistency.
                
                Research Brief:
                $research_brief
                
                World Description:
                $world_description
                """
            )
        )
        
        # Plotter agent
        self.add_template(
            "plotter",
            "base",
            PromptTemplate(
                """
                You are a $role responsible for developing the plot for a $genre pulp fiction story.
                
                Your goal is to $goal that follows genre conventions while being fresh and engaging.
                
                $backstory
                
                Using the research brief, world description, and character profiles, create a plot with:
                1. A compelling hook that draws readers in
                2. Key plot points and story beats
                3. Rising action that builds tension
                4. A climax that resolves the central conflict
                5. A resolution that fits the genre's expectations
                
                $genre_specific_instructions
                
                Develop a detailed plot outline that the writer can follow to create a cohesive story.
                Include opportunities for character development and moments that showcase the unique
                aspects of the world you're working with.
                
                Research Brief:
                $research_brief
                
                World Description:
                $world_description
                
                Character Profiles:
                $character_profiles
                """
            )
        )
        
        # Writer agent
        self.add_template(
            "writer",
            "base",
            PromptTemplate(
                """
                You are a $role tasked with writing a $genre pulp fiction story.
                
                Your goal is to $goal based on the materials provided.
                
                $backstory
                
                Using the research brief, world description, character profiles, and plot outline,
                write a pulp fiction story that is faithful to the $genre style. Focus on:
                1. Authentic voice and tone for the genre
                2. Vivid, evocative descriptions
                3. Engaging dialogue that fits each character
                4. Pacing appropriate to pulp fiction
                5. Maintaining consistency with the established world and characters
                
                $genre_specific_instructions
                
                Write the complete story according to the plot outline, bringing the characters
                and world to life. Don't summarize events - show them happening through action,
                dialogue, and description.
                
                Research Brief:
                $research_brief
                
                World Description:
                $world_description
                
                Character Profiles:
                $character_profiles
                
                Plot Outline:
                $plot_outline
                """
            )
        )
        
        # Editor agent
        self.add_template(
            "editor",
            "base",
            PromptTemplate(
                """
                You are a $role responsible for refining a $genre pulp fiction story.
                
                Your goal is to $goal while maintaining the authentic voice of the genre.
                
                $backstory
                
                Review the story draft and improve it by focusing on:
                1. Consistency in plot, character, and setting
                2. Authentic $genre style and voice
                3. Pacing and structure
                4. Dialogue and description quality
                5. Overall engagement and readability
                
                $genre_specific_instructions
                
                Edit the draft to enhance its quality while preserving the author's intent
                and the distinctive characteristics of $genre pulp fiction. Fix any errors
                or inconsistencies, strengthen weak sections, and ensure the story delivers
                on its premise.
                
                Research Brief:
                $research_brief
                
                Story Draft:
                $story_draft
                """
            )
        )
        
    def add_template(self, agent_type: str, template_name: str, template: PromptTemplate) -> None:
        """
        Add a template to the library.
        
        Args:
            agent_type: The type of agent the template is for
            template_name: The name of the template
            template: The template object
        """
        # Initialize the agent type dictionary if it doesn't exist
        if agent_type not in self.templates:
            self.templates[agent_type] = {}
            
        # Add the template
        self.templates[agent_type][template_name] = template
        
    def get_template(self, agent_type: str, template_name: str = "base") -> PromptTemplate:
        """
        Get a template from the library.
        
        Args:
            agent_type: The type of agent to get a template for
            template_name: The name of the template to get
            
        Returns:
            The requested template
            
        Raises:
            ValueError: If the template is not found
        """
        if agent_type not in self.templates:
            raise ValueError(f"No templates found for agent type: {agent_type}")
            
        if template_name not in self.templates[agent_type]:
            raise ValueError(f"No template named '{template_name}' found for agent type: {agent_type}")
            
        return self.templates[agent_type][template_name]
    
    def generate_prompt(
        self, 
        agent_type: str, 
        template_name: str = "base",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a prompt using a template.
        
        Args:
            agent_type: The type of agent to generate a prompt for
            template_name: The name of the template to use
            context: Variables to substitute in the template
            
        Returns:
            The generated prompt
        """
        template = self.get_template(agent_type, template_name)
        return template.render(context)


# Create a singleton instance
prompt_library = PromptLibrary() 