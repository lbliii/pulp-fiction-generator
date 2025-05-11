"""
Tests for the error handling module.
"""

import os
import pytest
import tempfile
import logging
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from pulp_fiction_generator.utils.errors import (
    # Exception classes
    PulpFictionError, TimeoutError, ConfigurationError, ModelServiceError,
    ModelConnectionError, ModelResponseError, ContentGenerationError,
    AgentError, StoryPersistenceError, InputValidationError, CliArgumentError,
    
    # Recovery strategies
    RecoveryStrategy, ModelRetryStrategy, FallbackPromptStrategy, ConfigurationFixStrategy,
    
    # Core functionality
    ErrorHandler, with_error_handling, DiagnosticCollector, timeout, setup_error_handling, DiagnosticLogger,
    RecoveryStrategyRegistry
)

# ===== Test Exception Classes =====

def test_exception_hierarchy():
    """Test that the exception hierarchy is correctly structured."""
    # Base class
    assert issubclass(PulpFictionError, Exception)
    
    # Direct subclasses of PulpFictionError
    assert issubclass(TimeoutError, PulpFictionError)
    assert issubclass(ConfigurationError, PulpFictionError)
    assert issubclass(ModelServiceError, PulpFictionError)
    assert issubclass(ContentGenerationError, PulpFictionError)
    assert issubclass(AgentError, PulpFictionError)
    assert issubclass(StoryPersistenceError, PulpFictionError)
    assert issubclass(InputValidationError, PulpFictionError)
    assert issubclass(CliArgumentError, PulpFictionError)
    
    # ModelService-related errors
    assert issubclass(ModelConnectionError, ModelServiceError)
    assert issubclass(ModelResponseError, ModelServiceError)

# ===== Test Timeout Context Manager =====

def test_timeout_raises_exception():
    """Test that the timeout context manager raises TimeoutError after specified seconds."""
    with pytest.raises(TimeoutError):
        with timeout(0.1):
            time.sleep(0.2)  # Sleep longer than the timeout

def test_timeout_does_not_raise_if_fast_enough():
    """Test that the timeout context manager doesn't raise if operation completes in time."""
    with timeout(0.2):
        time.sleep(0.1)  # Sleep shorter than the timeout

# ===== Test Diagnostic Info =====

def test_diagnostic_info_collection():
    """Test that diagnostic information is collected properly."""
    info = DiagnosticCollector.collect_all()
    
    # Check required fields
    assert "timestamp" in info
    assert "python_version" in info
    assert "platform" in info
    assert "environment_variables" in info
    assert "working_directory" in info
    assert "call_stack" in info

