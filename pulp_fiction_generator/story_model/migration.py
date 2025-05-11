"""
Migration notes for the story generator refactoring.

This module contains notes about the refactoring of the story generator and related
structure in the pulp_fiction_generator/story_model/ package.

These notes are intended for developers working on the codebase to understand
the structure and relationships between components.
"""

# Original: pulp_fiction_generator/crews/crew_coordinator.py:CrewCoordinator.generate_story
# New: pulp_fiction_generator/story_generation/story_generator.py:StoryGenerator

# Key method migrations:
# - StoryGenerator._execute_task() → story_model/execution.py:ExecutionEngine.execute_task()
# - StoryGenerator.validate_story_content() → story_model/validation.py:StoryValidator.validate_story_content()
# - Task creation code → story_model/tasks.py:TaskFactory
# - State management → story_model/state.py:StoryStateManager
# - Output models → story_model/models.py

# Migration Map:
# Old: pulp_fiction_generator/crews/story_generator.py:StoryGenerator
# New: pulp_fiction_generator/story/generator.py:StoryGenerator

# Key Component Changes:
# - StoryGenerator._execute_task() → story/execution.py:ExecutionEngine.execute_task()
# - StoryGenerator.validate_story_content() → story/validation.py:StoryValidator.validate_story_content()
# - Task creation code → story/tasks.py:TaskFactory
# - State management → story/state.py:StoryStateManager
# - Output models → story/models.py

# Migration Guide:
# 1. Import new StoryGenerator from pulp_fiction_generator.story instead of pulp_fiction_generator.crews.story_generator
# 2. Update any direct calls to internal methods with their new component counterparts
# 3. Replace dictionary-based results with StoryArtifacts objects 