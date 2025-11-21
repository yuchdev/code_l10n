# Configuration Reference

This document provides detailed information about all configuration options available in `code_l10n`.

## CodeL10nConfig Class

The main configuration class for the library.

```python
from code_l10n import CodeL10nConfig, Language
from pathlib import Path

config = CodeL10nConfig(
    source_paths=[Path("src")],
    # ... other options
)
```

## Configuration Options

### Required Options

#### `source_paths: list[Path]`

List of files or directories to process.

```python
# Process single directory
source_paths=[Path("src")]

# Process multiple paths
source_paths=[Path("src"), Path("include"), Path("lib")]

# Process single file
source_paths=[Path("src/main.py")]
```

### File Selection

#### `include_patterns: list[str]`

Glob patterns for files to include. Default: `["**/*"]` (all files).

```python
# Only Python files
include_patterns=["**/*.py"]

# Multiple file types
include_patterns=["**/*.cpp", "**/*.h", "**/*.hpp"]

# Specific directories
include_patterns=["src/**/*.py", "lib/**/*.py"]
```

#### `exclude_patterns: list[str]`

Glob patterns for files to exclude. Default: `[]` (none).

```python
# Exclude test files and build artifacts
exclude_patterns=[
    "**/test_*.py",
    "**/__pycache__/**",
    "**/build/**",
    "**/dist/**",
    "**/node_modules/**",
]
```

### Language Settings

#### `source_language: Language`

Language to detect and translate from. Default: `Language.UKRAINIAN`.

```python
from code_l10n import Language

source_language=Language.UKRAINIAN
source_language=Language.RUSSIAN
source_language=Language.POLISH
```

Available languages: `ENGLISH`, `UKRAINIAN`, `RUSSIAN`, `POLISH`, `FRENCH`, `GERMAN`, `CZECH`, `SPANISH`, `VIETNAMESE`, `ITALIAN`, `PORTUGUESE`, `DUTCH`, `SWEDISH`, `NORWEGIAN`, `DANISH`, `FINNISH`, `GREEK`, `TURKISH`, `ARABIC`, `HEBREW`, `HINDI`, `CHINESE`, `JAPANESE`, `KOREAN`.

#### `target_language: Language`

Language to translate to. Default: `Language.ENGLISH`.

```python
target_language=Language.ENGLISH
target_language=Language.FRENCH
```

#### `detect_source_language: bool`

If `True`, detects language per text fragment. If `False`, assumes all text is in `source_language`. Default: `True`.

```python
# Auto-detect language (recommended for mixed-language codebases)
detect_source_language=True

# Assume all comments are in source_language
detect_source_language=False
```

### Comment Style Customization

#### `comment_style_overrides: dict[str, dict]`

Custom comment style definitions for specific patterns. Default: `{}`.

```python
comment_style_overrides={
    "*.custom": {
        "line_markers": ["##"],
        "block_markers": [["###", "###"]],
        "docstring_markers": []
    },
    "*.special": {
        "line_markers": [";", "#"],
        "block_markers": [["/*", "*/"]],
        "docstring_markers": []
    }
}
```

Each style definition contains:
- `line_markers`: List of line comment prefixes
- `block_markers`: List of `[start, end]` pairs for block comments
- `docstring_markers`: List of `[start, end]` pairs for docstrings

### Translation Engine

#### `translation_engine: str`

Name of the translation engine to use. Default: `"internal"`.

Options:
- `"echo"`: Returns text unchanged (for testing)
- `"internal"`: Simple dictionary-based translation
- `"external"`: HTTP API-based translation

```python
translation_engine="echo"
translation_engine="internal"
translation_engine="external"
```

#### `translation_engine_options: dict[str, Any]`

Engine-specific options. Default: `{}`.

For `"external"` engine:

```python
translation_engine_options={
    "base_url": "https://api.example.com/translate",  # Required
    "api_key": "your-api-key",                        # Optional, direct key
    "api_key_env": "TRANSLATION_API_KEY",             # Optional, from environment
    "timeout": 30.0,                                   # Optional, default 10.0
}
```

### Post-Processing

#### `postprocess_profile: str`

Post-processing strategy for translated comments. Default: `"default"`.

Options:
- `"default"`: Preserve original comment structure
- `"prefer_block_comments"`: Convert multi-line `//` comments to `/* */`
- `"flatten_single_line"`: Convert to single-line comments when text has no newlines

```python
# Keep original structure
postprocess_profile="default"

# Convert to block comments
postprocess_profile="prefer_block_comments"

# Flatten short comments
postprocess_profile="flatten_single_line"
```

#### Post-Processing Examples

**Before (default):**
```cpp
// Перший рядок
// Другий рядок
```

**After (default):**
```cpp
// First line
// Second line
```

**After (prefer_block_comments):**
```cpp
/*
 * First line
 * Second line
 */
```

**After (flatten_single_line):**
```cpp
// First line Second line
```

### File Operations

#### `dry_run: bool`

If `True`, shows what would be done without modifying files. Default: `False`.

```python
dry_run=True   # Preview changes only
dry_run=False  # Actually modify files
```

#### `in_place: bool`

