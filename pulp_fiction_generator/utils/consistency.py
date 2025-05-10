"""
Consistency checking utilities for maintaining character and plot coherence.

This module provides tools to check for consistency issues in characters,
settings, and plot elements across a story to maintain narrative coherence.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from ..models.model_service import ModelService


class CharacterConsistencyChecker:
    """
    Class to check for character consistency issues in a story.
    
    This analyzes character attributes and behaviors across chapters to
    identify potential inconsistencies that would harm narrative coherence.
    """
    
    def __init__(self, model_service: Optional[ModelService] = None):
        """
        Initialize the character consistency checker.
        
        Args:
            model_service: Optional model service for AI-assisted checks
        """
        self.model_service = model_service
        
    def check_character_consistency(self, character: Dict[str, Any], 
                                   story_text: str) -> List[Dict[str, str]]:
        """
        Check for inconsistencies in a character throughout a story.
        
        Args:
            character: Character metadata dictionary
            story_text: Full text of the story
            
        Returns:
            List of inconsistency issues found
        """
        issues = []
        
        # Extract character name and key attributes
        name = character.get("name", "")
        if not name:
            return issues
            
        traits = character.get("traits", [])
        background = character.get("background", "")
        
        # Basic checks (without model)
        issues.extend(self._check_basic_character_consistency(name, traits, background, story_text))
        
        # AI-assisted checks (if model service is available)
        if self.model_service:
            issues.extend(self._check_ai_character_consistency(character, story_text))
            
        return issues
        
    def _check_basic_character_consistency(self, name: str, traits: List[str], 
                                         background: str, story_text: str) -> List[Dict[str, str]]:
        """
        Perform basic rule-based consistency checks for a character.
        
        Args:
            name: Character name
            traits: Character traits
            background: Character background
            story_text: Full text of the story
            
        Returns:
            List of inconsistency issues found
        """
        issues = []
        
        # Check for name variations
        name_variations = self._find_name_variations(name, story_text)
        if len(name_variations) > 1:
            issues.append({
                "type": "name_variation",
                "character": name,
                "description": f"Character name has multiple variations: {', '.join(name_variations)}",
                "severity": "warning"
            })
        
        # Check for missing character in later chapters
        if name in story_text[:len(story_text)//2] and name not in story_text[len(story_text)//2:]:
            issues.append({
                "type": "character_disappearance",
                "character": name,
                "description": f"Character {name} appears in early chapters but disappears later",
                "severity": "medium"
            })
        
        return issues
        
    def _check_ai_character_consistency(self, character: Dict[str, Any], 
                                      story_text: str) -> List[Dict[str, str]]:
        """
        Use AI to check for more complex character consistency issues.
        
        Args:
            character: Character metadata dictionary
            story_text: Full text of the story
            
        Returns:
            List of inconsistency issues found
        """
        if not self.model_service:
            return []
            
        issues = []
        name = character.get("name", "")
        
        # Prepare prompt for the model
        prompt = f"""
        Analyze the character "{name}" in this story for consistency issues.
        
        Character details:
        - Traits: {', '.join(character.get('traits', []))}
        - Background: {character.get('background', '')}
        - Motivations: {', '.join(character.get('motivations', []))}
        
        Story excerpt (focusing on sections with this character):
        
        {self._extract_character_contexts(name, story_text, max_length=1500)}
        
        Identify any inconsistencies in:
        1. Personality traits
        2. Speech patterns
        3. Motivations
        4. Background details
        5. Behaviors and decisions
        
        Format your response as a JSON array with objects having these fields:
        - "issue_type": The type of inconsistency
        - "description": A description of the inconsistency
        - "evidence": Text evidence for the inconsistency
        - "severity": "low", "medium", or "high"
        
        Example:
        [
          {
            "issue_type": "personality_shift",
            "description": "Character shows uncharacteristic bravery inconsistent with earlier cowardice",
            "evidence": "In Ch.1: 'John cowered in fear'...; In Ch.3: 'John charged fearlessly'",
            "severity": "medium"
          }
        ]
        
        If no issues are found, return an empty array.
        """
        
        try:
            response = self.model_service.get_completion(prompt)
            # Parse the response to extract issues
            # This is a simplification; in a real implementation you would have
            # more robust parsing and error handling
            if response.strip().startswith("[") and response.strip().endswith("]"):
                import json
                try:
                    ai_issues = json.loads(response)
                    for issue in ai_issues:
                        issues.append({
                            "type": issue.get("issue_type", "unknown"),
                            "character": name,
                            "description": issue.get("description", ""),
                            "evidence": issue.get("evidence", ""),
                            "severity": issue.get("severity", "medium")
                        })
                except json.JSONDecodeError:
                    # If parsing fails, add a generic issue
                    issues.append({
                        "type": "parsing_error",
                        "character": name,
                        "description": "Could not parse AI consistency check results",
                        "severity": "low"
                    })
        except Exception as e:
            # Handle any errors in the AI processing
            issues.append({
                "type": "ai_check_error",
                "character": name,
                "description": f"Error in AI consistency check: {str(e)}",
                "severity": "low"
            })
        
        return issues
    
    def _find_name_variations(self, name: str, text: str) -> Set[str]:
        """
        Find variations of a character name in text.
        
        Args:
            name: Base character name
            text: Text to search
            
        Returns:
            Set of name variations found
        """
        variations = {name}
        
        # Check for first/last name variations if name has multiple parts
        name_parts = name.split()
        if len(name_parts) > 1:
            # Add first name
            variations.add(name_parts[0])
            # Add last name with "Mr./Ms./Mrs." prefix
            variations.add(f"Mr. {name_parts[-1]}")
            variations.add(f"Ms. {name_parts[-1]}")
            variations.add(f"Mrs. {name_parts[-1]}")
            
        # Return only variations that actually appear in the text
        return {var for var in variations if var in text}
        
    def _extract_character_contexts(self, name: str, text: str, 
                                  max_length: int = 1500) -> str:
        """
        Extract parts of the text that mention the character.
        
        Args:
            name: Character name
            text: Full text
            max_length: Maximum length of extracted text
            
        Returns:
            Extracted text focusing on the character
        """
        # This is a simplified implementation
        # A more sophisticated version would use NLP to identify character mentions
        # and extract relevant paragraphs
        
        paragraphs = text.split("\n\n")
        character_paragraphs = []
        
        for para in paragraphs:
            if name in para:
                character_paragraphs.append(para)
                
        # If we have too much text, sample paragraphs from throughout the story
        if sum(len(p) for p in character_paragraphs) > max_length:
            # Take some from beginning, middle, and end
            total_paragraphs = len(character_paragraphs)
            sampled_paragraphs = []
            
            if total_paragraphs >= 3:
                # Beginning
                sampled_paragraphs.extend(character_paragraphs[:max(1, total_paragraphs//5)])
                # Middle
                mid_start = total_paragraphs//2 - max(1, total_paragraphs//10)
                mid_end = total_paragraphs//2 + max(1, total_paragraphs//10)
                sampled_paragraphs.extend(character_paragraphs[mid_start:mid_end])
                # End
                sampled_paragraphs.extend(character_paragraphs[-max(1, total_paragraphs//5):])
            else:
                sampled_paragraphs = character_paragraphs
                
            character_paragraphs = sampled_paragraphs
            
        # Join the paragraphs with indicators of their location
        result = ""
        for i, para in enumerate(character_paragraphs):
            if len(result) + len(para) > max_length:
                result += f"\n...(text truncated)..."
                break
            result += f"\n--- Excerpt {i+1} ---\n{para}"
            
        return result


class PlotConsistencyChecker:
    """
    Class to check for plot consistency issues in a story.
    
    This analyzes plot elements across chapters to identify potential
    contradictions, plot holes, or other narrative coherence issues.
    """
    
    def __init__(self, model_service: Optional[ModelService] = None):
        """
        Initialize the plot consistency checker.
        
        Args:
            model_service: Optional model service for AI-assisted checks
        """
        self.model_service = model_service
        
    def check_plot_consistency(self, plot_points: List[Dict[str, Any]], 
                             story_text: str) -> List[Dict[str, str]]:
        """
        Check for inconsistencies in plot elements throughout a story.
        
        Args:
            plot_points: List of plot point dictionaries
            story_text: Full text of the story
            
        Returns:
            List of inconsistency issues found
        """
        issues = []
        
        # Basic timeline consistency checks
        timeline_issues = self._check_timeline_consistency(plot_points)
        issues.extend(timeline_issues)
        
        # Check for unresolved plot threads
        unresolved_issues = self._check_unresolved_plot_threads(plot_points)
        issues.extend(unresolved_issues)
        
        # AI-assisted checks if model service is available
        if self.model_service:
            ai_issues = self._check_ai_plot_consistency(plot_points, story_text)
            issues.extend(ai_issues)
            
        return issues
        
    def _check_timeline_consistency(self, plot_points: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Check for timeline inconsistencies in plot points.
        
        Args:
            plot_points: List of plot point dictionaries
            
        Returns:
            List of inconsistency issues found
        """
        issues = []
        
        # Simple check for events out of sequence
        # In a real implementation, this would be more sophisticated
        
        # Sort plot points by chapter
        plot_by_chapter = {}
        for point in plot_points:
            chapter = point.get("chapter", 0)
            if chapter not in plot_by_chapter:
                plot_by_chapter[chapter] = []
            plot_by_chapter[chapter].append(point)
            
        # Look for timeline reversals
        time_markers = ["before", "after", "yesterday", "tomorrow", "earlier", "later"]
        
        for chapter in sorted(plot_by_chapter.keys()):
            for point in plot_by_chapter[chapter]:
                desc = point.get("description", "").lower()
                
                # Check for references to timeline that might conflict with chapter order
                for marker in time_markers:
                    if marker in desc:
                        # This is a simplification; a real implementation would
                        # parse the temporal relationships more carefully
                        issues.append({
                            "type": "timeline_reference",
                            "description": f"Plot point in chapter {chapter} contains temporal reference that should be checked: '{desc}'",
                            "severity": "info"
                        })
                        break
        
        return issues
        
    def _check_unresolved_plot_threads(self, plot_points: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Check for plot threads that are introduced but not resolved.
        
        Args:
            plot_points: List of plot point dictionaries
            
        Returns:
            List of inconsistency issues found
        """
        issues = []
        
        # This is a simplified implementation
        # A real implementation would track plot threads and their resolution
        
        # Check if the last chapter has significantly fewer plot points than earlier chapters
        plot_by_chapter = {}
        for point in plot_points:
            chapter = point.get("chapter", 0)
            if chapter not in plot_by_chapter:
                plot_by_chapter[chapter] = []
            plot_by_chapter[chapter].append(point)
            
        if not plot_by_chapter:
            return issues
            
        max_chapter = max(plot_by_chapter.keys())
        if max_chapter > 1 and len(plot_by_chapter.get(max_chapter, [])) < len(plot_by_chapter.get(max_chapter-1, [])) / 2:
            issues.append({
                "type": "potential_unresolved_threads",
                "description": f"Final chapter has significantly fewer plot points than previous chapter; may indicate unresolved plot threads",
                "severity": "warning"
            })
            
        return issues
        
    def _check_ai_plot_consistency(self, plot_points: List[Dict[str, Any]], 
                                 story_text: str) -> List[Dict[str, str]]:
        """
        Use AI to check for more complex plot consistency issues.
        
        Args:
            plot_points: List of plot point dictionaries
            story_text: Full text of the story
            
        Returns:
            List of inconsistency issues found
        """
        if not self.model_service:
            return []
            
        issues = []
        
        # Prepare plot points summary
        plot_summary = "Plot points by chapter:\n"
        plot_by_chapter = {}
        
        for point in plot_points:
            chapter = point.get("chapter", 0)
            if chapter not in plot_by_chapter:
                plot_by_chapter[chapter] = []
            plot_by_chapter[chapter].append(point.get("description", ""))
            
        for chapter in sorted(plot_by_chapter.keys()):
            plot_summary += f"Chapter {chapter}:\n"
            for point in plot_by_chapter[chapter]:
                plot_summary += f"- {point}\n"
        
        # Prepare prompt for the model
        prompt = f"""
        Analyze this story for plot consistency issues.
        
        {plot_summary}
        
        Look for these types of plot issues:
        1. Plot holes: Events that contradict established facts
        2. Character motivation inconsistencies: Actions that don't make sense for a character
        3. Unresolved plot threads: Important elements introduced but never resolved
        4. Deus ex machina: Convenient but implausible solutions to plot problems
        5. Timeline inconsistencies: Events that couldn't happen in the given order
        
        Format your response as a JSON array with objects having these fields:
        - "issue_type": The type of plot issue
        - "description": A description of the issue
        - "chapters_affected": The chapters where this issue appears
        - "severity": "low", "medium", or "high"
        
        Example:
        [
          {
            "issue_type": "plot_hole",
            "description": "The key to the vault is used in Ch.3, but was established as lost in Ch.2",
            "chapters_affected": [2, 3],
            "severity": "high"
          }
        ]
        
        If no issues are found, return an empty array.
        """
        
        try:
            response = self.model_service.get_completion(prompt)
            # Parse the response to extract issues
            if response.strip().startswith("[") and response.strip().endswith("]"):
                import json
                try:
                    ai_issues = json.loads(response)
                    for issue in ai_issues:
                        issues.append({
                            "type": issue.get("issue_type", "unknown"),
                            "description": issue.get("description", ""),
                            "chapters_affected": issue.get("chapters_affected", []),
                            "severity": issue.get("severity", "medium")
                        })
                except json.JSONDecodeError:
                    # If parsing fails, add a generic issue
                    issues.append({
                        "type": "parsing_error",
                        "description": "Could not parse AI plot consistency check results",
                        "severity": "low"
                    })
        except Exception as e:
            # Handle any errors in the AI processing
            issues.append({
                "type": "ai_check_error",
                "description": f"Error in AI plot consistency check: {str(e)}",
                "severity": "low"
            })
        
        return issues


class ConsistencyChecker:
    """
    Main class for checking consistency in a story.
    
    This combines character and plot consistency checking to provide
    a comprehensive analysis of potential narrative coherence issues.
    """
    
    def __init__(self, model_service: Optional[ModelService] = None):
        """
        Initialize the consistency checker.
        
        Args:
            model_service: Optional model service for AI-assisted checks
        """
        self.model_service = model_service
        self.character_checker = CharacterConsistencyChecker(model_service)
        self.plot_checker = PlotConsistencyChecker(model_service)
        
    def check_story_consistency(self, story_state) -> Dict[str, List[Dict[str, Any]]]:
        """
        Check a story for consistency issues.
        
        Args:
            story_state: StoryState object containing the story and metadata
            
        Returns:
            Dictionary with character_issues and plot_issues
        """
        story_text = story_state.get_full_story()
        
        # Check character consistency
        character_issues = []
        for character in story_state.metadata.characters:
            issues = self.character_checker.check_character_consistency(character, story_text)
            character_issues.extend(issues)
            
        # Check plot consistency
        plot_issues = self.plot_checker.check_plot_consistency(
            story_state.metadata.plot_points, story_text)
            
        return {
            "character_issues": character_issues,
            "plot_issues": plot_issues
        }
        
    def generate_consistency_report(self, story_state) -> str:
        """
        Generate a human-readable report of consistency issues.
        
        Args:
            story_state: StoryState object containing the story and metadata
            
        Returns:
            Formatted report of consistency issues
        """
        issues = self.check_story_consistency(story_state)
        
        report = f"# Consistency Report for \"{story_state.metadata.title}\"\n\n"
        
        # Character issues
        report += "## Character Consistency Issues\n\n"
        if not issues["character_issues"]:
            report += "No character consistency issues found.\n\n"
        else:
            for issue in issues["character_issues"]:
                severity = issue.get("severity", "medium")
                severity_marker = "⚠️" if severity == "high" else "ℹ️"
                
                report += f"{severity_marker} **{issue.get('character', 'Unknown character')}**: "
                report += f"{issue.get('description', 'Unknown issue')}\n"
                
                if "evidence" in issue and issue["evidence"]:
                    report += f"> {issue['evidence']}\n"
                    
                report += "\n"
        
        # Plot issues
        report += "## Plot Consistency Issues\n\n"
        if not issues["plot_issues"]:
            report += "No plot consistency issues found.\n\n"
        else:
            for issue in issues["plot_issues"]:
                severity = issue.get("severity", "medium")
                severity_marker = "⚠️" if severity == "high" else "ℹ️"
                
                report += f"{severity_marker} **{issue.get('type', 'Unknown issue')}**: "
                report += f"{issue.get('description', 'Unknown issue')}\n"
                
                if "chapters_affected" in issue and issue["chapters_affected"]:
                    chapters = ", ".join(str(ch) for ch in issue["chapters_affected"])
                    report += f"> Affects chapters: {chapters}\n"
                    
                report += "\n"
        
        return report 