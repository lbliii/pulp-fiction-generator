"""
Factory for creating exporters based on format.
"""

from typing import Dict, Optional, Type
import importlib
import pkgutil
import sys

from .base import BaseExporter
from .exceptions import ExporterDependencyError
from ...utils.errors import logger


class ExporterFactory:
    """Factory for creating exporters based on format."""
    
    _exporters: Dict[str, Type[BaseExporter]] = {}
    _initialized = False
    
    @classmethod
    def _initialize(cls):
        """
        Dynamically discover and register all exporters in the package.
        Uses the `get_format` method to determine the format key.
        """
        if cls._initialized:
            return
            
        # Import all exporter modules
        from . import plain, markdown, html, pdf, docx, epub, terminal
        
        # Register exporters
        for module_name in [plain, markdown, html, pdf, docx, epub, terminal]:
            for attr_name in dir(module_name):
                attr = getattr(module_name, attr_name)
                if (isinstance(attr, type) and 
                        issubclass(attr, BaseExporter) and 
                        attr is not BaseExporter):
                    # Register the exporter with its format
                    format_name = attr.get_format()
                    cls._exporters[format_name] = attr
                    
                    # Add aliases for some formats
                    if format_name == 'markdown':
                        cls._exporters['md'] = attr
        
        cls._initialized = True
    
    @classmethod
    def register_exporter(cls, exporter_class: Type[BaseExporter]):
        """
        Register a new exporter class.
        
        Args:
            exporter_class: The exporter class to register
        """
        cls._initialize()
        format_name = exporter_class.get_format()
        cls._exporters[format_name] = exporter_class
    
    @classmethod
    def create_exporter(cls, format_name: str) -> Optional[BaseExporter]:
        """
        Create and return an exporter for the specified format.
        
        Args:
            format_name: The format to export to
            
        Returns:
            An exporter instance for the format, or None if not available
            
        Raises:
            ExporterDependencyError: If the exporter has missing dependencies
        """
        cls._initialize()
        
        # Get lowercase format name
        format_name = format_name.lower()
        
        # Find exporter class for this format
        exporter_class = cls._exporters.get(format_name)
        if not exporter_class:
            logger.warning(f"No exporter available for format: {format_name}")
            return None
            
        # Check dependencies
        if not exporter_class.check_dependencies():
            raise ExporterDependencyError(
                f"Missing dependencies for {format_name} export"
            )
            
        # Create and return exporter instance
        return exporter_class()
    
    @classmethod
    def list_available_formats(cls) -> Dict[str, bool]:
        """
        List all registered formats and whether they are ready to use.
        
        Returns:
            Dict mapping format names to availability (True if dependencies are met)
        """
        cls._initialize()
        
        result = {}
        for fmt, exporter_class in cls._exporters.items():
            available = exporter_class.check_dependencies()
            result[fmt] = available
            
        return result 