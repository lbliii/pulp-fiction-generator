"""
Configuration and fixtures for pytest.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Model service mock fixture
@pytest.fixture
def mock_model_service():
    mock_service = MagicMock()
    mock_service.generate.return_value = "Test generated content"
    return mock_service

# Context fixture
@pytest.fixture
def basic_context():
    return {
        "genre": "test_genre",
        "title": "Test Story",
        "characters": [{"name": "Test Character", "role": "Protagonist"}],
        "setting": "Test Setting",
        "plot": {"outline": "Test plot outline"}
    } 