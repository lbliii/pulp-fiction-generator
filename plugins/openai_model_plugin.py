"""
OpenAI model plugin for Pulp Fiction Generator.

This plugin adds support for OpenAI API models to the generator.
"""

import os
from typing import Dict, List, Any, Type
from pulp_fiction_generator.plugins.base import ModelPlugin
from pulp_fiction_generator.models.model_service import ModelService

class OpenAIModelService(ModelService):
    """Model service for OpenAI API"""
    
    def __init__(self, api_key=None, model="gpt-4", **kwargs):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.config = kwargs
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize the OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package is not installed. Install with 'pip install openai'")
    
    def generate(self, prompt, parameters=None):
        """Generate a response from the model"""
        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": parameters.get("temperature", 0.7) if parameters else 0.7,
            "max_tokens": parameters.get("max_tokens", 1000) if parameters else 1000
        }
        
        response = self.client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def get_model_info(self):
        """Get information about the model"""
        return {
            "name": self.model,
            "provider": "OpenAI",
            "type": "chat",
            "capabilities": ["text-generation", "chat-completion"]
        }
    
    def get_token_count(self, text):
        """Get the token count for a text"""
        # This is a simple estimation for demonstration
        # In a real implementation, you would use tiktoken or similar
        return len(text.split()) * 1.33
    
    def get_default_parameters(self):
        """Get default parameters for the model"""
        return {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }

class OpenAIModelPlugin(ModelPlugin):
    """OpenAI API model plugin"""
    
    plugin_id = "openai"
    plugin_name = "OpenAI GPT Models"
    plugin_description = "Integration with OpenAI's GPT models via their API"
    plugin_version = "1.0.0"
    
    def get_model_service(self) -> Type:
        """Get the model service class"""
        return OpenAIModelService
    
    def get_supported_features(self) -> List[str]:
        """Get a list of features supported by this model"""
        return [
            "text-generation",
            "chat-completion",
            "prompt-templates",
            "temperature-control",
            "top-p-sampling"
        ]
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this model"""
        return {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "OpenAI API key"
                },
                "model": {
                    "type": "string",
                    "description": "Model name to use",
                    "enum": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                    "default": "gpt-4"
                },
                "temperature": {
                    "type": "number",
                    "description": "Sampling temperature",
                    "minimum": 0,
                    "maximum": 2,
                    "default": 0.7
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum tokens to generate",
                    "minimum": 1,
                    "default": 1000
                }
            },
            "required": ["api_key"]
        } 