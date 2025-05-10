"""
Base command classes for Pulp Fiction Generator CLI.
"""

from typing import Dict, List, Any, Optional, ClassVar, Callable
import typer
from rich.console import Console
from abc import ABC, abstractmethod
import functools
import sys
import inspect

from ..utils.errors import ErrorHandler, setup_error_handling, logger

console = Console()

# Helper function for improved error reporting in command callbacks
def with_error_handling(func):
    """Decorator to add consistent error handling to commands"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = ErrorHandler.handle_exception(
                e, 
                context={"command": func.__name__, "args": args, "kwargs": kwargs},
                show_traceback=kwargs.get("verbose", False)
            )
            
            # User-friendly error display
            console.print(f"\n[bold red]Error:[/bold red] {error_info['error_message']}")
            
            # Show detailed error location in verbose mode
            if kwargs.get("verbose", False):
                caller = error_info.get("caller", {})
                if caller:
                    console.print(f"[dim]Location: {caller.get('file')}:{caller.get('line')} in {caller.get('function')}[/dim]")
            
            # Show potential solutions for common errors
            if isinstance(e, NameError) and "Task" in str(e):
                console.print("[yellow]Hint: This might be due to a missing import. Make sure 'from crewai import Task' is properly imported.[/yellow]")
            elif "Failed to connect to Ollama" in str(e) or "Connection refused" in str(e):
                console.print("[yellow]Hint: Make sure Ollama is running with 'ollama serve' and the model is available.[/yellow]")
            
            # Always tell the user where to find more details
            if "log_file" in error_info:
                console.print(f"[dim]Detailed error information saved to {error_info['log_file']}[/dim]")
            
            sys.exit(1)
    
    return wrapper

def command_callback(cls, **options):
    """Create a Typer command callback for the class"""
    @with_error_handling
    def callback(**kwargs):
        return cls._run_impl(**kwargs)
    return callback

class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    # Class variables
    name: ClassVar[str] = ""
    help: ClassVar[str] = ""
    
    @classmethod
    def run(cls, **kwargs) -> Any:
        """Run the command"""
        return cls._run_impl(**kwargs)
    
    @classmethod
    @abstractmethod
    def _run_impl(cls, **kwargs) -> Any:
        """Implementation of the run method"""
        pass
    
    @staticmethod
    def success(message: str) -> None:
        """Display a success message"""
        console.print(f"[bold green]{message}[/bold green]")
    
    @staticmethod
    def error(message: str) -> None:
        """Display an error message"""
        console.print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def info(message: str) -> None:
        """Display an info message"""
        console.print(f"[blue]{message}[/blue]")


class GenerateCommand(BaseCommand):
    """Base class for generation commands"""
    
    @classmethod
    @with_error_handling
    def run(cls, **kwargs) -> Any:
        """Run the command with error handling"""
        return cls._run_impl(**kwargs)
    
    @classmethod
    @abstractmethod
    def _run_impl(cls, **kwargs) -> Any:
        """Implementation of the run method"""
        pass


class ListCommand(BaseCommand):
    """Base class for listing commands"""
    
    @classmethod
    @with_error_handling
    def run(cls, **kwargs) -> Any:
        """Run the command with error handling"""
        return cls._run_impl(**kwargs)
    
    @classmethod
    @abstractmethod
    def _run_impl(cls, **kwargs) -> Any:
        """Implementation of the run method"""
        pass


class CheckCommand(BaseCommand):
    """Base class for checking/validation commands"""
    
    @classmethod
    @with_error_handling
    def run(cls, **kwargs) -> Any:
        """Run the command with error handling"""
        return cls._run_impl(**kwargs)
    
    @classmethod
    @abstractmethod
    def _run_impl(cls, **kwargs) -> Any:
        """Implementation of the run method"""
        pass


class SetupCommand(BaseCommand):
    """Base class for setup/configuration commands"""
    
    @classmethod
    @with_error_handling
    def run(cls, **kwargs) -> Any:
        """Run the command with error handling"""
        return cls._run_impl(**kwargs)
    
    @classmethod
    @abstractmethod
    def _run_impl(cls, **kwargs) -> Any:
        """Implementation of the run method"""
        pass 