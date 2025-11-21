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


class TestExtractorCpp(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = CommentExtractor()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_single_line_comment(self):
        """Test extraction of single-line // comment."""
        content = """// This is a comment
int main() {
    return 0;
}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].segment_type, "line_block")
        self.assertEqual(segments[0].raw_text, "This is a comment")
    
    def test_multi_line_comment_block(self):
        """Test extraction of consecutive // comments."""
        content = """// First line
// Second line
// Third line
int main() {}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].segment_type, "line_block")
        self.assertEqual(segments[0].raw_text, "First line\nSecond line\nThird line")
    
    def test_block_comment_single_line(self):
        """Test extraction of single-line /* */ comment."""
        content = """/* This is a block comment */
int main() {}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        block_comments = [s for s in segments if s.segment_type == "block_comment"]
        self.assertEqual(len(block_comments), 1)
        self.assertIn("block comment", block_comments[0].raw_text)
    
    def test_block_comment_multi_line(self):
        """Test extraction of multi-line /* */ comment."""
        content = """/*
 * Multi-line
 * block comment
 */
int main() {}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        block_comments = [s for s in segments if s.segment_type == "block_comment"]
        self.assertEqual(len(block_comments), 1)
        self.assertIn("Multi-line", block_comments[0].raw_text)
    
    def test_mixed_comment_types(self):
        """Test extraction of both // and /* */ comments."""
        content = """// Line comment
/* Block comment */
int main() {
    // Another line comment
    return 0;
}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        line_blocks = [s for s in segments if s.segment_type == "line_block"]
        block_comments = [s for s in segments if s.segment_type == "block_comment"]
        
        self.assertGreater(len(line_blocks), 0)
        self.assertGreater(len(block_comments), 0)
    
    def test_indented_comments(self):
        """Test that indentation is preserved."""
        content = """int main() {
    // Indented comment
    return 0;
}
"""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text(content)
        
        style = CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")])
        segments = self.extractor.extract_segments(test_file, style)
        
        self.assertEqual(len(segments), 1)
        # Check that indent is captured
        self.assertEqual(segments[0].indent, "    ")


if __name__ == '__main__':
    unittest.main()
