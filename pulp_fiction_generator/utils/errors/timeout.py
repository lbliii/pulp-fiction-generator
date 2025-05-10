"""
Timeout handling utilities for function execution.

This module provides mechanisms to set timeouts for operations,
with different implementations based on the platform.
"""

import signal
import threading
import time
from contextlib import contextmanager
import logging

from .exceptions import TimeoutError

# Get logger
logger = logging.getLogger('pulp_fiction_generator')


class TimeoutManager:
    """
    Manages timeout handling for function calls.
    
    This class provides mechanisms to set timeouts for operations,
    with different implementations based on the platform.
    """
    
    @staticmethod
    @contextmanager
    def timeout(seconds: int):
        """
        Context manager for timing out function calls.
        
        Args:
            seconds: Maximum number of seconds to allow for the operation
            
        Raises:
            TimeoutError: If the operation times out
        """
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


# Alias for convenience
timeout = TimeoutManager.timeout 