# -*- coding: utf-8 -*-
"""
Comment style definitions and registry for supported file types.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple
import fnmatch


@dataclass
class CommentStyle:
    """
    Defines comment syntax for a file type.
    
    Attributes:
        line_markers: List of single-line comment markers (e.g., ["//", "#"])
        block_markers: List of (start, end) tuples for block comments (e.g., [("/*", "*/")])
        docstring_markers: List of (start, end) tuples for docstrings (e.g., [('"""', '"""')])
    """
    line_markers: List[str] = field(default_factory=list)
    block_markers: List[Tuple[str, str]] = field(default_factory=list)
    docstring_markers: List[Tuple[str, str]] = field(default_factory=list)


# Registry maps glob patterns or file names to CommentStyle
DEFAULT_COMMENT_STYLES: dict[str, CommentStyle] = {
    # C / C++ / Java / C# / JS / TS / Kotlin / Swift / Go / Rust
    "*.c": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.h": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.cpp": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.hpp": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.cc": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.cxx": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.hxx": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.java": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.cs": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.js": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.jsx": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.ts": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.tsx": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.kt": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.kts": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.swift": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.go": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.rs": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    
    # Python
    "*.py": CommentStyle(
        line_markers=["#"],
        block_markers=[],
        docstring_markers=[('"""', '"""'), ("'''", "'''")]
    ),
    
    # Shell / config-like with '#'
    "*.sh": CommentStyle(line_markers=["#"]),
    "*.bash": CommentStyle(line_markers=["#"]),
    "*.zsh": CommentStyle(line_markers=["#"]),
    "Dockerfile": CommentStyle(line_markers=["#"]),
    "Makefile": CommentStyle(line_markers=["#"]),
    "CMakeLists.txt": CommentStyle(line_markers=["#"]),
    "*.cmake": CommentStyle(line_markers=["#"]),
    "*.yaml": CommentStyle(line_markers=["#"]),
    "*.yml": CommentStyle(line_markers=["#"]),
    "*.toml": CommentStyle(line_markers=["#"]),
    "*.cfg": CommentStyle(line_markers=["#", ";"]),
    "*.conf": CommentStyle(line_markers=["#", ";"]),
    "*.ini": CommentStyle(line_markers=[";", "#"]),
    "*.properties": CommentStyle(line_markers=["#", "!"]),
    
    # SQL
    "*.sql": CommentStyle(
        line_markers=["--"],
        block_markers=[("/*", "*/")]
    ),
    
    # HTML / XML / templates
    "*.html": CommentStyle(block_markers=[("<!--", "-->")]),
    "*.htm": CommentStyle(block_markers=[("<!--", "-->")]),
    "*.xml": CommentStyle(block_markers=[("<!--", "-->")]),
    "*.vue": CommentStyle(block_markers=[("<!--", "-->")]),
    "*.svg": CommentStyle(block_markers=[("<!--", "-->")]),
    
    # PHP
    "*.php": CommentStyle(
        line_markers=["//", "#"],
        block_markers=[("/*", "*/")]
    ),
    
    # Ruby
    "*.rb": CommentStyle(
        line_markers=["#"],
        block_markers=[("=begin", "=end")]
    ),
    
    # Lua
    "*.lua": CommentStyle(
        line_markers=["--"],
        block_markers=[("--[[", "]]")]
    ),
    
    # Haskell
    "*.hs": CommentStyle(
        line_markers=["--"],
        block_markers=[("{-", "-}")]
    ),
    
    # R
    "*.r": CommentStyle(line_markers=["#"]),
    "*.R": CommentStyle(line_markers=["#"]),
    
    # Perl
    "*.pl": CommentStyle(line_markers=["#"]),
    "*.pm": CommentStyle(line_markers=["#"]),
    
    # Scala
    "*.scala": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    
    # Groovy
    "*.groovy": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    
    # CSS / SCSS / LESS
    "*.css": CommentStyle(block_markers=[("/*", "*/")]),
    "*.scss": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.sass": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.less": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    
    # Markdown
    "*.md": CommentStyle(block_markers=[("<!--", "-->")]),
    
    # LaTeX
    "*.tex": CommentStyle(line_markers=["%"]),
    
    # MATLAB / Octave
    "*.m": CommentStyle(line_markers=["%"], block_markers=[("%{", "%}")]),
    
    # Fortran
    "*.f": CommentStyle(line_markers=["!", "C", "c"]),
    "*.f90": CommentStyle(line_markers=["!"]),
    "*.f95": CommentStyle(line_markers=["!"]),
    
    # Ada
    "*.ada": CommentStyle(line_markers=["--"]),
    "*.adb": CommentStyle(line_markers=["--"]),
    "*.ads": CommentStyle(line_markers=["--"]),
    
    # Lisp / Scheme / Clojure
    "*.lisp": CommentStyle(line_markers=[";"]),
    "*.cl": CommentStyle(line_markers=[";"]),
    "*.scm": CommentStyle(line_markers=[";"]),
    "*.clj": CommentStyle(line_markers=[";"]),
    "*.cljs": CommentStyle(line_markers=[";"]),
    
    # Erlang
    "*.erl": CommentStyle(line_markers=["%"]),
    
    # Elixir
    "*.ex": CommentStyle(line_markers=["#"]),
    "*.exs": CommentStyle(line_markers=["#"]),
    
    # Nim
    "*.nim": CommentStyle(line_markers=["#"], block_markers=[("#[", "]#")]),
    
    # D
    "*.d": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/"), ("/+", "+/")]),
    
    # Zig
    "*.zig": CommentStyle(line_markers=["//"]),
    
    # V
    "*.v": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    
    # OCaml
    "*.ml": CommentStyle(block_markers=[("(*", "*)")]),
    "*.mli": CommentStyle(block_markers=[("(*", "*)")]),
    
    # F#
    "*.fs": CommentStyle(line_markers=["//"], block_markers=[("(*", "*)")]),
    "*.fsx": CommentStyle(line_markers=["//"], block_markers=[("(*", "*)")]),
    
    # PowerShell
    "*.ps1": CommentStyle(line_markers=["#"], block_markers=[("<#", "#>")]),
    
    # Batch
    "*.bat": CommentStyle(line_markers=["REM", "rem", "::"]),
    "*.cmd": CommentStyle(line_markers=["REM", "rem", "::"]),
    
    # Assembly
    "*.asm": CommentStyle(line_markers=[";", "#"]),
    "*.s": CommentStyle(line_markers=["#", "//", ";"]),
    
    # Verilog / VHDL
    "*.v": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.vh": CommentStyle(line_markers=["//"], block_markers=[("/*", "*/")]),
    "*.vhd": CommentStyle(line_markers=["--"]),
    "*.vhdl": CommentStyle(line_markers=["--"]),
}


def get_comment_style_for_path(path: Path, overrides: dict[str, dict] = None) -> CommentStyle | None:
    """
    Resolve CommentStyle for a given file path.
    
    Resolution order:
    1. Check overrides (highest priority)
    2. Check DEFAULT_COMMENT_STYLES by exact filename match
    3. Check DEFAULT_COMMENT_STYLES by glob pattern match
    
    Args:
        path: Path to the file
        overrides: Custom comment style overrides (pattern -> style dict)
        
    Returns:
        CommentStyle if found, None otherwise
        
    Examples:
        >>> style = get_comment_style_for_path(Path("file.cpp"))
        >>> style.line_markers
        ['//']
        >>> style = get_comment_style_for_path(Path("Makefile"))
        >>> style.line_markers
        ['#']
    """
    if overrides is None:
        overrides = {}
    
    filename = path.name
    
    # Check overrides first
    for pattern, style_dict in overrides.items():
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(str(path), pattern):
            return CommentStyle(**style_dict)
    
    # Check exact filename match
    if filename in DEFAULT_COMMENT_STYLES:
        return DEFAULT_COMMENT_STYLES[filename]
    
    # Check glob patterns
    for pattern, style in DEFAULT_COMMENT_STYLES.items():
        if fnmatch.fnmatch(filename, pattern):
            return style
    
    return None
