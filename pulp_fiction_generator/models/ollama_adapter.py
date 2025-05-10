"""
OllamaAdapter implements the ModelService interface for Ollama.
"""

import json
import os
from typing import Any, Dict, List, Optional

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
        # Use the centralized configuration with overrides if provided
        self.model_name = model_name or config.ollama.model
        self.api_base = api_base or config.ollama.host
        self.timeout = timeout
        
        # Get default resource configurations from config
        self.default_threads = config.ollama.threads
        self.default_gpu_layers = config.ollama.gpu_layers
        self.default_ctx_size = config.ollama.ctx_size
        self.default_batch_size = config.ollama.batch_size
    
    def get_default_ollama_params(self) -> Dict[str, Any]:
        """
        Get default Ollama parameters from configuration.
        
        Returns:
            Dictionary with default Ollama parameters
        """
        return config.get_ollama_params()
    
    def generate(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text from a prompt using Ollama's generate endpoint.
        
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
        
        # Make the request
        response = requests.post(
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
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt to generate from
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (higher = more random)
            max_tokens: Maximum number of tokens to generate
            stop: Sequences that stop generation
            **kwargs: Additional parameters passed to the API
            
        Returns:
            The generated text
        """
        response = self.api_generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop_sequences=stop,
            params=kwargs.get("params", None),
            timeout_seconds=kwargs.get("timeout_seconds", 120)
        )
        
        return response.get("response", "")
    
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