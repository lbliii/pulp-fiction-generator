"""
Western genre plugin for Pulp Fiction Generator.

This plugin adds the Western pulp fiction genre to the generator.
"""

from pulp_fiction_generator.plugins.base import GenrePlugin
from typing import Dict, List, Any

class WesternGenrePlugin(GenrePlugin):
    """Western genre plugin"""
    
    plugin_id = "western"
    plugin_name = "Western Pulp Fiction"
    plugin_description = "Classic Western pulp fiction with cowboys, outlaws, and frontier justice"
    plugin_version = "1.0.0"
    
    def get_prompt_enhancers(self) -> Dict[str, str]:
        """Get prompt enhancers for different agent types"""
        return {
            "researcher": """
                Focus on historical accuracy of the American frontier (1865-1900).
                Research common Western tropes: gunslingers, saloons, cattle drives, 
                outlaws, sheriffs, Native American relations, and frontier justice.
                Identify key historical events and figures of the era that could
                influence the story, such as the expansion of railroads, gold rushes,
                and famous outlaws like Billy the Kid or Jesse James.
            """,
            "worldbuilder": """
                Create a vivid Western frontier setting with:
                - Dusty frontier towns with wooden buildings, saloons, and jails
                - Wide open landscapes (deserts, mountains, plains)
                - Ranches, trails, and remote outposts
                - Realistic depictions of frontier life and its hardships
                Pay special attention to the isolation of frontier settlements and
                the contrast between civilization and wilderness.
            """,
            "character_creator": """
                Develop authentic Western characters with clear moral codes.
                Common archetypes include:
                - The stoic, principled gunslinger with a mysterious past
                - The determined sheriff or marshal upholding the law
                - The ruthless outlaw or gang leader
                - The saloon owner with connections to everyone in town
                - The newcomer from the East confronting frontier realities
                Ensure characters have distinctive speech patterns using authentic
                Western slang and dialects of the period.
            """,
            "plotter": """
                Craft a Western plot with these elements:
                - Clear lines between justice and lawlessness
                - Moral dilemmas that test character principles
                - Building tension leading to confrontations/showdowns
                - Themes of honor, revenge, redemption, and frontier justice
                - Limited use of technology (telegraph as most advanced)
                Structure should build toward a satisfying showdown or resolution
                where justice prevails (though perhaps at a cost).
            """,
            "writer": """
                Write in a spare, direct style appropriate to Western pulp fiction:
                - Sharp, minimal dialogue that reveals character
                - Vivid descriptions of the natural environment and weather
                - Tense action scenes, especially gunfights and chases
                - Sensory details of frontier life (dust, heat, smells, sounds)
                Balance action sequences with quieter moments of reflection.
                Use period-appropriate language and avoid modern terminology.
            """,
            "editor": """
                When editing, ensure:
                - Historical accuracy is maintained
                - Language remains period-appropriate
                - Action scenes are clear and impactful
                - Character motivations are consistent and understandable
                - Pacing maintains tension while allowing for character development
                - The moral code of the Western genre comes through clearly
            """
        }
    
    def get_character_templates(self) -> List[Dict[str, Any]]:
        """Get character templates for this genre"""
        return [
            {
                "name": "The Gunslinger",
                "archetype": "Protagonist",
                "background": "A skilled gunfighter with a troubled past, seeking redemption or a new start.",
                "traits": ["Fast draw", "Silent type", "Code of honor", "Haunted by past"],
                "motivations": ["Redemption", "Justice", "Peace", "Protecting the innocent"]
            },
            {
                "name": "The Outlaw",
                "archetype": "Antagonist",
                "background": "A ruthless criminal who lives by taking what they want, leading a gang of loyal followers.",
                "traits": ["Cunning", "Ruthless", "Charismatic", "Vengeful"],
                "motivations": ["Wealth", "Power", "Revenge", "Reputation"]
            },
            {
                "name": "The Sheriff",
                "archetype": "Authority/Ally",
                "background": "A law enforcer in a frontier town, trying to maintain order against difficult odds.",
                "traits": ["Determined", "Fair-minded", "Tough", "Weary"],
                "motivations": ["Law and order", "Protecting community", "Personal honor", "Legacy"]
            }
        ]
    
    def get_plot_templates(self) -> List[Dict[str, Any]]:
        """Get plot templates for this genre"""
        return [
            {
                "name": "Revenge Trail",
                "description": "A wronged protagonist hunts down those responsible for harming them or their loved ones.",
                "beats": [
                    "Protagonist suffers a devastating loss at the hands of villains",
                    "Gathering information/resources for the hunt",
                    "Tracking down and confronting minor antagonists",
                    "Discovering a larger conspiracy/motivation behind the attack",
                    "Final confrontation with the main antagonist",
                    "Aftermath showing the cost of revenge"
                ]
            },
            {
                "name": "Frontier Justice",
                "description": "A lawman must restore order to a troubled town against overwhelming odds.",
                "beats": [
                    "Lawman arrives in a town controlled by corruption or an outlaw gang",
                    "Assessment of the situation and gathering local allies",
                    "First confrontation that demonstrates the threat",
                    "Setback when antagonists retaliate",
                    "Regrouping and strategic planning",
                    "Final showdown to restore justice",
                    "Town begins rebuilding under new order"
                ]
            }
        ]
    
    def get_example_passages(self) -> List[Dict[str, str]]:
        """Get example passages for this genre"""
        return [
            {
                "description": "Character introduction",
                "text": """The stranger rode into town as the dust devils danced along the main street. His black duster was caked with the dirt of a hundred miles, and the worn Colt on his hip had notches enough to tell its own story. From beneath the shadow of his wide-brimmed hat, steel-gray eyes surveyed the town with the wariness of a man who'd seen too much to trust anything at first glance.""",
                "source": "Example Western introduction"
            },
            {
                "description": "Saloon scene",
                "text": """The batwing doors of the Silver Spur swung open, and the piano player's tune faltered for a half-beat before resuming. Conversations died like unwatered flowers as boots struck floorboards slick with spilled whiskey. The bartender's hand drifted below the counter, where a scattergun waited for trouble. In a town like Diablo Crossing, trouble never needed much invitation.""",
                "source": "Example Western setting"
            }
        ] 