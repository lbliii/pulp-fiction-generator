"""
Utility modules and components for the Pulp Fiction Generator.

This module provides various utility classes and functions used throughout
the Pulp Fiction Generator application.
"""

# Error handling components
from .errors import (
    PulpFictionError, TimeoutError, ConfigurationError,
    ModelServiceError, ModelConnectionError, ModelResponseError,
    ContentGenerationError, AgentError, StoryPersistenceError,
    InputValidationError, CliArgumentError,
    TimeoutManager, DiagnosticCollector, DiagnosticLogger,
    RecoveryStrategy, ModelRetryStrategy, FallbackPromptStrategy, ConfigurationFixStrategy,
    RecoveryStrategyRegistry, ErrorHandler, ErrorInformationExtractor,
    with_error_handling, setup_error_handling, timeout
)

# Context visualization components
from .context_visualizer import (
    ContextData, ContextDiffCalculator, ConsoleVisualizer,
    FileStorage, ContextVisualizer
)

# Re-export commonly used components for convenience
# This provides a clean API for importing from pulp_fiction_generator.utils
__all__ = [
    # Error handling
    'PulpFictionError', 'TimeoutError', 'ConfigurationError',
    'ModelServiceError', 'ModelConnectionError', 'ModelResponseError',
    'ContentGenerationError', 'AgentError', 'StoryPersistenceError',
    'InputValidationError', 'CliArgumentError',
    'TimeoutManager', 'DiagnosticCollector', 'DiagnosticLogger',
    'RecoveryStrategy', 'ModelRetryStrategy', 'FallbackPromptStrategy', 'ConfigurationFixStrategy',
    'RecoveryStrategyRegistry', 'ErrorHandler', 'ErrorInformationExtractor',
    'with_error_handling', 'setup_error_handling', 'timeout',
    
    # Context visualization
    'ContextData', 'ContextDiffCalculator', 'ConsoleVisualizer',
    'FileStorage', 'ContextVisualizer'
] 