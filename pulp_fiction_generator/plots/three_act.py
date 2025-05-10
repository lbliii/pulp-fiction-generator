"""
Three-Act Structure plot template implementation.
"""

from typing import Dict, List, Any

from .base import PlotTemplate, PlotStructure, PlotPoint, NarrativeArc


class ThreeActTemplate(PlotTemplate):
    """
    Classic Three-Act Structure used in countless stories, screenplays, and novels.
    
    This template provides a framework for stories divided into setup, confrontation,
    and resolution, with turning points between each act.
    """
    
    @property
    def name(self) -> str:
        return "three_act"
    
    @property
    def description(self) -> str:
        return "The classic three-act structure (setup, confrontation, resolution) used in countless stories, with key plot points at act transitions."
    
    @property
    def narrative_arc(self) -> NarrativeArc:
        return NarrativeArc.THREE_ACT
    
    def get_plot_structure(self) -> PlotStructure:
        plot_points = [
            # ACT I - SETUP
            PlotPoint(
                name="Exposition",
                description="The story opens by establishing the main character, setting, and status quo.",
                examples=["Rick's Cafe in Casablanca", "Marlowe in his detective office", "Indiana Jones teaching at university"],
                features={"act": 1, "position": "beginning", "purpose": "establish_world"}
            ),
            PlotPoint(
                name="Inciting Incident",
                description="An event occurs that disrupts the status quo and sets the story in motion.",
                examples=["Ugarte gives Rick the letters of transit", "A mysterious client hires Marlowe", "Indiana Jones is asked to find the Ark"],
                features={"act": 1, "position": "early", "purpose": "disrupt_status_quo"}
            ),
            PlotPoint(
                name="First Plot Point / End of Act I",
                description="The protagonist makes a decision that propels them into the main conflict, ending Act I.",
                examples=["Rick discovers Ilsa is in Casablanca", "Marlowe decides to investigate deeper", "Indiana Jones agrees to find the Ark"],
                features={"act": 1, "position": "end", "purpose": "point_of_no_return"}
            ),
            
            # ACT II - CONFRONTATION
            PlotPoint(
                name="Rising Action",
                description="The protagonist faces increasingly difficult obstacles related to the main conflict.",
                examples=["Rick deals with Ilsa's return", "Marlowe uncovers layers of deception", "Indiana Jones encounters rivals and obstacles"],
                features={"act": 2, "position": "beginning", "purpose": "escalate_conflict"}
            ),
            PlotPoint(
                name="Midpoint",
                description="A major event that changes the direction of the story, often with a revelation or raising of stakes.",
                examples=["Rick learns why Ilsa left him in Paris", "Marlowe discovers the true crime", "Indiana Jones discovers the Ark's location"],
                features={"act": 2, "position": "middle", "purpose": "change_direction"}
            ),
            PlotPoint(
                name="Complications and Higher Stakes",
                description="Further complications arise, raising the stakes and making the goal seem more difficult.",
                examples=["The Germans pressure Rick", "Marlowe is framed or threatened", "Indiana Jones loses the Ark to the Nazis"],
                features={"act": 2, "position": "late", "purpose": "increase_difficulty"}
            ),
            PlotPoint(
                name="Second Plot Point / End of Act II",
                description="The protagonist experiences their lowest point, leading to a new determination to resolve the conflict.",
                examples=["Rick seems to betray Ilsa to the Germans", "Marlowe is beaten or captured", "Indiana Jones is sealed in the tomb"],
                features={"act": 2, "position": "end", "purpose": "darkest_moment"}
            ),
            
            # ACT III - RESOLUTION
            PlotPoint(
                name="Climax",
                description="The final confrontation where the main conflict reaches its peak intensity.",
                examples=["Rick's plan at the airport", "Marlowe confronts the villain", "Indiana Jones faces the power of the Ark"],
                features={"act": 3, "position": "beginning", "purpose": "final_confrontation"}
            ),
            PlotPoint(
                name="Falling Action",
                description="The immediate aftermath of the climax, showing the consequences of the protagonist's actions.",
                examples=["Victor and Ilsa escape", "The case is solved", "The Ark is contained"],
                features={"act": 3, "position": "middle", "purpose": "show_consequences"}
            ),
            PlotPoint(
                name="Resolution",
                description="The story concludes, showing the new status quo and closing character arcs.",
                examples=["Rick and Louis walk into the fog", "Marlowe reflects on the case", "The Ark is stored in a warehouse"],
                features={"act": 3, "position": "end", "purpose": "establish_new_normal"}
            )
        ]
        
        return PlotStructure(
            name="Three-Act Structure",
            description="The classic dramatic structure divided into three acts: setup, confrontation, and resolution",
            plot_points=plot_points,
            narrative_arc=NarrativeArc.THREE_ACT,
            genre_affinities={
                "adventure": 0.8,
                "sci-fi": 0.8,
                "noir": 0.9
            }
        )
    
    def get_prompt_enhancement(self, agent_type: str) -> str:
        if agent_type == "researcher":
            return """
            When researching for a Three-Act Structure story, focus on:
            - Examples of successful stories in this genre using three-act structure
            - Common plot points and tropes that work well at each act transition
            - Typical conflicts and obstacles that appear in Act II for this genre
            - Effective inciting incidents that launch stories in this genre
            - Satisfying resolution patterns common to this genre
            - Pacing techniques appropriate to pulp fiction
            """
        elif agent_type == "worldbuilder":
            return """
            When building a world for a Three-Act Structure story, focus on:
            - Creating settings that naturally generate conflict
            - Designing locations that can evolve or change throughout the three acts
            - Establishing rules and limitations that will be tested in Act II
            - Building in potential for escalation of danger or stakes
            - Creating contrasting environments for different acts (safety vs. danger)
            - Designing settings that facilitate the key turning points
            """
        elif agent_type == "character_creator":
            return """
            When creating characters for a Three-Act Structure story, focus on:
            - Developing protagonists with clear wants vs. needs that drive the story
            - Creating antagonists who directly oppose the protagonist's goals
            - Designing supporting characters who can complicate Act II
            - Building in character flaws that will be tested during the story
            - Creating relationships that can evolve throughout the three acts
            - Establishing clear character motivations that justify their decisions at key plot points
            """
        elif agent_type == "plotter":
            return """
            When plotting a Three-Act Structure story, ensure you include:
            - A strong inciting incident that disrupts the status quo
            - A clear first plot point where the protagonist commits to the main conflict
            - Escalating complications throughout Act II
            - A significant midpoint that raises stakes or changes direction
            - A dark moment or low point at the end of Act II
            - A climactic confrontation that resolves the main conflict
            - A resolution that shows the new status quo
            
            Structure the story with approximately 25% for Act I, 50% for Act II, and 25% for Act III.
            Ensure that each act transition features a major turning point that propels the story forward.
            """
        elif agent_type == "writer":
            return """
            When writing a Three-Act Structure story, focus on:
            - Opening with a compelling introduction to character and setting
            - Creating a punchy inciting incident that hooks the reader
            - Maintaining increasing tension throughout Act II
            - Writing a powerful low point that tests the protagonist completely
            - Crafting a satisfying climax that pays off earlier setups
            - Delivering a resolution that ties up loose ends while staying true to pulp fiction conventions
            
            Use pacing appropriate to pulp fiction, with brisk exposition and action-focused scenes.
            Emphasize the key turning points at act transitions with dramatic writing.
            """
        elif agent_type == "editor":
            return """
            When editing a Three-Act Structure story, check for:
            - Clear act transitions marked by significant turning points
            - Proper pacing with Act I (~25%), Act II (~50%), and Act III (~25%)
            - Logical cause-and-effect relationships between plot points
            - Sufficient escalation of conflict throughout Act II
            - A compelling low point that tests the protagonist
            - A climax that resolves the central conflict
            - A satisfying conclusion that establishes a new status quo
            
            Ensure the story follows pulp fiction conventions while maintaining the structural integrity
            of the three-act format.
            """
        else:
            return ""
    
    def get_suitable_genres(self) -> Dict[str, float]:
        return {
            "adventure": 0.8,
            "sci-fi": 0.8,
            "noir": 0.9
        } 