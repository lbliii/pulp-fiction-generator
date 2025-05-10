"""
Hero's Journey plot template implementation.
"""

from typing import Dict, List, Any

from .base import PlotTemplate, PlotStructure, PlotPoint, NarrativeArc


class HeroesJourneyTemplate(PlotTemplate):
    """
    Classic Hero's Journey (Monomyth) plot structure as described by Joseph Campbell.
    
    This template provides the structure for the archetypal hero's journey,
    which appears in countless stories across cultures and time periods.
    """
    
    @property
    def name(self) -> str:
        return "hero's_journey"
    
    @property
    def description(self) -> str:
        return "The classic hero's journey (monomyth) structure where a hero ventures from the ordinary world into a region of supernatural wonder, faces trials, wins victory, and returns transformed."
    
    @property
    def narrative_arc(self) -> NarrativeArc:
        return NarrativeArc.HEROS_JOURNEY
    
    def get_plot_structure(self) -> PlotStructure:
        plot_points = [
            PlotPoint(
                name="Ordinary World",
                description="The hero is shown in their normal life, unaware of the adventures to come.",
                examples=["Luke Skywalker on Tatooine", "Frodo in the Shire", "Neo working as a programmer"],
                features={"position": "beginning", "purpose": "establish_status_quo"}
            ),
            PlotPoint(
                name="Call to Adventure",
                description="The hero receives a call to action that will require them to leave their ordinary world.",
                examples=["Luke receives Princess Leia's message", "Gandalf tells Frodo about the Ring", "Neo receives mysterious messages"],
                features={"position": "beginning", "purpose": "inciting_incident"}
            ),
            PlotPoint(
                name="Refusal of the Call",
                description="The hero initially refuses or is reluctant to heed the call to adventure.",
                examples=["Luke initially refuses to join Obi-Wan", "Frodo tries to give the Ring to Gandalf", "Neo initially walks away from Trinity"],
                features={"position": "beginning", "purpose": "show_reluctance"}
            ),
            PlotPoint(
                name="Meeting the Mentor",
                description="The hero meets a mentor figure who provides guidance, wisdom, or tools for the journey ahead.",
                examples=["Luke meets Obi-Wan", "Frodo seeks counsel from Gandalf", "Neo meets Morpheus"],
                features={"position": "beginning", "purpose": "provide_guidance"}
            ),
            PlotPoint(
                name="Crossing the Threshold",
                description="The hero leaves the ordinary world and enters the special world or adventure.",
                examples=["Luke leaves Tatooine", "Frodo leaves the Shire", "Neo takes the red pill"],
                features={"position": "beginning", "purpose": "enter_adventure"}
            ),
            PlotPoint(
                name="Tests, Allies, and Enemies",
                description="The hero faces tests, acquires allies, and confronts enemies in the special world.",
                examples=["Luke trains with the lightsaber", "Frodo meets the Fellowship", "Neo learns martial arts in the Construct"],
                features={"position": "middle", "purpose": "build_conflict"}
            ),
            PlotPoint(
                name="Approach to the Inmost Cave",
                description="The hero prepares for the major challenge ahead and may need to confront their greatest fears.",
                examples=["The Millennium Falcon approaches the Death Star", "The Fellowship enters Moria", "Neo prepares to re-enter the Matrix"],
                features={"position": "middle", "purpose": "intensify_stakes"}
            ),
            PlotPoint(
                name="Ordeal",
                description="The hero faces their greatest challenge or confronts death.",
                examples=["Luke is trapped in the trash compactor", "Frodo faces Shelob", "Neo is killed by Agent Smith"],
                features={"position": "middle", "purpose": "central_crisis"}
            ),
            PlotPoint(
                name="Reward (Seizing the Sword)",
                description="The hero survives the ordeal and obtains the reward, which could be an object, knowledge, or reconciliation.",
                examples=["Luke rescues Princess Leia", "Frodo takes possession of the Ring", "Neo realizes he is The One"],
                features={"position": "middle", "purpose": "achievement"}
            ),
            PlotPoint(
                name="The Road Back",
                description="The hero begins the journey back to the ordinary world, often pursued by vengeful forces.",
                examples=["The Millennium Falcon escapes the Death Star", "Frodo leaves the Fellowship", "Neo rushes to escape the Matrix"],
                features={"position": "end", "purpose": "begin_resolution"}
            ),
            PlotPoint(
                name="Resurrection",
                description="The hero faces a final test or challenge where everything is at stake, often requiring them to use all they've learned.",
                examples=["Luke uses the Force to destroy the Death Star", "Frodo at Mount Doom", "Neo defeats Agent Smith"],
                features={"position": "end", "purpose": "climax"}
            ),
            PlotPoint(
                name="Return with the Elixir",
                description="The hero returns to the ordinary world transformed, bringing something of value that benefits the community.",
                examples=["Luke becomes a hero of the Rebellion", "Frodo returns to the Shire", "Neo brings freedom to humanity"],
                features={"position": "end", "purpose": "resolution"}
            )
        ]
        
        return PlotStructure(
            name="Hero's Journey",
            description="The classic monomyth structure as described by Joseph Campbell",
            plot_points=plot_points,
            narrative_arc=NarrativeArc.HEROS_JOURNEY,
            genre_affinities={
                "adventure": 0.9,
                "sci-fi": 0.8,
                "noir": 0.5
            }
        )
    
    def get_prompt_enhancement(self, agent_type: str) -> str:
        if agent_type == "researcher":
            return """
            When researching for a Hero's Journey story, focus on:
            - Mythological themes and archetypes that resonate with the chosen genre
            - Example stories that follow the Hero's Journey structure in this genre
            - Symbolic objects or artifacts that could represent the "elixir" or reward
            - Types of mentors, allies, and enemies that typically appear in this genre
            - Common trials and challenges faced by heroes in this genre
            - Threshold guardians and gatekeepers between ordinary and special worlds
            """
        elif agent_type == "worldbuilder":
            return """
            When building a world for a Hero's Journey story, focus on:
            - Creating a contrast between the "ordinary world" and the "special world"
            - Designing thresholds or gateways between the different worlds
            - Establishing locations for key moments (mentor meeting, ordeal, etc.)
            - Creating environments that reflect the hero's internal state
            - Developing symbolic locations that represent rebirth or transformation
            - Building worlds that challenge the hero and reveal their character
            """
        elif agent_type == "character_creator":
            return """
            When creating characters for a Hero's Journey story, focus on:
            - Developing a protagonist with clear flaws and room for growth
            - Creating a mentor figure with wisdom and experience
            - Designing allies who complement the hero's weaknesses
            - Crafting enemies and threshold guardians who challenge the hero
            - Developing a shadow figure who represents the hero's dark side
            - Creating characters who change or reveal new aspects during the journey
            """
        elif agent_type == "plotter":
            return """
            When plotting a Hero's Journey story, ensure you include:
            - A clear ordinary world that establishes the hero's normal life
            - A compelling call to adventure that disrupts the status quo
            - An initial refusal that shows the hero's reluctance
            - A mentor meeting that provides guidance and aid
            - A threshold crossing that marks the point of no return
            - Tests and trials that build the hero's skills and confidence
            - A central ordeal that represents a symbolic death and rebirth
            - A reward that justifies the struggle
            - A road back that begins the resolution
            - A final resurrection challenge that tests everything learned
            - A return with something of value for the community
            
            Remember to adapt these elements to fit the pulp fiction style
            and genre-specific expectations.
            """
        elif agent_type == "writer":
            return """
            When writing a Hero's Journey story, focus on:
            - Establishing a sympathetic protagonist in their ordinary world
            - Creating a vivid contrast when they enter the special world
            - Building tension through increasingly difficult tests and trials
            - Making the central ordeal truly challenging and transformative
            - Showing the hero's growth through their actions and decisions
            - Writing a climactic resurrection scene that pays off the hero's journey
            - Demonstrating how the hero has changed upon their return
            
            Use the pulp fiction style appropriate to the genre while maintaining
            the emotional resonance of the hero's transformation.
            """
        elif agent_type == "editor":
            return """
            When editing a Hero's Journey story, check for:
            - Clear establishment of the ordinary world and status quo
            - A compelling call to adventure that raises stakes
            - A complete character arc showing the hero's transformation
            - Proper pacing through the stages of the journey
            - Meaningful tests and trials that build to the central ordeal
            - A satisfying climax that challenges the hero completely
            - A resolution that shows the impact of the journey
            
            Ensure the story maintains the pulp fiction style while hitting
            all the key emotional beats of the Hero's Journey.
            """
        else:
            return ""
    
    def get_suitable_genres(self) -> Dict[str, float]:
        return {
            "adventure": 0.9,
            "sci-fi": 0.8,
            "noir": 0.5
        } 