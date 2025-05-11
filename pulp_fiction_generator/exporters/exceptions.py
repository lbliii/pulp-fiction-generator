"""
Exception classes for the exporters package.
"""

class ExporterError(Exception):
    """Base class for all exporter-related exceptions."""
    pass


class ExporterDependencyError(ExporterError):
    """Raised when a required dependency is missing."""
    pass


class ExporterFileError(ExporterError):
    """Raised when there is an error writing to or reading from a file."""
    pass


class ExporterFormatError(ExporterError):
    """Raised when the content format is not valid for the exporter."""
    pass 