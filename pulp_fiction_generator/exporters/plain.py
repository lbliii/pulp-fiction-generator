"""
Plain text exporter for Pulp Fiction Generator.
"""

from .base import BaseExporter
from .exceptions import ExporterFileError


class PlainExporter(BaseExporter):
    """Exporter for plain text format."""
    
    def export(self, content: str, output_path: str) -> str:
        """
        Export content as plain text.
        
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
            raise ExporterFileError(f"Error exporting to plain text: {e}") from e 