# CLI Documentation

The `code-l10n` command-line tool provides a convenient interface for translating comments and docstrings in source code.

## Installation

After installing the package:

```bash
pip install code_l10n
```

The `code-l10n` command will be available in your PATH.

## Basic Usage

```bash
code-l10n --path <directory_or_file> [OPTIONS]
```

## Options

### Input/Output

#### `--path PATH` (required, repeatable)

Specifies files or directories to process. Can be used multiple times.

```bash
# Single directory
code-l10n --path src/

# Multiple paths
code-l10n --path src/ --path include/ --path lib/

# Single file
code-l10n --path src/main.py
```

#### `--include-pattern PATTERN` (optional, repeatable)

Glob pattern for files to include. Can be specified multiple times.

```bash
# Only Python files
code-l10n --path . --include-pattern "**/*.py"

# Multiple patterns
code-l10n --path . \
  --include-pattern "**/*.cpp" \
  --include-pattern "**/*.h"
```

#### `--exclude-pattern PATTERN` (optional, repeatable)

Glob pattern for files to exclude. Can be specified multiple times.

```bash
# Exclude test files and build directories
code-l10n --path . \
  --exclude-pattern "**/test_*" \
  --exclude-pattern "**/build/**" \
  --exclude-pattern "**/venv/**"
```

### Language Settings

#### `--source-language CODE`

Source language code to translate from. Examples: `uk`, `ru`, `fr`, `pl`.

```bash
code-l10n --path src/ --source-language uk --target-language en
```

#### `--target-language CODE`

Target language code to translate to. Default: `en`.

```bash
code-l10n --path src/ --source-language ru --target-language de
```

#### `--locale LOCALE`

Alternative way to specify source language using locale format (e.g., `uk-UA`, `ru-RU`).

```bash
code-l10n --path src/ --locale uk-UA
```

#### `--charset CHARSET`

Alternative way to specify source language using charset code.

```bash
code-l10n --path src/ --charset uk
```

#### `--no-detect`

Disable automatic language detection. Assumes all comments are in the source language.

```bash
code-l10n --path src/ --source-language uk --no-detect
```

### Translation Engine

#### `--translation-engine {echo|internal|external}`

Selects the translation engine. Default: `internal`.

- `echo`: Returns text unchanged (for testing)
- `internal`: Simple dictionary-based translation
- `external`: Uses external API

```bash
# Use internal translator
code-l10n --path src/ --translation-engine internal

# Use echo translator for testing
code-l10n --path src/ --translation-engine echo
```

#### `--translation-option KEY=VALUE` (repeatable)

Provides options for the translation engine. Can be specified multiple times.

```bash
# External API configuration
code-l10n --path src/ \
  --translation-engine external \
  --translation-option base_url=https://api.example.com/translate \
  --translation-option api_key_env=TRANSLATION_API_KEY \
  --translation-option timeout=30
```

### Post-Processing

#### `--postprocess-profile {default|prefer_block_comments|flatten_single_line}`

Selects the post-processing profile. Default: `default`.

- `default`: Preserves original comment structure
- `prefer_block_comments`: Converts multi-line `//` to `/* */`
- `flatten_single_line`: Converts to single-line when possible

```bash
# Convert multi-line comments to block style
code-l10n --path src/ --postprocess-profile prefer_block_comments
```

### Execution Control

#### `--dry-run`

Shows what would be done without actually modifying files.

```bash
code-l10n --path src/ --dry-run
```

#### `--no-backup`

Disables creation of backup files (`.bak`).

```bash
code-l10n --path src/ --no-backup
```

#### `--report PATH`

Saves a JSON report of changes to the specified file.

```bash
code-l10n --path src/ --report translation_report.json
```

### Logging

#### `--verbose`

Enables verbose output showing detailed progress.

```bash
code-l10n --path src/ --verbose
```

#### `--quiet`

Suppresses all output except errors.

```bash
code-l10n --path src/ --quiet
```

### Error Handling

#### `--fail-on-parse-errors`

Exits with an error if any file fails to parse. By default, errors are logged and processing continues.

```bash
code-l10n --path src/ --fail-on-parse-errors
```

## Examples

### Example 1: Translate Ukrainian to English

```bash
code-l10n \
  --path src/ \
  --source-language uk \
  --target-language en \
  --verbose
```

### Example 2: Process Specific File Types

```bash
code-l10n \
  --path . \
  --include-pattern "**/*.cpp" \
  --include-pattern "**/*.h" \
  --exclude-pattern "**/third_party/**" \
  --source-language ru \
  --target-language en
```

