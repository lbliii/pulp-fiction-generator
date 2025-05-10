"""
Console-based visualization for context data.
"""

from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax


class ConsoleVisualizer:
    """
    Visualizes context and agent interactions to the console.
    
    This class is responsible for creating rich console visualizations
    of context and agent interactions.
    """
    
    def __init__(self):
        """Initialize the console visualizer."""
        self.console = Console()
    
    def visualize_context(self, context: Dict[str, Any], stage: str):
        """
        Visualize the current context state in the console.
        
        Args:
            context: The current context object
            stage: Name of the current processing stage
        """
        self.console.print(f"\n[bold cyan]Context at stage: {stage}[/bold cyan]")
        
        # Create a tree visualization
        tree = Tree(f"[bold]Context ({stage})[/bold]")
        self._build_context_tree(tree, context)
        
        self.console.print(tree)
    
    def visualize_agent_interaction(
        self,
        agent_name: str,
        input_context: Dict[str, Any],
        output_context: Dict[str, Any],
        context_diff: Dict[str, tuple]
    ):
        """
        Visualize an agent interaction in the console.
        
        Args:
            agent_name: Name of the agent
            input_context: Context before agent processing
            output_context: Context after agent processing
            context_diff: Dictionary of context differences
        """
        self.console.print(f"\n[bold magenta]Agent Interaction: {agent_name}[/bold magenta]")
        
        # Display changes using panels
        if context_diff:
            for key, (old_val, new_val) in context_diff.items():
                self.console.print(f"[yellow]Modified: {key}[/yellow]")
                
                if isinstance(old_val, str) and isinstance(new_val, str) and len(old_val) > 50 and len(new_val) > 50:
                    # For large text values, show shortened version
                    self.console.print(Panel(
                        f"From: {old_val[:50]}...\nTo: {new_val[:50]}...",
                        title=f"Changes to {key}",
                        expand=False
                    ))
                else:
                    # For smaller values or non-string types
                    self.console.print(Panel(
                        f"From: {old_val}\nTo: {new_val}",
                        title=f"Changes to {key}",
                        expand=False
                    ))
        else:
            self.console.print("[green]No changes to context[/green]")
    
    def visualize_prompt_template(self, agent_name: str, template: str, variables: Dict[str, Any]):
        """
        Visualize a prompt template with its variables in the console.
        
        Args:
            agent_name: Name of the agent using the prompt
            template: The prompt template
            variables: Variables used in the template
        """
        self.console.print(f"\n[bold blue]Prompt Template: {agent_name}[/bold blue]")
        
        # Show template
        syntax = Syntax(
            template,
            "jinja2",
            theme="monokai",
            line_numbers=True,
            word_wrap=True
        )
        self.console.print(Panel(syntax, title="Template", expand=False))
        
        # Show variables
        var_tree = Tree("[bold]Template Variables[/bold]")
        self._build_context_tree(var_tree, variables)
        self.console.print(var_tree)
        
    def show_export_confirmation(self, output_path: str):
        """
        Show confirmation of export.
        
        Args:
            output_path: Path where the visualization was exported
        """
        self.console.print(f"\n[bold green]Visualization exported to: {output_path}[/bold green]")
    
    def _build_context_tree(self, tree, data, prefix=""):
        """
        Recursively build a tree visualization of the context.
        
        Args:
            tree: The tree to build
            data: The data to visualize
            prefix: Prefix for nested keys
        """
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    branch = tree.add(f"[bold blue]{key}[/bold blue] (dict)")
                    self._build_context_tree(branch, value, full_key)
                elif isinstance(value, list):
                    branch = tree.add(f"[bold blue]{key}[/bold blue] (list, {len(value)} items)")
                    
                    # If it's a list of primitives, just show them directly
                    if value and all(not isinstance(x, (dict, list)) for x in value):
                        if len(value) <= 5:  # Show all for small lists
                            branch.add(str(value))
                        else:  # For larger lists, show just a few items
                            branch.add(f"{str(value[:3])[:-1]}, ... , {str(value[-1:])}")
                    else:
                        # For lists of complex objects, show each separately
                        for i, item in enumerate(value[:3]):  # Limit to first 3 items
                            self._build_context_tree(branch, item, f"{full_key}[{i}]")
                        
                        if len(value) > 3:
                            branch.add(f"... ({len(value) - 3} more items)")
                else:
                    # Format string values to limit length in display
                    if isinstance(value, str) and len(value) > 100:
                        tree.add(f"[green]{key}[/green]: {value[:100]}...")
                    else:
                        tree.add(f"[green]{key}[/green]: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data[:5]):  # Limit to first 5 items
                if isinstance(item, (dict, list)):
                    branch = tree.add(f"[{i}]")
                    self._build_context_tree(branch, item, f"{prefix}[{i}]")
                else:
                    tree.add(f"[{i}]: {item}")
            
            if len(data) > 5:
                tree.add(f"... ({len(data) - 5} more items)")
        else:
            # Handle primitive values (should not typically happen at the root level)
            tree.add(str(data)) 