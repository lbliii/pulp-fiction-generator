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
    ):
        """
        Process messages and return a response.
        
        Args:
            messages: The messages to process
            kwargs: Additional parameters
            
        Returns:
            The response in LiteLLM format
        """
        # Check if streaming is requested in kwargs
        stream = kwargs.pop("stream", self.stream)
        # Allow overriding the response format
        response_format = kwargs.pop("response_format", self.response_format)
        
        params = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        
        if stream:
            return self._handle_streaming_response(params)
        else:
            return self._handle_non_streaming_response(params, response_format)
        
    def _handle_non_streaming_response(self, params, response_format=None):
        """
        Handle processing non-streaming response.
        
        Args:
            params: Parameters for the call
            response_format: Optional Pydantic model for structured response
            
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
        
        # Add response format information if provided
        if response_format:
            # Enhance the system message with the expected response format
            format_instructions = self._get_format_instructions(response_format)
            if system_message:
                system_message = f"{system_message}\n\n{format_instructions}"
            else:
                system_message = format_instructions
        
        # Call the OllamaAdapter with the extracted message
        start_time = time.time()
        response_text = self.ollama_adapter.generate_with_system(
            prompt=user_message,
            system_prompt=system_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        end_time = time.time()
        
        # Parse response as Pydantic model if requested
        if response_format and response_text:
            try:
                # Try to extract JSON from the response
                content = self._extract_json(response_text)
                if content:
                    # Parse with the provided model
                    parsed_response = response_format.model_validate(content)
                    # Convert back to a formatted string for CrewAI
                    response_text = parsed_response.model_dump_json(indent=2)
            except Exception as e:
                # If parsing fails, add a note to the response but still return the text
                response_text = f"{response_text}\n\n[Failed to parse as structured response: {str(e)}]"
        
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
    
    def _handle_streaming_response(self, params):
        """
        Handle processing streaming response.
        
        Args:
            params: Parameters for the call
            
        Returns:
            A streaming response iterator in LiteLLM format
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
        
        # Call the OllamaAdapter with streaming enabled
        chunk_generator = self.ollama_adapter.generate_with_system(
            prompt=user_message,
            system_prompt=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Create an iterator that yields streaming chunks in LiteLLM format
        return self._create_streaming_iterator(chunk_generator)
    
    def _create_streaming_iterator(self, chunk_generator):
        """
        Create an iterator that yields streaming chunks in LiteLLM format.
        
        Args:
            chunk_generator: Generator of text chunks
            
        Returns:
            Iterator yielding chunks in LiteLLM format
        """
        for i, chunk in enumerate(chunk_generator):
            yield {
                "id": f"adapter-stream-{int(time.time())}-{i}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": self.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "role": "assistant" if i == 0 else None,
                            "content": chunk
                        },
                        "finish_reason": None
                    }
                ]
            }
    
    def _get_format_instructions(self, model_class: Type[BaseModel]) -> str:
        """
        Generate format instructions for a Pydantic model.
        
        Args:
            model_class: The Pydantic model class
            
        Returns:
            Instructions string for the model
        """
        schema = model_class.model_json_schema()
        schema_str = json.dumps(schema, indent=2)
        
        instructions = (
            "Respond with a JSON object that conforms to the following schema. "
            "Do not include any explanation or text before or after the JSON object. "
            "Make sure your response is valid JSON.\n\n"
            f"Schema:\n{schema_str}"
        )
        
        # Add examples if the model has them (not implemented here)
        
        return instructions
    
    def _extract_json(self, text: str) -> Dict:
        """
        Extract JSON from a text response.
        
        Args:
            text: The text to extract JSON from
            
        Returns:
            Parsed JSON object or None if extraction fails
        """
        # Try to find JSON content within markdown code blocks
        import re
        
        # Look for JSON in markdown code blocks first
        json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_pattern, text)
        
        if matches:
            # Try to parse the largest match (most likely the complete JSON)
            matches.sort(key=len, reverse=True)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # If no JSON found in code blocks, try to parse the entire response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # As a last resort, look for lines that might be JSON
            for line in text.splitlines():
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
        
        # If we get here, we couldn't extract JSON
        raise ValueError("Could not extract valid JSON from response")
    
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