"""
Save the Cat plot template implementation.

Based on Blake Snyder's screenwriting guide "Save the Cat," this template
provides a specific beat sheet approach to story structure.
"""

from typing import Dict, List, Any

from .base import PlotTemplate, PlotStructure, PlotPoint, NarrativeArc


class SaveTheCatTemplate(PlotTemplate):
    """
    Save the Cat beat sheet structure based on Blake Snyder's screenwriting guide.
    
    This template provides a more detailed version of the three-act structure with
    specific "beats" that occur at particular points in the story.
    """
    
    @property
    def name(self) -> str:
        return "save_the_cat"
    
    @property
    def description(self) -> str:
        return "The 'Save the Cat' beat sheet structure popularized by Blake Snyder, featuring 15 key story beats that occur at specific points in the narrative."
    
    @property
    def narrative_arc(self) -> NarrativeArc:
        return NarrativeArc.SAVE_THE_CAT
    
    def get_plot_structure(self) -> PlotStructure:
        plot_points = [
            # ACT I
            PlotPoint(
                name="Opening Image",
                description="A snapshot of the protagonist's world before the adventure begins, establishing mood, tone, and stakes.",
                examples=["The empty streets of L.A. in Chinatown", "A murder scene in a noir detective story", "A gritty urban landscape"],
                features={"page": "1-2", "position": "beginning", "purpose": "establish_tone"}
            ),
            PlotPoint(
                name="Theme Stated",
                description="Someone (not the protagonist) states the theme or lesson the protagonist will learn.",
                examples=["'Forget it Jake, it's Chinatown'", "A warning about greed", "A piece of advice the hero ignores"],
                features={"page": "5", "position": "beginning", "purpose": "setup_theme"}
            ),
            PlotPoint(
                name="Setup",
                description="Introduce all main characters and their flaws, establish the status quo that will change.",
                examples=["Detective's daily routine", "The protagonist's unfulfilling life", "The corrupt world the hero inhabits"],
                features={"page": "1-10", "position": "beginning", "purpose": "introduce_world"}
            ),
            PlotPoint(
                name="Catalyst",
                description="A life-changing event that knocks down the old status quo and sets the story in motion.",
                examples=["A client with a mysterious case", "A murder that seems routine but isn't", "A job offer that's too good to be true"],
                features={"page": "12", "position": "early", "purpose": "inciting_incident"}
            ),
            PlotPoint(
                name="Debate",
                description="The protagonist questions whether to take the journey, weighing the pros and cons.",
                examples=["The detective considers turning down the case", "The hero weighs the risks", "Internal struggle about getting involved"],
                features={"page": "12-25", "position": "early", "purpose": "show_reluctance"}
            ),
            PlotPoint(
                name="Break into Two",
                description="The protagonist makes a choice and fully enters the adventure, leaving the old world behind.",
                examples=["Taking the case", "Agreeing to the dangerous mission", "Crossing a threshold into a new situation"],
                features={"page": "25", "position": "end_act_one", "purpose": "point_of_no_return"}
            ),
            
            # ACT II-A
            PlotPoint(
                name="B Story",
                description="Introduction of a secondary story, often involving a new relationship or love interest.",
                examples=["Meeting a femme fatale", "Encountering a helpful ally", "A relationship that complicates the main plot"],
                features={"page": "30", "position": "early_act_two", "purpose": "introduce_subplot"}
            ),
            PlotPoint(
                name="Fun and Games",
                description="The 'promise of the premise' where the concept is explored, often containing the trailer moments.",
                examples=["Detective work montage", "Navigating the criminal underworld", "Using skills to investigate"],
                features={"page": "30-55", "position": "early_act_two", "purpose": "explore_concept"}
            ),
            PlotPoint(
                name="Midpoint",
                description="A false peak or false collapse. Either things seem to go well or fall apart completely.",
                examples=["A major clue discovered", "A betrayal revealed", "A false victory that won't last"],
                features={"page": "55", "position": "middle", "purpose": "raise_stakes"}
            ),
            
            # ACT II-B
            PlotPoint(
                name="Bad Guys Close In",
                description="External and internal forces align against the protagonist, applying pressure and forcing mistakes.",
                examples=["Threats from powerful enemies", "Self-doubt creeping in", "Allies turning against the hero"],
                features={"page": "55-75", "position": "late_act_two", "purpose": "increase_obstacles"}
            ),
            PlotPoint(
                name="All Is Lost",
                description="The opposite of the Midpoint. If Midpoint was positive, this is negative and vice versa.",
                examples=["A crucial witness is killed", "Evidence is destroyed", "The hero is framed or defeated"],
                features={"page": "75", "position": "late_act_two", "purpose": "major_setback"}
            ),
            PlotPoint(
                name="Dark Night of the Soul",
                description="The protagonist's darkest moment, where all seems lost and they must dig deep to find the strength to continue.",
                examples=["Questioning whether to continue", "Hitting rock bottom", "Feeling utterly defeated"],
                features={"page": "75-85", "position": "late_act_two", "purpose": "lowest_point"}
            ),
            PlotPoint(
                name="Break into Three",
                description="The protagonist finds a new solution or inspiration, leading to Act Three and the resolution.",
                examples=["A realization about the case", "A new angle to investigate", "Finding the courage to continue"],
                features={"page": "85", "position": "end_act_two", "purpose": "find_solution"}
            ),
            
            # ACT III
            PlotPoint(
                name="Finale",
                description="The protagonist proves they've learned the theme lesson by applying new skills to defeat the bad guys.",
                examples=["Confronting the mastermind", "The climactic shootout", "Exposing the conspiracy"],
                features={"page": "85-110", "position": "act_three", "purpose": "resolution"}
            ),
            PlotPoint(
                name="Final Image",
                description="The opposite of the opening image, showing how much the world and character have changed.",
                examples=["A transformed city landscape", "The detective with a new outlook", "Visual symbol of change"],
                features={"page": "110", "position": "end", "purpose": "show_transformation"}
            )
        ]
        
        return PlotStructure(
            name="Save the Cat Beat Sheet",
            description="A 15-beat structure for storytelling based on Blake Snyder's screenwriting guide",
            plot_points=plot_points,
            narrative_arc=NarrativeArc.SAVE_THE_CAT,
            genre_affinities={
                "adventure": 0.7,
                "sci-fi": 0.7,
                "noir": 0.9
            }
        )
    
    def get_prompt_enhancement(self, agent_type: str) -> str:
        if agent_type == "researcher":
            return """
            When researching for a Save the Cat structure story, focus on:
            - Examples of noir or pulp fiction stories that follow similar beat patterns
            - Typical catalysts that set the story in motion for this genre
            - Common themes that are stated early but realized late in similar stories
            - The kinds of "Fun and Games" sequences that work well in this genre
            - Effective "Dark Night of the Soul" moments from classic stories
            - Visual contrasts that could work for opening and closing images
            """
        elif agent_type == "worldbuilder":
            return """
            When building a world for a Save the Cat structure story, focus on:
            - Creating settings that can be visually contrasted between opening and final images
            - Designing locations that naturally provide "Fun and Games" opportunities
            - Establishing environments that can darken or become more dangerous as the story progresses
            - Building in social or physical barriers that represent the protagonist's reluctance during the Debate
            - Creating thematically resonant settings for the Dark Night of the Soul
            - Designing visually striking locations for key beats, especially the Catalyst and Break into Three
            """
        elif agent_type == "character_creator":
            return """
            When creating characters for a Save the Cat structure story, focus on:
            - Developing a protagonist with clear flaws that will be addressed by the theme
            - Creating secondary characters who can state the theme without being obvious
            - Designing love interests or allies that embody the B Story values
            - Building villains who represent the antithesis of the theme
            - Creating characters whose transformations can be visually represented
            - Establishing character weaknesses that will be tested during the Dark Night of the Soul
            - Developing character relationships that can evolve from opening to final image
            """
        elif agent_type == "plotter":
            return """
            When plotting a Save the Cat structure story, ensure you include:
            - A visually striking opening image that establishes tone
            - A clear theme statement early in the story
            - A catalyst around the 10-15% mark that disrupts the status quo
            - A period of debate where the protagonist resists the call
            - A definitive break into act two around the 25% mark
            - Introduction of a B Story (often a relationship) early in act two
            - Fun and Games section that delivers the "promise of the premise"
            - A significant midpoint that raises stakes or changes direction
            - Increasing pressure from antagonistic forces after the midpoint
            - A clear "All Is Lost" moment around the 75% mark
            - A Dark Night of the Soul where the protagonist faces their deepest fears
            - A breakthrough moment leading to act three
            - A finale that shows the protagonist has learned and changed
            - A final image that contrasts with the opening
            
            Adapt these beats to the pulp fiction style while maintaining their structural function.
            """
        elif agent_type == "writer":
            return """
            When writing a Save the Cat structure story, focus on:
            - Creating a vivid contrast between opening and final images
            - Subtly weaving the theme throughout the narrative
            - Writing a punchy, unexpected catalyst that hooks the reader
            - Making the debate feel genuine without slowing the pace
            - Ensuring the "Fun and Games" section delivers on genre expectations
            - Creating a powerful midpoint that genuinely changes the story direction
            - Building tension consistently after the midpoint
            - Writing a devastating "All Is Lost" moment
            - Making the Dark Night of the Soul emotionally resonant
            - Ensuring the finale demonstrates the protagonist's growth
            
            Use the punchy, direct style of pulp fiction while hitting these key emotional beats.
            """
        elif agent_type == "editor":
            return """
            When editing a Save the Cat structure story, check for:
            - Clear placement of all 15 beats at appropriate points in the narrative
            - Thematic consistency throughout the story
            - Proper pacing that doesn't rush or drag any beat
            - A genuinely transformative character arc
            - Strong contrast between opening and final images
            - Emotional impact of the Dark Night of the Soul
            - Satisfying resolution that shows the character has changed
            - Coherent B Story that enhances rather than distracts from the main plot
            
            Ensure the story maintains pulp fiction's directness and energy while
            hitting all the structural beats effectively.
            """
        else:
            return ""
    
    def get_suitable_genres(self) -> Dict[str, float]:
        return {
            "adventure": 0.7,
            "sci-fi": 0.7,
            "noir": 0.9
        } 