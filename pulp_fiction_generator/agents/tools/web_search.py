"""
Web search tool for agents.

This module provides a tool for performing web searches from agents.
"""

from typing import Dict, List, Optional
import os
from crewai.tools import BaseTool
from pydantic import Field
from crewai_tools import SerperDevTool


class WebSearchTool(BaseTool):
    """
    Tool for performing web searches.
    
    This tool allows agents to perform web searches to find relevant information.
    Uses SerperDev API for search results.
    """
    
    name: str = "web_search"
    description: str = "Search the web for information on any topic to get up-to-date information"
    api_key: Optional[str] = Field(default=None, description="API key for the search service")
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """
        Perform a web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            String with search results
        """
        # Get API key from parameters or environment
        api_key = self.api_key or os.environ.get("SERPER_API_KEY")
        
        # Use the SerperDevTool for actual search results
        serper_tool = SerperDevTool(api_key=api_key)
        result = serper_tool.search(query, max_results=max_results)
        return result


def create_web_search_tool(**kwargs) -> WebSearchTool:
    """
    Factory function for creating a web search tool.
    
    Args:
        **kwargs: Arguments to pass to the WebSearchTool constructor
        
    Returns:
        WebSearchTool instance
    """
    return WebSearchTool(**kwargs) 