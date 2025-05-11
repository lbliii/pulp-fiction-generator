"""
Base exporter class that all exporters should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseExporter(ABC):
    """
    Abstract base class for story exporters.
    
    All exporter implementations must inherit from this class and implement
    the `export` method.
    """
    
    @abstractmethod
    def export(self, content: str, output_path: str) -> str:
        """
        Export content to the specified output path.
        
        Args:
            content (str): The story content to export
            output_path (str): Path where the exported file should be saved
            
        Returns:
            str: The path to the exported file
            
        Raises:
            ExporterError: If export fails for any reason
        """
        pass
    
    @classmethod
    def get_format(cls) -> str:
        """
        Get the format identifier for this exporter.
        
        By default, uses the lowercase class name without 'Exporter' suffix.
        Override this method if a different format name is needed.
        
        Returns:
            str: Format identifier (e.g., 'plain', 'html', 'pdf')
        """
        name = cls.__name__.lower()
        if name.endswith('exporter'):
            name = name[:-8]  # Remove 'exporter' suffix
        return name
    
    @staticmethod
    def check_dependencies() -> bool:
        """
        Check if all required dependencies for this exporter are installed.
        
        Returns:
            bool: True if all dependencies are available, False otherwise
        """
        return True  # Base implementation assumes no dependencies
    
    def get_extension(self) -> str:
        """
        Get the file extension for this exporter.
        
        By default, uses the format name as the extension.
        Override this method if a different extension is needed.
        
        Returns:
            str: File extension without the leading dot
        """
        return self.get_format()
    
    def extract_title(self, content: str) -> Optional[str]:
        """
        Extract the title from the content.
        
        Args:
            content (str): The story content
            
        Returns:
            Optional[str]: The title if found, None otherwise
        """
        lines = content.strip().split('\n')
        if lines and lines[0].startswith('#'):
            return lines[0].replace('#', '').strip()
        return None 