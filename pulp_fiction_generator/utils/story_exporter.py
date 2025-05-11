"""
Story export utility for the Pulp Fiction Generator.

This module provides functionality to export generated stories to various formats:
- HTML
- PDF
- Markdown
- Plain text
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# Try to import CrewAI tools
try:
    from crewai_tools import FileWriteTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False

class StoryExporter:
    """Exports generated stories to various formats."""
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the StoryExporter.
        
        Args:
            output_dir: Directory where exported files will be saved
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize FileWriteTool if available
        self.file_write_tool = None
        if CREWAI_TOOLS_AVAILABLE:
            self.file_write_tool = FileWriteTool()
    
    def _sanitize_filename(self, title: str) -> str:
        """
        Create a safe filename from a story title.
        
        Args:
            title: The story title
            
        Returns:
            A filename-safe version of the title
        """
        # Replace spaces with underscores and remove special characters
        safe_name = re.sub(r'[^\w\s-]', '', title).strip()
        # Replace multiple spaces with a single space, then replace spaces with underscores
        safe_name = re.sub(r'\s+', ' ', safe_name).replace(' ', '_')
        return safe_name
    
    def _write_to_file(self, filepath: str, content: str) -> None:
        """
        Write content to a file using FileWriteTool if available.
        
        Args:
            filepath: Path to the file
            content: Content to write
        """
        if CREWAI_TOOLS_AVAILABLE and self.file_write_tool:
            self.file_write_tool.write(filepath, content)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    
    def export_to_markdown(self, story_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export a story to Markdown format.
        
        Args:
            story_data: The story data (title, content, metadata)
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the exported file
        """
        title = story_data.get('title', 'Untitled Story')
        content = story_data.get('content', '')
        metadata = story_data.get('metadata', {})
        
        if not filename:
            filename = self._sanitize_filename(title)
        
        # Create markdown content
        md_content = f"# {title}\n\n"
        
        # Add metadata
        if metadata:
            md_content += "## Story Information\n\n"
            for key, value in metadata.items():
                if key != "tags" and key != "characters":
                    md_content += f"**{key.capitalize()}**: {value}\n"
            
            # Add tags if present
            if "tags" in metadata and metadata["tags"]:
                md_content += "\n**Tags**: " + ", ".join(metadata["tags"]) + "\n"
            
            # Add characters if present
            if "characters" in metadata and metadata["characters"]:
                md_content += "\n## Characters\n\n"
                for character in metadata["characters"]:
                    md_content += f"- **{character.get('name', 'Unnamed')}**: {character.get('description', 'No description')}\n"
            
            md_content += "\n---\n\n"
        
        # Add story content
        md_content += content
        
        # Add export timestamp
        md_content += f"\n\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*"
        
        # Write to file
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        self._write_to_file(filepath, md_content)
        
        return filepath
    
    def export_to_html(self, story_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export a story to HTML format with basic styling.
        
        Args:
            story_data: The story data (title, content, metadata)
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the exported file
        """
        title = story_data.get('title', 'Untitled Story')
        content = story_data.get('content', '')
        metadata = story_data.get('metadata', {})
        
        if not filename:
            filename = self._sanitize_filename(title)
        
        # Basic HTML template with CSS styling
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .metadata {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .story-content {{
            text-align: justify;
        }}
        .tag {{
            display: inline-block;
            background-color: #e0e0e0;
            padding: 3px 10px;
            border-radius: 15px;
            margin-right: 5px;
            font-size: 0.85em;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            font-size: 0.8em;
            color: #777;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {metadata_html}
    <div class="story-content">
        {content_html}
    </div>
    <div class="footer">
        Generated on {timestamp}
    </div>
</body>
</html>"""
        
        # Convert content to HTML paragraphs
        content_html = ""
        for paragraph in content.split('\n'):
            if paragraph.strip():
                content_html += f"<p>{paragraph}</p>\n"
        
        # Create metadata HTML
        metadata_html = ""
        if metadata:
            metadata_html = '<div class="metadata">\n'
            
            # Add basic metadata
            for key, value in metadata.items():
                if key not in ["tags", "characters"]:
                    metadata_html += f"<p><strong>{key.capitalize()}:</strong> {value}</p>\n"
            
            # Add tags if present
            if "tags" in metadata and metadata["tags"]:
                metadata_html += "<p><strong>Tags:</strong> "
                for tag in metadata["tags"]:
                    metadata_html += f'<span class="tag">{tag}</span> '
                metadata_html += "</p>\n"
            
            # Add characters if present
            if "characters" in metadata and metadata["characters"]:
                metadata_html += "<h2>Characters</h2>\n<ul>\n"
                for character in metadata["characters"]:
                    name = character.get('name', 'Unnamed')
                    desc = character.get('description', 'No description')
                    metadata_html += f"<li><strong>{name}:</strong> {desc}</li>\n"
                metadata_html += "</ul>\n"
            
            metadata_html += "</div>\n"
        
        # Fill in the template
        html_content = html_template.format(
            title=title,
            metadata_html=metadata_html,
            content_html=content_html,
            timestamp=datetime.now().strftime('%Y-%m-%d at %H:%M')
        )
        
        # Write to file
        filepath = os.path.join(self.output_dir, f"{filename}.html")
        self._write_to_file(filepath, html_content)
        
        return filepath
    
    def export_to_pdf(self, story_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export a story to PDF format.
        
        Args:
            story_data: The story data (title, content, metadata)
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the exported file
        """
        try:
            import weasyprint
        except ImportError:
            raise ImportError(
                "weasyprint is required for PDF export. "
                "Install it with: pip install weasyprint"
            )
            
        title = story_data.get('title', 'Untitled Story')
        
        if not filename:
            filename = self._sanitize_filename(title)
        
        # First export to HTML, then convert to PDF
        html_path = self.export_to_html(story_data, filename)
        pdf_path = os.path.join(self.output_dir, f"{filename}.pdf")
        
        # Convert HTML to PDF
        weasyprint.HTML(filename=html_path).write_pdf(pdf_path)
        
        return pdf_path
    
    def export_to_text(self, story_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Export a story to plain text format.
        
        Args:
            story_data: The story data (title, content, metadata)
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the exported file
        """
        title = story_data.get('title', 'Untitled Story')
        content = story_data.get('content', '')
        metadata = story_data.get('metadata', {})
        
        if not filename:
            filename = self._sanitize_filename(title)
        
        # Create plain text content
        text_content = f"{title.upper()}\n{'=' * len(title)}\n\n"
        
        # Add metadata
        if metadata:
            text_content += "STORY INFORMATION\n-----------------\n\n"
            for key, value in metadata.items():
                if key != "tags" and key != "characters":
                    text_content += f"{key.capitalize()}: {value}\n"
            
            # Add tags if present
            if "tags" in metadata and metadata["tags"]:
                text_content += f"\nTags: {', '.join(metadata['tags'])}\n"
            
            # Add characters if present
            if "characters" in metadata and metadata["characters"]:
                text_content += "\nCHARACTERS\n----------\n\n"
                for character in metadata["characters"]:
                    text_content += f"- {character.get('name', 'Unnamed')}: {character.get('description', 'No description')}\n"
            
            text_content += "\n" + ("-" * 40) + "\n\n"
        
        # Add story content
        text_content += content
        
        # Add export timestamp
        text_content += f"\n\n{'-' * 40}\nGenerated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}"
        
        # Write to file
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        self._write_to_file(filepath, text_content)
        
        return filepath
    
    def export_story(self, story_data: Dict[str, Any], formats: List[str], filename: Optional[str] = None) -> Dict[str, str]:
        """
        Export a story to multiple formats.
        
        Args:
            story_data: The story data (title, content, metadata)
            formats: List of formats to export to ("markdown", "html", "pdf", "text")
            filename: Optional custom filename (without extension)
            
        Returns:
            Dictionary mapping format names to exported file paths
        """
        results = {}
        
        format_exporters = {
            "markdown": self.export_to_markdown,
            "md": self.export_to_markdown,
            "html": self.export_to_html,
            "pdf": self.export_to_pdf,
            "text": self.export_to_text,
            "txt": self.export_to_text,
        }
        
        for fmt in formats:
            fmt = fmt.lower()
            if fmt in format_exporters:
                try:
                    filepath = format_exporters[fmt](story_data, filename)
                    results[fmt] = filepath
                except Exception as e:
                    print(f"Error exporting to {fmt}: {str(e)}")
            else:
                print(f"Unsupported format: {fmt}")
        
        return results 