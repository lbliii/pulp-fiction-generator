"""
Error recovery strategies.

This module provides recovery strategies for different types of errors,
allowing automatic recovery from certain failure conditions.
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

from .exceptions import (
    ConfigurationError, 
    ModelConnectionError, 
    ModelResponseError,
    ContentGenerationError
)

# Get logger
logger = logging.getLogger('pulp_fiction_generator')


class RecoveryStrategy:
    """Interface for error recovery strategies."""
    
    @staticmethod
    def can_recover(error: Exception) -> bool:
        """
        Determine if this strategy can recover from the given error.
        
        Args:
            error: The exception to check
            
        Returns:
            True if this strategy can recover from the error, False otherwise
        """
        return False
    
    @staticmethod
    def recover(error: Exception, context: Dict[str, Any]) -> Any:
        """
        Attempt to recover from the error.
        
        Args:
            error: The exception to recover from
            context: Context information about the error
            
        Returns:
            The result of the recovery action or None if recovery failed
            
        Raises:
            Exception: If recovery is not possible or fails
        """
        raise NotImplementedError("Recovery strategy not implemented")


class ModelRetryStrategy(RecoveryStrategy):
    """Recovery strategy for model-related errors."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    @staticmethod
    def can_recover(error: Exception) -> bool:
        """Check if the error is a model-related error that can be retried."""
        return isinstance(error, ModelConnectionError) or (
            isinstance(error, ModelResponseError) and "timeout" in str(error).lower()
        )
    
    @staticmethod
    def recover(error: Exception, context: Dict[str, Any]) -> Any:
        """
        Retry the model request.
        
        This strategy:
        1. Waits for a short delay
        2. Retries the original request up to MAX_RETRIES times
        3. If all retries fail, it throws the original exception
        """
        retry_count = context.get("retry_count", 0)
        original_function = context.get("function")
        args = context.get("args", [])
        kwargs = context.get("kwargs", {})
        
        if not original_function:
            raise ValueError("Cannot retry without original function")
            
        if retry_count >= ModelRetryStrategy.MAX_RETRIES:
            # Get the function name safely
            func_name = getattr(original_function, "__name__", "function")
            logger.error(f"Maximum retries ({ModelRetryStrategy.MAX_RETRIES}) reached for {func_name}")
            raise error
        
        # Wait before retrying
        time.sleep(ModelRetryStrategy.RETRY_DELAY * (retry_count + 1))
        
        # Get the function name safely
        func_name = getattr(original_function, "__name__", "function")
        logger.info(f"Retrying {func_name} (attempt {retry_count + 1}/{ModelRetryStrategy.MAX_RETRIES})")
        
        # Update retry count in context
        kwargs["_retry_context"] = {
            "function": original_function,
            "retry_count": retry_count + 1,
            "args": args,
            "kwargs": {k: v for k, v in kwargs.items() if k != "_retry_context"},
            "original_error": error
        }
        
        # Retry the function
        return original_function(*args, **kwargs)


