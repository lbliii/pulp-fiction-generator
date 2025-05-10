# Pulp Fiction Genres

The Pulp Fiction Generator supports multiple genres typical of the golden age of pulp fiction (1930s-1950s). Each genre has its own distinct characteristics, tropes, and styles that are incorporated into the generation process.

## Overview

Each genre implementation includes:
- Specialized prompts for agents
- Genre-specific tropes and conventions
- Characteristic settings and atmospheres
- Typical character archetypes
- Common plot structures and themes
- Representative examples for reference

## Supported Genres

### Noir/Hardboiled Detective

**Description**: Gritty crime fiction featuring tough, cynical characters in urban settings, often with moral ambiguity and pessimistic themes.

**Key Elements**:
- **Settings**: Rain-soaked cities, dimly lit offices, smoky bars, seedy hotels
- **Characters**: World-weary detectives, femme fatales, corrupt officials, ruthless criminals
- **Themes**: Corruption, betrayal, moral ambiguity, obsession
- **Style**: First-person narration, sparse dialogue, vivid metaphors, cynical outlook

**Notable Examples**: Works by Raymond Chandler, Dashiell Hammett, Mickey Spillane

**Sample Prompt Customization**:
```
Create a hardboiled detective story with morally ambiguous characters and a gritty urban setting. Use terse dialogue, vivid metaphors, and a cynical first-person perspective. The protagonist should be flawed but principled, facing corruption and betrayal.
```

### Science Fiction Adventure

**Description**: Action-packed stories set in futuristic or alien environments, focusing on advanced technology, space exploration, and encounters with extraterrestrial life.

**Key Elements**:
- **Settings**: Distant planets, space stations, alien landscapes, futuristic cities
- **Characters**: Space explorers, alien species, rogue scientists, interstellar outlaws
- **Themes**: Exploration, first contact, technological dangers, survival
- **Style**: Detailed technical descriptions, sense of wonder, fast-paced action

**Notable Examples**: Works by E.E. "Doc" Smith, Isaac Asimov, Ray Bradbury

**Sample Prompt Customization**:
```
Create a science fiction adventure set in a distant future with advanced technology and alien encounters. Balance action sequences with scientific explanations and a sense of wonder. Include detailed descriptions of technology and alien environments.
```

### Weird Tales/Horror

**Description**: Stories evoking fear, dread, and the supernatural, often featuring elements of cosmic horror, the occult, and psychological terror.

**Key Elements**:
- **Settings**: Isolated mansions, forgotten towns, ancient ruins, eerie landscapes
- **Characters**: Doomed investigators, occult practitioners, monstrous entities, cursed individuals
- **Themes**: Forbidden knowledge, cosmic horror, ancient evils, loss of sanity
- **Style**: Atmospheric descriptions, building dread, unreliable narration, unexplainable phenomena

**Notable Examples**: Works by H.P. Lovecraft, Robert E. Howard, Clark Ashton Smith

**Sample Prompt Customization**:
```
Create a weird horror tale with elements of cosmic terror and the supernatural. Build a mounting sense of dread through atmospheric descriptions and hints of ancient, incomprehensible forces. The protagonist should gradually discover disturbing truths that challenge their sanity.
```

### Adventure/Exploration

**Description**: Tales of daring expeditions to unexplored regions, lost civilizations, and dangerous quests, usually featuring heroic protagonists overcoming obstacles and adversaries.

**Key Elements**:
- **Settings**: Uncharted jungles, hidden temples, desert wastelands, mysterious islands
- **Characters**: Rugged explorers, treasure hunters, native guides, ruthless rivals
- **Themes**: Discovery, survival, conquest of nature, cultural clash
- **Style**: Detailed descriptions of exotic locations, action sequences, cliffhangers

**Notable Examples**: Works by Edgar Rice Burroughs, H. Rider Haggard, Talbot Mundy

