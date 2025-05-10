"""
Model service interfaces and implementations for language model interactions.

This module provides interfaces and implementations for interacting with
various language models through a consistent API.
"""

from .model_service import (
    TextGenerator,
    ChatInteractor,
    ModelInspector,
    TokenCounter,
    ModelService,
    ModelServiceAdapter,
    ModelServiceFactory
)

from .crewai_adapter import CrewAIModelAdapter
from .ollama_adapter import OllamaAdapter

__all__ = [
    # Model service interfaces
    'TextGenerator',
    'ChatInteractor',
    'ModelInspector',
    'TokenCounter',
    'ModelService',
    'ModelServiceAdapter',
    'ModelServiceFactory',
    
    # Model service implementations
    'CrewAIModelAdapter',
    'OllamaAdapter'
] 