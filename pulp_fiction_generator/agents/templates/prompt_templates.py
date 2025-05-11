"""
Prompt templates for agents.
"""

# Default prompt template with standard CrewAI format
DEFAULT_PROMPT_TEMPLATE = """
Task: {task}

{task_context}

Your response should be appropriate for the genre: {genre}.

Remember to consider:
- Genre conventions and tropes
- Target audience expectations
- Historical accuracy (if applicable)
- Consistency with previous work

Take a deep breath and work through this step-by-step.
"""

# Creative prompt template emphasizing imaginative thinking
CREATIVE_PROMPT_TEMPLATE = """
Task: {task}

{task_context}

Your response should be creative and original, while still appropriate for the genre: {genre}.

As you develop your ideas:
- Push beyond obvious and clichéd elements
- Seek unexpected connections between concepts
- Consider how to subvert reader expectations in satisfying ways
- Draw inspiration from unconventional sources
- Maintain the spirit of pulp fiction while adding your unique touch

Take a deep breath, let your imagination flow, and work through this step-by-step.
"""

# Analytical prompt template emphasizing structured thinking
ANALYTICAL_PROMPT_TEMPLATE = """
Task: {task}

{task_context}

Your response should be well-structured and logically sound, while appropriate for the genre: {genre}.

Follow this analytical approach:
1. Identify the core requirements of the task
2. Consider multiple potential solutions
3. Evaluate each option using objective criteria
4. Select the most effective approach
5. Implement the solution with attention to detail
6. Review your work to ensure consistency and completeness

Take a deep breath, apply systematic thinking, and work through this step-by-step.
""" 