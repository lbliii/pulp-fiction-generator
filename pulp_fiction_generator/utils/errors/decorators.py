"""
Decorators for error handling.

This module provides decorators that can be applied to functions
to provide standardized error handling.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar

from .handlers import ErrorHandler

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])

# Get logger
logger = logging.getLogger('pulp_fiction_generator')


def with_error_handling(
    func: Optional[F] = None, 
    collect_diagnostics: bool = True,
    show_traceback: bool = False,
    attempt_recovery: bool = True
) -> F:
    """
    Decorator that applies standard error handling to a function.
    
    Args:
        func: The function to decorate
        collect_diagnostics: Whether to collect diagnostic information
        show_traceback: Whether to print the traceback to stderr
        attempt_recovery: Whether to attempt automatic recovery
        
    Returns:
        The decorated function
    """
    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Check if this is a retry attempt
            retry_context = kwargs.pop("_retry_context", None)
            fallback_context = kwargs.pop("_fallback_context", None)
            
            try:
                return f(*args, **kwargs)
            except Exception as e:
                # Prepare context for error handling
                context = {}
                
                # Include retry info
                if retry_context:
                    context.update(retry_context)
                elif fallback_context:
                    context.update(fallback_context)
                else:
                    context["function"] = f
                    context["args"] = args
                    context["kwargs"] = kwargs
                
                # Handle the exception
                error_info = ErrorHandler.handle_exception(
                    e,
                    context=context,
                    collect_diagnostics=collect_diagnostics,
                    show_traceback=show_traceback,
                    attempt_recovery=attempt_recovery
                )
                
                # If we got a result from recovery, return it
                if isinstance(error_info, dict) and "recovery" in error_info and error_info["recovery"].get("success", False):
                    if "result" in error_info:
                        return error_info["result"]
                
                # Otherwise, re-raise the exception
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func) 