"""
Noir/Hardboiled Detective genre implementation.
"""

from typing import Any, Dict, List

from .base import GenreDefinition


class NoirGenre(GenreDefinition):
    """
    Noir/Hardboiled detective genre implementation.
    
    Gritty crime fiction featuring tough, cynical characters in urban settings,
    often with moral ambiguity and pessimistic themes.
    """
    
    @property
    def name(self) -> str:
        return "noir"
        
    @property
    def display_name(self) -> str:
        return "Noir/Hardboiled Detective"
        
    @property
    def description(self) -> str:
        return (
            "Gritty crime fiction featuring tough, cynical characters in urban settings, "
            "often with moral ambiguity and pessimistic themes."
        )
        
    def get_researcher_prompt_enhancer(self) -> str:
        return """
        Focus your research on hardboiled detective and noir fiction from the 1930s-1950s.
        Pay special attention to:
        
        - Urban settings (particularly cities like Los Angeles, New York, Chicago)
        - Crime investigation techniques of the era
        - Organized crime operations and structures
        - Period-appropriate language, slang, and dialogue
        - Social issues like corruption, class tension, and post-war disillusionment
        - Classic noir authors like Raymond Chandler, Dashiell Hammett, and James M. Cain
        - Film noir influences and visual elements
        - Common noir tropes: femme fatales, corrupt officials, flawed protagonists
        
        Your goal is to gather authentic elements that will make a convincing noir story.
        """
        
    def get_worldbuilder_prompt_enhancer(self) -> str:
        return """
        Create a shadowy, atmospheric noir world with these key elements:
        
        - A rain-soaked, neon-lit urban environment
        - Dimly lit streets, smoky bars, and seedy hotels
        - A pervasive sense of corruption and moral decay
        - Clear class divisions and social tensions
        - A time period typically between the 1930s and 1950s
        - Weather that reflects the mood (fog, rain, darkness)
        - Locations that evoke a sense of claustrophobia and paranoia
        
        Focus on creating vivid, sensory descriptions that capture the gritty atmosphere.
        Emphasize shadows, contrasts, and morally ambiguous spaces where characters 
        navigate the thin line between law and criminality.
        """
        
    def get_character_creator_prompt_enhancer(self) -> str:
        return """
        Develop morally complex, flawed characters typical of noir fiction:
        
        - Create a cynical, world-weary protagonist with a troubled past
        - Design a femme fatale or homme fatal with hidden motives
        - Include corrupt authority figures (police, politicians, judges)
        - Add criminal elements with their own codes of honor
        - Develop characters who blur the line between good and evil
        
        Characters should speak in terse, hardboiled dialogue with period-appropriate 
        slang. Their motivations should be complex and often contradictory, driven by 
        desperation, greed, lust, revenge, or a misguided sense of justice.
        """
        
    def get_plotter_prompt_enhancer(self) -> str:
        return """
        Construct a noir plot with these essential elements:
        
        - A central crime or mystery that pulls the protagonist in
        - A labyrinthine investigation revealing deeper corruption
        - Red herrings and false leads
        - Double-crosses and betrayals
        - A moral dilemma forcing the protagonist to make difficult choices
        - A climax that resolves the central mystery but at a personal cost
        - An ambiguous or bittersweet ending that questions moral certainties
        
        The pacing should alternate between tense action and reflective moments.
        The plot should gradually reveal layers of corruption and deception,
        with each revelation making the protagonist's situation more complex.
        """
        
    def get_writer_prompt_enhancer(self) -> str:
        return """
        Write with these noir stylistic elements:
        
        - First-person narration with a cynical, world-weary voice
        - Terse, clipped dialogue with period-appropriate slang
        - Vivid, sensory descriptions of urban decay
        - Creative similes and metaphors (like Chandler's "She was a blonde to make a bishop kick a hole in a stained-glass window")
        - Morally ambiguous scenarios with no clear right answers
        - Atmospheric descriptions emphasizing shadows, light contrasts, and weather
        - Moments of philosophical reflection about human nature and society
        
        Balance action scenes with character development. Use setting as characterization.
        Maintain a pessimistic undercurrent while avoiding melodrama.
        """
        
    def get_editor_prompt_enhancer(self) -> str:
        return """
        When editing noir fiction, focus on:
        
        - Consistency in the cynical, hardboiled tone
        - Authentic period details and language
        - Maintaining moral ambiguity throughout
        - Ensuring dialogue sounds natural but stylized
        - Preserving the atmospheric descriptions of urban settings
        - Checking that the plot maintains mystery while remaining coherent
        - Verifying that characters remain true to their flawed natures
        
        The final piece should feel like authentic noir fiction with its fatalistic 
        outlook, stylized prose, and morally complex characters. Enhance moments where 
        the tone falters or where modern sensibilities have leaked into the period setting.
        """
        
    def get_character_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "archetype": "Detective",
                "traits": ["cynical", "determined", "flawed", "intelligent"],
                "background": "Former police officer or military, now working solo",
                "motivations": ["justice", "redemption", "obsession"]
            },
            {
                "archetype": "Femme Fatale",
                "traits": ["seductive", "mysterious", "ambitious", "ruthless"],
                "background": "Troubled past, using charm to survive in a man's world",
                "motivations": ["escape", "wealth", "power", "revenge"]
            },
            {
                "archetype": "Corrupt Official",
                "traits": ["powerful", "greedy", "manipulative", "connected"],
                "background": "Rose through ranks by compromise and blackmail",
                "motivations": ["maintaining power", "greed", "covering past crimes"]
            },
            {
                "archetype": "Crime Boss",
                "traits": ["calculating", "ruthless", "charismatic", "paranoid"],
                "background": "Built empire from nothing through violence and cunning",
                "motivations": ["control", "respect", "expansion", "family legacy"]
            },
            {
                "archetype": "Beaten-down Victim",
                "traits": ["desperate", "scared", "secretive", "ordinary"],
                "background": "Normal life destroyed by contact with the underworld",
                "motivations": ["survival", "escape", "protection of loved ones"]
            }
        ]
        
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "The Frame-Up",
                "synopsis": "The protagonist is framed for a murder they didn't commit and must find the real killer while evading the police.",
                "key_events": [
                    "Protagonist discovers a dead body and becomes the prime suspect",
                    "Evidence is planted to ensure their conviction",
                    "Protagonist goes on the run while investigating",
                    "Discovery that the frame-up is connected to a larger conspiracy",
                    "Confrontation with the true killer reveals unexpected connections",
                    "Bittersweet resolution where truth comes at a heavy cost"
                ]
            },
            {
                "title": "The Missing Person",
                "synopsis": "A seemingly routine missing person case leads the detective into a web of corruption and danger.",
                "key_events": [
                    "Detective is hired to find a missing person by a client who's not telling the whole truth",
                    "Initial investigation reveals the missing person was involved in something dangerous",
                    "Detective uncovers connections to powerful people in the city",
                    "The case becomes personal as threats are made against the detective",
                    "Missing person is found dead or in hiding with crucial information",
                    "Final confrontation exposes corruption at the highest levels"
                ]
            },
            {
                "title": "The Betrayal",
                "synopsis": "A complex tale of loyalty and betrayal as the protagonist discovers their trusted ally is working against them.",
                "key_events": [
                    "Protagonist and ally work together on a dangerous case",
                    "Strange inconsistencies begin to appear in the ally's behavior",
                    "Protagonist discovers evidence of betrayal but holds onto hope",
                    "Confrontation forces the ally to reveal their true motives",
                    "Protagonist must make a moral choice about how to handle the betrayal",
                    "Resolution leaves relationships permanently altered"
                ]
            },
            {
                "title": "The Heist Gone Wrong",
                "synopsis": "A carefully planned heist spirals into chaos, leaving the survivors to deal with the consequences.",
                "key_events": [
                    "Assembly of a crew with specialized skills but conflicting personalities",
                    "Detailed planning of the seemingly perfect heist",
                    "The job goes catastrophically wrong due to betrayal or bad information",
                    "Aftermath leaves survivors on the run and turning on each other",
                    "Hidden aspects of the job are gradually revealed",
                    "Final confrontation resolves immediate danger but at great cost"
                ]
            }
        ]
        
    def get_example_passages(self) -> List[Dict[str, str]]:
        return [
            {
                "text": "I was wearing my powder-blue suit, with dark blue shirt, tie and display handkerchief, black brogues, black wool socks with dark blue clocks on them. I was neat, clean, shaved and sober, and I didn't care who knew it. I was everything the well-dressed private detective ought to be. I was calling on four million dollars.",
                "attribution": "Raymond Chandler, The Big Sleep"
            },
            {
                "text": "She gave me a smile I could feel in my hip pocket.",
                "attribution": "Raymond Chandler, Farewell, My Lovely"
            },
            {
                "text": "He looked about as inconspicuous as a tarantula on a slice of angel food.",
                "attribution": "Raymond Chandler, Farewell, My Lovely"
            },
            {
                "text": "I pushed her away. She came back like a rubber ball and made a grab for my hair with both hands. I ducked and reached for her arm and she slashed at me with something bright and sharp. I didn't see what it was. I just saw the flash of it going past my face. She was a little wildcat all right.",
                "attribution": "Raymond Chandler, The Lady in the Lake"
            },
            {
                "text": "Dead men are heavier than broken hearts.",
                "attribution": "Raymond Chandler, The Big Sleep"
            },
            {
                "text": "The muzzle of the Luger looked like the mouth of the Second Street tunnel.",
                "attribution": "Raymond Chandler, The Big Sleep"
            }
        ]
        
    def get_typical_settings(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "Detective's Office",
                "description": "A small, dusty office with venetian blinds casting striped shadows across the room. A desk with a bottle in the bottom drawer, a filing cabinet with more unpaid bills than cases, and a frosted glass door with the detective's name painted in flaking gold letters."
            },
            {
                "name": "Rain-Soaked Streets",
                "description": "Wet pavement reflecting neon signs, raindrops glistening on the brim of a fedora. Street lamps creating pools of dim light in the darkness, while rain drums steadily on the roofs of parked cars."
            },
            {
                "name": "Smoky Jazz Club",
                "description": "A basement club filled with cigarette smoke and the melancholy sounds of a saxophone. Dark corners where conversations can't be overheard, a long bar where lonely men nurse whiskeys, and a small stage where a singer with sad eyes performs for the half-empty room."
            },
            {
                "name": "Upscale Mansion",
                "description": "A luxurious home in the hills, showcasing wealth that may not have been earned honestly. Marble floors, expensive artwork, and well-dressed servants who see everything and say nothing. Crystal decanters of fine liquor and hidden rooms for private conversations."
            },
            {
                "name": "Police Precinct",
                "description": "A bustling, fluorescent-lit room full of ringing phones and the clack of typewriters. Overworked cops at cluttered desks, holding cells in the back, and interrogation rooms where the truth is optional. The air thick with cigarette smoke, coffee, and cynicism."
            },
            {
                "name": "Seedy Hotel",
                "description": "A run-down establishment where rooms can be rented by the hour. Peeling wallpaper, flickering lights, and a night clerk who doesn't ask questions or remember faces. Thin walls that don't hide arguments or gunshots well enough."
            }
        ] 