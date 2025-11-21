# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.cli import main, parse_translation_options


class TestCLI(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_parse_translation_options(self):
        """Test parsing of translation options."""
        options = ["key1=value1", "key2=value2"]
        result = parse_translation_options(options)
        
        self.assertEqual(result["key1"], "value1")
        self.assertEqual(result["key2"], "value2")
    
    def test_parse_translation_options_invalid(self):
        """Test that invalid options raise error."""
        options = ["invalid"]
        
        with self.assertRaises(ValueError):
            parse_translation_options(options)
    
    def test_cli_basic_usage(self):
        """Test basic CLI usage."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(test_file),
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        
        # Should exit successfully
        self.assertEqual(exit_code, 0)
    
    def test_cli_with_patterns(self):
        """Test CLI with include patterns."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(self.temp_dir),
            "--include-pattern", "*.py",
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_with_languages(self):
        """Test CLI with language options."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(test_file),
            "--source-language", "uk",
            "--target-language", "en",
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_with_locale(self):
        """Test CLI with locale option."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(test_file),
            "--locale", "uk-UA",
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_with_translation_engine(self):
        """Test CLI with translation engine options."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(test_file),
            "--translation-engine", "internal",
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_with_postprocess_profile(self):
        """Test CLI with post-processing profile."""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text("// comment\nint main() {}")
        
        argv = [
            "--path", str(test_file),
            "--postprocess-profile", "prefer_block_comments",
            "--dry-run",
            "--quiet"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_verbose(self):
        """Test CLI with verbose output."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        argv = [
            "--path", str(test_file),
            "--verbose",
            "--dry-run"
        ]
        
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)
    
    def test_cli_missing_path(self):
        """Test that missing --path argument is handled."""
        argv = ["--dry-run"]
        
        # argparse will raise SystemExit(2) for missing required arguments
        with self.assertRaises(SystemExit) as cm:
            main(argv)
        
        # Exit code should be 2 (argparse error code)
        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
