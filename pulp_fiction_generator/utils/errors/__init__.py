"""
Error handling package for the Pulp Fiction Generator.

This package provides components for consistent error handling, logging,
and diagnostic information collection throughout the application.
"""

from .exceptions import (
    PulpFictionError, TimeoutError, ConfigurationError, 
    ModelServiceError, ModelConnectionError, ModelResponseError,
    ContentGenerationError, AgentError, StoryPersistenceError,
    InputValidationError, CliArgumentError
)
from .timeout import TimeoutManager, timeout
from .diagnostics import DiagnosticCollector, DiagnosticLogger
from .recovery import (
    RecoveryStrategy, ModelRetryStrategy, FallbackPromptStrategy,
    ConfigurationFixStrategy, RecoveryStrategyRegistry
)
from .handlers import ErrorHandler, ErrorInformationExtractor
from .decorators import with_error_handling
from .setup import setup_error_handling, logger

__all__ = [
    # Exception classes
    "PulpFictionError", "TimeoutError", "ConfigurationError", 
    "ModelServiceError", "ModelConnectionError", "ModelResponseError",
    "ContentGenerationError", "AgentError", "StoryPersistenceError",
    "InputValidationError", "CliArgumentError",
    
    # Timeout handling
    "TimeoutManager", "timeout",
    
    # Diagnostic tools
    "DiagnosticCollector", "DiagnosticLogger",
    
    # Recovery strategies
    "RecoveryStrategy", "ModelRetryStrategy", "FallbackPromptStrategy",
    "ConfigurationFixStrategy", "RecoveryStrategyRegistry",
    
    # Error handling
    "ErrorHandler", "ErrorInformationExtractor",
    
    # Decorators
    "with_error_handling",
    
    # Setup
    "setup_error_handling", "logger"
] 