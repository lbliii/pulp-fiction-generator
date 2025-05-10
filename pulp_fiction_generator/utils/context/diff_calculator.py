"""
Utility for calculating differences between context states.
"""

from typing import Any, Dict


class ContextDiffCalculator:
    """
    Calculates differences between context states.
    
    This class provides methods to compare context states and identify changes.
    """
    
    @staticmethod
    def calculate_diff(before, after) -> Dict[str, tuple]:
        """
        Calculate differences between before and after context.
        
        Args:
            before: The context before changes
            after: The context after changes
            
        Returns:
            Dictionary mapping changed keys to (old_value, new_value) tuples
        """
        diff = {}
        
        # Handle case when contexts are not dictionaries
        if not isinstance(before, dict) or not isinstance(after, dict):
            if before != after:
                return {"content": (before, after)}
            return {}
        
        # Find keys in after that are not in before or have different values
        for key in after:
            if key not in before:
                diff[key] = (None, after[key])
            elif before[key] != after[key]:
                diff[key] = (before[key], after[key])
        
        # Find keys in before that are not in after
        for key in before:
            if key not in after:
                diff[key] = (before[key], None)
        
        return diff 