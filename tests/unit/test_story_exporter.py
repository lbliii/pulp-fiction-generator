"""
Unit tests for the StoryExporter class.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from pulp_fiction_generator.utils.story_exporter import StoryExporter


class TestStoryExporter(unittest.TestCase):
    """Test the StoryExporter class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for exports
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = StoryExporter(output_dir=self.temp_dir)
        
        # Sample story data for testing
        self.story_data = {
            "title": "The Mystery of Elm Street",
            "content": "It was a dark and stormy night.\n\nJohn looked out the window, his face illuminated by lightning.\n\n\"I've got to solve this case,\" he muttered.",
            "metadata": {
                "genre": "Mystery",
                "author": "AI Generator",
                "date": "2024-06-15",
                "tags": ["mystery", "detective", "noir"],
                "characters": [
                    {"name": "John Smith", "description": "A hardboiled detective with a troubled past"},
                    {"name": "Mary Johnson", "description": "A mysterious woman with secrets"}
                ]
            }
        }
    
    def tearDown(self):
        """Clean up after the tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_sanitize_filename(self):
        """Test the filename sanitization method."""
        test_cases = [
            ("My Story", "My_Story"),
            ("Hello, World!", "Hello_World"),
            ("File@Name#With$Special&Chars", "FileNameWithSpecialChars"),
            ("   Spaces   Around   ", "Spaces_Around"),
        ]
        
        for input_title, expected in test_cases:
            result = self.exporter._sanitize_filename(input_title)
            self.assertEqual(result, expected)
    
    def test_export_to_markdown(self):
        """Test exporting to Markdown format."""
        filepath = self.exporter.export_to_markdown(self.story_data)
        
        # Check if file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check file extension
        self.assertTrue(filepath.endswith(".md"))
        
        # Check content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Basic content checks
        self.assertIn("# The Mystery of Elm Street", content)
        self.assertIn("It was a dark and stormy night.", content)
        self.assertIn("**Genre**: Mystery", content)
        self.assertIn("**Tags**: mystery, detective, noir", content)
        self.assertIn("**John Smith**: A hardboiled detective with a troubled past", content)
    
    def test_export_to_html(self):
        """Test exporting to HTML format."""
        filepath = self.exporter.export_to_html(self.story_data)
        
        # Check if file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check file extension
        self.assertTrue(filepath.endswith(".html"))
        
        # Check content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Basic content checks
        self.assertIn("<title>The Mystery of Elm Street</title>", content)
        self.assertIn("<h1>The Mystery of Elm Street</h1>", content)
        self.assertIn("<p>It was a dark and stormy night.</p>", content)
        self.assertIn("<strong>Genre:</strong> Mystery", content)
        self.assertIn('<span class="tag">mystery</span>', content)
        self.assertIn("<strong>John Smith:</strong> A hardboiled detective with a troubled past", content)
    
    def test_export_to_text(self):
        """Test exporting to plain text format."""
        filepath = self.exporter.export_to_text(self.story_data)
        
        # Check if file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Check file extension
        self.assertTrue(filepath.endswith(".txt"))
        
        # Check content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Basic content checks
        self.assertIn("THE MYSTERY OF ELM STREET", content)
        self.assertIn("It was a dark and stormy night.", content)
        self.assertIn("Genre: Mystery", content)
        self.assertIn("Tags: mystery, detective, noir", content)
        self.assertIn("- John Smith: A hardboiled detective with a troubled past", content)
    
    def test_export_story_multiple_formats(self):
        """Test exporting to multiple formats at once."""
        formats = ["markdown", "html", "text"]
        results = self.exporter.export_story(self.story_data, formats)
        
        # Check that we have results for all requested formats
        self.assertEqual(len(results), len(formats))
        
        # Check that all files exist
        for fmt, filepath in results.items():
            self.assertTrue(os.path.exists(filepath))
        
        # Check file extensions
        self.assertTrue(results["markdown"].endswith(".md"))
        self.assertTrue(results["html"].endswith(".html"))
        self.assertTrue(results["text"].endswith(".txt"))
    
    def test_custom_filename(self):
        """Test using a custom filename."""
        custom_name = "custom_story_name"
        filepath = self.exporter.export_to_markdown(self.story_data, filename=custom_name)
        
        # Check if file exists with the custom name
        expected_path = os.path.join(self.temp_dir, f"{custom_name}.md")
        self.assertEqual(filepath, expected_path)
        self.assertTrue(os.path.exists(filepath))
    
    def test_pdf_export_import_error(self):
        """Test PDF export raises ImportError if weasyprint is not available."""
        # Use a context manager to temporarily modify __import__ to simulate missing weasyprint
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'weasyprint':
                raise ImportError("No module named 'weasyprint'")
            return original_import(name, *args, **kwargs)
        
        # Apply the mock import function
        builtins.__import__ = mock_import
        
        try:
            # Attempt to export to PDF, which should raise an ImportError
            with self.assertRaises(ImportError) as context:
                self.exporter.export_to_pdf(self.story_data)
            
            # Check error message
            self.assertIn("weasyprint is required for PDF export", str(context.exception))
        finally:
            # Restore the original import function
            builtins.__import__ = original_import 