### Example 3: Dry Run with Report

```bash
code-l10n \
  --path src/ \
  --source-language uk \
  --target-language en \
  --dry-run \
  --report preview.json \
  --verbose
```

### Example 4: Convert Comment Styles

```bash
code-l10n \
  --path src/ \
  --source-language pl \
  --target-language en \
  --postprocess-profile prefer_block_comments
```

### Example 5: Use External Translation API

```bash
export TRANSLATION_API_KEY="your-api-key-here"

code-l10n \
  --path src/ \
  --source-language uk \
  --target-language en \
  --translation-engine external \
  --translation-option base_url=https://api.translator.com/v1/translate \
  --translation-option api_key_env=TRANSLATION_API_KEY \
  --translation-option timeout=60
```

### Example 6: Process Multiple Projects

```bash
code-l10n \
  --path project1/src/ \
  --path project2/src/ \
  --path common/lib/ \
  --source-language ru \
  --target-language en \
  --no-backup \
  --report multi_project_report.json
```

### Example 7: Conservative Translation

```bash
code-l10n \
  --path src/ \
  --source-language uk \
  --target-language en \
  --no-detect \
  --postprocess-profile default \
  --dry-run
```

## Exit Codes

- `0`: Success
- `1`: General error (translation failures, file I/O errors)
- `2`: Configuration error (invalid arguments)
- `130`: Interrupted by user (Ctrl+C)

## Report Format

When using `--report`, the JSON report contains:

```json
{
  "files_processed": 42,
  "files_modified": 38,
  "files_skipped": 2,
  "files_failed": 2,
  "segments_processed": 156,
  "fragments_translated": 142,
  "errors": [
    {
      "file": "src/broken.py",
      "error": "Syntax error at line 10"
    }
  ],
  "file_details": [
    {
      "file": "src/example.py",
      "modified": true,
      "segments_processed": 5,
      "fragments_translated": 4
    }
  ]
}
```

## Environment Variables

### `TRANSLATION_API_KEY`

When using `--translation-option api_key_env=TRANSLATION_API_KEY`, the API key is read from this environment variable.

```bash
export TRANSLATION_API_KEY="your-secret-key"
code-l10n --path src/ --translation-engine external --translation-option api_key_env=TRANSLATION_API_KEY
```

## Tips and Best Practices

### 1. Always Test with Dry Run First

```bash
code-l10n --path src/ --dry-run --verbose --report preview.json
# Review preview.json
# If satisfied, run without --dry-run
code-l10n --path src/
```

### 2. Use Version Control

Ensure your code is committed before running translations:

```bash
git commit -am "Before translation"
code-l10n --path src/
git diff  # Review changes
```

### 3. Process in Stages

For large projects, process in stages:

```bash
# Stage 1: Core library
code-l10n --path src/core/

# Stage 2: Tests
code-l10n --path tests/

# Stage 3: Documentation
code-l10n --path docs/
```

### 4. Exclude Generated Code

```bash
code-l10n \
  --path . \
  --exclude-pattern "**/node_modules/**" \
  --exclude-pattern "**/build/**" \
  --exclude-pattern "**/dist/**" \
  --exclude-pattern "**/__pycache__/**"
```

### 5. Save Configuration in Scripts

Create a shell script for repeated use:

```bash
#!/bin/bash
# translate.sh

code-l10n \
  --path src/ \
  --path include/ \
  --source-language uk \
  --target-language en \
  --include-pattern "**/*.cpp" \
  --include-pattern "**/*.h" \
  --exclude-pattern "**/third_party/**" \
  --postprocess-profile prefer_block_comments \
  --report "reports/translation_$(date +%Y%m%d_%H%M%S).json" \
  --verbose \
  "$@"
```

## Troubleshooting

### Problem: No files are being processed

- Check that your `--include-pattern` matches your files
- Verify that `--exclude-pattern` isn't too broad
- Use `--verbose` to see which files are discovered

### Problem: Comments aren't being translated

- Verify the comment style is recognized (see supported file types)
- Check that language detection is working (try `--no-detect`)
- Use `--verbose` to see what's being detected

### Problem: Translation API fails

- Verify API endpoint is correct
- Check that API key environment variable is set
- Increase timeout with `--translation-option timeout=120`

## See Also

- [Usage Guide](usage.md) - Library API documentation
- [Configuration Reference](configuration.md) - Detailed configuration options
- [GitHub Repository](https://github.com/yuchdev/code_l10n) - Source code and issues
