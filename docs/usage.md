# Usage Guide

`code_l10n` is a Python library for localizing comments and docstrings in source code. It scans source files, detects comments in a specific language, and translates them to a target language.

## Installation

```bash
pip install code_l10n
```

## Basic Usage

### As a Library

```python
from pathlib import Path
from code_l10n import CodeL10nConfig, CodeL10nPipeline, Language

# Create configuration
config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=Language.UKRAINIAN,
    target_language=Language.ENGLISH,
    translation_engine="internal",
    dry_run=False
)

# Run pipeline
pipeline = CodeL10nPipeline(config)
report = pipeline.run()

# Check results
print(f"Processed {report['files_processed']} files")
print(f"Translated {report['fragments_translated']} fragments")
```

### As a Command-Line Tool

```bash
# Basic usage
code-l10n --path src/ --source-language uk --target-language en

# With include patterns
code-l10n --path src/ --include-pattern "**/*.py" --include-pattern "**/*.cpp"

# Dry run (preview changes without modifying files)
code-l10n --path src/ --dry-run --verbose
```

See [CLI documentation](cli.md) for more command-line options.

## Configuration

### Basic Options

```python
config = CodeL10nConfig(
    source_paths=[Path("src"), Path("include")],  # Paths to process
    source_language=Language.UKRAINIAN,            # Language to translate from
    target_language=Language.ENGLISH,              # Language to translate to
)
```

### File Selection

```python
config = CodeL10nConfig(
    source_paths=[Path(".")],
    include_patterns=["**/*.py", "**/*.cpp"],      # Only process these
    exclude_patterns=["**/test_*", "**/venv/**"],  # Skip these
)
```

### Language Detection

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    detect_source_language=True,   # Auto-detect language per fragment
    # If False, assume all comments are in source_language
)
```

### Translation Engines

#### Echo Translator (for testing)

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    translation_engine="echo",  # Returns text unchanged
)
```

#### Internal Simple Translator

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    translation_engine="internal",  # Simple dictionary-based translation
)
```

#### External API Translator

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    translation_engine="external",
    translation_engine_options={
        "base_url": "https://api.example.com/translate",
        "api_key_env": "TRANSLATION_API_KEY",  # Read from environment
        "timeout": 30.0,
    }
)
```

### Post-Processing Profiles

```python
# Default: preserve original comment structure
config = CodeL10nConfig(
    source_paths=[Path("src")],
    postprocess_profile="default",
)

# Prefer block comments: convert multi-line // to /* */
config = CodeL10nConfig(
    source_paths=[Path("src")],
    postprocess_profile="prefer_block_comments",
)

# Flatten to single line when possible
config = CodeL10nConfig(
    source_paths=[Path("src")],
    postprocess_profile="flatten_single_line",
)
```

### Backup and Reporting

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    create_backups=True,           # Create .bak files
    backup_extension=".bak",       # Backup file extension
    report_path=Path("report.json"),  # Save JSON report
)
```

## Supported Languages

The library supports detection and translation between:

- English (en)
- Ukrainian (uk)
- Russian (ru)
- Polish (pl)
- French (fr)
- German (de)
- Czech (cs)
- Spanish (es)
- Vietnamese (vi)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Swedish (sv)
- Norwegian (no)
- Danish (da)
- Finnish (fi)
- Greek (el)
- Turkish (tr)
- Arabic (ar)
- Hebrew (he)
- Hindi (hi)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)

## Supported File Types

The library recognizes comments and docstrings in 50+ file types including:

- **C/C++**: `*.c`, `*.cpp`, `*.h`, `*.hpp`
- **Java**: `*.java`
- **C#**: `*.cs`
- **JavaScript/TypeScript**: `*.js`, `*.jsx`, `*.ts`, `*.tsx`
- **Python**: `*.py` (including docstrings)
- **Go**: `*.go`
- **Rust**: `*.rs`
- **Ruby**: `*.rb`
- **PHP**: `*.php`
- **Shell**: `*.sh`, `*.bash`, `*.zsh`
- **SQL**: `*.sql`
- **HTML/XML**: `*.html`, `*.xml`
- **And many more...**

See [Configuration](configuration.md) for custom comment styles.

## Advanced Usage

### Custom Comment Styles

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    comment_style_overrides={
        "*.custom": {
            "line_markers": ["##"],
            "block_markers": [("###", "###")],
            "docstring_markers": []
        }
    }
)
```

### Programmatic Pipeline Control

```python
from code_l10n import (
    CodeL10nPipeline,
    EchoTranslator,
    PostProcessor,
    CommentExtractor,
    LanguageDetector,
)

# Create custom components
translator = EchoTranslator()
detector = LanguageDetector()
post_processor = PostProcessor("prefer_block_comments")

# Use in pipeline
pipeline = CodeL10nPipeline(config)
pipeline.translator = translator
report = pipeline.run()
```

### Working with Comment Segments

```python
from code_l10n import CommentExtractor, get_comment_style_for_path
from pathlib import Path

# Extract comments from a file
extractor = CommentExtractor()
file_path = Path("example.py")
style = get_comment_style_for_path(file_path)

if style:
    segments = extractor.extract_segments(file_path, style)
    
    for segment in segments:
        print(f"Type: {segment.segment_type}")
        print(f"Lines: {segment.start_line}-{segment.end_line}")
        print(f"Text: {segment.raw_text}")
```

## Error Handling

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    fail_on_parse_errors=False,  # Continue on errors
    verbose=True,                 # Show detailed logs
)

pipeline = CodeL10nPipeline(config)
report = pipeline.run()

# Check for errors
if report['files_failed'] > 0:
    print("Some files failed:")
    for error in report['errors']:
        print(f"  {error['file']}: {error['error']}")
```

## Examples

### Example 1: Translate Ukrainian Comments to English

```python
from pathlib import Path
from code_l10n import CodeL10nConfig, CodeL10nPipeline, Language

config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=Language.UKRAINIAN,
    target_language=Language.ENGLISH,
    translation_engine="internal",
    postprocess_profile="prefer_block_comments",
    create_backups=True,
)

pipeline = CodeL10nPipeline(config)
report = pipeline.run()
print(f"Done! Translated {report['fragments_translated']} comments")
```

### Example 2: Dry Run with Custom Patterns

```python
config = CodeL10nConfig(
    source_paths=[Path(".")],
    include_patterns=["**/*.cpp", "**/*.h"],
    exclude_patterns=["**/third_party/**", "**/build/**"],
    source_language=Language.RUSSIAN,
    target_language=Language.ENGLISH,
    dry_run=True,  # Don't modify files
    report_path=Path("translation_preview.json"),
)

pipeline = CodeL10nPipeline(config)
report = pipeline.run()
```

## Next Steps

- See [CLI documentation](cli.md) for command-line usage
- See [Configuration reference](configuration.md) for all options
- Check the [GitHub repository](https://github.com/yuchdev/code_l10n) for more examples
