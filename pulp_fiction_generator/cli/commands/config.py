"""
Command for managing configuration.
"""

from typing import Optional, List, Dict, Any
import typer
from pathlib import Path
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import yaml

from ..base import SetupCommand
from ...utils.config import Config, config

console = Console()

class ConfigCommand(SetupCommand):
    """Manage configuration settings"""
    
    name = "config"
    help = "View and modify configuration settings"
    
    @classmethod
    def _run_impl(
        cls,
        action: str = typer.Argument(
            "show", help="Action to perform (show, validate, save, reset)"
        ),
        section: Optional[str] = typer.Option(
            None, "--section", "-s", help="Configuration section to display"
        ),
        output_file: Optional[str] = typer.Option(
            None, "--output", "-o", help="File to save configuration to (for save action)"
        ),
        format: str = typer.Option(
            "table", "--format", "-f", help="Output format (table, yaml)"
        ),
    ):
        """Manage configuration settings"""
        if action == "show":
            cls._show_config(section, format)
        elif action == "validate":
            cls._validate_config()
        elif action == "save":
            cls._save_config(output_file)
        elif action == "reset":
            cls._reset_config()
        else:
            cls.error(f"Unknown action: {action}")
            return 1
        
        return 0
    
    @classmethod
    def _show_config(cls, section: Optional[str], format: str):
        """Show the current configuration"""
        # Convert configuration to dictionary
        config_dict = config.to_dict()
        
        # If a section is specified, only show that section
        if section:
            if section not in config_dict:
                cls.error(f"Configuration section not found: {section}")
                return
            
            data = {section: config_dict[section]}
        else:
            data = config_dict
        
        # Display in the requested format
        if format == "yaml":
            yaml_str = yaml.dump(data, default_flow_style=False)
            console.print(yaml_str)
        else:  # table format
            cls._print_config_table(data)
    
    @classmethod
    def _print_config_table(cls, data: Dict[str, Any], parent_key: str = ""):
        """Print configuration as a table"""
        for section, values in data.items():
            section_key = f"{parent_key}.{section}" if parent_key else section
            
            if isinstance(values, dict):
                # Create a table for this section
                table = Table(title=f"Configuration: {section_key}")
                table.add_column("Setting", style="cyan")
                table.add_column("Value", style="green")
                table.add_column("Source", style="dim")
                
                # Add rows for each setting
                for key, value in values.items():
                    # Skip nested dictionaries, they'll get their own table
                    if not isinstance(value, dict):
                        # Determine the source of this setting
                        env_var = cls._get_env_var_for_setting(section, key)
                        if env_var and os.environ.get(env_var.upper()):
                            source = f"Environment ({env_var})"
                        else:
                            source = "Config file or default"
                            
                        table.add_row(key, str(value), source)
                
                console.print(table)
                console.print()
                
                # Process nested dicts recursively with their own tables
                for key, value in values.items():
                    if isinstance(value, dict):
                        cls._print_config_table({key: value}, section_key)
            else:
                # This should not happen with our config structure, but just in case
                console.print(f"{section_key}: {values}")
    
    @classmethod
    def _get_env_var_for_setting(cls, section: str, key: str) -> Optional[str]:
        """Map a configuration key to its corresponding environment variable"""
        # Define mappings from config keys to env vars
        mappings = {
            "ollama": {
                "host": "OLLAMA_HOST",
                "model": "OLLAMA_MODEL",
                "threads": "OLLAMA_THREADS",
                "gpu_layers": "OLLAMA_GPU_LAYERS",
                "ctx_size": "OLLAMA_CTX_SIZE",
                "batch_size": "OLLAMA_BATCH_SIZE",
            },
            "app": {
                "debug": "DEBUG",
                "log_level": "LOG_LEVEL",
                "output_dir": "OUTPUT_DIR",
                "genres_dir": "GENRES_DIR",
            },
            "generation": {
                "max_retry_count": "MAX_RETRY_COUNT",
                "generation_timeout": "GENERATION_TIMEOUT",
                "temperature": "TEMPERATURE",
                "top_p": "TOP_P",
            },
            "agent": {
                "enable_delegation": "ENABLE_AGENT_DELEGATION",
                "verbose": "AGENT_VERBOSE",
            },
            "cache": {
                "enable_cache": "ENABLE_CACHE",
                "cache_dir": "CACHE_DIR",
                "max_cache_size": "MAX_CACHE_SIZE",
            },
        }
        
        # Look up the mapping
        return mappings.get(section, {}).get(key)
    
    @classmethod
    def _validate_config(cls):
        """Validate the current configuration"""
        errors = config.validate()
        
        if errors:
            console.print(Panel("[bold red]Configuration has errors:[/bold red]", expand=False))
            for error in errors:
                console.print(f"[red]- {error}[/red]")
            return 1
        else:
            cls.success("Configuration is valid.")
            return 0
    
    @classmethod
    def _save_config(cls, output_file: Optional[str]):
        """Save the current configuration to a file"""
        try:
            # Determine the output file path
            if output_file:
                file_path = Path(output_file)
            else:
                # Default to the first config path (user home directory)
                file_path = config._config_paths[0]
            
            # Save the configuration
            config.save_to_file(file_path)
            
            cls.success(f"Configuration saved to {file_path}")
            return 0
        except Exception as e:
            cls.error(f"Failed to save configuration: {e}")
            return 1
    
    @classmethod
    def _reset_config(cls):
        """Reset configuration to defaults"""
        # Create a new config instance with defaults
        new_config = Config()
        
        # Display the default configuration
        console.print(Panel("[bold yellow]Default configuration:[/bold yellow]", expand=False))
        cls._print_config_table(new_config.to_dict())
        
        # Ask for confirmation
        if not typer.confirm("Reset configuration to these defaults?"):
            console.print("Operation cancelled.")
            return 0
        
        # Save the default configuration
        try:
            new_config.save_to_file()
            cls.success("Configuration reset to defaults.")
            return 0
        except Exception as e:
            cls.error(f"Failed to reset configuration: {e}")
            return 1 