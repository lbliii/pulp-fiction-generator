"""
OllamaAdapter implements the ModelService interface for Ollama.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union, Callable, Iterator

import httpx
import requests
import signal
from contextlib import contextmanager
import time

from .model_service import ModelService
from ..utils.config import config


class TimeoutError(Exception):
    """Exception raised when a function call times out"""
    pass

class ConnectionError(Exception):
    """Exception raised when a connection to Ollama API fails"""
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timing out function calls"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Function call timed out after {seconds} seconds")
    
    # Set the timeout handler
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Reset the alarm and restore the original handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

class OllamaAdapter(ModelService):
    """
    Adapter for Ollama API implementing the ModelService interface.
    
    This adapter allows the application to interact with Ollama's API for
    text generation, providing a consistent interface regardless of the
    underlying model implementation.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Initialize the Ollama adapter.
        
        Args:
            model_name: Name of the Ollama model to use, overrides config if provided
            api_base: Base URL for the Ollama API, overrides config if provided
            timeout: Request timeout in seconds
        """
        # Check environment variables first, then use provided args, then fallback to config
        env_model = os.environ.get("OLLAMA_MODEL")
        env_host = os.environ.get("OLLAMA_HOST")
        
        # Set model name with priority: argument > environment > config
        self.model_name = model_name or env_model or config.ollama.model
        
        # Set API base with priority: argument > environment > config
        self.api_base = api_base or env_host or config.ollama.host
        
        self.timeout = timeout
        
        # Get default resource configurations from config
        self.default_threads = config.ollama.threads
        self.default_gpu_layers = config.ollama.gpu_layers
        self.default_ctx_size = config.ollama.ctx_size
        self.default_batch_size = config.ollama.batch_size
        
        # Verify connection on initialization
        self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """
        Verify that the Ollama API is reachable and the requested model exists.
        
        Returns:
            True if connection is successful
            
        Raises:
            ConnectionError: If connection to Ollama API fails
            ValueError: If the requested model is not available
        """
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=10)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama API returned error status: {response.status_code}")
            
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            # Check if the model exists (allowing for tags/versions)
            model_found = False
            base_model_name = self.model_name.split(":")[0] if ":" in self.model_name else self.model_name
            
            for name in model_names:
                if name == self.model_name or name.startswith(f"{base_model_name}:"):
                    model_found = True
                    break
            
            if not model_found:
                # Try to provide a helpful error message with available models
                available_models = ', '.join(model_names) if model_names else "No models found"
                raise ValueError(f"Model '{self.model_name}' not found. Available models: {available_models}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API at {self.api_base}: {str(e)}. Is Ollama running?")
    
    def get_default_ollama_params(self) -> Dict[str, Any]:
        """
        Get default Ollama parameters from configuration.
        
        Returns:
            Dictionary with default Ollama parameters
        """
        return config.get_ollama_params()
    
    def generate(self, messages, **kwargs):
        """
        Generate a response for the given messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            The generated text response
        """
        # Extract system message if present
        system_content = None
        prompt_messages = []
        
        for message in messages:
            if message.get("role") == "system":
                system_content = message.get("content", "")
            else:
                prompt_messages.append(message)
        
        # Format the conversation for Ollama
        formatted_prompt = self._format_messages(prompt_messages)
        
        # Get parameters
        stream = kwargs.get("stream", False)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", None)
        response_format = kwargs.get("response_format", None)
        
        # Handle streaming separately
        if stream:
            return self.stream_generate(messages, **kwargs)
        
        # Prepare request data
        request_data = {
            "model": self.model_name,
            "prompt": formatted_prompt,
            "temperature": temperature,
            "raw": True,  # Get raw completion without prompt
        }
        
        # Add system prompt if provided
        if system_content:
            request_data["system"] = system_content
            
        # Add max tokens if provided
        if max_tokens:
            request_data["num_predict"] = max_tokens
            
        # Add structure format instructions if specified
        if response_format and response_format.get("type") == "json":
            # Enhance system prompt with JSON instructions
            json_instruction = "\nYou must respond with valid JSON only, no other text."
            if system_content:
                request_data["system"] = system_content + json_instruction
            else:
                request_data["system"] = json_instruction
        
        # Call Ollama API
        response = self._call_api("/api/generate", request_data)
        
        # Extract the response text
        return response.get("response", "")
        
    def stream_generate(self, messages, **kwargs):
        """
        Stream a response for the given messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters to pass to the model
            
        Yields:
            Chunks of the generated response
        """
        # Extract system message if present
        system_content = None
        prompt_messages = []
        
        for message in messages:
            if message.get("role") == "system":
                system_content = message.get("content", "")
            else:
                prompt_messages.append(message)
        
        # Format the conversation for Ollama
        formatted_prompt = self._format_messages(prompt_messages)
        
        # Get parameters
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", None)
        response_format = kwargs.get("response_format", None)
        
        # Prepare request data
        request_data = {
            "model": self.model_name,
            "prompt": formatted_prompt,
            "temperature": temperature,
            "raw": True,  # Get raw completion without prompt
            "stream": True  # Enable streaming
        }
        
        # Add system prompt if provided
        if system_content:
            request_data["system"] = system_content
            
        # Add max tokens if provided
        if max_tokens:
            request_data["num_predict"] = max_tokens
            
        # Add structure format instructions if specified
        if response_format and response_format.get("type") == "json":
            # Enhance system prompt with JSON instructions
            json_instruction = "\nYou must respond with valid JSON only, no other text."
            if system_content:
                request_data["system"] = system_content + json_instruction
            else:
                request_data["system"] = json_instruction
        
        # Stream from Ollama API
        response = self._stream_api("/api/generate", request_data)
        
        # Process the streaming response
        for chunk in response:
            if "response" in chunk:
                yield chunk["response"]
                
    def _stream_api(self, endpoint, data):
        """
        Call the Ollama API with streaming.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Yields:
            Chunks of the streaming response
        """
        import requests
        import json
        from requests.exceptions import RequestException
        
        url = f"{self.api_base}{endpoint}"
        
        try:
            # Make the streaming request
            with requests.post(
                url,
                json=data,
                stream=True,
                timeout=self.timeout
            ) as response:
                # Check for errors
                response.raise_for_status()
                
                # Process the streaming response
                buffer = ""
                for line in response.iter_lines():
                    if line:
                        # Decode the line
                        buffer += line.decode("utf-8")
                        
                        # Process any complete JSON objects
                        while "\n" in buffer:
                            line_json, buffer = buffer.split("\n", 1)
                            try:
                                chunk = json.loads(line_json)
                                yield chunk
                            except json.JSONDecodeError:
                                # Skip invalid JSON
                                pass
                
                # Process any remaining data
                if buffer:
                    try:
                        chunk = json.loads(buffer)
                        yield chunk
                    except json.JSONDecodeError:
                        # Skip invalid JSON
                        pass
                        
        except RequestException as e:
            # Handle request exceptions
            print(f"Error streaming from Ollama API: {e}")
            raise
                
    def _format_messages(self, messages):
        """
        Format messages for Ollama's API.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted conversation string
        """
        formatted = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
            # Ignore system messages as they're handled separately
        
        # Join with double newlines for clear separation
        return "\n\n".join(formatted)
        
    def _call_api(self, endpoint, data=None, method="POST"):
        """
        Call the Ollama API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            method: HTTP method
            
        Returns:
            API response as a dictionary
        """
        # ... existing code ...
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response in a chat context using Ollama's chat endpoint.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            parameters: Optional generation parameters
            
        Returns:
            The generated response
        """
        chat_url = f"{self.api_base}/api/chat"
        
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        
        # Initialize options with default parameters
        payload["options"] = self.get_default_ollama_params()
        
        # Add any additional parameters
        if parameters:
            # Check for Ollama resource parameters
            if "ollama_params" in parameters:
                for key, value in parameters["ollama_params"].items():
                    payload["options"][key] = value
                # Remove the ollama_params to prevent it from being added directly
                ollama_params = parameters.pop("ollama_params")
            
            # Add remaining parameters
            payload.update({k: v for k, v in parameters.items() if k not in ["model", "messages", "stream"]})
        
        # Make the request
        response = requests.post(
            chat_url, 
            json=payload,
            timeout=self.timeout
        )
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}, {response.text}")
        
        # Parse the response
        response_data = response.json()
        
        return response_data.get("message", {}).get("content", "")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently configured model.
        
        Returns:
            Dictionary with model information
        
        Raises:
            Exception: If the model cannot be found or the API request fails
        """
        # First check if the model exists
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            if response.status_code != 200:
                raise Exception(f"Failed to get model list: {response.status_code} - {response.text}")
            
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            # Check if the model exists (allowing for tags/versions)
            model_found = False
            for name in model_names:
                if name == self.model_name or name.startswith(f"{self.model_name}:"):
                    model_found = True
                    break
            
            if not model_found:
                raise Exception(f"Model '{self.model_name}' not found. Available models: {', '.join(model_names)}")
            
            # Now get details about the specific model
            show_url = f"{self.api_base}/api/show"
            payload = {"name": self.model_name}
            
            model_response = requests.post(show_url, json=payload)
            if model_response.status_code != 200:
                # If we can't get details but we know the model exists, return a simplified result
                return {"name": self.model_name, "exists": True}
            
            return model_response.json()
        except Exception as e:
            if "Connection refused" in str(e):
                raise Exception(f"Failed to connect to Ollama API: {e}. Is Ollama running?")
            raise
    
    def api_generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 120,
    ) -> Dict[str, Any]:
        """
        Generate text using the Ollama API directly.
        
        Args:
            prompt: The prompt to generate from
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (higher = more random)
            max_tokens: Maximum number of tokens to generate
            stop_sequences: Sequences that stop generation
            params: Additional model parameters
            timeout_seconds: Timeout in seconds for the API call
            
        Returns:
            Dictionary with the API response
            
        Raises:
            Exception: If the API request fails
        """
        # Build the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": self.get_default_ollama_params().copy()
        }
        
        # Add optional parameters
        if system_prompt:
            payload["system"] = system_prompt
            
        if temperature is not None:
            payload["options"]["temperature"] = temperature
            
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
            
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences
            
        # Update with any additional parameters
        if params:
            payload["options"].update(params)
        
        # Make the API request with timeout
        try:
            with timeout(timeout_seconds):
                response = requests.post(f"{self.api_base}/api/generate", json=payload)
        except TimeoutError:
            raise Exception(f"Ollama API request timed out after {timeout_seconds} seconds")
        
        if response.status_code != 200:
            raise Exception(f"Failed to generate text: {response.status_code} - {response.text}")
        
        return response.json()
    
    def generate_with_system(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Generate text with an optional system prompt.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop: Stop sequences to end generation
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            If stream=False: The generated text
            If stream=True: An iterator of text chunks
        """
        # Create parameters dictionary
        params = {
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
            
        if stop is not None:
            params["stop"] = stop
            
        # If system prompt is provided, use it
        if system_prompt:
            params["system"] = system_prompt
            
        return self.generate(prompt, params, stream=stream)
    
    async def generate_async(
        self, 
        prompt: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text asynchronously from a prompt.
        
        Args:
            prompt: The input text to generate from
            parameters: Optional generation parameters
            
        Returns:
            The generated text
        """
        generate_url = f"{self.api_base}/api/generate"
        
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        # Initialize options with default parameters
        payload["options"] = self.get_default_ollama_params()
        
        # Add any additional parameters
        if parameters:
            # Check for Ollama resource parameters
            if "ollama_params" in parameters:
                for key, value in parameters["ollama_params"].items():
                    payload["options"][key] = value
                # Remove the ollama_params to prevent it from being added directly
                ollama_params = parameters.pop("ollama_params")
            
            # Add remaining parameters
            payload.update({k: v for k, v in parameters.items() if k not in ["model", "prompt", "stream"]})
        
        # Make the async request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                generate_url, 
                json=payload,
                timeout=self.timeout
            )
            
            # Check for errors
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code}, {response.text}")
            
            # Parse the response
            response_data = response.json()
            
            return response_data.get("response", "")
    
    def get_planning_llm(self):
        """
        Get an LLM instance specifically for planning tasks.
        
        Planning typically requires more reasoning capabilities, 
        so this method configures an appropriate model.
        
        Returns:
            An LLM instance suitable for planning tasks
        """
        # Create a version of this adapter configured for planning
        # In a more complete implementation, this would return a proper LLM instance
        # but for now we'll just return self to fix the immediate error
        return self
    
    def get_function_calling_llm(self):
        """
        Get an LLM instance optimized for function calling.
        
        Function calling requires specific capabilities to parse and generate
        structured outputs for tool use.
        
        Returns:
            An LLM instance suitable for function calling
        """
        # Create a version of this adapter configured for function calling
        # Similar to the planning LLM, we'll return self for now
        return self 