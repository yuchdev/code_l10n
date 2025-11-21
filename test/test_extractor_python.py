# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.extractor import CommentExtractor
from code_l10n.comment_styles import CommentStyle


class TestExtractorPython(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = CommentExtractor()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_single_line_comment(self):
        """Test extraction of single-line # comments."""
        content = """# This is a comment
print("hello")
"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"])
        segments = self.extractor.extract_segments(test_file, style)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].segment_type, "line_block")
        self.assertEqual(segments[0].raw_text, "This is a comment")
        self.assertEqual(segments[0].start_line, 1)
    
    def test_multi_line_comment_block(self):
        """Test extraction of consecutive # comments."""
        content = """# First line
# Second line
# Third line
print("hello")
"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"])
        segments = self.extractor.extract_segments(test_file, style)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].segment_type, "line_block")
        self.assertEqual(segments[0].raw_text, "First line\nSecond line\nThird line")
        self.assertEqual(segments[0].start_line, 1)
        self.assertEqual(segments[0].end_line, 3)
    
    def test_docstring_module(self):
        """Test extraction of module docstring."""
        content = '''"""This is a module docstring."""
def foo():
    pass
'''
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"], docstring_markers=[('"""', '"""')])
        segments = self.extractor.extract_segments(test_file, style)
        
        # Find docstring segment
        docstrings = [s for s in segments if s.segment_type == "docstring"]
        self.assertEqual(len(docstrings), 1)
        self.assertEqual(docstrings[0].raw_text, "This is a module docstring.")
    
    def test_docstring_function(self):
        """Test extraction of function docstring."""
        content = '''def foo():
    """Function docstring."""
    return 42
'''
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"], docstring_markers=[('"""', '"""')])
        segments = self.extractor.extract_segments(test_file, style)
        
        docstrings = [s for s in segments if s.segment_type == "docstring"]
        self.assertEqual(len(docstrings), 1)
        self.assertEqual(docstrings[0].raw_text, "Function docstring.")
    
    def test_multi_line_docstring(self):
        """Test extraction of multi-line docstring."""
        content = '''def foo():
    """
    Multi-line
    docstring.
    """
    return 42
'''
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"], docstring_markers=[('"""', '"""')])
        segments = self.extractor.extract_segments(test_file, style)
        
        docstrings = [s for s in segments if s.segment_type == "docstring"]
        self.assertEqual(len(docstrings), 1)
        self.assertIn("Multi-line", docstrings[0].raw_text)
        self.assertIn("docstring", docstrings[0].raw_text)
    
    def test_mixed_comments_and_docstrings(self):
        """Test that both comments and docstrings are extracted."""
        content = '''# Module comment
"""Module docstring."""

def foo():
    # Function comment
    """Function docstring."""
    pass
'''
        test_file = self.temp_dir / "test.py"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["#"], docstring_markers=[('"""', '"""')])
        segments = self.extractor.extract_segments(test_file, style)
        
        # Should have both line comments and docstrings
        line_blocks = [s for s in segments if s.segment_type == "line_block"]
        docstrings = [s for s in segments if s.segment_type == "docstring"]
        
        self.assertGreater(len(line_blocks), 0)
        self.assertGreater(len(docstrings), 0)


if __name__ == '__main__':
    unittest.main()
