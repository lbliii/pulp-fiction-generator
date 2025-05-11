"""
Utilities for managing crew memory.

This module provides functions for resetting different types of memory
components and managing memory persistence.
"""

import os
import shutil
import logging
from typing import Optional, Union
from pathlib import Path

from crewai import Crew

logger = logging.getLogger(__name__)

def get_memory_path(genre: Optional[str] = None, storage_dir: str = "./.memory") -> str:
    """
    Get the path to memory storage for a genre.
    
    Args:
        genre: Optional genre to get memory for
        storage_dir: Base storage directory
        
    Returns:
        Path to memory directory
    """
    if genre:
        return os.path.join(storage_dir, genre.lower().replace(" ", "_"))
    return storage_dir

def reset_memory(
    memory_type: str = "all", 
    genre: Optional[str] = None, 
    storage_dir: str = "./.memory",
    crew: Optional[Crew] = None
) -> bool:
    """
    Reset a specific type of memory or all memory.
    
    Args:
        memory_type: Type of memory to reset (all, short, long, entities, knowledge, kickoff_outputs)
        genre: Optional genre to reset memory for
        storage_dir: Base storage directory
        crew: Optional crew object for direct reset
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # If a crew object is provided, use its reset method directly
        if crew:
            crew.reset_memories(command_type=memory_type)
            logger.info(f"Reset {memory_type} memory using crew object")
            return True
            
        # Otherwise use file system operations
        base_path = get_memory_path(genre, storage_dir)
        
        if memory_type == "all":
            # Reset all memories for the genre or all genres
            if genre:
                if os.path.exists(base_path):
                    shutil.rmtree(base_path)
                    os.makedirs(base_path, exist_ok=True)
                    logger.info(f"Reset all memory for genre '{genre}'")
            else:
                # Reset memory for all genres
                if os.path.exists(storage_dir):
                    shutil.rmtree(storage_dir)
                    os.makedirs(storage_dir, exist_ok=True)
                    logger.info("Reset all memory for all genres")
        elif memory_type == "short":
            # Reset short-term memory
            memory_path = os.path.join(base_path, "chroma")
            if os.path.exists(memory_path):
                shutil.rmtree(memory_path)
                logger.info(f"Reset short-term memory for {genre if genre else 'all genres'}")
        elif memory_type == "long":
            # Reset long-term memory
            memory_path = os.path.join(base_path, "long_term_memory.db")
            if os.path.exists(memory_path):
                os.remove(memory_path)
                logger.info(f"Reset long-term memory for {genre if genre else 'all genres'}")
        elif memory_type == "entities":
            # Reset entity memory
            memory_path = os.path.join(base_path, "entity")
            if os.path.exists(memory_path):
                shutil.rmtree(memory_path)
                logger.info(f"Reset entity memory for {genre if genre else 'all genres'}")
        elif memory_type == "knowledge":
            # Reset knowledge
            memory_path = os.path.join(base_path, "knowledge")
            if os.path.exists(memory_path):
                shutil.rmtree(memory_path)
                logger.info(f"Reset knowledge memory for {genre if genre else 'all genres'}")
        elif memory_type == "kickoff_outputs":
            # Reset latest kickoff outputs
            memory_path = os.path.join(base_path, "outputs.json")
            if os.path.exists(memory_path):
                os.remove(memory_path)
                logger.info(f"Reset latest kickoff outputs for {genre if genre else 'all genres'}")
        else:
            logger.warning(f"Unknown memory type: {memory_type}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error resetting memory: {e}")
        return False

def export_memory(
    output_dir: str,
    genre: Optional[str] = None,
    storage_dir: str = "./.memory"
) -> bool:
    """
    Export memory to a specific directory.
    
    Args:
        output_dir: Directory to export memory to
        genre: Optional genre to export memory for
        storage_dir: Base storage directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        base_path = get_memory_path(genre, storage_dir)
        
        if not os.path.exists(base_path):
            logger.warning(f"No memory found for {genre if genre else 'any genre'}")
            return False
            
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export memory
        if genre:
            # Export specific genre
            genre_dir = os.path.join(output_dir, genre.lower().replace(" ", "_"))
            os.makedirs(genre_dir, exist_ok=True)
            
            # Copy memory files
            for item in os.listdir(base_path):
                s = os.path.join(base_path, item)
                d = os.path.join(genre_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
        else:
            # Export all genres
            shutil.copytree(storage_dir, output_dir, dirs_exist_ok=True)
            
        logger.info(f"Exported memory for {genre if genre else 'all genres'} to {output_dir}")
        return True
    except Exception as e:
        logger.error(f"Error exporting memory: {e}")
        return False

def list_memory_contents(
    genre: Optional[str] = None,
    storage_dir: str = "./.memory"
) -> dict:
    """
    List memory contents.
    
    Args:
        genre: Optional genre to list memory for
        storage_dir: Base storage directory
        
    Returns:
        Dictionary with memory information
    """
    try:
        base_path = get_memory_path(genre, storage_dir)
        
        if not os.path.exists(base_path):
            return {"status": "not_found", "message": f"No memory found for {genre if genre else 'any genre'}"}
            
        memory_info = {"status": "success", "memory": {}}
        
        if genre:
            # List memory for specific genre
            memory_info["genre"] = genre
            
            # Check short-term memory
            short_term_path = os.path.join(base_path, "chroma")
            memory_info["memory"]["short_term"] = os.path.exists(short_term_path)
            
            # Check long-term memory
            long_term_path = os.path.join(base_path, "long_term_memory.db")
            memory_info["memory"]["long_term"] = os.path.exists(long_term_path)
            
            # Check entity memory
            entity_path = os.path.join(base_path, "entity")
            memory_info["memory"]["entity"] = os.path.exists(entity_path)
            
            # Check knowledge
            knowledge_path = os.path.join(base_path, "knowledge")
            memory_info["memory"]["knowledge"] = os.path.exists(knowledge_path)
            
            # Check latest kickoff outputs
            outputs_path = os.path.join(base_path, "outputs.json")
            memory_info["memory"]["kickoff_outputs"] = os.path.exists(outputs_path)
        else:
            # List memory for all genres
            genres = []
            
            for item in os.listdir(storage_dir):
                item_path = os.path.join(storage_dir, item)
                if os.path.isdir(item_path):
                    genres.append(item)
                    
            memory_info["genres"] = genres
            
        return memory_info
    except Exception as e:
        logger.error(f"Error listing memory contents: {e}")
        return {"status": "error", "message": str(e)} 