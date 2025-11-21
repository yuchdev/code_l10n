# -*- coding: utf-8 -*-
"""
Pipeline orchestration for code localization.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from .config import CodeL10nConfig
from .comment_styles import get_comment_style_for_path
from .extractor import CommentExtractor
from .detector import LanguageDetector
from .translator import build_translator_from_config
from .postprocess import PostProcessor
from .io_utils import (
    discover_files,
    is_binary_file,
    read_file_lines,
    write_file_lines,
    create_backup
)
from .segments import CommentSegment


logger = logging.getLogger(__name__)


class CodeL10nPipeline:
    """
    Orchestrates the complete code localization pipeline.
    """
    
    def __init__(self, config: CodeL10nConfig):
        """
        Initialize pipeline with configuration.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.translator = build_translator_from_config(config)
        self.detector = LanguageDetector()
        self.post_processor = PostProcessor(config.postprocess_profile)
        self.extractor = CommentExtractor()
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the full pipeline.
        
        Returns:
            Dictionary with processing report
        """
        # Configure logging
        if self.config.verbose:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        logger.info("Starting code localization pipeline")
        
        # Discover files
        logger.info(f"Discovering files in {len(self.config.source_paths)} path(s)")
        files = discover_files(
            self.config.source_paths,
            self.config.include_patterns,
            self.config.exclude_patterns
        )
        logger.info(f"Found {len(files)} file(s) to process")
        
        # Process each file
        report = {
            'files_processed': 0,
            'files_modified': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'segments_processed': 0,
            'fragments_translated': 0,
            'errors': [],
            'file_details': []
        }
        
        for file_path in files:
            try:
                file_report = self._process_file(file_path)
                report['files_processed'] += 1
                
                if file_report['modified']:
                    report['files_modified'] += 1
                elif file_report['skipped']:
                    report['files_skipped'] += 1
                
                report['segments_processed'] += file_report['segments_processed']
                report['fragments_translated'] += file_report['fragments_translated']
                report['file_details'].append(file_report)
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                report['files_failed'] += 1
                report['errors'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
                
                if self.config.fail_on_parse_errors:
                    raise
        
        # Save report if requested
        if self.config.report_path:
            self._save_report(report)
        
        # Print summary
        logger.info(f"Pipeline complete: {report['files_processed']} processed, "
                   f"{report['files_modified']} modified, {report['files_skipped']} skipped, "
                   f"{report['files_failed']} failed")
        logger.info(f"Translated {report['fragments_translated']} fragment(s) "
                   f"in {report['segments_processed']} segment(s)")
        
        return report
    
    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file.
        
        Returns:
            Dictionary with file processing details
        """
        logger.debug(f"Processing {file_path}")
        
        file_report = {
            'file': str(file_path),
            'modified': False,
            'skipped': False,
            'segments_processed': 0,
            'fragments_translated': 0,
            'error': None
        }
        
        # Skip binary files
        if is_binary_file(file_path):
            logger.debug(f"Skipping binary file: {file_path}")
            file_report['skipped'] = True
            file_report['error'] = 'Binary file'
            return file_report
        
        # Get comment style
        style = get_comment_style_for_path(file_path, self.config.comment_style_overrides)
        if not style:
            logger.debug(f"No comment style for {file_path}, skipping")
            file_report['skipped'] = True
            file_report['error'] = 'No comment style'
            return file_report
        
        # Extract segments
        try:
            segments = self.extractor.extract_segments(file_path, style)
        except Exception as e:
            logger.warning(f"Failed to extract segments from {file_path}: {e}")
            file_report['skipped'] = True
            file_report['error'] = f'Extraction failed: {e}'
            return file_report
        
        if not segments:
            logger.debug(f"No comments found in {file_path}")
            file_report['skipped'] = True
            return file_report
        
        logger.debug(f"Found {len(segments)} segment(s) in {file_path}")
        
        # Process segments
        modifications = []
        for segment in segments:
            translated_text, num_translated = self._process_segment(segment)
            
            if num_translated > 0:
                # Apply post-processing
                final_text = self.post_processor.apply(segment, translated_text, style)
                modifications.append((segment, final_text))
                file_report['fragments_translated'] += num_translated
            
            file_report['segments_processed'] += 1
        
        # Apply modifications to file if any
        if modifications:
            if not self.config.dry_run:
                self._apply_modifications(file_path, modifications)
                file_report['modified'] = True
                logger.info(f"Modified {file_path}: {file_report['fragments_translated']} fragment(s) translated")
            else:
                file_report['modified'] = False
                logger.info(f"[DRY RUN] Would modify {file_path}: {file_report['fragments_translated']} fragment(s)")
        
        return file_report
    
    def _process_segment(self, segment: CommentSegment) -> tuple[str, int]:
        """
        Process a single comment segment: detect language and translate.
        
        Returns:
            Tuple of (translated_text, num_fragments_translated)
        """
        if self.config.detect_source_language:
            # Detect language fragments
            fragments = self.detector.detect_fragments(segment.raw_text)
            
            # Translate fragments in source language
            translated_parts = []
            num_translated = 0
            
            for fragment in fragments:
                if fragment.language == self.config.source_language:
                    # Translate this fragment
                    try:
                        translated = self.translator.translate(
                            fragment.text,
                            self.config.source_language,
                            self.config.target_language
                        )
                        translated_parts.append(translated)
                        num_translated += 1
                    except Exception as e:
                        logger.warning(f"Translation failed for fragment: {e}")
                        translated_parts.append(fragment.text)
                else:
                    # Keep as-is
                    translated_parts.append(fragment.text)
            
            # Reconstruct text
            translated_text = ''.join(translated_parts)
            return translated_text, num_translated
        
        else:
            # Treat entire segment as source language
            try:
                translated_text = self.translator.translate(
                    segment.raw_text,
                    self.config.source_language,
                    self.config.target_language
                )
                return translated_text, 1
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
                return segment.raw_text, 0
    
    def _apply_modifications(self, file_path: Path, modifications: List[tuple]) -> None:
        """
        Apply segment modifications to file.
        
        Args:
            file_path: Path to file
            modifications: List of (segment, new_text) tuples
        """
        # Create backup if requested
        if self.config.create_backups:
            create_backup(file_path, self.config.backup_extension)
        
        # Read original lines
        lines = read_file_lines(file_path)
        
        # Sort modifications by start_line (descending) to apply from bottom to top
        # This avoids line number offset issues
        modifications_sorted = sorted(modifications, key=lambda m: m[0].start_line, reverse=True)
        
        for segment, new_text in modifications_sorted:
            # Replace lines [start_line-1 : end_line] with new_text
            # Lines are 1-based, list indices are 0-based
            start_idx = segment.start_line - 1
            end_idx = segment.end_line  # end_line is inclusive, so we don't subtract 1 for slicing
            
            # Split new_text into lines
            new_lines = new_text.splitlines(keepends=True)
            
            # Ensure all lines have line endings
            new_lines = [line if line.endswith('\n') else line + '\n' for line in new_lines]
            
            # Replace
            lines[start_idx:end_idx] = new_lines
        
        # Write modified file
        write_file_lines(file_path, lines)
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """
        Save processing report to JSON file.
        """
        try:
            self.config.report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to {self.config.report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
