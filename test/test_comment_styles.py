# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.comment_styles import CommentStyle, get_comment_style_for_path, DEFAULT_COMMENT_STYLES


class TestCommentStyles(unittest.TestCase):
    
    def test_cpp_style(self):
        """Test that .cpp files have correct comment style."""
        style = get_comment_style_for_path(Path("test.cpp"))
        self.assertIsNotNone(style)
        self.assertIn("//", style.line_markers)
        self.assertIn(("/*", "*/"), style.block_markers)
    
    def test_python_style(self):
        """Test that .py files have correct comment style."""
        style = get_comment_style_for_path(Path("test.py"))
        self.assertIsNotNone(style)
        self.assertIn("#", style.line_markers)
        self.assertIn(('"""', '"""'), style.docstring_markers)
    
    def test_makefile_exact_match(self):
        """Test exact filename matching for Makefile."""
        style = get_comment_style_for_path(Path("Makefile"))
        self.assertIsNotNone(style)
        self.assertIn("#", style.line_markers)
    
    def test_shell_script(self):
        """Test shell script comment style."""
        style = get_comment_style_for_path(Path("script.sh"))
        self.assertIsNotNone(style)
        self.assertIn("#", style.line_markers)
    
    def test_html_style(self):
        """Test HTML comment style."""
        style = get_comment_style_for_path(Path("page.html"))
        self.assertIsNotNone(style)
        self.assertIn(("<!--", "-->"), style.block_markers)
    
    def test_sql_style(self):
        """Test SQL comment style."""
        style = get_comment_style_for_path(Path("query.sql"))
        self.assertIsNotNone(style)
        self.assertIn("--", style.line_markers)
        self.assertIn(("/*", "*/"), style.block_markers)
    
    def test_unknown_extension(self):
        """Test that unknown extensions return None."""
        style = get_comment_style_for_path(Path("file.unknown"))
        self.assertIsNone(style)
    
    def test_override(self):
        """Test that overrides work correctly."""
        overrides = {
            "*.custom": {
                "line_markers": ["##"],
                "block_markers": [],
                "docstring_markers": []
            }
        }
        style = get_comment_style_for_path(Path("test.custom"), overrides)
        self.assertIsNotNone(style)
        self.assertEqual(["##"], style.line_markers)
    
    def test_default_styles_coverage(self):
        """Test that we have styles defined for many file types."""
        # Check some common extensions are present
        common_extensions = [
            '*.py', '*.cpp', '*.java', '*.js', '*.go', '*.rs',
            '*.sh', '*.sql', '*.html', '*.php', '*.rb'
        ]
        for pattern in common_extensions:
            self.assertIn(pattern, DEFAULT_COMMENT_STYLES,
                         f"Missing style for {pattern}")


if __name__ == '__main__':
    unittest.main()
