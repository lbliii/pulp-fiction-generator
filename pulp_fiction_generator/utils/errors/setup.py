"""
Setup utilities for error handling.

This module provides functions to set up global error handling
for the application, including logging configuration.
"""

import sys
import logging
import traceback
from pathlib import Path

from .diagnostics import DiagnosticCollector, DiagnosticLogger

# Configure default logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger('pulp_fiction_generator')


def setup_error_handling(log_to_file: bool = True, log_level: int = logging.INFO):
    """
    Set up global error handling for the application.
    
    Args:
        log_to_file: Whether to log errors to a file
        log_level: The logging level to use
    """
    # Configure logging
    logger.setLevel(log_level)
    
    # Add file handler if requested
    if log_to_file:
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True, parents=True)
        
        file_handler = logging.FileHandler(log_dir / "pulp_fiction_generator.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        logger.addHandler(file_handler)
    
    # Set up global exception handler
    def global_exception_handler(exctype, value, tb):
        """
        Global handler for uncaught exceptions.
        
        Args:
            exctype: The exception type
            value: The exception value
            tb: The traceback
        """
        # Log the error
        logger.critical(f"Uncaught {exctype.__name__}: {value}")
        
        # Show traceback
        traceback.print_exception(exctype, value, tb)
        
        # Collect diagnostics
        info = DiagnosticCollector.collect_all()
        DiagnosticLogger.log_diagnostics(info)
    
    # Register the global exception handler
    sys.excepthook = global_exception_handler 