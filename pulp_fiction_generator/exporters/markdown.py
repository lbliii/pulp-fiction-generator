"""
Markdown exporter for Pulp Fiction Generator.
"""

from .base import BaseExporter
from .exceptions import ExporterFileError


class MarkdownExporter(BaseExporter):
    """Exporter for markdown format."""
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export content as markdown.
        
        Args:
            content: The story content to export
            output_path: Path where the exported file should be saved
            
        Returns:
            The path to the exported file
            
        Raises:
            ExporterFileError: If unable to write to the output file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return output_path
        except Exception as e:
            raise ExporterFileError(f"Error exporting to markdown: {e}") from e
    
    @classmethod
    def get_format(cls) -> str:
        """
        Get the format identifier for this exporter.
        
        Returns:
            str: Format identifier ('markdown')
        """
        return "markdown" 