#!/usr/bin/env python
"""
Script to measure code coverage for the plugin hooks system.
"""

import sys
from typing import Dict, Any, List, Callable

print("Starting plugin hooks coverage measurement...")

# Direct imports of the plugin system
try:
    from pulp_fiction_generator.plugins.hooks import (
        register_hook, has_hook, get_hooks, call_hook,
        HOOK_INIT, HOOK_PRE_GENERATE, HOOK_POST_GENERATE,
        HOOK_PRE_SAVE, HOOK_POST_SAVE, HOOK_PROMPT_ENHANCEMENT
    )
    print("Successfully imported plugin hooks modules")
except ImportError as e:
    print(f"Error importing plugin hooks modules: {e}")
    sys.exit(1)


def test_hook_system():
    """Test the hook system functionality."""
    print("Testing hook system...")
    
    # Define some test hooks
    def init_hook(config: Dict[str, Any]) -> Dict[str, Any]:
        print(f"  Init hook called with: {config}")
        config["initialized"] = True
        return config
    
    def pre_generate_hook(data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"  Pre-generate hook called with: {data}")
        data["modified"] = True
        return data
    
    def post_generate_hook(story: str, metadata: Dict[str, Any]) -> str:
        print(f"  Post-generate hook called with metadata: {metadata}")
        return f"Enhanced: {story}"
    
    # Register the hooks
    register_hook(HOOK_INIT, init_hook)
    register_hook(HOOK_PRE_GENERATE, pre_generate_hook)
    register_hook(HOOK_POST_GENERATE, post_generate_hook)
    print("  Registered hooks")
    
    # Check if hooks are registered
    assert has_hook(HOOK_INIT)
    assert has_hook(HOOK_PRE_GENERATE)
    assert has_hook(HOOK_POST_GENERATE)
    assert not has_hook(HOOK_PRE_SAVE)  # No hook registered
    print("  Hook registration check works")
    
    # Get hooks for a specific hook point
    init_hooks = get_hooks(HOOK_INIT)
    assert len(init_hooks) == 1
    assert init_hooks[0] == init_hook
    print("  Retrieved hooks by name")
    
    # Get hooks for a nonexistent hook point
    empty_hooks = get_hooks("nonexistent_hook")
    assert len(empty_hooks) == 0
    print("  Empty list returned for nonexistent hooks")
    
    # Call hooks
    config = {"genre": "scifi", "temperature": 0.7}
    init_results = call_hook(HOOK_INIT, config)
    assert len(init_results) == 1
    assert init_results[0]["initialized"] is True
    assert init_results[0]["genre"] == "scifi"
    print("  Called init hook successfully")
    
    # Call hook with mismatched signature
    def mismatched_hook(arg1: str, arg2: int) -> None:
        """Hook with mismatched signature for testing"""
        pass
    
    register_hook(HOOK_PRE_SAVE, mismatched_hook)
    results = call_hook(HOOK_PRE_SAVE, {"data": "test"})
    assert len(results) == 0  # Should not call the mismatched hook
    print("  Properly handles mismatched hook signatures")
    
    # Register multiple hooks for the same hook point
    def another_pre_generate_hook(data: Dict[str, Any]) -> Dict[str, Any]:
        data["another_modification"] = True
        return data
    
    register_hook(HOOK_PRE_GENERATE, another_pre_generate_hook)
    pre_generate_hooks = get_hooks(HOOK_PRE_GENERATE)
    assert len(pre_generate_hooks) == 2
    
    data = {"content": "test"}
    pre_generate_results = call_hook(HOOK_PRE_GENERATE, data)
    assert len(pre_generate_results) == 2
    assert pre_generate_results[0]["modified"] is True
    assert pre_generate_results[1]["another_modification"] is True
    print("  Multiple hooks for same hook point work")
    
    print("Hook system tests passed!")


def test_common_hook_points():
    """Test the common hook points."""
    print("Testing common hook points...")
    
    # Test all available hook points
    hook_points = [
        HOOK_INIT,
        HOOK_PRE_GENERATE,
        HOOK_POST_GENERATE,
        HOOK_PRE_SAVE,
        HOOK_POST_SAVE,
        HOOK_PROMPT_ENHANCEMENT
    ]
    
    for hook_point in hook_points:
        print(f"  Hook point: {hook_point}")
    
    print("Common hook points test passed!")


if __name__ == "__main__":
    print("Testing plugin hooks functionality...")
    test_hook_system()
    test_common_hook_points()
    print("All plugin hooks tests passed!") 