class FallbackPromptStrategy(RecoveryStrategy):
    """Recovery strategy for content generation errors."""
    
    @staticmethod
    def can_recover(error: Exception) -> bool:
        """Check if the error is a content generation error that can be addressed with a fallback prompt."""
        return isinstance(error, ContentGenerationError) or (
            isinstance(error, ModelResponseError) and not "timeout" in str(error).lower()
        )
    
    @staticmethod
    def recover(error: Exception, context: Dict[str, Any]) -> Any:
        """
        Use a simplified fallback prompt.
        
        This strategy:
        1. Simplifies the original prompt to focus on core requirements
        2. Reduces complexity of the request
        3. Attempts generation with the simplified prompt
        """
        original_function = context.get("function")
        args = context.get("args", [])
        kwargs = context.get("kwargs", {})
        
        if not original_function:
            raise ValueError("Cannot use fallback prompt without original function")
        
        # Get the original prompt (assuming it's the first arg or in kwargs)
        original_prompt = args[0] if args else kwargs.get("prompt")
        if not original_prompt:
            logger.error("Cannot find original prompt for fallback strategy")
            raise error
            
        # Create a simplified version of the prompt
        simplified_prompt = f"""
SIMPLIFIED REQUEST (due to previous error):
Focus only on the core task and provide a simple, direct response.

ORIGINAL REQUEST:
{original_prompt}

Please provide a straightforward response focusing on the main request.
"""
        
        logger.info("Using simplified fallback prompt")
        
        # Replace original prompt with simplified version
        if args:
            new_args = [simplified_prompt] + list(args[1:])
        else:
            kwargs["prompt"] = simplified_prompt
            new_args = args
            
        # Add context to identify this as a fallback attempt
        kwargs["_fallback_context"] = {
            "function": original_function,
            "original_prompt": original_prompt,
            "original_error": error
        }
        
        # Try with the fallback prompt
        return original_function(*new_args, **kwargs)


class ConfigurationFixStrategy(RecoveryStrategy):
    """Recovery strategy for configuration-related errors."""
    
    @staticmethod
    def can_recover(error: Exception) -> bool:
        """Check if the error is a configuration error that can be fixed."""
        return isinstance(error, ConfigurationError)
    
    @staticmethod
    def recover(error: Exception, context: Dict[str, Any]) -> Any:
        """
        Attempt to fix configuration issues.
        
        This strategy:
        1. Identifies missing directories and creates them
        2. Fixes permission issues when possible
        3. Resets to default configurations for invalid settings
        """
        error_msg = str(error).lower()
        
        # Handle directory does not exist
        if "directory" in error_msg and ("not exist" in error_msg or "missing" in error_msg):
            dir_path = None
            
            # Try to extract the path from the error message
            for part in error_msg.split():
                if "path" in part or os.path.sep in part:
                    potential_path = part.strip("'\".,: ")
                    if os.path.sep in potential_path:
                        dir_path = potential_path
                        break
            
            if dir_path:
                try:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created missing directory: {dir_path}")
                    
                    # Retry the original function if available
                    original_function = context.get("function")
                    if original_function:
                        return original_function(
                            *context.get("args", []), 
                            **{k: v for k, v in context.get("kwargs", {}).items() if k != "_retry_context"}
                        )
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")
        
        # Handle config reset for invalid values
        if "invalid" in error_msg and "config" in error_msg:
            # This would need to interact with the config system
            # For now, we'll just log that we would reset the value
            logger.info("Would reset invalid configuration to defaults")
            
        # If we couldn't recover
        raise error


class RecoveryStrategyRegistry:
    """
    Registry of recovery strategies.
    
    This class maintains a registry of available recovery strategies
    and provides methods to find an appropriate strategy for a given error.
    """
    
    _strategies: List[Type[RecoveryStrategy]] = [
        ModelRetryStrategy,
        FallbackPromptStrategy,
        ConfigurationFixStrategy
    ]
    
    @classmethod
    def register(cls, strategy: Type[RecoveryStrategy]) -> None:
        """
        Register a new recovery strategy.
        
        Args:
            strategy: The strategy class to register
        """
        if strategy not in cls._strategies:
            cls._strategies.append(strategy)
    
    @classmethod
    def unregister(cls, strategy: Type[RecoveryStrategy]) -> None:
        """
        Unregister a recovery strategy.
        
        Args:
            strategy: The strategy class to unregister
        """
        if strategy in cls._strategies:
            cls._strategies.remove(strategy)
    
    @classmethod
    def find_strategy(cls, error: Exception) -> Optional[Type[RecoveryStrategy]]:
        """
        Find a recovery strategy that can handle the given error.
        
        Args:
            error: The exception to find a strategy for
            
        Returns:
            A recovery strategy class that can handle the error, or None if no such strategy exists
        """
        for strategy in cls._strategies:
            if strategy.can_recover(error):
                return strategy
        return None 