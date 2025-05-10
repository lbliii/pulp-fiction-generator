from typing import Dict, List, Any, Optional
from .base import GenreDefinition


class AdventureGenre(GenreDefinition):
    @property
    def name(self) -> str:
        return "adventure"

    @property
    def display_name(self) -> str:
        return "Adventure"

    def get_researcher_prompt_enhancer(self) -> str:
        return """
        As a researcher for adventure pulp fiction, focus on the following elements:
        
        - Exotic locations: jungles, remote islands, ancient ruins, desert oases, mountain peaks
        - Historical periods: 1920s-1950s for classic adventure, ancient civilizations, Age of Exploration
        - Lost treasures: ancient artifacts, legendary jewels, forgotten technologies
        - Natural obstacles: treacherous rivers, deadly animals, harsh climates, dense forests
        - Human adversaries: rival explorers, crime syndicates, pirates, cultists, corrupt officials
        - Indigenous cultures: their customs, beliefs, and relationship with outsiders
        - Mythological elements: legends that may have a basis in reality
        - Transportation methods: steamships, early airplanes, jeeps, riverboats, camels
        - Survival techniques appropriate to the setting
        - Historical events that could provide backdrop (wars, archaeological discoveries)
        
        Focus on creating a rich, immersive world filled with danger, mystery, and the promise of discovery.
        Emphasize the authenticity of the period and setting, while maintaining the sense of wonder and excitement.
        """

    def get_worldbuilder_prompt_enhancer(self) -> str:
        return """
        As a world builder for adventure pulp fiction, focus on creating:
        
        - Vividly detailed exotic locations: ancient temples covered in vines, bustling foreign ports, mysterious caves, treacherous mountain passes
        - Rich sensory details: the humid air of the jungle, the blinding sand of the desert, the salty spray of the ocean
        - Geography that creates natural challenges: raging rivers, steep cliffs, unstable ruins
        - Weather conditions that influence the story: monsoons, sandstorms, fog, intense heat
        - Hidden dangers: quicksand, poisonous plants, disease, predatory animals
        - Secret passages, hidden chambers, and unexpected discoveries
        - Contrast between civilization and wilderness
        - Maps and navigational challenges
        - Local populations with distinct cultures, traditions, and relationships with outsiders
        - Historical context that influences the setting: colonial presence, recent conflicts, archaeological expeditions
        
        Create a world that feels authentic yet exotic, dangerous yet irresistibly enticing to explorers and adventure seekers.
        Balance realism with the larger-than-life quality of pulp adventure.
        """

    def get_character_creator_prompt_enhancer(self) -> str:
        return """
        As a character creator for adventure pulp fiction, focus on:
        
        - Protagonists with specialized skills: archaeologists, explorers, pilots, big game hunters, soldiers of fortune, guides
        - Motivations: pursuit of knowledge, fame, fortune, redemption, family legacy
        - Distinctive physical traits that hint at past adventures: scars, tanned skin, weather-beaten faces
        - Equipment and clothing appropriate to the setting and period
        - Sidekicks with complementary skills: translators, mechanics, scholars, local guides
        - Rivals who mirror the protagonist but with darker motivations
        - Indigenous characters with deep knowledge of the environment
        - Villains with complex motivations: collectors willing to kill for artifacts, power-hungry leaders, zealots
        - Character backgrounds that tie them to the setting or quest
        - Personality traits that both help and hinder: curiosity, stubbornness, overconfidence
        
        Create characters that embody the spirit of adventure - resourceful, determined, and willing to risk everything for discovery.
        Balance larger-than-life heroism with human flaws and limitations.
        """

    def get_plotter_prompt_enhancer(self) -> str:
        return """
        As a plotter for adventure pulp fiction, focus on:
        
        - Inciting incidents that thrust the protagonist into adventure: mysterious maps, urgent telegrams, chance discoveries
        - Quest structures with clear objectives: find the lost city, recover the stolen artifact, rescue the kidnapped explorer
        - Escalating dangers and obstacles that test the protagonist's abilities
        - Red herrings and false leads that add complexity to the journey
        - Betrayals and shifting alliances among expedition members
        - Ticking clock elements: monsoon season approaching, rival expedition gaining ground, ancient curse taking effect
        - Discoveries that change the nature of the quest: what seemed to be a simple treasure hunt reveals larger stakes
        - Indigenous encounters that either help or hinder the protagonist
        - Ancient traps and puzzles that must be solved
        - Climactic confrontations in dramatic locations: temple inner sanctums, volcano rims, crumbling bridges
        - Narrow escapes and last-minute rescues
        
        Create plots that maintain a breathless pace while building to an exciting climax.
        Balance action sequences with moments of discovery and wonder.
        """

    def get_writer_prompt_enhancer(self) -> str:
        return """
        As a writer for adventure pulp fiction, focus on:
        
        - Vivid action sequences with concrete, sensory details
        - Moments of awe and discovery described through the protagonist's perspective
        - Quick, punchy dialogue that reveals character and advances the plot
        - Cultural encounters portrayed with respect while maintaining period authenticity
        - Cliffhangers that end chapters and maintain tension
        - Varying sentence rhythm: short, staccato sentences for action; longer, descriptive passages for setting
        - Weather and environment as active forces that impact characters
        - First-person or close third-person perspective that puts readers in the moment
        - Period-appropriate language and terminology
        - Balance between descriptive passages and fast-moving action
        
        Craft prose that transports readers to exotic locales and immerses them in pulse-pounding adventure.
        Emphasize the physicality of the adventure - the strain, pain, and triumph of overcoming obstacles.
        """

    def get_editor_prompt_enhancer(self) -> str:
        return """
        As an editor for adventure pulp fiction, ensure:
        
        - The pace never drags; cut excessive description during action sequences
        - Every scene contributes to the adventure or character development
        - The stakes remain clear and escalate appropriately
        - The protagonist faces genuine peril and overcomes obstacles through skill, knowledge, and determination
        - Cultural portrayals, while reflecting the pulp adventure genre, avoid the most problematic stereotypes
        - Historical and geographical details feel authentic but don't overwhelm the narrative
        - Action sequences are coherent and physically plausible
        - The sense of discovery and wonder remains present throughout
        - The resolution feels earned but might leave room for future adventures
        - The story delivers on the promise of exotic adventure and satisfying discovery
        
        Refine the work to deliver the breathless pace, vivid settings, and thrilling action that adventure readers expect.
        Maintain the delicate balance between authenticity and the larger-than-life quality of pulp adventure.
        """

    def get_character_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "archetype": "The Adventurous Professor",
                "description": "An academic whose knowledge is matched only by their thirst for discovery. Equally at home in ivy-covered halls and unexplored ruins.",
                "traits": ["knowledgeable", "curious", "stubborn", "resourceful"],
                "examples": ["Indiana Jones", "Professor Challenger"]
            },
            {
                "archetype": "The Rugged Explorer",
                "description": "A seasoned adventurer who has navigated the world's most dangerous places. Values experience over book learning.",
                "traits": ["tough", "pragmatic", "independent", "cynical"],
                "examples": ["Allan Quatermain", "Rick O'Connell"]
            },
            {
                "archetype": "The Aristocratic Thrill-Seeker",
                "description": "A wealthy individual seeking escape from society's constraints through adventure. Uses money and connections to mount expeditions.",
                "traits": ["privileged", "daring", "charismatic", "arrogant"],
                "examples": ["Lord John Roxton", "Lara Croft"]
            },
            {
                "archetype": "The Local Guide",
                "description": "A person native to the region with invaluable knowledge of the terrain, customs, and dangers. Often underestimated by outsiders.",
                "traits": ["perceptive", "adaptable", "proud", "mysterious"],
                "examples": ["Queequeg", "Sallah"]
            },
            {
                "archetype": "The Determined Journalist",
                "description": "A reporter seeking the story of a lifetime. Willing to face danger to get the scoop and reveal the truth.",
                "traits": ["persistent", "observant", "skeptical", "brave"],
                "examples": ["Nellie Bly", "Carl Kolchak"]
            },
            {
                "archetype": "The Mercenary",
                "description": "A soldier of fortune who officially works for pay but may develop deeper loyalties. Expert in weapons and survival.",
                "traits": ["skilled", "practical", "cautious", "honor-bound"],
                "examples": ["Brendan Fraser's Rick O'Connell", "Han Solo"]
            },
            {
                "archetype": "The Rival Explorer",
                "description": "A competitor in the race for discovery. May have a personal history with the protagonist and similar skills.",
                "traits": ["competitive", "determined", "brilliant", "unscrupulous"],
                "examples": ["Belloq from Raiders of the Lost Ark", "Professor Moriarty"]
            },
            {
                "archetype": "The Wealthy Collector",
                "description": "A powerful figure who funds expeditions to acquire rare artifacts. May begin as an ally before revealing darker intentions.",
                "traits": ["sophisticated", "obsessive", "controlling", "ruthless"],
                "examples": ["Charles Kane", "Walter Donovan"]
            }
        ]

    def get_setting_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Lost Jungle City",
                "description": "An ancient civilization hidden deep in uncharted jungle, with stone temples, mysterious technologies, and possibly descendants of the original inhabitants.",
                "features": ["overgrown pyramids", "stone idols", "hidden traps", "forgotten treasures"],
                "dangers": ["hostile tribes", "poisonous wildlife", "collapsing structures", "ancient curses"]
            },
            {
                "name": "Desert Expedition",
                "description": "A journey across vast desert landscapes in search of a legendary oasis, buried city, or tomb hidden beneath the shifting sands.",
                "features": ["endless dunes", "mirages", "ancient caravan routes", "hidden oases"],
                "dangers": ["sandstorms", "dehydration", "scorpions", "hostile nomads"]
            },
            {
                "name": "Uncharted Island",
                "description": "A remote island far from shipping lanes, potentially home to prehistoric life, pirate treasures, or the remnants of an unknown civilization.",
                "features": ["volcanic peaks", "hidden caves", "pristine beaches", "dense interior jungles"],
                "dangers": ["carnivorous wildlife", "headhunters", "treacherous terrain", "active volcanoes"]
            },
            {
                "name": "Himalayan Quest",
                "description": "An expedition to the roof of the world, seeking a hidden monastery, the abominable snowman, or a pass to a valley lost in time.",
                "features": ["towering peaks", "rope bridges", "hidden mountain passes", "ancient monasteries"],
                "dangers": ["avalanches", "freezing temperatures", "oxygen deprivation", "superstitious porters"]
            },
            {
                "name": "Colonial Port City",
                "description": "A bustling hub of commerce where cultures clash, information is traded, and expeditions are launched into the interior.",
                "features": ["crowded bazaars", "exclusive European clubs", "seedy waterfronts", "warehouses full of exotic goods"],
                "dangers": ["spies", "thieves", "corrupt officials", "rival expedition leaders"]
            },
            {
                "name": "Ancient Tombs",
                "description": "The final resting place of kings or holy men, filled with treasures, artwork, and possibly supernatural guardians.",
                "features": ["hieroglyphics", "burial chambers", "ceremonial artifacts", "complex layouts"],
                "dangers": ["booby traps", "cave-ins", "curses", "tomb robbers"]
            },
            {
                "name": "Amazon River Journey",
                "description": "An expedition up one of the world's greatest rivers, penetrating deeper into unknown territory with each passing day.",
                "features": ["winding waterways", "indigenous villages", "diverse ecosystems", "rapids and waterfalls"],
                "dangers": ["piranhas", "hostile tribes", "disease", "river pirates"]
            },
            {
                "name": "Arctic Expedition",
                "description": "A race against time and elements to reach an unexplored region, lost ship, or hidden passage at the top of the world.",
                "features": ["ice floes", "aurora borealis", "endless days/nights", "pristine wilderness"],
                "dangers": ["hypothermia", "polar bears", "starvation", "madness from isolation"]
            }
        ]

    def get_plot_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "The Lost Treasure Hunt",
                "structure": [
                    "Discovery of a map or clue to a legendary treasure",
                    "Assembly of an expedition team with various skills",
                    "Journey to a remote starting point encountering initial obstacles",
                    "Main expedition faced with environmental challenges and rivalries within the team",
                    "Discovery that another group is pursuing the same goal",
                    "Major setback that separates the team or costs lives",
                    "Discovery of the treasure site guarded by ancient traps or guardians",
                    "Final confrontation with rival expedition at the treasure location",
                    "Escape with or without the treasure as the site self-destructs or is reclaimed by nature"
                ]
            },
            {
                "name": "The Rescue Mission",
                "structure": [
                    "News of a missing expedition, kidnapped individual, or stranded group",
                    "Protagonist's personal connection to the missing party revealed",
                    "Assembly of a rescue team and gathering of intelligence",
                    "Journey to the last known location encountering evidence of what happened",
                    "Discovery of the true danger that claimed the previous expedition",
                    "Finding survivors or captives guarded by antagonists",
                    "Failed first rescue attempt leading to capture or retreat",
                    "Development of a new plan exploiting newly discovered knowledge",
                    "Dramatic rescue and harrowing escape from the danger zone"
                ]
            },
            {
                "name": "The Ancient Mystery",
                "structure": [
                    "Discovery of an artifact or text hinting at an ancient mystery",
                    "Academic debate about the meaning with skeptics and believers",
                    "Decision to mount an expedition to prove a theory",
                    "Journey to a remote location guided by historical clues",
                    "Discovery of evidence confirming parts of the legend but raising new questions",
                    "Realization that solving the mystery might have dangerous consequences",
                    "Hostile force attempts to stop the expedition from proceeding",
                    "Reaching the heart of the mystery and confronting its reality",
                    "Decision to reveal, destroy, or protect the discovery from the world"
                ]
            },
            {
                "name": "The Race Against Time",
                "structure": [
                    "Introduction of a deadline: seasonal change, astronomical event, political situation",
                    "Explanation of why the deadline is crucial to the adventure's success",
                    "Accelerated preparation and departure, possibly missing crucial supplies",
                    "Initial fast progress followed by a major delay or detour",
                    "Realization that a rival expedition has a head start",
                    "Risky decision to take a dangerous shortcut to make up time",
                    "Apparent failure as the deadline approaches with too much distance remaining",
                    "Last-minute opportunity or insight that provides a final chance",
                    "Dramatic arrival just in time or moments too late with consequences"
                ]
            },
            {
                "name": "The Forbidden Discovery",
                "structure": [
                    "Rumors of a place or artifact that official sources deny exists",
                    "Discovery of evidence proving the rumors might be true",
                    "Warnings from authorities or locals not to pursue the investigation",
                    "Secret departure on an unauthorized expedition",
                    "Journey marked by signs that others have tried and failed before",
                    "Discovery of the forbidden place or object and initial wonder",
                    "Realization of why it was forbidden as danger manifests",
                    "Struggle to contain or escape the unleashed threat",
                    "Return to civilization with a burden of secret knowledge"
                ]
            }
        ]

    def get_tropes(self) -> List[str]:
        return [
            "The ancient map with a portion missing",
            "Quicksand pits and rope swinging escapes",
            "Ancient booby traps that still work perfectly",
            "The loyal native guide who knows the terrain",
            "The treacherous expedition member who betrays the team",
            "Lost civilizations with advanced technology or magic",
            "The curse that follows those who disturb ancient sites",
            "Wild animal attacks requiring quick thinking to survive",
            "The narrow escape from a collapsing tomb/temple/cave",
            "Using an ancient artifact to defeat supernatural enemies",
            "The final handshake between rivals who earned mutual respect",
            "The villain's death by poetic justice (consumed by what they sought)",
            "The decision to leave treasure behind for the greater good",
            "The unexpected romance between adventurer and local/team member",
            "The triumphant return with proof of discovery (or empty-handed but wiser)"
        ]

    def get_example_passages(self) -> List[str]:
        return [
            """
            McAllister squinted at the crumbling stone face, its features worn by three thousand years of desert winds. The hieroglyphs beneath it seemed to shimmer in the merciless sun. "This is it," he breathed, wiping sweat from his brow. "The entrance to the lost tomb of Nephren-Ka." Behind him, the camels grunted restlessly as Hassan, his Egyptian guide, nervously scanned the horizon. "We should not be here, Professor," he whispered. "The desert people speak of a curse." McAllister barely heard him, his fingers already tracing the hidden seam in the rock. "Nonsense, Hassan. In an hour, we'll be standing where no man has stood since the time of the pharaohs." He didn't notice the silhouettes of riders appearing on the distant dune, nor the glint of sun on rifle barrels.
            """,
            """
            The Amazon closed around their small boat like a living thing, the wall of vegetation so thick on either bank that it seemed they were traveling down a green tunnel. The air hung heavy with moisture and the sounds of unseen creatures. Rivera guided the craft with practiced ease around a partly submerged log. "Three days more to reach the falls," he said, "then we walk." Madison nodded, checking her father's journal against the crude map they'd been following. "And you're sure no one else has tried to find this city?" Rivera's laugh held no humor. "Those who tried never returned, señorita. The Karawaya don't like visitors." He tapped the rifle resting at his feet. "We bring guns. Maybe we have better luck." Madison wasn't listening anymore, her attention caught by something unnatural among the vines—the unmistakable shape of a human skull.
            """,
            """
            Frost bit at Harper's cheeks as he hauled himself up the icy face, the wind threatening to tear him from the mountain with each gust. Fifty feet above, Tenzing had already reached the narrow ledge and was securing the rope. "Still think this is a shortcut?" Chen called from below, her voice nearly lost in the howling gale. Harper didn't waste breath answering. The ancient map had shown a cave system that could lead them past the impassable glacier—if it existed at all. As his gloved hand finally gripped the ledge, Tenzing helped pull him up. "Look," the Sherpa said simply, pointing. There, half-hidden by snow, was a dark opening in the rock face, and beside it, carved symbols identical to those on their map. Harper laughed despite his exhaustion. "We've found it! The passage to Shambhala!"
            """,
            """
            The jungle night erupted in gunfire. Van Halen dropped flat behind the fallen log as bullets splintered bark inches above his head. Across the small clearing, he could see Santiago pinned down behind the ruins of the stone altar. "So much for our friendly welcome!" Santiago shouted, returning fire with his revolver. Van Halen counted at least five muzzle flashes among the trees—Ortega's men had followed them after all. His hand closed around the small golden idol in his pocket, its surface still warm to the touch despite the cool night air. "We need to reach the river!" he called. "The boat—" His words died as a new sound rose above the gunfire—a low, rumbling growl unlike anything he'd ever heard. The shooting abruptly stopped. In the sudden silence, something large moved in the darkness beyond the trees.
            """
        ] 