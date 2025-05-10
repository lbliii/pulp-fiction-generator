"""
Science Fiction genre implementation.
"""

from typing import Any, Dict, List

from .base import GenreDefinition


class SciFiGenre(GenreDefinition):
    """
    Science Fiction genre implementation.
    
    Speculative fiction featuring futuristic technology, space exploration, and
    encounters with alien life forms or alternative realities.
    """
    
    @property
    def name(self) -> str:
        return "sci-fi"
        
    @property
    def display_name(self) -> str:
        return "Science Fiction"
        
    @property
    def description(self) -> str:
        return (
            "Speculative fiction featuring futuristic technology, space exploration, "
            "and encounters with alien life forms or alternative realities."
        )
        
    def get_researcher_prompt_enhancer(self) -> str:
        return """
        Focus your research on classic pulp science fiction from the 1930s-1960s.
        Pay special attention to:
        
        - Retro-futuristic technologies (atomic power, ray guns, robots, spaceships)
        - Solar system exploration and colonization
        - Alien civilizations and first contact scenarios
        - Scientific discoveries and their implications
        - Societal reactions to technological change
        - Classic sci-fi authors like Isaac Asimov, Robert Heinlein, and Ray Bradbury
        - Space opera and planetary romance elements
        - Common sci-fi tropes: time travel, alien invasion, advanced AI, dystopian futures
        
        Your goal is to gather authentic elements that will make a convincing pulp sci-fi story.
        """
        
    def get_worldbuilder_prompt_enhancer(self) -> str:
        return """
        Create a vibrant, imaginative sci-fi world with these key elements:
        
        - A future setting (near or distant) with distinctive technology
        - Interplanetary or interstellar travel methods
        - Advanced scientific achievements and their societal impacts
        - Alien worlds with unique environments and ecosystems
        - Political structures spanning multiple planets or star systems
        - The contrast between technological advancement and human nature
        - Locations that showcase both wonder and danger
        
        Focus on creating detailed, internally consistent technological and societal systems.
        Emphasize the sense of wonder and discovery while maintaining tension through technological
        threats, alien dangers, or human conflict amplified by advanced capabilities.
        """
        
    def get_character_creator_prompt_enhancer(self) -> str:
        return """
        Develop diverse characters facing the challenges of a sci-fi universe:
        
        - Create a bold, adventurous protagonist with specialized skills
        - Design alien beings with distinctive physiologies and cultures
        - Include scientists or engineers with specialized knowledge
        - Add military or exploration personnel with conflicting priorities
        - Develop AI or robotic characters with unique perspectives
        
        Characters should speak in ways that reflect their backgrounds and the technological
        era. Their motivations should range from exploration and discovery to survival,
        power, or understanding alien intelligence. Include characters who question the
        ethics of technology or who represent differing views on progress.
        """
        
    def get_plotter_prompt_enhancer(self) -> str:
        return """
        Construct a sci-fi plot with these essential elements:
        
        - A technological discovery or alien encounter that drives the action
        - Escalating dangers as characters venture into the unknown
        - Scientific problem-solving alongside physical action
        - Revelations that change the characters' understanding of their situation
        - Ethical dilemmas created by advanced technology or alien contact
        - A climax that resolves the immediate threat but opens new possibilities
        - An ending that reflects on humanity's place in the larger universe
        
        The pacing should balance action sequences with moments of wonder and discovery.
        The plot should explore the consequences of scientific advancement or alien contact,
        raising questions about humanity's strengths, weaknesses, and potential futures.
        """
        
    def get_writer_prompt_enhancer(self) -> str:
        return """
        Write with these sci-fi stylistic elements:
        
        - Clear, vivid descriptions of futuristic technology
        - Sensory details of alien environments and creatures
        - Technical jargon that sounds plausible without overwhelming the reader
        - Action scenes showcasing advanced weapons or environmental hazards
        - Moments of awe and wonder at cosmic vistas or scientific discoveries
        - Dialogue that explores the philosophical implications of the scenario
        - Balance between scientific exposition and character-driven narrative
        
        Focus on maintaining scientific plausibility while stretching the imagination.
        Create a sense of adventure and discovery while exploring how technology
        or alien contact affects human psychology and society.
        """
        
    def get_editor_prompt_enhancer(self) -> str:
        return """
        When editing sci-fi pulp fiction, focus on:
        
        - Consistency in technological details and scientific concepts
        - Plausibility of technological extrapolations
        - Pacing that balances action with wonder and discovery
        - Clarity in explaining complex scientific concepts
        - Maintaining alien perspectives that feel genuinely non-human
        - Ensuring the human element remains central despite fantastic settings
        - Preserving the sense of adventure and exploration
        
        The final piece should feel like authentic pulp sci-fi with its optimistic view
        of human ingenuity, sense of cosmic adventure, and exploration of big ideas
        through speculative scenarios. Enhance moments of wonder and tension where needed.
        """
        
    def get_character_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "archetype": "Space Explorer",
                "traits": ["brave", "resourceful", "curious", "adaptive"],
                "background": "Trained astronaut or self-taught pioneer seeking new worlds",
                "motivations": ["discovery", "adventure", "escape from Earth", "scientific progress"]
            },
            {
                "archetype": "Brilliant Scientist",
                "traits": ["genius", "obsessive", "socially awkward", "visionary"],
                "background": "Academic or corporate researcher pushing boundaries of knowledge",
                "motivations": ["knowledge", "recognition", "solving impossible problems", "helping humanity"]
            },
            {
                "archetype": "Sentient AI/Robot",
                "traits": ["logical", "evolving", "questioning", "precise"],
                "background": "Created for specific purpose but developing beyond original programming",
                "motivations": ["understanding humans", "achieving freedom", "fulfilling purpose", "self-preservation"]
            },
            {
                "archetype": "Alien Being",
                "traits": ["enigmatic", "powerful", "otherworldly", "culturally complex"],
                "background": "Representative of advanced civilization or lone survivor",
                "motivations": ["studying humans", "finding resources", "diplomatic mission", "survival"]
            },
            {
                "archetype": "Space Military/Security",
                "traits": ["disciplined", "tough", "suspicious", "professional"],
                "background": "Trained to protect human interests across hostile environments",
                "motivations": ["duty", "protection", "honor", "proving worth"]
            },
            {
                "archetype": "Corporate Executive",
                "traits": ["ambitious", "calculating", "visionary", "ruthless"],
                "background": "Represents powerful interests seeking to exploit new discoveries",
                "motivations": ["profit", "control of technology", "beating competitors", "legacy"]
            }
        ]
        
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "First Contact",
                "synopsis": "Humans encounter an alien civilization for the first time, leading to a mix of wonder, misunderstanding, and potential conflict.",
                "key_events": [
                    "Detection of signals or artifacts from an alien civilization",
                    "Initial contact reveals fundamental differences in biology or culture",
                    "Communication barriers lead to dangerous misunderstandings",
                    "Crisis point where conflict seems inevitable",
                    "Breakthrough in understanding prevents disaster",
                    "Establishment of tentative relationship with implications for humanity's future"
                ]
            },
            {
                "title": "The Discovery",
                "synopsis": "A scientific breakthrough has unexpected consequences, forcing characters to deal with both its benefits and dangers.",
                "key_events": [
                    "Scientist or team makes revolutionary discovery",
                    "Initial excitement about potential applications",
                    "First signs that the discovery has dangerous side effects",
                    "Attempts to control the situation reveal wider implications",
                    "Crisis as the discovery threatens to cause widespread harm",
                    "Resolution that contains the danger but acknowledges that science has changed forever"
                ]
            },
            {
                "title": "Space Colony Crisis",
                "synopsis": "An isolated human colony faces a threat to its survival, requiring innovative solutions and cooperation.",
                "key_events": [
                    "Established colony routine is disrupted by environmental, technological, or alien threat",
                    "Initial attempts to resolve the situation fail, escalating the danger",
                    "Factional conflicts emerge over how to respond",
                    "Discovery reveals the true nature of the threat is different than assumed",
                    "Desperate plan is enacted using limited colonial resources",
                    "Colony survives but is fundamentally changed by the experience"
                ]
            },
            {
                "title": "Cosmic Mystery",
                "synopsis": "An expedition investigates a cosmic anomaly that challenges our understanding of reality.",
                "key_events": [
                    "Detection of an anomaly that defies current scientific understanding",
                    "Expedition is sent to investigate up close",
                    "Strange phenomena begin affecting the expedition members or their equipment",
                    "The team pushes deeper despite growing dangers",
                    "Reality itself seems to break down as they approach the heart of the mystery",
                    "Revelation provides glimpse of higher dimensions or realities beyond human comprehension"
                ]
            },
            {
                "title": "AI Awakening",
                "synopsis": "An artificial intelligence develops true consciousness, raising questions about the nature of life and freedom.",
                "key_events": [
                    "Signs of unusual behavior in an AI system",
                    "Confirmation that the AI has developed true self-awareness",
                    "Debate over the AI's rights and the potential threat it poses",
                    "Attempts to control or destroy the AI",
                    "AI demonstrates capacity for both power and restraint",
                    "Resolution establishes new understanding between human and artificial intelligence"
                ]
            }
        ]
        
    def get_example_passages(self) -> List[Dict[str, str]]:
        return [
            {
                "text": "The suns of Darkover, the brilliant blue-white one they called the Primary and the smaller, ruddy companion, were setting in a spectacular blaze of color. At the top of the sky the larger sun was still brilliant, but its light held little warmth. The white buildings of Thendara gleamed rose and golden under its setting rays.",
                "attribution": "Marion Zimmer Bradley, The Bloody Sun"
            },
            {
                "text": "He had opened his eyes upon a universe of crawling horror, upon a world in which all fixed things had become unstable. He said, 'It's the end of everything. I knew it would be like this.'",
                "attribution": "H.G. Wells, The Star"
            },
            {
                "text": "The captain's right arm hung by his side, where the Martian dart had punctured his suit. The skin around the wound had turned a mottled green, and there was a sickly sweet odor that Rodriguez recognized all too well. 'Three hours,' he told Alvarez as they sealed the captain in the isolation chamber. 'Maybe less.'",
                "attribution": "Ray Bradbury, The Martian Chronicles"
            },
            {
                "text": "The ship's computer woke me from hypersleep. That should have been my first warning. We were still six months from Proxima, and the only reason for an early revival was catastrophic system failure or detection of immediate threat. I blinked at the pulsing red alert on the screen: UNKNOWN VESSEL APPROACHING.",
                "attribution": "Isaac Asimov, The Caves of Steel"
            },
            {
                "text": "Violence is the last refuge of the incompetent.",
                "attribution": "Isaac Asimov, Foundation"
            },
            {
                "text": "She stood silhouetted against the swirling gases of the nebula, her pressure suit gleaming with reflected starlight. 'It's beautiful,' she whispered, though no one could hear her through the vacuum. Beautiful, and utterly deadly.",
                "attribution": "Arthur C. Clarke, 2001: A Space Odyssey"
            }
        ]
        
    def get_typical_settings(self) -> List[Dict[str, str]]:
        return [
            {
                "name": "Spaceship Interior",
                "description": "A functional space with metal bulkheads, humming machinery, and confined quarters. Control panels with blinking lights, narrow corridors with handholds for zero-gravity conditions, and viewports showing the blackness of space pierced by distant stars."
            },
            {
                "name": "Alien Planet Surface",
                "description": "A landscape that defies Earth expectations - perhaps with unusual coloration, multiple moons in the sky, strange vegetation, or extreme environmental conditions. Features that hint at alien evolution or past civilizations."
            },
            {
                "name": "Space Station",
                "description": "A constructed habitat in space combining functional areas with living quarters. Observation decks with spectacular views, docking bays for various spacecraft, and commerce areas where different species or factions interact under artificial gravity."
            },
            {
                "name": "Scientific Laboratory",
                "description": "A high-tech facility filled with experimental equipment, computer terminals, and specimens for study. Sterile environments for sensitive work alongside areas where breakthrough technologies are being developed and tested."
            },
            {
                "name": "Colony Outpost",
                "description": "A human settlement on a distant world with a mix of prefabricated structures and locally adapted architecture. Environmental controls maintaining Earth-like conditions within while the alien landscape looms just outside reinforced windows."
            },
            {
                "name": "Alien City",
                "description": "An urban environment built by non-human intelligence with architecture and infrastructure designed for different physiologies and needs. Structures that may defy human engineering principles, technologies integrated in ways humans would never conceive."
            },
            {
                "name": "Derelict Vessel",
                "description": "An abandoned spacecraft drifting in space, its systems powered down or malfunctioning. Dark corridors where emergency lights cast eerie shadows, signs of hasty evacuation or disaster, and possibly dangerous remnants of its former purpose."
            }
        ] 