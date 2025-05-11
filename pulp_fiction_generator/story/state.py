"""
Story state management.

Handles persistence and retrieval of story generation artifacts.
"""

from typing import Dict, Any, Optional, Union, List
import json
import os
import re
from pathlib import Path
import string
import logging

# Try to import CrewAI tools
try:
    from crewai_tools import FileReadTool, FileWriteTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False

from ..utils.errors import logger

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's safe for filesystem use.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove illegal characters
    s = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Trim whitespace
    s = s.strip()
    # Limit length
    return s[:100]

class StoryStateManager:
    """
    Manages the state of a story generation process.
    
    This class is responsible for tracking the state of tasks, chapters,
    and other artifacts during story generation. It also provides
    persistence capabilities to save state between runs.
    """
    
    def __init__(self, base_dir: str = "output"):
        """
        Initialize the story state manager.
        
        Args:
            base_dir: Base directory for persistent storage
        """
        self.base_dir = base_dir
        self.project_dir = "default_project"
        self.task_outputs: Dict[str, Dict[int, Any]] = {}
        self.chapters: Dict[int, str] = {}
        
        # Create file tools if available
        self.file_read_tool = None
        self.file_write_tool = None
        if CREWAI_TOOLS_AVAILABLE:
            self.file_read_tool = FileReadTool()
            self.file_write_tool = FileWriteTool()
    
    def add_task_output(self, task_type: str, chapter_num: int, output: Any) -> None:
        """
        Add a task output to the state.
        
        Args:
            task_type: Type of task
            chapter_num: Chapter number
            output: The task output
        """
        # Skip empty outputs
        if output is None:
            return
            
        # Initialize task type if needed
        if task_type not in self.task_outputs:
            self.task_outputs[task_type] = {}
            
        # Add to in-memory cache
        self.task_outputs[task_type][chapter_num] = output
        
        # Persist to storage
        self._persist_task_output(task_type, chapter_num, output)
    
    def has_completed_task(self, task_type: str, chapter_num: int) -> bool:
        """
        Check if a task has been completed.
        
        Args:
            task_type: Type of task to check
            chapter_num: Chapter number to check
            
        Returns:
            True if the task has been completed, False otherwise
        """
        # First check in-memory cache
        if task_type in self.task_outputs and chapter_num in self.task_outputs[task_type]:
            return True
            
        # Then check persistent storage
        try:
            filepath = self._get_task_filepath(task_type, chapter_num)
            return os.path.exists(filepath)
        except Exception as e:
            logger.warning(f"Error checking task completion status: {e}")
            return False
    
    def get_task_output(self, task_type: str, chapter_num: int) -> Optional[str]:
        """
        Get the output of a completed task.
        
        Args:
            task_type: Type of task to retrieve
            chapter_num: Chapter number to retrieve
            
        Returns:
            Task output content or None if not found
        """
        # First check in-memory cache
        if task_type in self.task_outputs and chapter_num in self.task_outputs[task_type]:
            return self.task_outputs[task_type][chapter_num]
        
        # Then try to load from persistent storage
        try:
            filepath = self._get_task_filepath(task_type, chapter_num)
            if os.path.exists(filepath):
                if CREWAI_TOOLS_AVAILABLE and self.file_read_tool:
                    # Use FileReadTool
                    content = self.file_read_tool.read(filepath)
                else:
                    # Fallback to direct file reading
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                
                # Cache the loaded content
                if task_type not in self.task_outputs:
                    self.task_outputs[task_type] = {}
                self.task_outputs[task_type][chapter_num] = content
                return content
        except Exception as e:
            logger.warning(f"Error loading task output: {e}")
        
        return None
    
    def _get_task_filepath(self, task_type: str, chapter_num: int) -> str:
        """
        Get the filepath for a task's output.
        
        Args:
            task_type: Type of task
            chapter_num: Chapter number
            
        Returns:
            Filepath for the task output
        """
        # Sanitize task_type to prevent directory traversal
        safe_task_type = sanitize_filename(task_type)
        
        # Ensure chapter_num is a positive integer
        safe_chapter_num = max(1, int(chapter_num))
        
        # Use pathlib for proper path joining that works cross-platform
        return str(Path(self.base_dir) / self.project_dir / f"chapter_{safe_chapter_num}" / f"{safe_task_type}.txt")
    
    def _persist_task_output(self, task_type: str, chapter_num: int, output: Any) -> None:
        """
        Save a task output to persistent storage.
        
        Args:
            task_type: Type of task
            chapter_num: Chapter number
            output: Task output content
        """
        if output is None:
            return
            
        try:
            filepath = self._get_task_filepath(task_type, chapter_num)
            directory = os.path.dirname(filepath)
            
            # Ensure directory exists
            os.makedirs(directory, exist_ok=True)
            
            # Write content to file using FileWriteTool if available
            if CREWAI_TOOLS_AVAILABLE and self.file_write_tool:
                self.file_write_tool.write(filepath, str(output))
            else:
                # Fallback to direct file writing
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(output))
                    
            logger.info(f"Saved {task_type} output for chapter {chapter_num} to {filepath}")
        except Exception as e:
            logger.error(f"Error persisting task output: {e}")
    
    def set_project_directory(self, title: str) -> None:
        """
        Set the project directory based on story title.
        
        Args:
            title: Story title
        """
        if not title or not isinstance(title, str):
            title = "untitled_project"
            
        # Sanitize the project directory name
        self.project_dir = sanitize_filename(title.lower().replace(" ", "_"))
        
        # Ensure it's not empty after sanitization
        if not self.project_dir:
            self.project_dir = "untitled_project"
        
    def get_artifacts_for_chapter(self, chapter_num: int) -> Dict[str, Any]:
        """
        Get all artifacts for a specific chapter.
        
        Args:
            chapter_num: Chapter number
            
        Returns:
            Dictionary of all artifacts for the chapter
        """
        artifacts = {}
        
        for task_type in ["research", "worldbuilding", "characters", "plot", "draft", "final_story"]:
            artifacts[task_type] = self.get_task_output(task_type, chapter_num)
            
        return artifacts
    
    def add_chapter(self, chapter_num: int, chapter_content: str) -> None:
        """
        Add a chapter to the state.
        
        Args:
            chapter_num: Chapter number
            chapter_content: The content of the chapter
        """
        self.chapters[chapter_num] = chapter_content
        # Also save as a task output for compatibility
        self.add_task_output("final_story", chapter_num, chapter_content)
    
    def get_chapter(self, chapter_num: int) -> Optional[str]:
        """
        Get a chapter from the state.
        
        Args:
            chapter_num: Chapter number
            
        Returns:
            The chapter content or None if not found
        """
        # First check in-memory cache
        if chapter_num in self.chapters:
            return self.chapters[chapter_num]
            
        # Then try to get from final_story task output
        return self.get_task_output("final_story", chapter_num)
    
    def get_chapters(self) -> List[int]:
        """
        Get a list of all chapter numbers.
        
        Returns:
            List of chapter numbers
        """
        # Combine chapters from memory and task outputs
        chapter_nums = set(self.chapters.keys())
        
        # Add chapter numbers from final_story task output
        if "final_story" in self.task_outputs:
            chapter_nums.update(self.task_outputs["final_story"].keys())
            
        return sorted(list(chapter_nums))
    
    def get_task_types(self, chapter_num: int) -> List[str]:
        """
        Get a list of all task types for a chapter.
        
        Args:
            chapter_num: Chapter number
            
        Returns:
            List of task types
        """
        task_types = []
        
        # Check all task outputs for this chapter
        for task_type, chapters in self.task_outputs.items():
            if chapter_num in chapters:
                task_types.append(task_type)
                
        return task_types 