"""
Hook points for plugins to extend the Pulp Fiction Generator.
"""

from typing import Dict, List, Any, Callable, Optional
import inspect

# Dictionary to store registered hooks
_hooks: Dict[str, List[Callable]] = {}

def register_hook(hook_name: str, callback: Callable) -> None:
    """Register a callback for a hook point"""
    if hook_name not in _hooks:
        _hooks[hook_name] = []
    
    _hooks[hook_name].append(callback)

def has_hook(hook_name: str) -> bool:
    """Check if any callbacks are registered for a hook"""
    return hook_name in _hooks and len(_hooks[hook_name]) > 0

def get_hooks(hook_name: str) -> List[Callable]:
    """Get all callbacks registered for a hook"""
    return _hooks.get(hook_name, [])

def call_hook(hook_name: str, *args, **kwargs) -> List[Any]:
    """Call all callbacks registered for a hook and return their results"""
    results = []
    
    for callback in get_hooks(hook_name):
        # Check if the callback signature matches the provided arguments
        sig = inspect.signature(callback)
        
        try:
            # Try to bind the arguments to the callback's signature
            sig.bind(*args, **kwargs)
            
            # If successful, call the callback and store the result
            result = callback(*args, **kwargs)
            results.append(result)
        except TypeError:
            # If binding fails, the callback signature doesn't match
            print(f"Warning: Hook callback {callback.__name__} signature doesn't match hook {hook_name}")
    
    return results

# Define common hook points
HOOK_INIT = "init"
HOOK_PRE_GENERATE = "pre_generate"
HOOK_POST_GENERATE = "post_generate"
HOOK_PRE_SAVE = "pre_save"
HOOK_POST_SAVE = "post_save"
HOOK_PROMPT_ENHANCEMENT = "prompt_enhancement" 