"""
Context Visualizer for debugging agent interactions.

This module provides tools to visualize the context flow between agents
and the decision-making process during story generation.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import rich
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax


class ContextVisualizer:
    """
    Visualizes agent context and interactions for debugging.
    
    This class provides methods to visualize the context object at different
    stages of processing, track changes between agent handoffs, and generate
    debug output for agent decision-making.
    """
    
    def __init__(self, output_dir: Optional[str] = None, enabled: bool = True):
        """
        Initialize the context visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            enabled: Whether visualization is enabled
        """
        self.enabled = enabled
        self.console = Console()
        
        # Set up output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(os.getcwd(), "debug_output")
        
        if enabled and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Tracking state
        self.context_history = []
        self.agent_interactions = []
    
    def visualize_context(self, context: Dict[str, Any], stage: str = "unnamed"):
        """
        Visualize the current context state.
        
        Args:
            context: The current context object
            stage: Name of the current processing stage
        """
        if not self.enabled:
            return
        
        # Save context to history
        timestamp = datetime.now().isoformat()
        self.context_history.append({
            "stage": stage,
            "timestamp": timestamp,
            "context": context.copy() if isinstance(context, dict) else context
        })
        
        # Create visualization
        self.console.print(f"\n[bold cyan]Context at stage: {stage}[/bold cyan]")
        
        # Create a tree visualization
        tree = Tree(f"[bold]Context ({stage})[/bold]")
        self._build_context_tree(tree, context)
        
        self.console.print(tree)
        
        # Save JSON snapshot
        self._save_context_snapshot(context, stage, timestamp)
    
    def track_agent_interaction(
        self,
        agent_name: str,
        input_context: Dict[str, Any],
        output_context: Dict[str, Any],
        prompt: Optional[str] = None,
        response: Optional[str] = None
    ):
        """
        Track and visualize an agent interaction.
        
        Args:
            agent_name: Name of the agent
            input_context: Context before agent processing
            output_context: Context after agent processing
            prompt: The prompt sent to the agent (optional)
            response: The response from the agent (optional)
        """
        if not self.enabled:
            return
        
        timestamp = datetime.now().isoformat()
        
        # Save interaction
        interaction = {
            "agent": agent_name,
            "timestamp": timestamp,
            "input_context": input_context.copy() if isinstance(input_context, dict) else input_context,
            "output_context": output_context.copy() if isinstance(output_context, dict) else output_context,
            "prompt": prompt,
            "response": response
        }
        self.agent_interactions.append(interaction)
        
        # Visualize differences in context
        self.console.print(f"\n[bold magenta]Agent Interaction: {agent_name}[/bold magenta]")
        
        # Find and display changes
        context_diff = self._calculate_context_diff(input_context, output_context)
        
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
        
        # Save detailed interaction log
        self._save_interaction_log(interaction, agent_name, timestamp)
    
    def show_prompt_template(self, agent_name: str, template: str, variables: Dict[str, Any]):
        """
        Visualize a prompt template with its variables.
        
        Args:
            agent_name: Name of the agent using the prompt
            template: The prompt template
            variables: Variables used in the template
        """
        if not self.enabled:
            return
        
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
    
    def export_visualization_html(self, output_path: Optional[str] = None):
        """
        Export the visualization history as an HTML file.
        
        Args:
            output_path: Path to save the HTML file, or None to use default location
        """
        if not self.enabled or not self.context_history:
            return
        
        if not output_path:
            output_path = os.path.join(
                self.output_dir,
                f"context_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )
        
        # Simple HTML export of context history
        html_content = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "  <title>Story Generation Debug Visualization</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; margin: 20px; }",
            "    .stage { margin-bottom: 30px; border: 1px solid #ccc; padding: 10px; border-radius: 5px; }",
            "    .stage-header { background-color: #f0f0f0; padding: 5px; margin-bottom: 10px; }",
            "    .context { white-space: pre-wrap; }",
            "    .agent { background-color: #e6f7ff; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <h1>Story Generation Debug Visualization</h1>"
        ]
        
        # Add context history
        html_content.append("  <h2>Context History</h2>")
        for entry in self.context_history:
            html_content.extend([
                f"  <div class='stage'>",
                f"    <div class='stage-header'>",
                f"      <strong>Stage:</strong> {entry['stage']} <em>({entry['timestamp']})</em>",
                f"    </div>",
                f"    <div class='context'>",
                f"      <pre>{json.dumps(entry['context'], indent=2)}</pre>",
                f"    </div>",
                f"  </div>"
            ])
        
        # Add agent interactions
        html_content.append("  <h2>Agent Interactions</h2>")
        for interaction in self.agent_interactions:
            html_content.extend([
                f"  <div class='stage agent'>",
                f"    <div class='stage-header'>",
                f"      <strong>Agent:</strong> {interaction['agent']} <em>({interaction['timestamp']})</em>",
                f"    </div>",
                f"    <h3>Prompt</h3>",
                f"    <div class='context'>",
                f"      <pre>{interaction.get('prompt', 'No prompt recorded')}</pre>",
                f"    </div>",
                f"    <h3>Response</h3>",
                f"    <div class='context'>",
                f"      <pre>{interaction.get('response', 'No response recorded')}</pre>",
                f"    </div>",
                f"    <h3>Context Changes</h3>",
                f"    <div class='context'>"
            ])
            
            # Calculate and display context differences
            context_diff = self._calculate_context_diff(
                interaction['input_context'], 
                interaction['output_context']
            )
            
            if context_diff:
                diff_html = []
                for key, (old_val, new_val) in context_diff.items():
                    diff_html.append(f"<strong>{key}</strong>:")
                    diff_html.append(f"<div style='color: #999;'>From: {str(old_val)[:500]}{'...' if str(old_val) and len(str(old_val)) > 500 else ''}</div>")
                    diff_html.append(f"<div style='color: #009900;'>To: {str(new_val)[:500]}{'...' if str(new_val) and len(str(new_val)) > 500 else ''}</div>")
                    diff_html.append("<hr>")
                
                html_content.append("<br>".join(diff_html))
            else:
                html_content.append("<em>No changes to context</em>")
            
            html_content.extend([
                f"    </div>",
                f"  </div>"
            ])
        
        # Close the HTML document
        html_content.extend([
            "</body>",
            "</html>"
        ])
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("\n".join(html_content))
        
        self.console.print(f"\n[bold green]Visualization exported to: {output_path}[/bold green]")
        
        return output_path
    
    def _build_context_tree(self, tree, data, prefix=""):
        """Recursively build a tree visualization of the context."""
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
    
    def _calculate_context_diff(self, before, after):
        """Calculate differences between before and after context."""
        diff = {}
        
        # Handle case when contexts are not dictionaries
        if not isinstance(before, dict) or not isinstance(after, dict):
            if before != after:
                return {"content": (before, after)}
            return {}
        
        # Find keys in after that are not in before or have different values
        for key in after:
            if key not in before:
                diff[key] = (None, after[key])
            elif before[key] != after[key]:
                diff[key] = (before[key], after[key])
        
        # Find keys in before that are not in after
        for key in before:
            if key not in after:
                diff[key] = (before[key], None)
        
        return diff
    
    def _save_context_snapshot(self, context, stage, timestamp):
        """Save a JSON snapshot of the context."""
        if not self.enabled:
            return
        
        filename = f"context_{stage.replace(' ', '_')}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(context, f, indent=2)
    
    def _save_interaction_log(self, interaction, agent_name, timestamp):
        """Save a detailed log of an agent interaction."""
        if not self.enabled:
            return
        
        filename = f"interaction_{agent_name.replace(' ', '_')}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(interaction, f, indent=2) 