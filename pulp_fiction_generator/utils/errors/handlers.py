"""
Error handling components.

This module provides the central error handling facilities for the application,
including the main ErrorHandler class and information extraction.
"""

import inspect
import logging
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from .diagnostics import DiagnosticCollector, DiagnosticLogger
from .recovery import RecoveryStrategyRegistry

# Get logger
logger = logging.getLogger('pulp_fiction_generator')


class ErrorInformationExtractor:
    """
    Extracts information from exceptions.
    
    This class is responsible for gathering relevant information
    from exceptions to help with diagnosis and handling.
    """
    
    @staticmethod
    def extract_error_info(e: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract information from an exception.
        
        Args:
            e: The exception to extract information from
            context: Additional context about where/why the exception occurred
            
        Returns:
            Dictionary with error information
        """
        # Get the basic error information
        error_info = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "context": context
        }
        
        # Get caller information
        frame = inspect.currentframe().f_back.f_back  # Go back two frames to get the caller
        if frame:
            caller_info = {
                "file": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": frame.f_lineno
            }
            error_info["caller"] = caller_info
        
        return error_info


class ErrorHandler:
    """Central error handling facility for the application."""
    
    @classmethod
    def handle_exception(
        cls,
        e: Exception, 
        context: Optional[Dict[str, Any]] = None,
        collect_diagnostics: bool = True,
        show_traceback: bool = False,
        callback: Optional[Callable[[Exception, Dict[str, Any]], None]] = None,
        attempt_recovery: bool = True
    ) -> Dict[str, Any]:
        """
        Handle an exception in a standard way across the application.
        
        Args:
            e: The exception to handle
            context: Additional context about where/why the exception occurred
            collect_diagnostics: Whether to collect diagnostic information
            show_traceback: Whether to print the traceback to stderr
            callback: Optional callback to execute with the exception and error info
            attempt_recovery: Whether to attempt automatic recovery
            
        Returns:
            Dictionary with error information and diagnostics
        """
        context = context or {}
        
        # Get the basic error information
        error_info = ErrorInformationExtractor.extract_error_info(e, context)
        
        # Initialize recovery field
        error_info["recovery"] = {
            "attempted": False,
            "reason": "Recovery not attempted"
        }
        
        # Collect full diagnostic information if requested
        if collect_diagnostics:
            error_info["diagnostics"] = DiagnosticCollector.collect_all()
            
            # Save diagnostics to file
            try:
                log_file = DiagnosticLogger.save_to_file(error_info)
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
                logger.error(f"Error in callback: {callback_error}")
        
        # Attempt recovery if requested
        if attempt_recovery:
            recovery_result = cls._attempt_recovery(e, context, error_info)
            if recovery_result is not None:
                return recovery_result
        else:
            error_info["recovery"]["reason"] = "Recovery not requested"
        
        return error_info
    
    @classmethod
    def _attempt_recovery(
        cls, 
        error: Exception, 
        context: Dict[str, Any], 
        error_info: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Attempt to recover from an error.
        
        Args:
            error: The exception to recover from
            context: Context information about the error
            error_info: Information about the error
            
        Returns:
            The result of the recovery action or None if recovery failed
        """
        strategy = RecoveryStrategyRegistry.find_strategy(error)
        if strategy:
            logger.info(f"Attempting recovery with {strategy.__name__}")
            try:
                recovery_result = strategy.recover(error, context)
                error_info["recovery"] = {
                    "attempted": True,
                    "strategy": strategy.__name__,
                    "success": True
                }
                logger.info(f"Recovery successful with {strategy.__name__}")
                return (error_info, recovery_result)
            except Exception as recovery_error:
                error_info["recovery"] = {
                    "attempted": True,
                    "strategy": strategy.__name__,
                    "success": False,
                    "recovery_error": str(recovery_error)
                }
                logger.warning(f"Recovery attempt with {strategy.__name__} failed: {recovery_error}")
        else:
            error_info["recovery"] = {
                "attempted": False,
                "reason": "No suitable recovery strategy found"
            }
        
        return None 