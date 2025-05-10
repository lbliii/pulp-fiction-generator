"""
Model service interfaces and abstractions for language model interactions.

This module defines a set of small, focused interfaces for different aspects
of language model interactions, allowing for more modular implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class TextGenerator(ABC):
    """
    Interface for text generation capabilities.
    
    This interface focuses solely on generating text from prompts.
    """
    
    @abstractmethod
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input text to generate from
            parameters: Optional generation parameters (temperature, etc.)
            
        Returns:
            The generated text
        """
        pass
    
    def batch_generate(
        self, 
        prompts: List[str], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate text for multiple prompts.
        Default implementation calls generate() for each prompt.
        
        Args:
            prompts: List of prompts to generate from
            parameters: Optional generation parameters
            
        Returns:
            List of generated texts
        """
        return [self.generate(prompt, parameters) for prompt in prompts]


class ChatInteractor(ABC):
    """
    Interface for chat-based interactions.
    
    This interface focuses solely on generating responses in a chat context.
    """
    
    @abstractmethod
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response in a chat context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            parameters: Optional generation parameters
            
        Returns:
            The generated response
        """
        pass


class ModelInspector(ABC):
    """
    Interface for inspecting model capabilities and properties.
    
    This interface focuses solely on retrieving information about models.
    """
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        pass


class TokenCounter(ABC):
    """
    Interface for tokenization and token counting.
    
    This interface focuses solely on tokenization operations.
    """
    
    def tokenize(self, text: str) -> List[int]:
        """
        Tokenize text into token IDs.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of token IDs
        """
        return []
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.
        
        Args:
            text: The text to count tokens in
            
        Returns:
            Number of tokens
        """
        return len(self.tokenize(text))


class ModelService(TextGenerator, ChatInteractor, ModelInspector, TokenCounter):
    """
    Comprehensive interface for language model services.
    
    This interface combines all the more focused interfaces to provide
    a complete set of model interaction capabilities. Implementations
    can choose to implement just some of the interfaces if they don't
    support all capabilities.
    """
    pass


class ModelServiceAdapter:
    """
    Adapter for making any implementation of the specific interfaces
    compatible with the full ModelService interface.
    
    This class allows using partial implementations (e.g., just TextGenerator)
    in contexts that expect the full ModelService interface.
    """
    
    def __init__(
        self,
        text_generator: Optional[TextGenerator] = None,
        chat_interactor: Optional[ChatInteractor] = None,
        model_inspector: Optional[ModelInspector] = None,
        token_counter: Optional[TokenCounter] = None
    ):
        """
        Initialize the adapter with implementations of specific interfaces.
        
        Args:
            text_generator: Implementation of TextGenerator
            chat_interactor: Implementation of ChatInteractor
            model_inspector: Implementation of ModelInspector
            token_counter: Implementation of TokenCounter
        """
        self.text_generator = text_generator
        self.chat_interactor = chat_interactor
        self.model_inspector = model_inspector
        self.token_counter = token_counter or TokenCounter()
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Delegate to text_generator implementation."""
        if not self.text_generator:
            raise NotImplementedError("Text generation not supported by this model service")
        return self.text_generator.generate(prompt, parameters)
    
    def batch_generate(
        self, 
        prompts: List[str], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Delegate to text_generator implementation."""
        if not self.text_generator:
            raise NotImplementedError("Text generation not supported by this model service")
        return self.text_generator.batch_generate(prompts, parameters)
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Delegate to chat_interactor implementation."""
        if not self.chat_interactor:
            raise NotImplementedError("Chat interaction not supported by this model service")
        return self.chat_interactor.chat(messages, parameters)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Delegate to model_inspector implementation."""
        if not self.model_inspector:
            raise NotImplementedError("Model inspection not supported by this model service")
        return self.model_inspector.get_model_info()
    
    def tokenize(self, text: str) -> List[int]:
        """Delegate to token_counter implementation."""
        return self.token_counter.tokenize(text)
    
    def count_tokens(self, text: str) -> int:
        """Delegate to token_counter implementation."""
        return self.token_counter.count_tokens(text)


class ModelServiceFactory:
    """
    Factory for creating model service instances.
    
    This class provides methods to create different types of model services
    based on configuration and available implementations.
    """
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> ModelService:
        """
        Create a model service from configuration.
        
        Args:
            config: Configuration for the model service
            
        Returns:
            Configured model service
            
        Raises:
            ValueError: If the configuration is invalid or the model type is not supported
        """
        model_type = config.get("model_type")
        
        if not model_type:
            raise ValueError("Model type must be specified in configuration")
            
        # Implement specific model service creation logic here
        # This would typically dispatch to other factory methods
        # based on the model_type
        
        raise ValueError(f"Unsupported model type: {model_type}") 