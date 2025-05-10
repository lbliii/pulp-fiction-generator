"""
Error handling utilities for the Pulp Fiction Generator.

This module provides tools for consistent error handling, logging,
and diagnostic information collection throughout the application.
"""

import os
import sys
import traceback
import inspect
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import json
import signal
from contextlib import contextmanager
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger('pulp_fiction_generator')

class TimeoutError(Exception):
    """Exception raised when a function call times out"""
    pass

@contextmanager
def timeout(seconds: int):
    """Context manager for timing out function calls"""
    # For Unix-like systems, use signal-based timeout
    if hasattr(signal, 'SIGALRM'):
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Function call timed out after {seconds} seconds")
        
        # Set the timeout handler
        original_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            # Reset the alarm and restore the original handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)
    
    # For Windows or other systems without SIGALRM, use thread-based timeout
    else:
        timer = None
        timeout_occurred = False
        main_thread = threading.current_thread()
        
        def timeout_thread():
            nonlocal timeout_occurred
            start_time = time.time()
            # Wait for the timeout to occur
            while time.time() - start_time < seconds:
                time.sleep(0.1)
                # If the main operation completed, the timer will be set to None
                if timer is None:
                    return
            # If we got here, the timeout occurred
            timeout_occurred = True
            logger.warning(f"Operation timed out after {seconds} seconds")
            # Try to raise a TimeoutError in the main thread
            # Note: This might not be effective on all platforms
            if hasattr(main_thread, "_thread__stop"):
                main_thread._thread__stop()
        
        # Start the timeout thread
        timer = threading.Thread(target=timeout_thread)
        timer.daemon = True
        timer.start()
        
        try:
            yield
        finally:
            # Mark timer as completed
            timer = None
            if timeout_occurred:
                raise TimeoutError(f"Operation timed out after {seconds} seconds")

class DiagnosticInfo:
    """Collects diagnostic information about the system and application state."""
    
    @staticmethod
    def collect() -> Dict[str, Any]:
        """Collect diagnostic information about the current system and environment."""
        info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform,
            "environment_variables": {
                k: v for k, v in os.environ.items() 
                if k.startswith(("OLLAMA_", "PFG_", "PATH", "PYTHONPATH"))
            },
            "working_directory": os.getcwd(),
            "call_stack": traceback.format_stack(),
        }
        
        # Add ollama-specific diagnostics if available
        try:
            import requests
            try:
                ollama_response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if ollama_response.status_code == 200:
                    info["ollama_status"] = "running"
                    info["ollama_models"] = ollama_response.json().get("models", [])
                else:
                    info["ollama_status"] = f"error: {ollama_response.status_code}"
            except Exception as e:
                info["ollama_status"] = f"error: {str(e)}"
        except ImportError:
            info["ollama_status"] = "unknown - requests package not available"
            
        return info
    
    @staticmethod
    def save_to_file(info: Dict[str, Any], base_dir: str = "./logs") -> str:
        """Save diagnostic information to a file."""
        log_dir = Path(base_dir)
        log_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"diagnostic_{timestamp}.json"
        
        with open(log_file, "w") as f:
            json.dump(info, f, indent=2, default=str)
            
        return str(log_file)

class ErrorHandler:
    """Central error handling facility for the application."""
    
    @staticmethod
    def handle_exception(
        e: Exception, 
        context: Optional[Dict[str, Any]] = None,
        collect_diagnostics: bool = True,
        show_traceback: bool = False,
        callback: Optional[Callable[[Exception, Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Handle an exception in a standard way across the application.
        
        Args:
            e: The exception to handle
            context: Additional context about where/why the exception occurred
            collect_diagnostics: Whether to collect diagnostic information
            show_traceback: Whether to print the traceback to stderr
            callback: Optional callback to execute with the exception and error info
            
        Returns:
            Dictionary with error information and diagnostics
        """
        # Get the basic error information
        error_info = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Get caller information
        frame = inspect.currentframe().f_back
        if frame:
            caller_info = {
                "file": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": frame.f_lineno
            }
            error_info["caller"] = caller_info
        
        # Collect full diagnostic information if requested
        if collect_diagnostics:
            error_info["diagnostics"] = DiagnosticInfo.collect()
            
            # Save diagnostics to file
            try:
                log_file = DiagnosticInfo.save_to_file(error_info)
                error_info["log_file"] = log_file
                logger.error(f"Error details saved to {log_file}")
            except Exception as log_error:
                logger.error(f"Failed to save diagnostic information: {log_error}")
        
        # Log the error
        logger.error(f"Error in {error_info.get('caller', {}).get('function', 'unknown')}: "
                    f"{error_info['error_type']}: {error_info['error_message']}")
        
        # Show traceback if requested
        if show_traceback:
            traceback.print_exc()
        
        # Execute callback if provided
        if callback:
            try:
                callback(e, error_info)
            except Exception as callback_error:
                logger.error(f"Error in error handling callback: {callback_error}")
        
        return error_info

def setup_error_handling(log_to_file: bool = True, log_level: int = logging.INFO):
    """
    Set up application-wide error handling.
    
    Args:
        log_to_file: Whether to log to a file
        log_level: The logging level to use
    """
    # Set logging level
    logger.setLevel(log_level)
    
    # Add file handler if requested
    if log_to_file:
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"pfg_{timestamp}.log"
        
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to {log_file}")
        
    # Set up global exception handler
    def global_exception_handler(exctype, value, tb):
        logger.critical("Unhandled exception", exc_info=(exctype, value, tb))
        sys.__excepthook__(exctype, value, tb)
    
    sys.excepthook = global_exception_handler
    
    logger.info("Error handling system initialized") 