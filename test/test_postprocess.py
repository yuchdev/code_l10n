# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.postprocess import PostProcessor, render_line_block, render_block_comment, render_docstring
from code_l10n.segments import CommentSegment
from code_l10n.comment_styles import CommentStyle


class TestPostProcessor(unittest.TestCase):
    
    def test_render_line_block(self):
        """Test rendering of line comment block."""
        result = render_line_block("    ", "//", "Line 1\nLine 2")
        
        self.assertIn("// Line 1", result)
        self.assertIn("// Line 2", result)
        self.assertTrue(result.startswith("    "))
    
    def test_render_block_comment_single_line(self):
        """Test rendering of single-line block comment."""
        result = render_block_comment("    ", "/*", "*/", "Comment")
        
        self.assertIn("/*", result)
        self.assertIn("Comment", result)
        self.assertIn("*/", result)
    
    def test_render_block_comment_multi_line(self):
        """Test rendering of multi-line block comment."""
        result = render_block_comment("    ", "/*", "*/", "Line 1\nLine 2")
        
        self.assertIn("/*", result)
        self.assertIn("*", result)  # Should have * prefix
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("*/", result)
    
    def test_render_docstring_single_line(self):
        """Test rendering of single-line docstring."""
        result = render_docstring("    ", '"""', "Docstring")
        
        self.assertIn('"""', result)
        self.assertIn("Docstring", result)
    
    def test_render_docstring_multi_line(self):
        """Test rendering of multi-line docstring."""
        result = render_docstring("    ", '"""', "Line 1\nLine 2")
        
        self.assertIn('"""', result)
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
    
    def test_default_profile_preserves_structure(self):
        """Test that default profile preserves original structure."""
        processor = PostProcessor("default")
        
        segment = CommentSegment(
            file_path=Path("test.cpp"),
            segment_type="line_block",
            start_line=1,
            end_line=2,
            indent="    ",
            marker="//",
            end_marker=None,
            raw_text="Original"
        )
        
        result = processor.apply(segment, "Translated", CommentStyle())
        
        # Should preserve line comment format
        self.assertIn("//", result)
        self.assertIn("Translated", result)
    
    def test_prefer_block_comments_converts(self):
        """Test that prefer_block_comments converts multi-line to block."""
        processor = PostProcessor("prefer_block_comments")
        
        segment = CommentSegment(
            file_path=Path("test.cpp"),
            segment_type="line_block",
            start_line=1,
            end_line=3,
            indent="",
            marker="//",
            end_marker=None,
            raw_text="Line 1\nLine 2\nLine 3"
        )
        
        style = CommentStyle(
            line_markers=["//"],
            block_markers=[("/*", "*/")]
        )
        
        result = processor.apply(segment, "Line 1\nLine 2\nLine 3", style)
        
        # Should convert to block comment
        self.assertIn("/*", result)
        self.assertIn("*/", result)
    
    def test_flatten_single_line_converts(self):
        """Test that flatten_single_line converts short text."""
        processor = PostProcessor("flatten_single_line")
        
        segment = CommentSegment(
            file_path=Path("test.cpp"),
            segment_type="line_block",
            start_line=1,
            end_line=1,
            indent="",
            marker="//",
            end_marker=None,
            raw_text="Original"
        )
        
        style = CommentStyle(line_markers=["//"])
        
        result = processor.apply(segment, "Translated", style)
        
        # Should be single line
        self.assertIn("//", result)
        self.assertIn("Translated", result)
    
    def test_postprocess_docstring(self):
        """Test post-processing of docstrings."""
        processor = PostProcessor("default")
        
        segment = CommentSegment(
            file_path=Path("test.py"),
            segment_type="docstring",
            start_line=1,
            end_line=1,
            indent="    ",
            marker='"""',
            end_marker='"""',
            raw_text="Original docstring"
        )
        
        result = processor.apply(segment, "Translated docstring", CommentStyle())
        
        self.assertIn('"""', result)
        self.assertIn("Translated docstring", result)


if __name__ == '__main__':
    unittest.main()
