"""
Configuration management system for the Pulp Fiction Generator.

This module provides a centralized Config class that handles:
1. Default configurations
2. Environment variable overrides
3. User configuration files
4. Configuration validation
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, TypeVar, Type, cast
from dataclasses import dataclass, field, asdict

# Type for configuration schemas
T = TypeVar('T', bound='ConfigSection')

@dataclass
class ConfigSection:
    """Base class for configuration sections"""
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create a configuration section from a dictionary"""
        # Filter the dictionary to only include fields that are part of the dataclass
        field_names = [f.name for f in cls.__dataclass_fields__.values()]
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration section to a dictionary"""
        return asdict(self)

@dataclass
class OllamaConfig(ConfigSection):
    """Ollama-specific configuration"""
    host: str = "http://localhost:11434"
    model: str = "llama3.2"
    threads: int = 8
    gpu_layers: int = 32
    ctx_size: int = 8192
    batch_size: int = 512

@dataclass
class AppConfig(ConfigSection):
    """General application configuration"""
    debug: bool = False
    log_level: str = "info"
    output_dir: str = "./output"
    genres_dir: str = "./pulp_fiction_generator/genres"
    enable_telemetry: bool = False
    
    def validate(self) -> List[str]:
        """Validate the application configuration"""
        errors = []
        
        # Validate log level
        valid_log_levels = ["debug", "info", "warning", "error", "critical"]
        if self.log_level.lower() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.log_level}. Must be one of {valid_log_levels}")
        
        # Validate paths
        output_dir = Path(self.output_dir)
        if not output_dir.exists() and not output_dir.parent.exists():
            errors.append(f"Output directory parent path does not exist: {output_dir.parent}")
        
        genres_dir = Path(self.genres_dir)
        if not genres_dir.exists():
            errors.append(f"Genres directory does not exist: {genres_dir}")
        
        return errors

@dataclass
class GenerationConfig(ConfigSection):
    """Configuration for story generation"""
    max_retry_count: int = 3
    generation_timeout: int = 300
    temperature: float = 0.7
    top_p: float = 0.9
    
    def validate(self) -> List[str]:
        """Validate the generation configuration"""
        errors = []
        
        # Validate numeric ranges
        if self.temperature < 0 or self.temperature > 2:
            errors.append(f"Temperature must be between 0 and 2, got {self.temperature}")
        
        if self.top_p < 0 or self.top_p > 1:
            errors.append(f"Top-p must be between 0 and 1, got {self.top_p}")
        
        if self.max_retry_count < 0:
            errors.append(f"Max retry count must be positive, got {self.max_retry_count}")
        
        if self.generation_timeout < 0:
            errors.append(f"Generation timeout must be positive, got {self.generation_timeout}")
        
        return errors

@dataclass
class AgentConfig(ConfigSection):
    """Configuration for agents"""
    enable_delegation: bool = False
    verbose: bool = True
    
    def validate(self) -> List[str]:
        """Validate the agent configuration"""
        # No specific validation rules for now
        return []

@dataclass
class CacheConfig(ConfigSection):
    """Configuration for model caching"""
    enable_cache: bool = True
    cache_dir: str = "./.cache"
    max_cache_size: int = 1024  # MB
    
    def validate(self) -> List[str]:
        """Validate the cache configuration"""
        errors = []
        
        # Validate paths
        cache_dir = Path(self.cache_dir)
        if not cache_dir.exists() and not cache_dir.parent.exists():
            errors.append(f"Cache directory parent path does not exist: {cache_dir.parent}")
        
        # Validate numeric ranges
        if self.max_cache_size <= 0:
            errors.append(f"Max cache size must be positive, got {self.max_cache_size}")
        
        return errors

@dataclass
class Config:
    """
    Main configuration class that aggregates all configuration sections.
    
    This class handles loading configuration from multiple sources in order of priority:
    1. Command-line arguments (highest priority)
    2. Environment variables
    3. User configuration file
    4. Default values (lowest priority)
    """
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    app: AppConfig = field(default_factory=AppConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Additional configurations can be loaded as needed
    _additional: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Configuration file paths
    _config_paths: List[Path] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize configuration after the dataclass is created"""
        # Set default configuration paths
        self._config_paths = [
            Path.home() / ".pulp-fiction" / "config.yaml",
            Path.cwd() / "config.yaml",
            Path.cwd() / ".pulp-fiction.yaml"
        ]
        
        # Load configuration from file
        self.load_from_file()
        
        # Load configuration from environment variables
        self.load_from_env()
    
    def load_from_file(self) -> bool:
        """
        Load configuration from the first available configuration file.
        
        Returns:
            True if a configuration file was loaded, False otherwise.
        """
        for config_path in self._config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = yaml.safe_load(f)
                    
                    if not config_data:
                        continue
                    
                    self._update_from_dict(config_data)
                    return True
                except Exception as e:
                    print(f"Error loading configuration from {config_path}: {e}")
        
        return False
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # Ollama config
        if os.environ.get("OLLAMA_HOST"):
            self.ollama.host = os.environ.get("OLLAMA_HOST")
        
        if os.environ.get("OLLAMA_MODEL"):
            self.ollama.model = os.environ.get("OLLAMA_MODEL")
        
        if os.environ.get("OLLAMA_THREADS"):
            self.ollama.threads = int(os.environ.get("OLLAMA_THREADS"))
        
        if os.environ.get("OLLAMA_GPU_LAYERS"):
            self.ollama.gpu_layers = int(os.environ.get("OLLAMA_GPU_LAYERS"))
        
        if os.environ.get("OLLAMA_CTX_SIZE"):
            self.ollama.ctx_size = int(os.environ.get("OLLAMA_CTX_SIZE"))
        
        if os.environ.get("OLLAMA_BATCH_SIZE"):
            self.ollama.batch_size = int(os.environ.get("OLLAMA_BATCH_SIZE"))
        
        # App config
        if os.environ.get("DEBUG"):
            self.app.debug = os.environ.get("DEBUG").lower() in ("true", "1", "yes")
        
        if os.environ.get("LOG_LEVEL"):
            self.app.log_level = os.environ.get("LOG_LEVEL")
        
        if os.environ.get("OUTPUT_DIR"):
            self.app.output_dir = os.environ.get("OUTPUT_DIR")
        
        if os.environ.get("GENRES_DIR"):
            self.app.genres_dir = os.environ.get("GENRES_DIR")
        
        # Generation config
        if os.environ.get("MAX_RETRY_COUNT"):
            self.generation.max_retry_count = int(os.environ.get("MAX_RETRY_COUNT"))
        
        if os.environ.get("GENERATION_TIMEOUT"):
            self.generation.generation_timeout = int(os.environ.get("GENERATION_TIMEOUT"))
        
        if os.environ.get("TEMPERATURE"):
            self.generation.temperature = float(os.environ.get("TEMPERATURE"))
        
        if os.environ.get("TOP_P"):
            self.generation.top_p = float(os.environ.get("TOP_P"))
        
        # Agent config
        if os.environ.get("ENABLE_AGENT_DELEGATION"):
            self.agent.enable_delegation = os.environ.get("ENABLE_AGENT_DELEGATION").lower() in ("true", "1", "yes")
        
        if os.environ.get("AGENT_VERBOSE"):
            self.agent.verbose = os.environ.get("AGENT_VERBOSE").lower() in ("true", "1", "yes")
        
        # Cache config
        if os.environ.get("ENABLE_CACHE"):
            self.cache.enable_cache = os.environ.get("ENABLE_CACHE").lower() in ("true", "1", "yes")
        
        if os.environ.get("CACHE_DIR"):
            self.cache.cache_dir = os.environ.get("CACHE_DIR")
        
        if os.environ.get("MAX_CACHE_SIZE"):
            self.cache.max_cache_size = int(os.environ.get("MAX_CACHE_SIZE"))
    
    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.
        
        Args:
            data: Dictionary with configuration values
        """
        # Update Ollama config
        if "ollama" in data:
            self.ollama = OllamaConfig.from_dict(data["ollama"])
        
        # Update app config
        if "app" in data:
            self.app = AppConfig.from_dict(data["app"])
        
        # Update generation config
        if "generation" in data:
            self.generation = GenerationConfig.from_dict(data["generation"])
        
        # Update agent config
        if "agent" in data:
            self.agent = AgentConfig.from_dict(data["agent"])
        
        # Update cache config
        if "cache" in data:
            self.cache = CacheConfig.from_dict(data["cache"])
        
        # Store additional configurations
        for key, value in data.items():
            if key not in ["ollama", "app", "generation", "agent", "cache"] and isinstance(value, dict):
                self._additional[key] = value
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Dictionary with plugin configuration, or empty dict if not found
        """
        return self._additional.get(plugin_id, {})
    
    def validate(self) -> List[str]:
        """
        Validate the configuration.
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        # Validate each section
        errors.extend(self.app.validate())
        errors.extend(self.generation.validate())
        errors.extend(self.agent.validate())
        errors.extend(self.cache.validate())
        
        # Add plugin validation here when needed
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        config_dict = {
            "ollama": self.ollama.to_dict(),
            "app": self.app.to_dict(),
            "generation": self.generation.to_dict(),
            "agent": self.agent.to_dict(),
            "cache": self.cache.to_dict()
        }
        
        # Add additional configurations
        for key, value in self._additional.items():
            config_dict[key] = value
        
        return config_dict
    
    def save_to_file(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save the configuration to a file.
        
        Args:
            path: Path to the file, or None to use the first default path
        """
        if path is None:
            path = self._config_paths[0]
        
        if isinstance(path, str):
            path = Path(path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the configuration
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
    
    def get_ollama_params(self) -> Dict[str, Any]:
        """
        Get Ollama parameters in the format expected by the OllamaAdapter.
        
        Returns:
            Dictionary with Ollama parameters
        """
        return {
            "num_thread": self.ollama.threads,
            "num_gpu": self.ollama.gpu_layers,
            "num_ctx": self.ollama.ctx_size,
            "num_batch": self.ollama.batch_size
        }


# Create a global configuration instance
config = Config() 