If `True`, modifies files in place. Default: `True`.

```python
in_place=True  # Modify original files
```

#### `create_backups: bool`

If `True`, creates backup files before modification. Default: `True`.

```python
create_backups=True   # Save .bak files
create_backups=False  # Don't create backups
```

#### `backup_extension: str`

Extension for backup files. Default: `".bak"`.

```python
backup_extension=".bak"
backup_extension=".backup"
backup_extension=".orig"
```

### Reporting

#### `report_path: Optional[Path]`

Path to save JSON report of changes. Default: `None` (no report).

```python
report_path=Path("translation_report.json")
report_path=None  # No report
```

Report format:
```json
{
  "files_processed": 42,
  "files_modified": 38,
  "files_skipped": 2,
  "files_failed": 2,
  "segments_processed": 156,
  "fragments_translated": 142,
  "errors": [...],
  "file_details": [...]
}
```

### Logging and Error Handling

#### `verbose: bool`

Enable verbose logging. Default: `False`.

```python
verbose=True   # Detailed logs
verbose=False  # Normal logs
```

#### `fail_on_parse_errors: bool`

If `True`, raises exception on parse errors. If `False`, logs errors and continues. Default: `False`.

```python
fail_on_parse_errors=True   # Stop on first error
fail_on_parse_errors=False  # Continue on errors
```

## Complete Configuration Example

```python
from code_l10n import CodeL10nConfig, Language
from pathlib import Path

config = CodeL10nConfig(
    # Input/output
    source_paths=[
        Path("src"),
        Path("include"),
        Path("lib")
    ],
    include_patterns=[
        "**/*.cpp",
        "**/*.h",
        "**/*.hpp"
    ],
    exclude_patterns=[
        "**/third_party/**",
        "**/build/**",
        "**/test/**"
    ],
    
    # Language settings
    source_language=Language.UKRAINIAN,
    target_language=Language.ENGLISH,
    detect_source_language=True,
    
    # Comment style overrides
    comment_style_overrides={
        "*.inc": {
            "line_markers": ["//"],
            "block_markers": [["/*", "*/"]],
            "docstring_markers": []
        }
    },
    
    # Translation
    translation_engine="external",
    translation_engine_options={
        "base_url": "https://translate.api.example.com/v1/translate",
        "api_key_env": "TRANSLATION_API_KEY",
        "timeout": 60.0
    },
    
    # Post-processing
    postprocess_profile="prefer_block_comments",
    
    # File operations
    dry_run=False,
    in_place=True,
    create_backups=True,
    backup_extension=".bak",
    
    # Reporting
    report_path=Path("reports/translation.json"),
    
    # Logging
    verbose=True,
    fail_on_parse_errors=False
)
```

## Configuration Presets

### Development/Testing Preset

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    translation_engine="echo",
    dry_run=True,
    verbose=True,
    report_path=Path("test_report.json")
)
```

### Production Preset

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=Language.UKRAINIAN,
    target_language=Language.ENGLISH,
    translation_engine="external",
    translation_engine_options={
        "base_url": os.environ["TRANSLATION_API_URL"],
        "api_key_env": "TRANSLATION_API_KEY",
        "timeout": 120.0
    },
    postprocess_profile="prefer_block_comments",
    create_backups=True,
    report_path=Path(f"reports/translation_{datetime.now():%Y%m%d_%H%M%S}.json"),
    verbose=False,
    fail_on_parse_errors=False
)
```

### Conservative Preset (No Language Detection)

```python
config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=Language.RUSSIAN,
    target_language=Language.ENGLISH,
    detect_source_language=False,  # Assume all comments are Russian
    translation_engine="internal",
    postprocess_profile="default",  # Keep original structure
    create_backups=True,
    dry_run=False
)
```

## Default Comment Styles

The library includes built-in support for 50+ file types. Some examples:

### C/C++ Family
```python
CommentStyle(
    line_markers=["//"],
    block_markers=[("/*", "*/")]
)
```

### Python
```python
CommentStyle(
    line_markers=["#"],
    block_markers=[],
    docstring_markers=[('"""', '"""'), ("'''", "'''")]
)
```

### Shell Scripts
```python
CommentStyle(
    line_markers=["#"],
    block_markers=[]
)
```

### HTML/XML
```python
CommentStyle(
    line_markers=[],
    block_markers=[("<!--", "-->")]
)
```

### SQL
```python
CommentStyle(
    line_markers=["--"],
    block_markers=[("/*", "*/")]
)
```

See `code_l10n.comment_styles.DEFAULT_COMMENT_STYLES` for the complete list.

## Locale Normalization

You can specify languages using various formats:

```python
from code_l10n import normalize_locale, Language

# Full locale
lang = normalize_locale("uk-UA")  # -> Language.UKRAINIAN

# Language code only
lang = normalize_locale("uk")     # -> Language.UKRAINIAN

# Using in config
config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=normalize_locale("uk-UA")
)
```

## See Also

- [Usage Guide](usage.md) - Library usage examples
- [CLI Documentation](cli.md) - Command-line interface
- [GitHub Repository](https://github.com/yuchdev/code_l10n) - Source code
