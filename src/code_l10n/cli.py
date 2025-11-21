# -*- coding: utf-8 -*-
"""
Command-line interface for code_l10n.
"""
import argparse
import sys
import logging
from pathlib import Path
from .config import CodeL10nConfig
from .enums import Language, normalize_locale
from .pipeline import CodeL10nPipeline


def parse_translation_options(options_list: list[str]) -> dict:
    """
    Parse KEY=VALUE pairs into dictionary.
    
    Args:
        options_list: List of "KEY=VALUE" strings
        
    Returns:
        Dictionary of options
    """
    options = {}
    for opt in options_list:
        if '=' not in opt:
            raise ValueError(f"Invalid option format: '{opt}'. Expected KEY=VALUE")
        key, value = opt.split('=', 1)
        options[key.strip()] = value.strip()
    return options


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.
    """
    parser = argparse.ArgumentParser(
        prog='code-l10n',
        description='Localize comments and docstrings in source code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process Python files, translate Ukrainian to English
  code-l10n --path src/ --source-language uk --target-language en
  
  # Process C++ files with specific patterns
  code-l10n --path src/ --include-pattern "**/*.cpp" --include-pattern "**/*.h"
  
  # Use external translation API
  code-l10n --path src/ --translation-engine external \\
    --translation-option base_url=https://api.example.com/translate \\
    --translation-option api_key_env=TRANSLATION_API_KEY
  
  # Dry run with verbose output
  code-l10n --path src/ --dry-run --verbose
        '''
    )
    
    # Input/output
    parser.add_argument(
        '--path',
        action='append',
        dest='paths',
        required=True,
        help='File or directory to process (can be specified multiple times)'
    )
    parser.add_argument(
        '--include-pattern',
        action='append',
        dest='include_patterns',
        default=[],
        help='Glob pattern for files to include (can be specified multiple times)'
    )
    parser.add_argument(
        '--exclude-pattern',
        action='append',
        dest='exclude_patterns',
        default=[],
        help='Glob pattern for files to exclude (can be specified multiple times)'
    )
    
    # Language settings
    lang_group = parser.add_argument_group('language settings')
    lang_group.add_argument(
        '--source-language',
        dest='source_language',
        help=f'Source language code (e.g., uk, ru, fr). Supported: {", ".join(l.value for l in Language)}'
    )
    lang_group.add_argument(
        '--target-language',
        dest='target_language',
        default='en',
        help='Target language code (default: en)'
    )
    lang_group.add_argument(
        '--locale',
        help='Locale string (e.g., uk-UA) - alternative to --source-language'
    )
    lang_group.add_argument(
        '--charset',
        help='Charset code (e.g., uk) - alternative to --source-language'
    )
    lang_group.add_argument(
        '--no-detect',
        action='store_true',
        dest='no_detect',
        help='Disable language detection; assume all comments are in source language'
    )
    
    # Translation engine
    trans_group = parser.add_argument_group('translation settings')
    trans_group.add_argument(
        '--translation-engine',
        choices=['echo', 'internal', 'external'],
        default='internal',
        help='Translation engine to use (default: internal)'
    )
    trans_group.add_argument(
        '--translation-option',
        action='append',
        dest='translation_options',
        default=[],
        help='Translation engine option in KEY=VALUE format (can be specified multiple times)'
    )
    
    # Post-processing
    parser.add_argument(
        '--postprocess-profile',
        choices=['default', 'prefer_block_comments', 'flatten_single_line'],
        default='default',
        help='Post-processing profile (default: default)'
    )
    
    # Execution control
    exec_group = parser.add_argument_group('execution control')
    exec_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without modifying files'
    )
    exec_group.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    exec_group.add_argument(
        '--report',
        dest='report_path',
        help='Path to save JSON report of changes'
    )
    
    # Logging
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    log_group.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress non-error output'
    )
    
    # Error handling
    parser.add_argument(
        '--fail-on-parse-errors',
        action='store_true',
        help='Exit with error if any file fails to parse'
    )
    
    return parser


def main(argv=None):
    """
    Main CLI entry point.
    
    Args:
        argv: Command-line arguments (for testing)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    try:
        # Determine source language
        source_language = None
        if args.source_language:
            source_language = normalize_locale(args.source_language)
        elif args.locale:
            source_language = normalize_locale(args.locale)
        elif args.charset:
            source_language = normalize_locale(args.charset)
        else:
            # Default to Ukrainian
            source_language = Language.UKRAINIAN
        
        # Determine target language
        target_language = normalize_locale(args.target_language)
        
        # Parse translation options
        translation_options = parse_translation_options(args.translation_options)
        
        # Convert paths
        source_paths = [Path(p) for p in args.paths]
        
        # Create config
        config = CodeL10nConfig(
            source_paths=source_paths,
            include_patterns=args.include_patterns if args.include_patterns else ["**/*"],
            exclude_patterns=args.exclude_patterns,
            source_language=source_language,
            target_language=target_language,
            detect_source_language=not args.no_detect,
            translation_engine=args.translation_engine,
            translation_engine_options=translation_options,
            postprocess_profile=args.postprocess_profile,
            dry_run=args.dry_run,
            create_backups=not args.no_backup,
            report_path=Path(args.report_path) if args.report_path else None,
            verbose=args.verbose,
            fail_on_parse_errors=args.fail_on_parse_errors
        )
        
        # Configure logging
        if args.quiet:
            logging.basicConfig(level=logging.ERROR, format='%(message)s')
        elif args.verbose:
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        # Run pipeline
        pipeline = CodeL10nPipeline(config)
        report = pipeline.run()
        
        # Exit with error if there were failures
        if report['files_failed'] > 0:
            return 1
        
        return 0
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
