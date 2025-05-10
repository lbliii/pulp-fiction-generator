"""
Custom exception classes for the Pulp Fiction Generator.

This module defines all the custom exception types used throughout the application,
creating a clear hierarchy of error types.
"""


class PulpFictionError(Exception):
    """Base class for all Pulp Fiction Generator exceptions"""
    pass


class TimeoutError(PulpFictionError):
    """Exception raised when a function call times out"""
    pass


class ConfigurationError(PulpFictionError):
    """Exception raised when there is an issue with configuration"""
    pass


class ModelServiceError(PulpFictionError):
    """Base class for model service related errors"""
    pass


class ModelConnectionError(ModelServiceError):
    """Exception raised when connection to the model service fails"""
    pass


class ModelResponseError(ModelServiceError):
    """Exception raised when model response is invalid or unusable"""
    pass


class ContentGenerationError(PulpFictionError):
    """Exception raised when content generation fails"""
    pass


class AgentError(PulpFictionError):
    """Exception raised when there is an issue with an agent"""
    pass


class StoryPersistenceError(PulpFictionError):
    """Exception raised when there is an issue with story persistence"""
    pass


class InputValidationError(PulpFictionError):
    """Exception raised when user input fails validation"""
    pass


class CliArgumentError(PulpFictionError):
    """Exception raised when CLI arguments are invalid"""
    pass 