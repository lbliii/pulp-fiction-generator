"""
Diagnostic information collection utilities.

This module handles collecting and logging diagnostic information
about the system and application state to help diagnose issues.
"""

import os
import sys
import traceback
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

# Get logger
logger = logging.getLogger('pulp_fiction_generator')


class DiagnosticCollector:
    """
    Collects diagnostic information about the system and application state.
    
    This class is responsible for gathering information that can help
    diagnose issues when they occur.
    """
    
    @staticmethod
    def collect_system_info() -> Dict[str, Any]:
        """
        Collect information about the current system.
        
        Returns:
            Dictionary with system information
        """
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "environment_variables": {
                k: v for k, v in os.environ.items() 
                if k.startswith(("OLLAMA_", "PFG_", "PATH", "PYTHONPATH"))
            },
            "working_directory": os.getcwd(),
        }
    
    @staticmethod
    def collect_stack_trace() -> List[str]:
        """
        Collect the current stack trace.
        
        Returns:
            List of stack frames
        """
        return traceback.format_stack()
    
    @staticmethod
    def collect_ollama_status() -> Dict[str, Any]:
        """
        Collect information about the Ollama service.
        
        Returns:
            Dictionary with Ollama status
        """
        ollama_info = {}
        
        try:
            import requests
            try:
                ollama_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if ollama_response.status_code == 200:
                    ollama_info["status"] = "running"
                    ollama_info["models"] = ollama_response.json().get("models", [])
                else:
                    ollama_info["status"] = f"error: {ollama_response.status_code}"
            except Exception as e:
                ollama_info["status"] = f"error: {str(e)}"
        except ImportError:
            ollama_info["status"] = "unknown - requests package not available"
        
        return ollama_info
    
    @staticmethod
    def collect_all() -> Dict[str, Any]:
        """
        Collect all diagnostic information.
        
        Returns:
            Dictionary with all diagnostic information
        """
        return {
            "timestamp": datetime.now().isoformat(),
            **DiagnosticCollector.collect_system_info(),
            "call_stack": DiagnosticCollector.collect_stack_trace(),
            "ollama_status": DiagnosticCollector.collect_ollama_status()
        }


class DiagnosticLogger:
    """
    Handles logging and storage of diagnostic information.
    
    This class is responsible for saving diagnostic information
    to appropriate locations for later analysis.
    """
    
    @staticmethod
    def save_to_file(info: Dict[str, Any], base_dir: str = "./logs") -> str:
        """
        Save diagnostic information to a file.
        
        Args:
            info: Diagnostic information to save
            base_dir: Directory to save the file in
            
        Returns:
            Path to the saved file
        """
        log_dir = Path(base_dir)
        log_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"diagnostic_{timestamp}.json"
        
        with open(log_file, "w") as f:
            json.dump(info, f, indent=2, default=str)
            
        return str(log_file)
    
    @staticmethod
    def log_diagnostics(info: Dict[str, Any], base_dir: str = "./logs") -> str:
        """
        Log diagnostic information and save to a file.
        
        Args:
            info: Diagnostic information to log
            base_dir: Directory to save the file in
            
        Returns:
            Path to the saved file
        """
        # Log a summary to the logger
        logger.info(f"Diagnostic information collected at {info.get('timestamp', 'unknown time')}")
        
        # Save the full details to a file
        file_path = DiagnosticLogger.save_to_file(info, base_dir)
        logger.info(f"Full diagnostic information saved to {file_path}")
        
        return file_path 