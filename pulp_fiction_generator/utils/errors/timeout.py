"""
Timeout handling utilities for function execution.

This module provides mechanisms to set timeouts for operations,
with different implementations based on the platform.
"""

import signal
import threading
import time
import platform
from contextlib import contextmanager
import logging
import sys

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
        # For Unix-like systems (but not macOS), use signal-based timeout
        if hasattr(signal, 'SIGALRM') and platform.system() != 'Darwin':
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
        
        # For Windows, macOS or other systems without SIGALRM, use thread-based timeout
        else:
            # Use an event for better synchronization
            completed = threading.Event()
            
            def check_timeout():
                """Thread that checks if the operation has timed out"""
                start_time = time.time()
                
                # Wait either for completion or timeout
                while not completed.is_set() and time.time() - start_time < seconds:
                    # Check every 0.1 seconds
                    completed.wait(0.1)
                
                # If completed was not set, then we timed out
                if not completed.is_set():
                    logger.warning(f"Operation timed out after {seconds} seconds")
                    # Since we can't reliably interrupt the main thread on all platforms,
                    # we'll record the timeout and let the main thread handle it
                    check_timeout.timed_out = True
            
            # Initialize the flag
            check_timeout.timed_out = False
            
            # Start the timeout thread
            timer_thread = threading.Thread(target=check_timeout)
            timer_thread.daemon = True
            timer_thread.start()
            
            try:
                yield
            finally:
                # Set the completion event to stop the timer thread
                completed.set()
                
                # Wait for the timer thread to finish
                timer_thread.join(0.5)  # Wait up to 0.5s for the thread to finish
                
                # Check if we timed out
                if check_timeout.timed_out:
                    logger.error(f"Function call timed out after {seconds} seconds")
                    raise TimeoutError(f"Function call timed out after {seconds} seconds")


# Alias for convenience
timeout = TimeoutManager.timeout 