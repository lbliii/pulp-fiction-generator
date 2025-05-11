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


# Ensure these methods are part of an actual ModelService implementation class
class ConcreteModelService(ModelService):
    """
    Concrete implementation of ModelService interface.
    
    This provides a complete implementation of all methods in the ModelService interface.
    """
    
    def __init__(self, config: Dict[str, Any], adapter):
        """
        Initialize the concrete model service.
        
        Args:
            config: Configuration for the model service
            adapter: Adapter for the underlying model implementation
        """
        self.config = config
        self.adapter = adapter
        self.default_model_name = config.get("default_model_name", "gpt-3.5-turbo")
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate text from a prompt."""
        # Implementation
        return "Generated text"
    
    def batch_generate(self, prompts: List[str], parameters: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate text for multiple prompts."""
        # Implementation
        return ["Generated text" for _ in prompts]
    
    def chat(self, messages: List[Dict[str, str]], parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response in a chat context."""
        # Implementation
        return "Chat response"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        # Implementation
        return {"model": self.default_model_name}
    
    def tokenize(self, text: str) -> List[int]:
        """Tokenize text into token IDs."""
        # Implementation
        return []
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text."""
        # Implementation
        return 0
    
    def get_planning_llm(self):
        """
        Get an LLM instance specifically for planning tasks.
        
        Planning typically requires more reasoning capabilities, 
        so this method configures an appropriate model.
        
        Returns:
            An LLM instance suitable for planning tasks
        """
        # Use the model with best reasoning capabilities 
        # (planning typically works best with a good reasoning model)
        planning_model = self.config.get("planning_model_name", self.default_model_name)
        
        # Configure planning-specific parameters
        planning_config = {
            "model": planning_model,
            "temperature": 0.2,  # Lower temperature for more focused planning
            "max_tokens": 2000,  # Plans may need more tokens
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**planning_config)
    
    def get_function_calling_llm(self):
        """
        Get an LLM instance optimized for function calling.
        
        Function calling requires specific capabilities to parse and generate
        structured outputs for tool use, so this method configures an appropriate model.
        
        Returns:
            An LLM instance suitable for function calling
        """
        # Use model that's best for function calling
        function_model = self.config.get("function_calling_model_name", self.default_model_name)
        
        # Configure function calling specific parameters
        function_config = {
            "model": function_model,
            "temperature": 0.1,  # Low temperature for more deterministic outputs
            "max_tokens": 1500,  # Reasonable token limit for function outputs
            "tools_format": "json",  # Ensure proper JSON formatting for tools
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**function_config)
    
    def get_story_outline_llm(self):
        """
        Get an LLM instance optimized for generating structured story outlines.
        
        Returns:
            An LLM instance configured for generating story outlines
        """
        from ..models.schema import StoryOutline
        
        # Configure story outline specific parameters
        outline_config = {
            "model": self.default_model_name,
            "temperature": 0.7,  # Moderate temperature for creativity with consistency
            "max_tokens": 2500,  # Generous token limit for detailed outlines
            "response_format": StoryOutline,  # Use the StoryOutline Pydantic model
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**outline_config)
    
    def get_worldbuilding_llm(self):
        """
        Get an LLM instance optimized for worldbuilding with structured output.
        
        Returns:
            An LLM instance configured for worldbuilding
        """
        from ..models.schema import WorldBuildingSchema
        
        # Configure worldbuilding specific parameters
        worldbuilding_config = {
            "model": self.default_model_name,
            "temperature": 0.75,  # Higher temperature for more creative worldbuilding
            "max_tokens": 3000,  # Large token limit for detailed world descriptions
            "response_format": WorldBuildingSchema,  # Use the WorldBuildingSchema Pydantic model
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**worldbuilding_config)
    
    def get_creative_llm(self):
        """
        Get an LLM instance optimized for creative generation.
        
        Returns:
            An LLM instance configured for creative content
        """
        # Configure creative generation specific parameters
        creative_config = {
            "model": self.default_model_name,
            "temperature": 0.8,  # Higher temperature for more creative outputs
            "max_tokens": 2000,  # Reasonable token limit for creative content
            "top_p": 0.9,  # Nucleus sampling for more diverse outputs
            "frequency_penalty": 0.5,  # Reduce repetition
            "presence_penalty": 0.5,  # Encourage diverse topics
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**creative_config)
    
    def get_streaming_llm(self):
        """
        Get an LLM instance configured for streaming responses.
        
        Returns:
            An LLM instance with streaming enabled
        """
        # Configure streaming specific parameters
        streaming_config = {
            "model": self.default_model_name,
            "temperature": 0.7,  # Moderate temperature for general use
            "stream": True,  # Enable streaming
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**streaming_config)
    
    def get_historical_analysis_llm(self):
        """
        Get an LLM instance optimized for historical analysis with structured output.
        
        Returns:
            An LLM instance configured for historical analysis
        """
        from ..models.schema import DateLocaleAnalysis
        
        # Configure historical analysis specific parameters
        history_config = {
            "model": self.default_model_name,
            "temperature": 0.3,  # Lower temperature for more factual outputs
            "max_tokens": 2000,  # Reasonable token limit for analysis
            "response_format": DateLocaleAnalysis,  # Use the DateLocaleAnalysis Pydantic model
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**history_config)
    
    def get_feedback_llm(self):
        """
        Get an LLM instance optimized for providing structured feedback.
        
        Returns:
            An LLM instance configured for feedback
        """
        from ..models.schema import StoryFeedback
        
        # Configure feedback specific parameters
        feedback_config = {
            "model": self.default_model_name,
            "temperature": 0.4,  # Moderate-low temperature for balanced feedback
            "max_tokens": 1500,  # Reasonable token limit for feedback
            "response_format": StoryFeedback,  # Use the StoryFeedback Pydantic model
        }
        
        # Create and return the LLM instance
        return self.adapter.get_llm(**feedback_config) 