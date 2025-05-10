"""
CrewAI-compatible adapter for Ollama.

This module provides a compatibility layer between our OllamaAdapter
and CrewAI's litellm-based interface.
"""

import os
import time
from typing import Any, Dict, List, Mapping, Optional, Union

# Import the necessary components
from ..models.ollama_adapter import OllamaAdapter


class CrewAIModelAdapter:
    """
    Adapter that makes our OllamaAdapter compatible with CrewAI.
    
    This adapter provides a compatibility layer for using our OllamaAdapter
    with CrewAI, which uses litellm under the hood and expects specific
    provider prefixes for model names.
    """
    
    def __init__(
        self, 
        ollama_adapter: OllamaAdapter,
        model_prefix: str = "ollama/"
    ):
        """
        Initialize the CrewAI adapter.
        
        Args:
            ollama_adapter: The OllamaAdapter instance to wrap
            model_prefix: The prefix to add to the model name for litellm
        """
        self.ollama_adapter = ollama_adapter
        self.model_prefix = model_prefix
        self.model = f"{model_prefix}{ollama_adapter.model_name}"
        
    def __call__(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """
        Make the class callable directly for CrewAI.
        
        Args:
            messages: The messages to process
            kwargs: Additional parameters
            
        Returns:
            The response in LiteLLM format
        """
        return self.call(messages=messages, **kwargs)
    
    def call(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """
        Process messages and return a response.
        
        Args:
            messages: The messages to process
            kwargs: Additional parameters
            
        Returns:
            The response in LiteLLM format
        """
        params = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        return self._handle_non_streaming_response(params)
        
    def _handle_non_streaming_response(self, params):
        """
        Handle processing non-streaming response.
        
        Args:
            params: Parameters for the call
            
        Returns:
            The response in LiteLLM format
        """
        # Extract the message content
        if not params.get("messages"):
            raise ValueError("No messages provided")
            
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens")
            
        # Get the final user message and optionally system message
        user_message = None
        system_message = None
        for message in params["messages"]:
            if message.get("role") == "user":
                user_message = message.get("content", "")
            elif message.get("role") == "system":
                system_message = message.get("content", "")
        
        if not user_message:
            raise ValueError("No user message found in messages")
        
        # Call the OllamaAdapter with the extracted message
        start_time = time.time()
        response_text = self.ollama_adapter.generate(
            prompt=user_message,
            system_prompt=system_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        end_time = time.time()
        
        # Format the response to match litellm's expected structure
        response = {
            "id": f"adapter-{int(time.time())}",
            "object": "chat.completion",
            "created": int(start_time),
            "model": self.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # We don't track these
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        return response
    
    def completion(
        self, 
        model: str = None, 
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion compatible with litellm/CrewAI.
        
        Args:
            model: The model name (will be ignored in favor of self.model)
            messages: List of messages to process
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            A response dict compatible with litellm's format
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
            
        return self._handle_non_streaming_response(params) 