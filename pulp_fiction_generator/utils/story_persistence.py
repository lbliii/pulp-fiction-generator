"""
Story state persistence utilities for saving and loading story data.

This module provides functionality to save stories to disk in a structured format,
including story content and metadata about characters, settings, and plot points.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from ..story.state import StoryStateManager
    from ..story.models import StoryArtifacts


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
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}  # Track completed tasks and their outputs
        
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
            "artifacts": self.artifacts,
            "completed_tasks": self.completed_tasks
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
        metadata.completed_tasks = data.get("completed_tasks", {})
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
        
    def add_task_output(self, task_type: str, chapter_num: int, output: str, 
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add the output of a task to the story's metadata.
        
        Args:
            task_type: Type of task (e.g., "research", "worldbuilding", "prose", etc.)
            chapter_num: Chapter number this task is associated with
            output: Text output from the task
            metadata: Additional metadata about the task
        """
        if not self.metadata.completed_tasks.get(str(chapter_num)):
            self.metadata.completed_tasks[str(chapter_num)] = {}
            
        # Ensure we're not storing empty outputs
        if output is None or (isinstance(output, str) and not output.strip()):
            import logging
            logging.warning(f"Attempted to store empty output for task {task_type} in chapter {chapter_num}")
            return
            
        self.metadata.completed_tasks[str(chapter_num)][task_type] = {
            "output": output,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # If this is a final prose or editor task, add it as a chapter
        if task_type in ["prose", "editor", "final_story"] and output:
            # Only add as chapter if we don't already have this chapter
            if len(self.chapters) < chapter_num:
                try:
                    self.add_chapter(output)
                except ValueError as e:
                    # Log the error but don't raise to avoid crashing the process
                    import logging
                    logging.error(f"Failed to add chapter from task output: {e}")
        
        self.metadata.update_last_modified()
        
    def get_task_output(self, task_type: str, chapter_num: int) -> Optional[str]:
        """
        Get the output of a previously completed task.
        
        Args:
            task_type: Type of task
            chapter_num: Chapter number
            
        Returns:
            The task output text or None if not found
        """
        chapter_tasks = self.metadata.completed_tasks.get(str(chapter_num), {})
        task_data = chapter_tasks.get(task_type)
        
        if task_data:
            return task_data.get("output")
        return None
        
    def has_completed_task(self, task_type: str, chapter_num: int) -> bool:
        """
        Check if a task has been completed.
        
        Args:
            task_type: Type of task
            chapter_num: Chapter number
            
        Returns:
            True if the task has been completed and has valid output, False otherwise
        """
        chapter_tasks = self.metadata.completed_tasks.get(str(chapter_num), {})
        task_data = chapter_tasks.get(task_type)
        
        # Check if task exists and has a non-empty output
        if task_data and task_data.get("output"):
            output = task_data.get("output")
            if isinstance(output, str) and output.strip():
                return True
        return False
        
    def get_project_dirname(self) -> str:
        """
        Get the directory name for this project based on the title.
        
        Returns:
            The directory name to use for the project
        """
        return self.metadata.title.lower().replace(" ", "_")
        
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

    def to_story_state_manager(self) -> 'StoryStateManager':
        """
        Convert this StoryState to a StoryStateManager from the story module.
        
        Returns:
            StoryStateManager instance with data from this StoryState
        """
        # Import here to avoid circular imports
        from ..story.state import StoryStateManager
        
        # Create a new StoryStateManager
        manager = StoryStateManager()
        
        # Set project directory based on title
        manager.set_project_directory(self.metadata.title)
        
        # Copy chapters - self.chapters is a list, enumerate to get chapter numbers
        for i, chapter_content in enumerate(self.chapters, 1):
            manager.add_chapter(i, chapter_content)
        
        # Copy task outputs
        for chapter_num, tasks in self.metadata.completed_tasks.items():
            for task_type, task_data in tasks.items():
                manager.add_task_output(task_type, int(chapter_num), task_data.get("output", ""))
        
        return manager
    
    @classmethod
    def from_story_state_manager(cls, manager: 'StoryStateManager', genre: str, title: Optional[str] = None) -> 'StoryState':
        """
        Create a StoryState from a StoryStateManager.
        
        Args:
            manager: StoryStateManager instance to convert
            genre: The genre of the story
            title: The title of the story, if known
            
        Returns:
            StoryState instance with data from the manager
        """
        # Create a new StoryState
        state = cls(genre, title)
        
        # Copy chapters
        for chapter_num in manager.get_chapters():
            chapter_content = manager.get_chapter(chapter_num)
            if chapter_content:
                state.add_chapter(chapter_content)
        
        # Copy task outputs
        for chapter_num in manager.get_chapters():
            for task_type in manager.get_task_types(chapter_num):
                task_output = manager.get_task_output(task_type, chapter_num)
                if task_output:
                    state.add_task_output(task_type, chapter_num, task_output)
        
        return state


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
    
    def get_project_dir(self, story_state: StoryState) -> Path:
        """
        Get the project directory for a story state.
        
        Args:
            story_state: The story state
            
        Returns:
            Path object for the project directory
        """
        project_dir = self.output_dir / story_state.get_project_dirname()
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
        
    def save_story(self, story_state: StoryState, filename: Optional[str] = None) -> str:
        """
        Save a story to a file.
        
        Args:
            story_state: StoryState instance to save
            filename: Optional filename, will be auto-generated if not provided
            
        Returns:
            The path to the saved file
            
        Raises:
            StoryPersistenceError: If there's an error saving the story
        """
        try:
            # Ensure title for saving
            if not story_state.metadata.title:
                story_state.metadata.title = "Untitled Story"
                
            # Update last modified timestamp
            story_state.metadata.update_last_modified()
            
            # Get or create a project directory based on the title
            project_dir = self.get_project_dir(story_state)
            
            # Create the project directory if it doesn't exist
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Sanitize title for filename if needed
            title_slug = story_state.get_project_dirname()
            
            # Determine the filename
            if not filename:
                # Generate a filename based on title and timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{title_slug}_{timestamp}.json"
            
            # Save as JSON
            json_path = project_dir / filename
            
            with open(json_path, "w") as f:
                # Convert story state to serializable dict
                story_dict = story_state.to_dict()
                json.dump(story_dict, f, indent=2)
                
            # Also save a Markdown version
            md_path = project_dir / f"{title_slug}.md"
            
            with open(md_path, "w") as f:
                # Generate a nice markdown file
                f.write(f"# {story_state.metadata.title}\n\n")
                f.write(f"**Genre:** {story_state.metadata.genre}\n")
                f.write(f"**Created:** {story_state.metadata.creation_date}\n")
                f.write(f"**Updated:** {story_state.metadata.last_modified}\n\n")
                
                # Add tags if present
                if story_state.metadata.tags:
                    tags_str = ", ".join([f"#{tag}" for tag in story_state.metadata.tags])
                    f.write(f"**Tags:** {tags_str}\n\n")
                
                # Get the story content
                full_story = story_state.get_full_story()
                f.write(full_story)
            
            return str(json_path)
        except (OSError, IOError) as e:
            from ..utils.errors import StoryPersistenceError
            raise StoryPersistenceError(f"Error saving story: {e}") from e
        
    def load_story(self, filename: str) -> StoryState:
        """
        Load a story state from disk.
        
        Args:
            filename: Path to the story file or project name
            
        Returns:
            The loaded story state
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid story file
        """
        # First check if it's a direct file path
        filepath = Path(filename)
        
        # If not an absolute path, check if it's a project name or file in output dir
        if not filepath.is_absolute():
            project_dir = self.output_dir / filename
            
            # If it's a directory (project name)
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    try:
                        with open(project_file, "r", encoding="utf-8") as f:
                            project_data = json.load(f)
                        latest_story_file = project_data.get("latest_story_file")
                        if latest_story_file:
                            filepath = project_dir / latest_story_file
                        else:
                            raise ValueError(f"No story file found in project: {filename}")
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid project file: {project_file}")
                else:
                    # Try to find any JSON file in the directory
                    json_files = list(project_dir.glob("*.json"))
                    if not json_files or len(json_files) == 0:
                        raise FileNotFoundError(f"No story files found in project: {filename}")
                    # Use the most recently modified file
                    filepath = max(json_files, key=lambda f: f.stat().st_mtime)
            else:
                # Check if it's a file in the output directory
                filepath = self.output_dir / filename
                
                # If still not found, check each project directory for this file
                if not filepath.exists():
                    for project_dir in self.output_dir.glob("*"):
                        if project_dir.is_dir():
                            potential_path = project_dir / filename
                            if potential_path.exists():
                                filepath = potential_path
                                break
            
        if not filepath.exists():
            raise FileNotFoundError(f"Story file not found: {filepath}")
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            return StoryState.from_dict(data)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid story file format: {filepath}")
            
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects in the output directory.
        
        Returns:
            List of project metadata
        """
        projects = []
        
        for project_dir in self.output_dir.glob("*"):
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    try:
                        with open(project_file, "r", encoding="utf-8") as f:
                            project_data = json.load(f)
                        
                        projects.append({
                            "name": project_dir.name,
                            "title": project_data.get("title", "Untitled"),
                            "genre": project_data.get("genre", "unknown"),
                            "chapters": project_data.get("chapter_count", 0),
                            "modified": project_data.get("last_modified", ""),
                            "latest_file": project_data.get("latest_story_file", "")
                        })
                    except (json.JSONDecodeError, IOError):
                        # Add with limited information
                        projects.append({
                            "name": project_dir.name,
                            "title": project_dir.name.replace("_", " ").title(),
                            "error": "Invalid project file"
                        })
                else:
                    # Check for JSON files to infer project information
                    json_files = list(project_dir.glob("*.json"))
                    if json_files:
                        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                        try:
                            with open(latest_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            
                            metadata = data.get("metadata", {})
                            projects.append({
                                "name": project_dir.name,
                                "title": metadata.get("title", project_dir.name.replace("_", " ").title()),
                                "genre": metadata.get("genre", "unknown"),
                                "chapters": metadata.get("chapter_count", 0),
                                "modified": metadata.get("last_modified", ""),
                                "latest_file": latest_file.name
                            })
                        except (json.JSONDecodeError, IOError):
                            # Add with limited information
                            projects.append({
                                "name": project_dir.name,
                                "title": project_dir.name.replace("_", " ").title(),
                                "error": "Invalid story files"
                            })
                
        return projects
    
    def list_stories(self) -> List[Dict[str, Any]]:
        """
        List all stories in the output directory.
        
        Returns:
            List of story file metadata
        """
        stories = []
        
        for project_dir in self.output_dir.glob("*"):
            if project_dir.is_dir():
                for file in project_dir.glob("*.json"):
                    # Skip project files
                    if file.name == "project.json":
                        continue
                        
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            
                        metadata = data.get("metadata", {})
                        stories.append({
                            "project": project_dir.name,
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
    
    def load_story_to_state_manager(self, filename: str) -> 'StoryStateManager':
        """
        Load a story from disk and convert it to a StoryStateManager.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            StoryStateManager instance
        """
        story_state = self.load_story(filename)
        return story_state.to_story_state_manager()
    
    def save_story_from_state_manager(self, manager: 'StoryStateManager', genre: str, title: Optional[str] = None, filename: Optional[str] = None) -> str:
        """
        Save a story from a StoryStateManager to disk.
        
        Args:
            manager: StoryStateManager to save
            genre: The genre of the story
            title: The title of the story, if known
            filename: Optional filename to save to
            
        Returns:
            The path to the saved file
        """
        story_state = StoryState.from_story_state_manager(manager, genre, title)
        return self.save_story(story_state, filename) 