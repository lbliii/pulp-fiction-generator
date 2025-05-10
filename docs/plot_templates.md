# Plot Templates

This document outlines the plot template system in the Pulp Fiction Generator, explaining how to use plot templates, create custom ones, and integrate them into your storytelling process.

## Overview

Plot templates provide structured narrative frameworks that guide the story generation process. They define key plot points, narrative arcs, and genre-appropriate story elements that help create more cohesive and engaging stories.

The plot template system is designed to be:
- **Flexible**: Templates can be applied to different genres and adapted to your specific story needs
- **Modular**: You can create custom templates or use the built-in ones
- **Story-enhancing**: Templates guide story generation without being overly prescriptive

## Available Plot Templates

The Pulp Fiction Generator includes several built-in plot templates:

1. **Hero's Journey (Monomyth)**: The classic hero's journey structure as described by Joseph Campbell, featuring 12 key stages from the ordinary world to the return with the elixir.

2. **Three-Act Structure**: The traditional dramatic structure divided into setup, confrontation, and resolution, used in countless stories, plays, and screenplays.

3. **Save the Cat**: Blake Snyder's modernized beat sheet approach to storytelling, featuring 15 specific beats that occur at particular points in the narrative.

You can view all available templates and their details using the command:

```bash
python -m pulp_fiction_generator list-plots
```

## Using Plot Templates

To generate a story with a specific plot template:

```bash
python -m pulp_fiction_generator --genre noir --plot three_act
```

When continuing a story, the system will automatically use the same plot template from the previous session:

```bash
python -m pulp_fiction_generator --continue my_story.json --chapters 1
```

## How Plot Templates Work

When you select a plot template, the system:

1. **Loads the template structure**: The template's plot points, narrative arc, and other elements are loaded
2. **Enhances agent prompts**: Each agent (researcher, plotter, writer, etc.) receives guidance specific to the template
3. **Maps chapters to plot points**: For multi-chapter stories, the system determines which plot points should be addressed in each chapter
4. **Maintains consistency**: The plot structure is tracked across chapters and story continuation sessions

## Plot Template Structure

Each plot template defines:

- **Plot points**: Key story beats or events that form the narrative
- **Narrative arc**: The overall story structure (Hero's Journey, Three-Act, etc.)
- **Agent-specific guidance**: Customized prompts for each agent in the generation process
- **Genre affinities**: How well the template works with different genres

## Creating Custom Plot Templates

You can create your own plot templates by following these steps:

1. Create a new Python file in `pulp_fiction_generator/plots/`
2. Implement a class that extends `PlotTemplate` from `pulp_fiction_generator/plots/base.py`
3. Define plot points, narrative arc, and agent-specific prompt enhancements
4. Register your template by importing it or placing it in the plots directory

Here's a simplified example:

```python
from pulp_fiction_generator.plots.base import PlotTemplate, PlotStructure, PlotPoint, NarrativeArc

class MyCustomTemplate(PlotTemplate):
    @property
    def name(self) -> str:
        return "my_template"
        
    @property
    def description(self) -> str:
        return "My custom plot template description"
        
    @property
    def narrative_arc(self) -> NarrativeArc:
        return NarrativeArc.THREE_ACT
        
    def get_plot_structure(self) -> PlotStructure:
        plot_points = [
            PlotPoint(
                name="Opening",
                description="The story begins...",
                examples=["Example from a well-known story"]
            ),
            # Add more plot points...
        ]
        
        return PlotStructure(
            name="My Custom Structure",
            description="A custom plot structure",
            plot_points=plot_points,
            narrative_arc=self.narrative_arc
        )
        
    def get_prompt_enhancement(self, agent_type: str) -> str:
        # Return different guidance based on agent type
        if agent_type == "plotter":
            return "Guidance for the plotter agent..."
        # Handle other agent types...
        
    def get_suitable_genres(self) -> Dict[str, float]:
        return {
            "noir": 0.9,
            "sci-fi": 0.7
        }
```

## Plot Structure Validation

The system includes validation capabilities to ensure generated stories follow the selected plot template. This helps maintain narrative coherence and proper story structure.

The validator checks for:
- Presence of required plot points
- Proper sequence of story events
- Consistency with the chosen narrative arc
- Genre-appropriate implementation of the template

## Best Practices

1. **Match templates to genres**: Choose templates that work well with your genre (check the "Suitable Genres" column in `list-plots` output)
2. **Consider story length**: For shorter stories (1-3 chapters), simpler templates may work better
3. **Be flexible**: Templates are guides, not rigid rules - allow for creative adaptation
4. **Understand the narrative arc**: Familiarize yourself with the underlying structure of your chosen template
5. **Pay attention to plot points**: Review the plot points in your template to understand the intended narrative flow

## Troubleshooting

- **Story feels disjointed**: Try using a simpler template or reducing the number of plot points
- **Repetitive structures**: Switch to a different template or create a custom one
- **Plot point mismatch**: Ensure your genre works well with the selected template
- **Template not found**: Check the spelling and use `list-plots` to see available templates 