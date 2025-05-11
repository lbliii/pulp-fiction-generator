"""
Response templates for agents.
"""

# Default response template with standard CrewAI format
DEFAULT_RESPONSE_TEMPLATE = """
Here is my response to the task:

{response}

Let me know if you need any clarification or have questions about my response.
"""

# Creative response template emphasizing creative elements
CREATIVE_RESPONSE_TEMPLATE = """
Here is my creative response to the task:

{response}

The key creative elements I've incorporated:
- {creative_element_1}
- {creative_element_2}
- {creative_element_3}

I've aimed to balance creativity with genre expectations. Let me know if you'd like me to adjust the creative direction.
"""

# Analytical response template emphasizing reasoning
ANALYTICAL_RESPONSE_TEMPLATE = """
Here is my analytical response to the task:

{response}

My reasoning process:
1. {reasoning_step_1}
2. {reasoning_step_2}
3. {reasoning_step_3}

Key considerations that informed my approach:
- {consideration_1}
- {consideration_2}
- {consideration_3}

Let me know if you'd like me to elaborate on any part of my analysis.
""" 