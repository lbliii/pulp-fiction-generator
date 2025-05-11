"""
Loader for agent tools.
"""

from typing import Any, Dict, List, Optional, Union

from .tool_registry import registry


class ToolLoader:
    """
    Responsible for loading and creating tool instances from configurations.
    
    This class handles the creation of tool instances based on configurations.
    """
    
    @staticmethod
    def load_tools(tool_configs: Optional[List[Union[str, Dict[str, Any]]]] = None) -> List[Any]:
        """
        Load tools from configurations.
        
        Args:
            tool_configs: List of tool configurations or tool names
            
        Returns:
            List of tool instances
            
        Raises:
            ValueError: If a tool configuration is invalid
        """
        if not tool_configs:
            return []
            
        tools = []
        
        for config in tool_configs:
            if isinstance(config, str):
                # Simple tool name
                tool = registry.create_tool(config)
                tools.append(tool)
            elif isinstance(config, dict):
                # Tool configuration with name and parameters
                name = config.get("name")
                if not name:
                    raise ValueError("Tool configuration must include a 'name' field")
                    
                # Extract tool-specific configuration
                tool_config = config.get("config", {})
                
                # Create the tool instance
                tool = registry.create_tool(name, **tool_config)
                tools.append(tool)
            else:
                raise ValueError(f"Invalid tool configuration type: {type(config)}")
                
        return tools 