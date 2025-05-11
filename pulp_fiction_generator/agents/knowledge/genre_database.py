"""
Genre database knowledge source for agents.

This module provides a knowledge source for genre-specific information.
"""

from typing import Dict, List, Optional, Any
from pydantic import Field
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource


class GenreDatabaseKnowledge(BaseKnowledgeSource):
    """
    Knowledge source for genre information.
    
    This knowledge source provides access to genre-specific information and tropes.
    """
    
    genre: str = Field(default="generic", description="Genre to focus on")
    
    def load_content(self) -> Dict[str, str]:
        """
        Load the genre content.
        
        Returns:
            Dictionary mapping content IDs to content
        """
        genre_info = self._get_genre_info()
        return {f"genre_{self.genre}": genre_info}
    
    def validate_content(self, content: Any) -> bool:
        """
        Validate that the content is in the correct format.
        
        Args:
            content: The content to validate
            
        Returns:
            True if the content is valid, False otherwise
        """
        return True  # Genre database content is generated internally, so it's always valid
    
    def _get_genre_info(self) -> str:
        """Get information about the genre."""
        genre_data = {
            "noir": "Noir fiction is characterized by cynicism, fatalism, and moral ambiguity. Common elements include crime, corruption, and flawed protagonists.",
            "sci-fi": "Science fiction explores the impact of imagined scientific or technological advances on society or individuals. Common elements include future settings, advanced technology, and speculative science.",
            "adventure": "Adventure fiction features exciting, dangerous undertakings or experiences. Common elements include exotic settings, action sequences, and heroic protagonists.",
            "generic": "General pulp fiction often features fast-paced, plot-driven narratives with vivid action and characters."
        }
        
        return genre_data.get(self.genre.lower(), "No specific information available for this genre.")
    
    def add(self) -> None:
        """Process and store the genre information."""
        content = self.load_content()
        for _, text in content.items():
            chunks = self._chunk_text(text)
            self.chunks.extend(chunks)

        # Only try to save documents if storage is available
        if self.storage is not None:
            self._save_documents()


def create_genre_database(**kwargs) -> GenreDatabaseKnowledge:
    """
    Factory function for creating a genre database knowledge source.
    
    Args:
        **kwargs: Arguments to pass to the GenreDatabaseKnowledge constructor
        
    Returns:
        GenreDatabaseKnowledge instance
    """
    return GenreDatabaseKnowledge(**kwargs) 