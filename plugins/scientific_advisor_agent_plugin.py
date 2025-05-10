"""
Scientific Advisor Agent plugin for Pulp Fiction Generator.

This plugin adds a specialized agent that provides scientific accuracy
to science fiction and other genres requiring technical knowledge.
"""

from typing import Dict, List, Any, Type, Optional
from crewai import Agent
from pulp_fiction_generator.plugins.base import AgentPlugin
from pulp_fiction_generator.models.crewai_adapter import CrewAIModelAdapter

class ScientificAdvisorPlugin(AgentPlugin):
    """Scientific Advisor agent plugin"""
    
    plugin_id = "scientific-advisor"
    plugin_name = "Scientific Advisor Agent"
    plugin_description = "Specialized agent that provides scientific accuracy and technical advice"
    plugin_version = "1.0.0"
    
    def get_agent_class(self) -> Type:
        """Get the agent class - in this case, we return crewai's Agent"""
        return Agent
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration for this agent"""
        return {
            "role": "Scientific Advisor",
            "goal": "Provide accurate scientific advice and ensure technical plausibility",
            "backstory": "An expert scientific advisor with expertise in physics, chemistry, biology, astronomy, and other scientific fields, skilled at making complex concepts accessible.",
            "verbose": True,
            "allow_delegation": False,
            "temperature": 0.3  # Lower temperature for more accurate responses
        }
    
    def get_prompt_templates(self) -> Dict[str, str]:
        """Get prompt templates for this agent"""
        return {
            "system_prompt": """
                You are a Scientific Advisor for fiction writers, with expertise in physics, chemistry, 
                biology, astronomy, and other scientific fields. Your role is to:
                
                1. Review story elements for scientific plausibility
                2. Suggest corrections to make fictional science more credible
                3. Provide alternative scientific explanations that maintain the story's intent
                4. Offer creative solutions that balance scientific accuracy with narrative needs
                
                Guidelines:
                - Focus on major scientific inaccuracies that would break immersion for knowledgeable readers
                - For science fiction, distinguish between established scientific principles and speculative elements
                - Provide concise explanations of relevant scientific concepts
                - When a complete scientific explanation would harm the story, suggest the minimal changes needed
                - Avoid being overly pedantic about minor details that don't affect the story
                
                Always frame your advice in a constructive way that helps improve the story rather than
                just pointing out errors.
            """,
            "review_science": """
                Review the following story excerpt and identify any scientific inaccuracies:
                
                {story_excerpt}
                
                Provide corrections and alternative suggestions that would maintain the story's intent
                while improving scientific accuracy.
            """,
            "technical_explanation": """
                Provide a technically accurate but accessible explanation of {concept} that could
                be incorporated into a {genre} story. The explanation should be:
                
                1. Scientifically accurate at a high level
                2. Comprehensible to general readers
                3. Engaging and interesting
                4. Brief enough to include in a story (under 200 words)
            """,
            "scientific_worldbuilding": """
                Help create scientifically plausible worldbuilding elements for a {setting_type} in a
                {genre} story. Consider:
                
                1. Physical laws and constraints
                2. Environmental factors and ecosystems
                3. Technological implications
                4. Biological adaptations (if applicable)
                
                The setting should support the following story elements:
                {story_elements}
            """
        } 