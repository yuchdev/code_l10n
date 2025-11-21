# Code L10n

A Python library and CLI tool for localizing comments and docstrings in source code.

## Overview

`code_l10n` scans source trees for comments and docstrings in many programming and configuration languages, detects portions written in a specific non-English language (e.g., Ukrainian), and translates them using a pluggable translation engine. The translated text is written back into the source code while preserving formatting and allowing configurable post-processing transformations.

## Features

- **50+ Programming Languages**: Supports C/C++, Python, Java, JavaScript, TypeScript, Go, Rust, Ruby, PHP, Shell scripts, SQL, HTML, and many more
- **Smart Language Detection**: Automatically detects language per sentence/fragment within comments
- **AST-Based Python Parsing**: Accurate extraction of docstrings using Python's Abstract Syntax Tree
- **Multiple Translation Engines**:
  - Echo translator (for testing)
  - Internal simple dictionary-based translator
  - External API translator (pluggable)
- **Flexible Post-Processing**: 
  - Preserve original structure
  - Convert multi-line `//` comments to `/* */` blocks
  - Flatten to single-line comments
- **Safe Operations**: 
  - Dry-run mode to preview changes
  - Automatic backup creation
  - Atomic file writes
  - Detailed JSON reports

## Installation

```bash
pip install code_l10n
```

## Quick Start

### Command Line

```bash
# Translate Ukrainian comments to English
code-l10n --path src/ --source-language uk --target-language en

# Dry run with preview
code-l10n --path src/ --source-language uk --dry-run --verbose

# Process specific file types
code-l10n --path . --include-pattern "**/*.py" --include-pattern "**/*.cpp"
```

### Python Library

```python
from pathlib import Path
from code_l10n import CodeL10nConfig, CodeL10nPipeline, Language

# Configure
config = CodeL10nConfig(
    source_paths=[Path("src")],
    source_language=Language.UKRAINIAN,
    target_language=Language.ENGLISH,
    translation_engine="internal",
    dry_run=False
)

# Run
pipeline = CodeL10nPipeline(config)
report = pipeline.run()

print(f"Processed {report['files_processed']} files")
print(f"Translated {report['fragments_translated']} fragments")
```

## Supported Languages

English, Ukrainian, Russian, Polish, French, German, Czech, Spanish, Vietnamese, Italian, Portuguese, Dutch, Swedish, Norwegian, Danish, Finnish, Greek, Turkish, Arabic, Hebrew, Hindi, Chinese, Japanese, Korean, and more.

## Supported File Types

C/C++, Java, C#, JavaScript, TypeScript, Python, Go, Rust, Ruby, PHP, Shell scripts, SQL, HTML/XML, Lua, Haskell, R, Perl, Scala, CSS/SCSS, Markdown, LaTeX, MATLAB, Fortran, Lisp, Erlang, and many others.

## Example Transformations

**Before:**
```python
# Це функція для обчислення суми
def calculate_sum(a, b):
    """Повертає суму двох чисел."""
    return a + b
```

**After:**
```python
# This is a function to calculate the sum
def calculate_sum(a, b):
    """Returns the sum of two numbers."""
    return a + b
```

## Documentation

- [Usage Guide](docs/usage.md) - Detailed library API documentation
- [CLI Documentation](docs/cli.md) - Command-line interface reference
- [Configuration Reference](docs/configuration.md) - All configuration options

## Architecture

The library is organized into several focused modules:

- `enums.py` - Language definitions and normalization
- `config.py` - Configuration data structures
- `comment_styles.py` - Comment syntax definitions for 50+ file types
- `segments.py` - Comment segment representation
- `extractor.py` - Comment and docstring extraction
- `detector.py` - Language detection for text fragments
- `translator.py` - Translation engine interface and implementations
- `postprocess.py` - Post-processing transformations
- `io_utils.py` - File discovery and I/O operations
- `pipeline.py` - Orchestration of the full processing pipeline
- `cli.py` - Command-line interface

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover -s test -v

# Run specific test module
python -m unittest test.test_extractor_python -v
```

### Project Structure

```
code_l10n/
├── src/
│   └── code_l10n/
│       ├── __init__.py
│       ├── cli.py
│       ├── comment_styles.py
│       ├── config.py
│       ├── detector.py
│       ├── enums.py
│       ├── extractor.py
│       ├── io_utils.py
│       ├── pipeline.py
│       ├── postprocess.py
│       ├── segments.py
│       └── translator.py
├── test/
│   ├── test_comment_styles.py
│   ├── test_extractor_python.py
│   ├── test_extractor_cpp.py
│   ├── test_detector.py
│   ├── test_translator.py
│   ├── test_postprocess.py
│   ├── test_pipeline_integration.py
│   └── test_cli.py
├── docs/
│   ├── usage.md
│   ├── cli.md
│   └── configuration.md
├── pyproject.toml
├── setup.py
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.

## Author

Yurii Cherkasov (strategarius@protonmail.com)

## Links

- [GitHub Repository](https://github.com/yuchdev/code_l10n)
- [PyPI Package](https://pypi.org/project/code-l10n/)
- [Issue Tracker](https://github.com/yuchdev/code_l10n/issues)

