"""
CrewAI-compatible adapter for Ollama.

This module provides a compatibility layer between our OllamaAdapter
and CrewAI's litellm-based interface.
"""

import os
import time
import json
from typing import Any, Dict, List, Mapping, Optional, Union, Type, TypeVar, Iterator, Generic

from pydantic import BaseModel

# Import the necessary components
from ..models.ollama_adapter import OllamaAdapter

# Type variable for Pydantic model
T = TypeVar('T', bound=BaseModel)

class CrewAIModelAdapter(Generic[T]):
    """
    Adapter that makes our OllamaAdapter compatible with CrewAI.
    
    This adapter provides a compatibility layer for using our OllamaAdapter
    with CrewAI, which uses litellm under the hood and expects specific
    provider prefixes for model names.
    """
    
    def __init__(
        self, 
        ollama_adapter: OllamaAdapter,
        model_prefix: str = "ollama/",
        response_format: Optional[Type[T]] = None,
        stream: bool = False
    ):
        """
        Initialize the CrewAI adapter.
        
        Args:
            ollama_adapter: The OllamaAdapter instance to wrap
            model_prefix: The prefix to add to the model name for litellm
            response_format: Optional Pydantic model class for structured responses
            stream: Whether to enable streaming by default
        """
        self.ollama_adapter = ollama_adapter
        self.model_prefix = model_prefix
        self.model = f"{model_prefix}{ollama_adapter.model_name}"
        self.response_format = response_format
        self.stream = stream
        
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
    ) -> Dict[str, Any]:
        """
        Call the model with the provided messages.
        
        Args:
            messages: The messages to process
            kwargs: Additional parameters
            
        Returns:
            The response in LiteLLM format
        """
        # Apply the response format if specified and not overridden in kwargs
        if self.response_format and "response_format" not in kwargs:
            kwargs["response_format"] = {"type": "json"}
            
        # Apply streaming setting if not overridden
        if "stream" not in kwargs:
            kwargs["stream"] = self.stream
            
        # Get the response from the Ollama adapter
        raw_response = self.ollama_adapter.generate(
            messages=messages,
            **kwargs
        )
        
        # Format the response to match LiteLLM's expected format
        response = {
            "id": f"gen_{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": raw_response,
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": -1,  # Not available from Ollama
                "completion_tokens": -1,  # Not available from Ollama
                "total_tokens": -1  # Not available from Ollama
            }
        }
        
        # Parse as structured response if needed
        if self.response_format and not kwargs.get("stream", False):
            try:
                # Try to parse the response as JSON
                parsed_json = json.loads(raw_response)
                # Validate and convert to the Pydantic model
                structured_response = self.response_format.parse_obj(parsed_json)
                # Return both the raw response format and the structured data
                response["structured_data"] = structured_response
            except Exception as e:
                # Log the error but continue with the unstructured response
                print(f"Failed to parse structured response: {e}")
        
        return response

    def stream_call(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream responses from the model.
        
        Args:
            messages: The messages to process
            kwargs: Additional parameters
            
        Returns:
            Iterator yielding response chunks
        """
        # Force streaming mode
        kwargs["stream"] = True
        
        # Get streaming response from Ollama adapter
        for chunk in self.ollama_adapter.stream_generate(
            messages=messages,
            **kwargs
        ):
            # Format the chunk to match LiteLLM's expected format for streaming
            formatted_chunk = {
                "id": f"gen_{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": self.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant",
                            "content": chunk,
                        },
                        "finish_reason": None
                    }
                ]
            }
            
            yield formatted_chunk
    
    def completion(
        self, 
        model: str = None, 
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Type[BaseModel]] = None,
        stream: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion compatible with litellm/CrewAI.
        
        Args:
            model: The model name (will be ignored in favor of self.model)
            messages: List of messages to process
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            response_format: Optional Pydantic model for structured response
            stream: Whether to stream the response
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
            
        if response_format is not None:
            params["response_format"] = response_format
            
        if stream is not None:
            params["stream"] = stream
            
        return self.call(**params) 