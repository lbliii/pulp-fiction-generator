"""
Exception classes for the plugin system.
"""

class PluginError(Exception):
    """Base class for all plugin-related exceptions"""
    pass

class PluginLoadError(PluginError):
    """Raised when a plugin cannot be loaded"""
    pass

class PluginValidationError(PluginError):
    """Raised when a plugin fails validation"""
    pass

class PluginRegistrationError(PluginError):
    """Raised when a plugin cannot be registered"""
    pass

class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not found"""
    pass 