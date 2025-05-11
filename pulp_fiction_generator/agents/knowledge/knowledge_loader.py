"""
Loader for agent knowledge sources.
"""

from typing import Any, Dict, List, Optional, Union

from .knowledge_registry import registry


class KnowledgeLoader:
    """
    Responsible for loading and creating knowledge source instances from configurations.
    
    This class handles the creation of knowledge source instances based on configurations.
    """
    
    @staticmethod
    def load_sources(source_configs: Optional[List[Union[str, Dict[str, Any]]]] = None) -> List[Any]:
        """
        Load knowledge sources from configurations.
        
        Args:
            source_configs: List of knowledge source configurations or source names
            
        Returns:
            List of knowledge source instances
            
        Raises:
            ValueError: If a knowledge source configuration is invalid
        """
        if not source_configs:
            return []
            
        sources = []
        
        for config in source_configs:
            if isinstance(config, str):
                # Simple source name
                source = registry.create_source(config)
                sources.append(source)
            elif isinstance(config, dict):
                # Source configuration with name and parameters
                name = config.get("name")
                if not name:
                    raise ValueError("Knowledge source configuration must include a 'name' field")
                    
                # Extract source-specific configuration
                source_config = config.get("config", {})
                
                # Create the source instance
                source = registry.create_source(name, **source_config)
                sources.append(source)
            else:
                raise ValueError(f"Invalid knowledge source configuration type: {type(config)}")
                
        return sources 