"""
ModelService defines the interface for interacting with language models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class ModelService(ABC):
    """
    Abstract base class for model services.
    
    This class defines the interface that all model service implementations
    must adhere to, allowing for different model backends to be used
    interchangeably.
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
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        pass
    
    def tokenize(self, text: str) -> List[int]:
        """
        Tokenize text into token IDs. Default implementation returns empty list.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of token IDs
        """
        return []
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text. Default implementation uses tokenize().
        
        Args:
            text: The text to count tokens in
            
        Returns:
            Number of tokens
        """
        return len(self.tokenize(text))
    
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