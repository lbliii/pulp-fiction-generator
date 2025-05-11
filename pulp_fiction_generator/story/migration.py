"""
Migration documentation for the StoryGenerator refactoring.

This file documents the transition from the monolithic StoryGenerator
in pulp_fiction_generator/crews/story_generator.py to the new modular
structure in the pulp_fiction_generator/story/ package.

No backward compatibility is maintained - applications should migrate
to the new structure.
"""

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