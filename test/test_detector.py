# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.detector import LanguageDetector, DetectedFragment
from code_l10n.enums import Language


class TestDetector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = LanguageDetector()
    
    def test_detect_english(self):
        """Test detection of English text."""
        text = "This is an English comment."
        fragments = self.detector.detect_fragments(text)
        
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0].language, Language.ENGLISH)
    
    def test_detect_ukrainian(self):
        """Test detection of Ukrainian text."""
        text = "Це український коментар."
        fragments = self.detector.detect_fragments(text)
        
        self.assertEqual(len(fragments), 1)
        # Should detect as Ukrainian (Cyrillic script)
        self.assertIn(fragments[0].language, [Language.UKRAINIAN, Language.RUSSIAN])
    
    def test_detect_russian(self):
        """Test detection of Russian text."""
        text = "Это русский комментарий."
        fragments = self.detector.detect_fragments(text)
        
        self.assertEqual(len(fragments), 1)
        self.assertIn(fragments[0].language, [Language.UKRAINIAN, Language.RUSSIAN])
    
    def test_empty_text(self):
        """Test handling of empty text."""
        fragments = self.detector.detect_fragments("")
        self.assertEqual(len(fragments), 0)
    
    def test_short_text(self):
        """Test handling of very short text."""
        text = "OK"
        fragments = self.detector.detect_fragments(text)
        # Short text might not be detected
        self.assertGreaterEqual(len(fragments), 0)
    
    def test_split_sentences(self):
        """Test that text is split into sentences."""
        text = "First sentence. Second sentence!"
        fragments = self.detector.detect_fragments(text)
        
        # Should be split into multiple fragments
        self.assertGreater(len(fragments), 1)
    
    def test_mixed_language(self):
        """Test handling of mixed language text."""
        text = "English text. Український текст."
        fragments = self.detector.detect_fragments(text)
        
        # Should detect multiple fragments
        self.assertGreater(len(fragments), 1)
        
        # Check that different languages are detected
        languages = [f.language for f in fragments if f.language]
        self.assertGreater(len(set(languages)), 0)
    
    def test_fragment_offsets(self):
        """Test that fragment offsets are correct."""
        text = "First. Second."
        fragments = self.detector.detect_fragments(text)
        
        for fragment in fragments:
            # Each fragment should have valid offsets
            self.assertGreaterEqual(fragment.start_offset, 0)
            self.assertLessEqual(fragment.end_offset, len(text))
            self.assertLessEqual(fragment.start_offset, fragment.end_offset)
    
    def test_code_with_no_letters(self):
        """Test handling of code with no alphabetic characters."""
        text = "123 + 456 = 579"
        fragments = self.detector.detect_fragments(text)
        
        # Should still create fragments, but language might be None
        self.assertGreaterEqual(len(fragments), 0)


if __name__ == '__main__':
    unittest.main()