def test_diagnostic_info_save_to_file():
    """Test that diagnostic information can be saved to a file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        info = {"test": "data"}
        filepath = DiagnosticLogger.save_to_file(info, base_dir=tmpdirname)
        
        # Check that file exists
        assert os.path.exists(filepath)
        
        # Check that file contains the info
        import json
        with open(filepath, 'r') as f:
            saved_info = json.load(f)
        assert saved_info == info

# ===== Test Recovery Strategies =====

def test_recovery_strategy_interface():
    """Test the RecoveryStrategy base class interface."""
    # Base class should always return False for can_recover
    assert RecoveryStrategy.can_recover(Exception()) is False
    
    # Base class should raise NotImplementedError for recover
    with pytest.raises(NotImplementedError):
        RecoveryStrategy.recover(Exception(), {})

def test_model_retry_strategy():
    """Test the ModelRetryStrategy."""
    # Check what errors it can recover from
    assert ModelRetryStrategy.can_recover(ModelConnectionError())
    assert ModelRetryStrategy.can_recover(ModelResponseError("timeout occurred"))
    assert not ModelRetryStrategy.can_recover(Exception())
    
    # Test recovery with a mock function
    mock_function = MagicMock()
    context = {
        "function": mock_function,
        "retry_count": 0,
        "args": [1, 2],
        "kwargs": {"key": "value"}
    }
    
    # Should call the original function with _retry_context added
    ModelRetryStrategy.recover(ModelConnectionError(), context)
    mock_function.assert_called_once()
    args, kwargs = mock_function.call_args
    assert args == (1, 2)
    assert "key" in kwargs
    assert "_retry_context" in kwargs
    assert kwargs["_retry_context"]["retry_count"] == 1
    
    # Test maximum retries
    with pytest.raises(ModelConnectionError):
        ModelRetryStrategy.recover(
            ModelConnectionError(), 
            {**context, "retry_count": ModelRetryStrategy.MAX_RETRIES}
        )

def test_fallback_prompt_strategy():
    """Test the FallbackPromptStrategy."""
    # Check what errors it can recover from
    assert FallbackPromptStrategy.can_recover(ContentGenerationError())
    assert FallbackPromptStrategy.can_recover(ModelResponseError("invalid content"))
    assert not FallbackPromptStrategy.can_recover(ModelResponseError("timeout occurred"))
    
    # Test recovery with a mock function
    mock_function = MagicMock()
    
    # Test with positional prompt
    context = {
        "function": mock_function,
        "args": ["Original complex prompt", "other arg"],
        "kwargs": {"key": "value"}
    }
    
    FallbackPromptStrategy.recover(ContentGenerationError(), context)
    mock_function.assert_called_once()
    args, kwargs = mock_function.call_args
    assert "SIMPLIFIED REQUEST" in args[0]
    assert "Original complex prompt" in args[0]
    assert args[1] == "other arg"
    assert "_fallback_context" in kwargs
    
    # Test with keyword prompt
    mock_function.reset_mock()
    context = {
        "function": mock_function,
        "args": [],
        "kwargs": {"prompt": "Original complex prompt", "key": "value"}
    }
    
    FallbackPromptStrategy.recover(ContentGenerationError(), context)
    mock_function.assert_called_once()
    args, kwargs = mock_function.call_args
    assert "SIMPLIFIED REQUEST" in kwargs["prompt"]
    assert "Original complex prompt" in kwargs["prompt"]
    assert "_fallback_context" in kwargs

def test_configuration_fix_strategy():
    """Test the ConfigurationFixStrategy."""
    # Check what errors it can recover from
    assert ConfigurationFixStrategy.can_recover(ConfigurationError())
    assert not ConfigurationFixStrategy.can_recover(Exception())
    
    # Test directory creation
    with tempfile.TemporaryDirectory() as tmpdirname:
        test_dir = os.path.join(tmpdirname, "test_dir")
        mock_function = MagicMock()
        context = {
            "function": mock_function,
            "args": [],
            "kwargs": {}
        }
        
        error = ConfigurationError(f"Directory does not exist: {test_dir}")
        
        # Should create the directory and retry the function
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            try:
                ConfigurationFixStrategy.recover(error, context)
            except ConfigurationError:
                # Expected to re-raise if recovery not complete
                pass
            
            mock_mkdir.assert_called_once()

# ===== Test Error Handler =====

def test_error_handler_basic():
    """Test basic error handling without recovery attempts."""
    error = ValueError("Test error")
    
    # Handle without recovery
    result = ErrorHandler.handle_exception(
        error, 
        context={"test": "context"},
        collect_diagnostics=False,
        attempt_recovery=False
    )
    
    # Check result
    assert result["error_type"] == "ValueError"
    assert result["error_message"] == "Test error"
    assert result["context"]["test"] == "context"
    assert result["recovery"]["attempted"] is False

def test_error_handler_with_recovery():
    """Test error handling with recovery."""
    # Create a custom recovery strategy
    class TestRecoveryStrategy(RecoveryStrategy):
        @staticmethod
        def can_recover(error):
            return isinstance(error, ValueError)
        
        @staticmethod
        def recover(error, context):
            return "Recovered result"
    
    # Register the strategy
    RecoveryStrategyRegistry.register(TestRecoveryStrategy)
    
    # Attempt recovery
    result = ErrorHandler.handle_exception(
        ValueError("Test error"), 
        context={},
        collect_diagnostics=False,
        attempt_recovery=True
    )
    
    # Should be a tuple with error info and recovery result
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert result[0]["recovery"]["attempted"] is True
    assert result[0]["recovery"]["success"] is True
    assert result[1] == "Recovered result"
    
    # Clean up
    RecoveryStrategyRegistry.unregister(TestRecoveryStrategy)

# ===== Test Error Handling Decorator =====

def test_with_error_handling_decorator_no_error():
    """Test the with_error_handling decorator when no error occurs."""
    @with_error_handling
    def test_function(a, b):
        return a + b
    
    # Function should work normally
    assert test_function(1, 2) == 3

def test_with_error_handling_decorator_with_unrecoverable_error():
    """Test the with_error_handling decorator with an unrecoverable error."""
    @with_error_handling
    def test_function():
        raise ValueError("Test error")
    
    # Should re-raise the error
    with pytest.raises(ValueError):
        test_function()

def test_with_error_handling_decorator_with_recovery():
    """Test the with_error_handling decorator with a recoverable error."""
    # Create a custom recovery strategy
    class TestRecoveryStrategy(RecoveryStrategy):
        @staticmethod
        def can_recover(error):
            return isinstance(error, ValueError)
        
        @staticmethod
        def recover(error, context):
            return "Recovered result"
    
    # Register the strategy
    RecoveryStrategyRegistry.register(TestRecoveryStrategy)
    
    @with_error_handling
    def test_function():
        raise ValueError("Test error")
    
    # Should return the recovered result
    assert test_function() == "Recovered result"
    
    # Clean up
    RecoveryStrategyRegistry.unregister(TestRecoveryStrategy)

def test_with_error_handling_decorator_with_retry():
    """Test that the decorator properly handles retry contexts."""
    mock_function = MagicMock(side_effect=[ModelConnectionError(), "success"])
    
    @with_error_handling
    def test_function(*args, **kwargs):
        return mock_function(*args, **kwargs)
    
    # Set up the retry context
    result = test_function(_retry_context={
        "function": test_function,
        "retry_count": 0,
        "args": [],
        "kwargs": {}
    })
    
    # Should have called the function twice
    assert mock_function.call_count == 2
    assert result == "success"

# ===== Test Setup Function =====

def test_setup_error_handling():
    """Test that error handling setup works correctly."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        log_dir = Path(tmpdirname) / "logs"
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('logging.FileHandler') as mock_file_handler:
                with patch('sys.excepthook') as mock_excepthook:
                    with patch.object(Path, 'cwd', return_value=Path(tmpdirname)):
                        setup_error_handling()
                        
                        # Should create log directory
                        mock_mkdir.assert_called()
                        
                        # Should add file handler
                        mock_file_handler.assert_called()
                        
                        # Should set up global exception hook
                        assert mock_excepthook != sys.__excepthook__ 