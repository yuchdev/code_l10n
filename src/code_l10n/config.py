# -*- coding: utf-8 -*-
"""
Configuration data structures for the code_l10n library.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from .enums import Language


@dataclass
class CodeL10nConfig:
    """
    Configuration for code localization pipeline.
    
    Attributes:
        source_paths: List of files or directories to process
        include_patterns: Glob patterns for files to include (default: ["**/*"])
        exclude_patterns: Glob patterns for files to exclude
        source_language: Language to detect and translate from
        target_language: Language to translate to
        detect_source_language: If True, detect language; if False, assume source_language
        comment_style_overrides: Custom comment style definitions per pattern
        translation_engine: Name of translation engine ("internal", "external", "echo")
        translation_engine_options: Engine-specific options
        postprocess_profile: Post-processing strategy name
        dry_run: If True, don't modify files
        in_place: If True, modify files in place
        create_backups: If True, create backup files before modification
        backup_extension: Extension for backup files
        report_path: Path to save JSON report of changes
        verbose: Enable verbose logging
        fail_on_parse_errors: If True, fail on parsing errors; if False, skip files with errors
    """
    source_paths: list[Path]
    include_patterns: list[str] = field(default_factory=lambda: ["**/*"])
    exclude_patterns: list[str] = field(default_factory=list)
    source_language: Language = Language.UKRAINIAN
    target_language: Language = Language.ENGLISH
    detect_source_language: bool = True
    
    comment_style_overrides: dict[str, dict] = field(default_factory=dict)
    
    translation_engine: str = "internal"
    translation_engine_options: Dict[str, Any] = field(default_factory=dict)
    
    postprocess_profile: str = "default"
    
    dry_run: bool = False
    in_place: bool = True
    create_backups: bool = True
    backup_extension: str = ".bak"
    
    report_path: Optional[Path] = None
    
    verbose: bool = False
    fail_on_parse_errors: bool = False
