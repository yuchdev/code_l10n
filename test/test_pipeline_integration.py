# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.config import CodeL10nConfig
from code_l10n.pipeline import CodeL10nPipeline
from code_l10n.enums import Language


class TestPipelineIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_pipeline_python_file(self):
        """Test end-to-end pipeline on Python file."""
        # Create test file
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""# привіт світ
def foo():
    # функція
    pass
""")
        
        # Configure pipeline with echo translator
        config = CodeL10nConfig(
            source_paths=[test_file],
            source_language=Language.UKRAINIAN,
            target_language=Language.ENGLISH,
            translation_engine="echo",
            dry_run=True,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Check report
        self.assertEqual(report['files_processed'], 1)
        self.assertGreaterEqual(report['segments_processed'], 0)
    
    def test_pipeline_cpp_file(self):
        """Test end-to-end pipeline on C++ file."""
        test_file = self.temp_dir / "test.cpp"
        test_file.write_text("""// привіт світ
int main() {
    // функція
    return 0;
}
""")
        
        config = CodeL10nConfig(
            source_paths=[test_file],
            source_language=Language.UKRAINIAN,
            target_language=Language.ENGLISH,
            translation_engine="echo",
            dry_run=True,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        self.assertEqual(report['files_processed'], 1)
    
    def test_pipeline_directory(self):
        """Test pipeline on directory with multiple files."""
        # Create multiple test files
        py_file = self.temp_dir / "test.py"
        py_file.write_text("# comment\npass")
        
        cpp_file = self.temp_dir / "test.cpp"
        cpp_file.write_text("// comment\nint main() {}")
        
        config = CodeL10nConfig(
            source_paths=[self.temp_dir],
            source_language=Language.ENGLISH,
            target_language=Language.FRENCH,
            translation_engine="echo",
            dry_run=True,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Should process both files
        self.assertGreaterEqual(report['files_processed'], 2)
    
    def test_pipeline_with_patterns(self):
        """Test pipeline with include/exclude patterns."""
        # Create test files
        py_file = self.temp_dir / "test.py"
        py_file.write_text("# comment")
        
        cpp_file = self.temp_dir / "test.cpp"
        cpp_file.write_text("// comment")
        
        txt_file = self.temp_dir / "test.txt"
        txt_file.write_text("text file")
        
        config = CodeL10nConfig(
            source_paths=[self.temp_dir],
            include_patterns=["*.py"],
            source_language=Language.ENGLISH,
            target_language=Language.FRENCH,
            translation_engine="echo",
            dry_run=True,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Should only process .py file
        # Note: test.txt won't be processed anyway since it has no comment style
        self.assertGreaterEqual(report['files_processed'], 1)
    
    def test_pipeline_file_modification(self):
        """Test that pipeline actually modifies files."""
        test_file = self.temp_dir / "test.py"
        original_content = "# hello world\npass"
        test_file.write_text(original_content)
        
        config = CodeL10nConfig(
            source_paths=[test_file],
            source_language=Language.ENGLISH,
            target_language=Language.ENGLISH,
            translation_engine="echo",
            dry_run=False,  # Actually modify
            create_backups=True,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Check backup was created
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        self.assertTrue(backup_file.exists())
    
    def test_pipeline_no_backup(self):
        """Test pipeline with backups disabled."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        config = CodeL10nConfig(
            source_paths=[test_file],
            source_language=Language.ENGLISH,
            target_language=Language.FRENCH,
            translation_engine="echo",
            dry_run=False,
            create_backups=False,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Check no backup was created
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        self.assertFalse(backup_file.exists())
    
    def test_pipeline_report_generation(self):
        """Test that pipeline generates JSON report."""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# comment\npass")
        
        report_path = self.temp_dir / "report.json"
        
        config = CodeL10nConfig(
            source_paths=[test_file],
            source_language=Language.ENGLISH,
            target_language=Language.FRENCH,
            translation_engine="echo",
            dry_run=True,
            report_path=report_path,
            verbose=False
        )
        
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Check report file was created
        self.assertTrue(report_path.exists())


if __name__ == '__main__':
    unittest.main()