**Sample Prompt Customization**:
```
Create an adventure tale set in an unexplored region with ancient ruins and hidden dangers. Feature a determined protagonist on a quest for discovery, facing natural hazards, hostile natives, and competing explorers. Include vivid descriptions of exotic locations and thrilling action sequences.
```

### Western

**Description**: Stories set in the American Old West, featuring cowboys, outlaws, lawmen, and frontier justice, often involving conflicts over land, resources, and competing visions of civilization.

**Key Elements**:
- **Settings**: Frontier towns, dusty plains, mountain ranges, isolated ranches
- **Characters**: Gunslingers, sheriffs, outlaws, Native Americans, homesteaders
- **Themes**: Justice, revenge, wilderness vs. civilization, personal honor
- **Style**: Laconic dialogue, vivid landscape descriptions, action-centered

**Notable Examples**: Works by Zane Grey, Louis L'Amour, Max Brand

**Sample Prompt Customization**:
```
Create a Western tale set in the American frontier featuring conflicts between law and lawlessness. Include sparse, impactful dialogue and vivid descriptions of the rugged landscape. The protagonist should embody frontier values while facing moral dilemmas and dangerous adversaries.
```

### Espionage/Spy Fiction

**Description**: Intrigue-filled stories of international espionage, featuring spies, counter-intelligence, covert operations, and global threats.

**Key Elements**:
- **Settings**: Foreign capitals, secret headquarters, luxury resorts, enemy territory
- **Characters**: Secret agents, double agents, handlers, foreign operatives
- **Themes**: Loyalty, betrayal, global security, political intrigue
- **Style**: Plot twists, tense action sequences, technical details, exotic locations

**Notable Examples**: Works by John Buchan, E. Phillips Oppenheim, Helen MacInnes

**Sample Prompt Customization**:
```
Create an espionage thriller set during a period of international tension. Feature a skilled but vulnerable agent navigating deception and danger in exotic locations. Include detailed tradecraft, unexpected betrayals, and high-stakes action sequences.
```

## Genre Implementation

Each genre is implemented as a module containing:

1. **GenreDefinition**: Class defining core genre elements and requirements
2. **AgentPromptEnhancers**: Specialized prompt modifications for each agent role
3. **GenreExamples**: Reference excerpts to guide style and content
4. **GenreCharacterTemplates**: Typical character archetypes and traits
5. **GenrePlotStructures**: Common narrative patterns and story beats

Example genre module structure:

```python
class NoirGenre(GenreDefinition):
    """Noir/Hardboiled detective genre implementation"""
    
    name = "noir"
    display_name = "Noir/Hardboiled Detective"
    description = "Gritty crime fiction featuring tough, cynical characters..."
    
    def get_researcher_prompt_enhancer(self):
        """Return prompt enhancer for the researcher agent"""
        return """
        Focus your research on crime fiction from the 1930s-1950s.
        Look for elements like:
        - Urban settings (particularly cities like Los Angeles, New York, Chicago)
        - Crime investigation techniques of the era
        - Organized crime operations and structures
        - Period-appropriate language, slang, and dialogue
        - Social issues like corruption, class tension, and post-war disillusionment
        """
    
    # Additional methods for other agents...
    
    def get_character_templates(self):
        """Return character templates for this genre"""
        return [
            {
                "archetype": "Detective",
                "traits": ["cynical", "determined", "flawed", "intelligent"],
                "background": "Former police officer or military, now working solo",
                "motivations": ["justice", "redemption", "obsession"]
            },
            # Additional character templates...
        ]
```

## Extensibility

The genre system is designed to be extensible, allowing:

1. **New Genre Addition**: Create a new genre class implementing the GenreDefinition interface
2. **Genre Customization**: Modify existing genres with custom elements
3. **Genre Fusion**: Combine elements from multiple genres
4. **Era Adaptation**: Adapt genres to different historical periods

To add a new genre, developers would:
1. Create a new class inheriting from GenreDefinition
2. Implement required methods for agent prompt enhancement
3. Define genre-specific elements like character templates
4. Register the genre in the GenreRegistry
5. Add any specialized tools or resources for the genre 