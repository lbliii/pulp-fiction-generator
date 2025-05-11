"""
Execution engine for running tasks and crews.

Handles execution, error handling, and timeouts.
"""

from typing import Any, Dict, Optional, Union, List

from crewai import Task, Crew
from pydantic import BaseModel

from ..utils.errors import ErrorHandler, logger, timeout, TimeoutError


class ExecutionEngine:
    """
    Handles the execution of tasks and crews.
    
    This class isolates the execution logic from the story generation
    process, making it more modular and maintainable.
    """
    
    def __init__(self, debug_mode: bool = False, verbose: bool = False, max_retries: int = 2):
        """
        Initialize the execution engine.
        
        Args:
            debug_mode: Whether to enable debug mode
            verbose: Whether to enable verbose logging
            max_retries: Maximum number of retry attempts for timeout failures
        """
        self.debug_mode = debug_mode
        self.verbose = verbose
        self.max_retries = max_retries
    
    def execute_task(
        self, 
        task: Task, 
        timeout_seconds: int = 120,
        retry_count: int = 0
    ) -> str:
        """
        Execute a task and return its result.
        
        Args:
            task: The task to execute
            timeout_seconds: Maximum time to wait for task completion
            retry_count: Current retry attempt (used internally)
            
        Returns:
            The result of the task execution
            
        Raises:
            TimeoutError: If the task execution times out after max retries
        """
        # Add task context to diagnostic information
        context = {
            "task_description": task.description,
            "agent_name": task.agent.name if hasattr(task.agent, "name") else "Unknown",
            "expected_output": task.expected_output,
        }
        
        logger.info(f"Starting task execution: {context['agent_name']}")
        logger.info(f"Task description: {task.description[:100]}...")
        
        # Create a simple crew with just this task
        single_task_crew = Crew(
            agents=[task.agent],
            tasks=[task],
            verbose=self.verbose,
        )
        
        try:
            # Execute the crew with a timeout
            logger.info(f"Executing crew with timeout of {timeout_seconds} seconds")
            with timeout(timeout_seconds):
                result = single_task_crew.kickoff()
                
            logger.info(f"Task completed successfully, result length: {len(result)} chars")
            
            # Access task output directly
            task_output = None
            if hasattr(task, 'output'):
                # Check if we have a structured output
                if hasattr(task.output, 'parsed') and task.output.parsed:
                    logger.info(f"Task has structured output: {type(task.output.parsed)}")
                    
                    # For structured outputs, we'll use the content field or convert to string
                    if hasattr(task.output.parsed, 'content'):
                        task_output = task.output.parsed.content
                    else:
                        task_output = str(task.output.parsed)
                else:
                    # Use raw output
                    task_output = task.output.raw
            else:
                task_output = result
            
            # Execute callback if present
            if hasattr(task, 'callback') and callable(task.callback):
                logger.info("Executing task callback")
                try:
                    task.callback(task)
                except Exception as e:
                    logger.error(f"Error in task callback: {e}")
            
            return task_output or result
            
        except TimeoutError:
            error_msg = f"Task execution timed out after {timeout_seconds} seconds"
            logger.warning(error_msg)
            
            # Implement retry mechanism for timeouts
            if retry_count < self.max_retries:
                retry_count += 1
                logger.info(f"Retrying task execution (attempt {retry_count}/{self.max_retries})")
                
                # Increase timeout for retry attempts
                new_timeout = int(timeout_seconds * 1.5)
                logger.info(f"Increasing timeout to {new_timeout} seconds for retry")
                
                # Recursive call with incremented retry count
                return self.execute_task(task, new_timeout, retry_count)
            else:
                logger.error(f"Task execution failed after {retry_count} retries")
                raise TimeoutError(f"Task execution timed out after {retry_count+1} attempts (last timeout: {timeout_seconds}s)")
            
        except Exception as e:
            # Enhance the exception with task context and diagnostic information
            error_info = ErrorHandler.handle_exception(
                e, 
                context=context,
                collect_diagnostics=True,
                show_traceback=self.debug_mode
            )
            
            # Log that we're attempting to recover
            logger.warning(f"Task execution failed. Attempting to return partial results.")
            
            # If we have a partial result in the context, use it
            if hasattr(single_task_crew, "last_result") and single_task_crew.last_result:
                logger.info("Recovered partial result from failed task.")
                return single_task_crew.last_result
                
            # Raise the original exception with enhanced context
            raise
    
    def execute_crew(
        self, 
        crew: Crew, 
        custom_inputs: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 300,
        retry_count: int = 0,
        crew_factory = None  # Optional CrewFactory instance to get stored custom inputs
    ) -> str:
        """
        Execute a crew and return its result.
        
        Args:
            crew: The crew to execute
            custom_inputs: Optional custom inputs for the crew
            timeout_seconds: Maximum time to wait for execution
            retry_count: Current retry attempt (used internally)
            crew_factory: Optional CrewFactory to retrieve stored custom inputs
            
        Returns:
            The result of the crew execution
            
        Raises:
            TimeoutError: If the crew execution times out after max retries
        """
        try:
            # Execute the crew with a timeout
            logger.info(f"Starting crew execution with timeout of {timeout_seconds} seconds")
            
            with timeout(timeout_seconds):
                # First, check if there are stored custom inputs in the crew_factory
                stored_inputs = None
                if crew_factory:
                    stored_inputs = crew_factory.get_custom_inputs(crew)
                    if stored_inputs:
                        logger.info(f"Using custom_inputs from CrewFactory storage")
                
                # If we have stored inputs, use those
                if stored_inputs:
                    result = crew.kickoff(inputs=stored_inputs)
                # Otherwise, use the custom_inputs from the method parameter
                elif custom_inputs:
                    logger.info(f"Using custom_inputs from method parameter")
                    result = crew.kickoff(inputs=custom_inputs)
                else:
                    logger.info(f"No custom_inputs provided")
                    result = crew.kickoff()
                
            logger.info(f"Crew execution complete, result length: {len(result)} characters")
            
            return result
        except TimeoutError:
            error_msg = f"Crew execution timed out after {timeout_seconds} seconds"
            logger.warning(error_msg)
            
            # Implement retry mechanism for timeouts
            if retry_count < self.max_retries:
                retry_count += 1
                logger.info(f"Retrying crew execution (attempt {retry_count}/{self.max_retries})")
                
                # Increase timeout for retry attempts
                new_timeout = int(timeout_seconds * 1.5)
                logger.info(f"Increasing timeout to {new_timeout} seconds for retry")
                
                # Recursive call with incremented retry count
                return self.execute_crew(crew, custom_inputs, new_timeout, retry_count)
            else:
                logger.error(f"Crew execution failed after {retry_count} retries")
                raise TimeoutError(f"Crew execution timed out after {retry_count+1} attempts (last timeout: {timeout_seconds}s)")
        except Exception as e:
            # Enhance the exception with crew context and diagnostic information
            error_info = ErrorHandler.handle_exception(
                e, 
                context={"crew": str(crew)},
                collect_diagnostics=True,
                show_traceback=self.debug_mode
            )
            
            # Re-raise the exception with enhanced context
            raise 