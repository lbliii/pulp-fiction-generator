"""
Factory for creating and configuring model services for the application.
"""

import os
from typing import Dict, Any, Optional

from .model_service import ModelService
from .ollama_adapter import OllamaAdapter

class ModelFactory:
    """
    Factory for creating and configuring model services.
    
    This class is responsible for creating and configuring model 
    services based on environment settings or explicit configuration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model factory.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    def create_model_service(self) -> ModelService:
        """
        Create and configure a model service based on environment settings.
        
        Returns:
            A configured model service
        """
        # Get model name from environment or config
        model_name = self.config.get("model", os.getenv("OLLAMA_MODEL", "llama3.2"))
        
        # Create and return the Ollama adapter
        return OllamaAdapter(
            model_name=model_name,
            num_threads=self._get_int_config("ollama_threads", "OLLAMA_THREADS"),
            num_gpu_layers=self._get_int_config("ollama_gpu_layers", "OLLAMA_GPU_LAYERS"),
            context_size=self._get_int_config("ollama_ctx_size", "OLLAMA_CTX_SIZE"),
            batch_size=self._get_int_config("ollama_batch_size", "OLLAMA_BATCH_SIZE")
        )
    
    def _get_int_config(self, config_key: str, env_var: str) -> Optional[int]:
        """
        Get an integer configuration value from config or environment.
        
        Args:
            config_key: Key in the config dictionary
            env_var: Environment variable name
            
        Returns:
            The integer value if found and valid, None otherwise
        """
        # Try to get from config first
        value = self.config.get(config_key)
        
        # If not in config, try environment
        if value is None:
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    value = int(env_value)
                except ValueError:
                    value = None
        
        return value 