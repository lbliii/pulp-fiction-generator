"""
Directory initialization utilities.

These utilities ensure that required directories exist for the application to work properly.
"""

import os
import logging
import errno
import tempfile
import shutil
from pathlib import Path
import time
import random

# Try to import CrewAI tools
try:
    from crewai_tools import DirectoryReadTool, DirectorySearchTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str, max_retries: int = 3) -> bool:
    """
    Ensure that a specific directory exists with proper error handling.
    
    Args:
        directory_path: Path to the directory
        max_retries: Maximum number of retries for handling race conditions
        
    Returns:
        True if successful, False otherwise
    """
    path = Path(directory_path)
    
    # If directory already exists, return immediately
    if path.exists() and path.is_dir():
        return True
    
    # Create the directory using CrewAI tools if available
    if CREWAI_TOOLS_AVAILABLE:
        try:
            # DirectoryReadTool doesn't have a direct method to create directories,
            # but we can ensure a directory exists by creating it with os.makedirs
            # and then validating it exists with the tool
            os.makedirs(directory_path, exist_ok=True)
            directory_tool = DirectoryReadTool()
            
            # Verify directory exists by trying to list its contents
            # This will throw an error if the directory doesn't exist
            directory_tool.list(directory_path)
            logger.info(f"Created directory: {directory_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory using DirectoryReadTool: {e}")
            # Fall back to the traditional method
            pass
        
    # If CrewAI tools aren't available or failed, use traditional approach
    retries = 0
    retry_delay = 0.1  # Initial delay in seconds
    
    while retries < max_retries:
        try:
            # Create directory with parents and exist_ok to handle race conditions
            path.mkdir(parents=True, exist_ok=True)
            
            # Verify that the directory now exists
            if path.exists() and path.is_dir():
                logger.info(f"Created directory: {directory_path}")
                return True
            else:
                # If the directory wasn't created, we'll retry
                retries += 1
                retry_delay = min(1.0, retry_delay * 2) + random.uniform(0, 0.1)
                time.sleep(retry_delay)
                continue
                
        except FileExistsError:
            # This happens in race conditions where the directory is created
            # between the exists check and the mkdir call
            if path.exists() and path.is_dir():
                return True
            else:
                # Something exists but it's not a directory - this is a real problem
                logger.error(f"Path exists but is not a directory: {directory_path}")
                return False
                
        except PermissionError:
            logger.error(f"Permission denied when creating directory: {directory_path}")
            return False
            
        except OSError as e:
            if e.errno == errno.EEXIST and path.is_dir():
                # Directory exists (another race condition case)
                return True
            elif retries < max_retries - 1:
                # Retry other OSErrors
                logger.warning(f"OSError when creating directory {directory_path}: {e}. Retrying...")
                retries += 1
                # Exponential backoff with jitter
                retry_delay = min(1.0, retry_delay * 2) + random.uniform(0, 0.1)
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to create directory after {max_retries} attempts: {directory_path}, error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error creating directory {directory_path}: {e}")
            return False
    
    # If we get here, we've exhausted our retries
    logger.error(f"Failed to create directory after {max_retries} attempts: {directory_path}")
    return False

def ensure_directories_exist():
    """
    Ensure that all required directories exist for the application.
    
    Creates directories for logs, output, and other necessary paths.
    Returns a list of directories that failed to be created.
    """
    directories = [
        "logs",
        "logs/steps",
        "logs/tasks",
        "logs/events",
        "logs/errors",
        "output",
        "output/stories",
        "output/visualizations",
        "qdrant_data"  # For vector database persistent storage
    ]
    
    failed_dirs = []
    
    for directory in directories:
        if not ensure_directory_exists(directory):
            failed_dirs.append(directory)
            
    return failed_dirs

def clean_temp_directories():
    """
    Clean up any temporary directories created by the application.
    """
    try:
        temp_dir = os.path.join(tempfile.gettempdir(), "pulp_fiction_generator")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean temporary directories: {e}")

def initialize_app_directories():
    """
    Initialize all application directories and return success status.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        failed_dirs = ensure_directories_exist()
        
        if failed_dirs:
            dirs_str = ", ".join(failed_dirs)
            logger.error(f"Failed to create some directories: {dirs_str}")
            return False
            
        logger.info("All directories initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error during directory initialization: {e}")
        return False 