"""
File storage for context visualization data.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, List

from ..context.diff_calculator import ContextDiffCalculator


class FileStorage:
    """
    Handles storage and retrieval of context visualization data.
    
    This class is responsible for saving context snapshots, agent interactions,
    and export visualizations to files.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the file storage.
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def save_context_snapshot(self, context: Dict[str, Any], stage: str, timestamp: str) -> str:
        """
        Save a JSON snapshot of the context.
        
        Args:
            context: The context to save
            stage: The stage name
            timestamp: The timestamp of the snapshot
            
        Returns:
            The path to the saved snapshot
        """
        filename = f"context_{stage.replace(' ', '_')}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(context, f, indent=2)
            
        return filepath
    
    def save_interaction_log(self, interaction: Dict[str, Any], agent_name: str, timestamp: str) -> str:
        """
        Save a detailed log of an agent interaction.
        
        Args:
            interaction: The interaction details
            agent_name: The name of the agent
            timestamp: The timestamp of the interaction
            
        Returns:
            The path to the saved interaction log
        """
        filename = f"interaction_{agent_name.replace(' ', '_')}_{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(interaction, f, indent=2)
            
        return filepath
    
    def export_html(self, context_history: List[Dict[str, Any]], agent_interactions: List[Dict[str, Any]]) -> str:
        """
        Export the visualization history as an HTML file.
        
        Args:
            context_history: The context history to export
            agent_interactions: The agent interactions to export
            
        Returns:
            The path to the exported HTML file
        """
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
        for entry in context_history:
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
        for interaction in agent_interactions:
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
            context_diff = ContextDiffCalculator.calculate_diff(
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
        
        return output_path 