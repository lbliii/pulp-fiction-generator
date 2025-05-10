"""
Plot structure validator for ensuring stories follow a plot template.
"""

from typing import Dict, List, Any, Optional

from .base import PlotStructure, PlotPoint


class PlotValidator:
    """
    Validates that a story follows a given plot structure.
    
    This class provides tools for checking whether a story adheres
    to a particular plot structure and narrative arc, and offers
    suggestions for improvement.
    """
    
    def __init__(self, model_service=None):
        """
        Initialize the plot validator.
        
        Args:
            model_service: Optional model service for AI-assisted validation
        """
        self.model_service = model_service
        
    def validate(self, story_text: str, plot_structure: PlotStructure) -> Dict[str, Any]:
        """
        Validate a story against a plot structure.
        
        Args:
            story_text: The text of the story to validate
            plot_structure: The plot structure to validate against
            
        Returns:
            A dictionary with validation results, including:
            - valid: Boolean indicating overall validity
            - missing_plot_points: List of plot points not found
            - out_of_order_plot_points: List of plot points in wrong order
            - strength: Float indicating how well the story follows the structure (0.0-1.0)
            - suggestions: List of improvement suggestions
        """
        result = {
            "valid": True,
            "missing_plot_points": [],
            "out_of_order_plot_points": [],
            "strength": 0.0,
            "suggestions": []
        }
        
        # If we have a model service, use AI for validation
        if self.model_service:
            return self._ai_validate(story_text, plot_structure)
            
        # Otherwise, perform basic keyword-based validation
        return self._basic_validate(story_text, plot_structure)
    
    def _basic_validate(self, story_text: str, plot_structure: PlotStructure) -> Dict[str, Any]:
        """
        Perform basic validation using keyword matching.
        
        Args:
            story_text: The text of the story to validate
            plot_structure: The plot structure to validate against
            
        Returns:
            Validation results dictionary
        """
        result = {
            "valid": True,
            "missing_plot_points": [],
            "out_of_order_plot_points": [],
            "strength": 0.0,
            "suggestions": []
        }
        
        story_text_lower = story_text.lower()
        found_points = []
        found_indices = []
        
        # Look for plot points by name and keywords
        for i, plot_point in enumerate(plot_structure.plot_points):
            point_name_lower = plot_point.name.lower()
            point_desc_lower = plot_point.description.lower()
            
            # Check if plot point is mentioned by name or description
            if point_name_lower in story_text_lower or any(keyword.lower() in story_text_lower 
                                                        for keyword in point_desc_lower.split()
                                                        if len(keyword) > 5):
                found_points.append(plot_point.name)
                # Find the earliest occurrence of the plot point
                name_pos = story_text_lower.find(point_name_lower)
                desc_pos = story_text_lower.find(point_desc_lower)
                
                if name_pos != -1 and desc_pos != -1:
                    found_indices.append(min(name_pos, desc_pos))
                elif name_pos != -1:
                    found_indices.append(name_pos)
                elif desc_pos != -1:
                    found_indices.append(desc_pos)
                else:
                    # If we can't find the exact position, approximate it
                    found_indices.append(len(story_text_lower) * (i / len(plot_structure.plot_points)))
            else:
                result["missing_plot_points"].append(plot_point.name)
        
        # Check for out-of-order plot points
        if len(found_indices) >= 2:
            for i in range(len(found_indices) - 1):
                if found_indices[i] > found_indices[i + 1]:
                    result["out_of_order_plot_points"].append(
                        f"{found_points[i]} appears after {found_points[i + 1]}"
                    )
        
        # Calculate strength based on found plot points and order
        if plot_structure.plot_points:
            # 70% of strength is based on coverage of plot points
            coverage_strength = 0.7 * (len(found_points) / len(plot_structure.plot_points))
            
            # 30% of strength is based on correct order
            order_strength = 0.3 * (1.0 - (len(result["out_of_order_plot_points"]) / 
                                          max(1, len(found_points) - 1)))
            
            result["strength"] = coverage_strength + order_strength
        
        # Generate basic suggestions
        if result["missing_plot_points"]:
            result["suggestions"].append(
                f"Consider including these missing plot points: {', '.join(result['missing_plot_points'])}"
            )
            
        if result["out_of_order_plot_points"]:
            result["suggestions"].append(
                "Some plot points appear out of sequence. Consider reordering events in the story."
            )
            
        # Overall validity
        result["valid"] = (result["strength"] >= 0.6 and 
                          len(result["out_of_order_plot_points"]) <= len(plot_structure.plot_points) / 3)
        
        return result
    
    def _ai_validate(self, story_text: str, plot_structure: PlotStructure) -> Dict[str, Any]:
        """
        Perform AI-assisted validation.
        
        Args:
            story_text: The text of the story to validate
            plot_structure: The plot structure to validate against
            
        Returns:
            Validation results dictionary
        """
        # Default result structure
        result = {
            "valid": True,
            "missing_plot_points": [],
            "out_of_order_plot_points": [],
            "strength": 0.8,
            "suggestions": []
        }
        
        try:
            # Prepare the prompt for the AI to analyze the story
            prompt = self._build_validation_prompt(story_text, plot_structure)
            
            # Get response from the model
            response = self.model_service.generate_text(prompt)
            
            # Parse the response to extract validation results
            parsed_result = self._parse_validation_response(response)
            if parsed_result:
                result.update(parsed_result)
                
        except Exception as e:
            # Fall back to basic validation on error
            result = self._basic_validate(story_text, plot_structure)
            result["suggestions"].append(f"AI validation failed: {str(e)}")
            
        return result
    
    def _build_validation_prompt(self, story_text: str, plot_structure: PlotStructure) -> str:
        """
        Build a prompt for AI-assisted plot validation.
        
        Args:
            story_text: The text of the story to validate
            plot_structure: The plot structure to validate against
            
        Returns:
            Prompt string for the AI model
        """
        # Create a concise version of the story if it's too long
        story_summary = story_text
        if len(story_text) > 6000:
            # Use first and last portions for context
            story_summary = story_text[:3000] + "\n\n[...story continues...]\n\n" + story_text[-3000:]
        
        plot_points_str = "\n".join([
            f"- {pp.name}: {pp.description}" for pp in plot_structure.plot_points
        ])
        
        return f"""
        I need you to analyze this story and determine how well it follows the plot structure provided below.
        
        Plot Structure: {plot_structure.name}
        
        Plot Points (in expected order):
        {plot_points_str}
        
        Story to analyze:
        {story_summary}
        
        Please evaluate:
        1. Which plot points are present in the story?
        2. Which plot points are missing?
        3. Are the plot points in the correct order?
        4. How strongly does the story adhere to the structure (0.0-1.0)?
        5. What suggestions would you give to better follow this structure?
        
        Format your response as a JSON object with these keys:
        - missing_plot_points: array of plot point names
        - out_of_order_plot_points: array of string descriptions of order issues
        - strength: float between 0.0 and 1.0
        - suggestions: array of string suggestions
        - valid: boolean indicating if the story sufficiently follows the structure
        
        Response:
        """
    
    def _parse_validation_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the AI validation response into a structured result.
        
        Args:
            response: The text response from the AI
            
        Returns:
            Dictionary with validation results, or None if parsing failed
        """
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON object in the response
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                
                # Ensure all required keys are present
                required_keys = ["missing_plot_points", "out_of_order_plot_points", 
                                "strength", "suggestions", "valid"]
                if all(key in result for key in required_keys):
                    return result
                    
        except (json.JSONDecodeError, AttributeError):
            pass
            
        return None
    
    
class PlotStructureAnalyzer:
    """
    Analyzes a story to determine which plot structure it follows.
    
    This class can identify the narrative arc and plot structure
    that best matches a given story.
    """
    
    def __init__(self, model_service=None):
        """
        Initialize the plot structure analyzer.
        
        Args:
            model_service: Optional model service for AI-assisted analysis
        """
        self.model_service = model_service
        self.validator = PlotValidator(model_service)
        
    def analyze(self, story_text: str, plot_structures: List[PlotStructure]) -> Dict[str, Any]:
        """
        Analyze a story to determine which plot structure it best follows.
        
        Args:
            story_text: The text of the story to analyze
            plot_structures: List of plot structures to compare against
            
        Returns:
            Dictionary with analysis results, including:
            - best_match: Name of the best matching plot structure
            - scores: Dictionary mapping structure names to match scores (0.0-1.0)
            - details: Dictionary with detailed validation results for each structure
        """
        results = {
            "best_match": None,
            "scores": {},
            "details": {}
        }
        
        best_score = 0.0
        best_match = None
        
        # Validate against each plot structure
        for structure in plot_structures:
            validation = self.validator.validate(story_text, structure)
            score = validation["strength"]
            
            results["scores"][structure.name] = score
            results["details"][structure.name] = validation
            
            if score > best_score:
                best_score = score
                best_match = structure.name
        
        results["best_match"] = best_match
        
        return results 