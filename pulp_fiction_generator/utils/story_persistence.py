"""
Story state persistence utilities for saving and loading story data.

This module provides functionality to save stories to disk in a structured format,
including story content and metadata about characters, settings, and plot points.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class StoryMetadata:
    """
    Class to track and manage story metadata.
    
    This includes information about characters, settings, plot points,
    and other elements that need to be maintained across chapters.
    """
    
    def __init__(self, genre: str, title: Optional[str] = None):
        """
        Initialize story metadata.
        
        Args:
            genre: The genre of the story
            title: The title of the story, if known
        """
        self.genre = genre
        self.title = title or "Untitled Story"
        self.characters: List[Dict[str, Any]] = []
        self.settings: List[Dict[str, str]] = []
        self.plot_points: List[Dict[str, Any]] = []
        self.tags: Set[str] = set()
        self.creation_date = datetime.datetime.now().isoformat()
        self.last_modified = self.creation_date
        self.chapter_count = 0
        self.word_count = 0
        self.plot_template: Optional[str] = None
        self.current_plot_point_index: int = 0
        self.artifacts: Dict[str, Any] = {}  # Storage for generation artifacts
        
    def add_character(self, character: Dict[str, Any]) -> None:
        """
        Add a character to the story metadata.
        
        Args:
            character: Character details dictionary with name, traits, etc.
        """
        # Check if character already exists
        for existing in self.characters:
            if existing.get("name") == character.get("name"):
                # Update existing character
                existing.update(character)
                return
                
        # Add new character
        self.characters.append(character)
        
    def add_setting(self, setting: Dict[str, str]) -> None:
        """
        Add a setting to the story metadata.
        
        Args:
            setting: Setting details dictionary with name and description
        """
        # Check if setting already exists
        for existing in self.settings:
            if existing.get("name") == setting.get("name"):
                # Update existing setting
                existing.update(setting)
                return
                
        # Add new setting
        self.settings.append(setting)
        
    def add_plot_point(self, plot_point: Dict[str, Any]) -> None:
        """
        Add a plot point to the story metadata.
        
        Args:
            plot_point: Plot point dictionary with description and chapter
        """
        self.plot_points.append(plot_point)
        
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the story metadata.
        
        Args:
            tag: Tag string
        """
        self.tags.add(tag)
        
    def update_word_count(self, chapter_text: str) -> None:
        """
        Update the word count based on added chapter text.
        
        Args:
            chapter_text: Text of the chapter to count
        """
        words = chapter_text.split()
        self.word_count += len(words)
        
    def increment_chapter_count(self) -> None:
        """Increment the chapter count."""
        self.chapter_count += 1
        
    def update_last_modified(self) -> None:
        """Update the last modified timestamp to now."""
        self.last_modified = datetime.datetime.now().isoformat()
        
    def add_artifact(self, key: str, content: Any) -> None:
        """
        Add a generation artifact to the metadata.
        
        Args:
            key: Identifier for the artifact (e.g., 'research', 'worldbuilding')
            content: The artifact content
        """
        self.artifacts[key] = content
        self.update_last_modified()
    
    def get_artifact(self, key: str) -> Optional[Any]:
        """
        Retrieve a generation artifact.
        
        Args:
            key: Identifier for the artifact
            
        Returns:
            The artifact content, or None if not found
        """
        return self.artifacts.get(key)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the metadata to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the metadata
        """
        return {
            "genre": self.genre,
            "title": self.title,
            "characters": self.characters,
            "settings": self.settings,
            "plot_points": self.plot_points,
            "tags": list(self.tags),
            "creation_date": self.creation_date,
            "last_modified": self.last_modified,
            "chapter_count": self.chapter_count,
            "word_count": self.word_count,
            "plot_template": self.plot_template,
            "current_plot_point_index": self.current_plot_point_index,
            "artifacts": self.artifacts
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryMetadata':
        """
        Create a StoryMetadata instance from a dictionary.
        
        Args:
            data: Dictionary with metadata
            
        Returns:
            StoryMetadata instance
        """
        metadata = cls(data["genre"], data.get("title", "Untitled Story"))
        metadata.characters = data.get("characters", [])
        metadata.settings = data.get("settings", [])
        metadata.plot_points = data.get("plot_points", [])
        metadata.tags = set(data.get("tags", []))
        metadata.creation_date = data.get("creation_date", metadata.creation_date)
        metadata.last_modified = data.get("last_modified", metadata.last_modified)
        metadata.chapter_count = data.get("chapter_count", 0)
        metadata.word_count = data.get("word_count", 0)
        metadata.plot_template = data.get("plot_template", None)
        metadata.current_plot_point_index = data.get("current_plot_point_index", 0)
        metadata.artifacts = data.get("artifacts", {})
        return metadata


class StoryState:
    """
    Class to manage the complete state of a story.
    
    This includes the content of all chapters as well as metadata about
    the story elements that need to be maintained for continuity.
    """
    
    def __init__(self, genre: str, title: Optional[str] = None):
        """
        Initialize story state.
        
        Args:
            genre: The genre of the story
            title: The title of the story, if known
        """
        self.metadata = StoryMetadata(genre, title)
        self.chapters: List[str] = []
        
    def add_chapter(self, chapter_text: str, characters: Optional[List[Dict[str, Any]]] = None,
                    settings: Optional[List[Dict[str, str]]] = None,
                    plot_points: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add a chapter to the story state.
        
        Args:
            chapter_text: Text content of the chapter
            characters: List of characters featured in the chapter
            settings: List of settings featured in the chapter
            plot_points: List of plot points in the chapter
            
        Raises:
            ValueError: If chapter_text is empty or invalid
        """
        # Validate chapter content
        if not chapter_text:
            raise ValueError("Cannot add empty chapter to story state")
        
        if not isinstance(chapter_text, str):
            raise ValueError(f"Chapter content must be a string, got {type(chapter_text).__name__}")
            
        # Check for error markers that might indicate failed generation
        if chapter_text.startswith("ERROR:") or chapter_text.startswith("Task execution failed:"):
            raise ValueError(f"Cannot add error message as chapter: {chapter_text[:100]}...")
            
        # Add the chapter
        self.chapters.append(chapter_text)
        self.metadata.increment_chapter_count()
        self.metadata.update_word_count(chapter_text)
        
        # Update metadata with chapter elements
        if characters:
            for character in characters:
                self.metadata.add_character(character)
                
        if settings:
            for setting in settings:
                self.metadata.add_setting(setting)
                
        if plot_points:
            for plot_point in plot_points:
                plot_point["chapter"] = len(self.chapters)
                self.metadata.add_plot_point(plot_point)
                
        self.metadata.update_last_modified()
        
    def get_full_story(self) -> str:
        """
        Get the full story text.
        
        Returns:
            The complete story text with chapter formatting
        """
        if not self.chapters:
            return ""
            
        story_text = f"# {self.metadata.title}\n\n"
        
        for i, chapter in enumerate(self.chapters, 1):
            story_text += f"## Chapter {i}\n\n{chapter}\n\n"
            
        return story_text
        
    def get_chapter(self, chapter_num: int) -> Optional[str]:
        """
        Get a specific chapter text.
        
        Args:
            chapter_num: 1-based chapter number
            
        Returns:
            The chapter text, or None if chapter doesn't exist
        """
        if 1 <= chapter_num <= len(self.chapters):
            return self.chapters[chapter_num - 1]
        return None
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the story state to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the story state
        """
        return {
            "metadata": self.metadata.to_dict(),
            "chapters": self.chapters
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryState':
        """
        Create a StoryState instance from a dictionary.
        
        Args:
            data: Dictionary with story state
            
        Returns:
            StoryState instance
        """
        metadata = data.get("metadata", {})
        genre = metadata.get("genre", "unknown")
        title = metadata.get("title", "Untitled Story")
        
        story_state = cls(genre, title)
        story_state.metadata = StoryMetadata.from_dict(metadata)
        story_state.chapters = data.get("chapters", [])
        
        return story_state


class StoryPersistence:
    """
    Utility class for saving and loading story state.
    """
    
    def __init__(self, output_dir: str = "./output"):
        """
        Initialize story persistence.
        
        Args:
            output_dir: Directory for story files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def save_story(self, story_state: StoryState, filename: Optional[str] = None) -> str:
        """
        Save a story state to disk.
        
        Args:
            story_state: The story state to save
            filename: Optional filename to use, otherwise generated from title
            
        Returns:
            The path where the story was saved
        """
        # Create filename from title if not provided
        if not filename:
            title_slug = story_state.metadata.title.lower().replace(" ", "_")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title_slug}_{timestamp}.json"
            
        # Ensure .json extension
        if not filename.endswith(".json"):
            filename += ".json"
            
        # Create full path
        filepath = self.output_dir / filename
        
        # Update last modified timestamp
        story_state.metadata.update_last_modified()
        
        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(story_state.to_dict(), f, indent=2, ensure_ascii=False)
            
        return str(filepath)
        
    def load_story(self, filename: str) -> StoryState:
        """
        Load a story state from disk.
        
        Args:
            filename: Path to the story file
            
        Returns:
            The loaded story state
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid story file
        """
        filepath = Path(filename)
        if not filepath.is_absolute():
            filepath = self.output_dir / filepath
            
        if not filepath.exists():
            raise FileNotFoundError(f"Story file not found: {filepath}")
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            return StoryState.from_dict(data)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid story file format: {filepath}")
            
    def list_stories(self) -> List[Dict[str, Any]]:
        """
        List all stories in the output directory.
        
        Returns:
            List of story file metadata
        """
        stories = []
        
        for file in self.output_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                metadata = data.get("metadata", {})
                stories.append({
                    "filename": file.name,
                    "title": metadata.get("title", "Untitled"),
                    "genre": metadata.get("genre", "unknown"),
                    "chapters": metadata.get("chapter_count", 0),
                    "created": metadata.get("creation_date", ""),
                    "modified": metadata.get("last_modified", "")
                })
            except (json.JSONDecodeError, IOError):
                # Skip invalid files
                continue
                
        return stories
    
    def search_stories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search stories by metadata.
        
        Args:
            query: Search term to look for in titles, character names, etc.
            
        Returns:
            List of matching story metadata
        """
        query = query.lower()
        results = []
        
        for file in self.output_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                
                # Search in title
                if query in metadata.get("title", "").lower():
                    results.append(self._extract_story_metadata(file, metadata))
                    continue
                    
                # Search in tags
                if any(query in tag.lower() for tag in metadata.get("tags", [])):
                    results.append(self._extract_story_metadata(file, metadata))
                    continue
                    
                # Search in character names
                if any(query in char.get("name", "").lower() for char in metadata.get("characters", [])):
                    results.append(self._extract_story_metadata(file, metadata))
                    continue
                    
                # Search in setting names
                if any(query in setting.get("name", "").lower() for setting in metadata.get("settings", [])):
                    results.append(self._extract_story_metadata(file, metadata))
                    continue
                    
            except (json.JSONDecodeError, IOError):
                # Skip invalid files
                continue
                
        return results
                
    def _extract_story_metadata(self, filepath: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant story metadata for display.
        
        Args:
            filepath: Path to the story file
            metadata: Story metadata dictionary
            
        Returns:
            Dictionary with extracted metadata
        """
        return {
            "filename": filepath.name,
            "title": metadata.get("title", "Untitled"),
            "genre": metadata.get("genre", "unknown"),
            "chapters": metadata.get("chapter_count", 0),
            "created": metadata.get("creation_date", ""),
            "modified": metadata.get("last_modified", ""),
            "characters": len(metadata.get("characters", [])),
            "word_count": metadata.get("word_count", 0)
        } 