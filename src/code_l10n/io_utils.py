# -*- coding: utf-8 -*-
"""
File I/O utilities for the code_l10n library.
"""
import logging
from pathlib import Path
from typing import List, Iterator
import fnmatch


logger = logging.getLogger(__name__)


def discover_files(
    source_paths: List[Path],
    include_patterns: List[str],
    exclude_patterns: List[str]
) -> List[Path]:
    """
    Discover files to process based on include/exclude patterns.
    
    Args:
        source_paths: List of file or directory paths
        include_patterns: Glob patterns for files to include
        exclude_patterns: Glob patterns for files to exclude
        
    Returns:
        List of file paths to process
    """
    discovered = []
    
    for source_path in source_paths:
        if source_path.is_file():
            # Check if this single file matches patterns
            if should_include_file(source_path, include_patterns, exclude_patterns):
                discovered.append(source_path)
        elif source_path.is_dir():
            # Walk directory
            for file_path in walk_directory(source_path, include_patterns, exclude_patterns):
                discovered.append(file_path)
        else:
            logger.warning(f"Path does not exist or is not a file/directory: {source_path}")
    
    return discovered


def walk_directory(
    directory: Path,
    include_patterns: List[str],
    exclude_patterns: List[str]
) -> Iterator[Path]:
    """
    Walk directory and yield files matching patterns.
    
    Args:
        directory: Directory to walk
        include_patterns: Glob patterns for files to include
        exclude_patterns: Glob patterns for files to exclude
        
    Yields:
        File paths matching criteria
    """
    for path in directory.rglob('*'):
        if path.is_file():
            if should_include_file(path, include_patterns, exclude_patterns):
                yield path


def should_include_file(
    file_path: Path,
    include_patterns: List[str],
    exclude_patterns: List[str]
) -> bool:
    """
    Check if a file should be included based on patterns.
    
    Args:
        file_path: File to check
        include_patterns: Patterns to include
        exclude_patterns: Patterns to exclude
        
    Returns:
        True if file should be included
    """
    # Check exclude patterns first (highest priority)
    for pattern in exclude_patterns:
        if matches_pattern(file_path, pattern):
            return False
    
    # Check include patterns
    if not include_patterns:
        return True
    
    for pattern in include_patterns:
        if matches_pattern(file_path, pattern):
            return True
    
    return False


def matches_pattern(file_path: Path, pattern: str) -> bool:
    """
    Check if a file path matches a glob pattern.
    
    Supports both simple patterns (*.py) and path patterns (**/test_*.py).
    
    Args:
        file_path: File path to check
        pattern: Glob pattern
        
    Returns:
        True if path matches pattern
    """
    # Match against filename
    if fnmatch.fnmatch(file_path.name, pattern):
        return True
    
    # Match against relative path (if pattern contains path separators)
    if '/' in pattern or '\\' in pattern:
        # Normalize pattern
        pattern_path = Path(pattern)
        
        # Try matching full path
        if fnmatch.fnmatch(str(file_path), pattern):
            return True
        
        # Try matching parts of the path
        for parent in [file_path] + list(file_path.parents):
            if fnmatch.fnmatch(str(parent), pattern):
                return True
    
    return False


def is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
    """
    Check if a file is binary by attempting to decode it as UTF-8.
    
    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample
        
    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        # Check for NULL bytes (common in binary files)
        if b'\x00' in sample:
            return True
        
        # Try to decode as UTF-8
        sample.decode('utf-8')
        return False
    
    except (UnicodeDecodeError, IOError):
        return True


def read_file_lines(file_path: Path) -> List[str]:
    """
    Read file as list of lines, preserving line endings.
    
    Args:
        file_path: Path to file
        
    Returns:
        List of lines with line endings preserved
        
    Raises:
        IOError: If file cannot be read
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        return f.readlines()


def write_file_lines(file_path: Path, lines: List[str]) -> None:
    """
    Write lines to file atomically.
    
    Args:
        file_path: Path to file
        lines: Lines to write (with line endings)
        
    Raises:
        IOError: If file cannot be written
    """
    # Write to temporary file first
    temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Atomic rename
        temp_path.replace(file_path)
    
    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        raise


def create_backup(file_path: Path, backup_extension: str = '.bak') -> Path:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to file
        backup_extension: Extension for backup file
        
    Returns:
        Path to backup file
        
    Raises:
        IOError: If backup cannot be created
    """
    backup_path = file_path.with_suffix(file_path.suffix + backup_extension)
    
    # Read original and write to backup
    with open(file_path, 'rb') as src:
        content = src.read()
    
    with open(backup_path, 'wb') as dst:
        dst.write(content)
    
    logger.debug(f"Created backup: {backup_path}")
    return backup_path
