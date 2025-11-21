# -*- coding: utf-8 -*-
"""
Data structures for representing comment and docstring segments.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


CommentSegmentType = Literal["line_block", "block_comment", "docstring"]


@dataclass
class CommentSegment:
    """
    Represents a contiguous comment or docstring block extracted from a file.
    
    Attributes:
        file_path: Path to the source file
        segment_type: Type of comment segment
        start_line: Starting line number (1-based, inclusive)
        end_line: Ending line number (1-based, inclusive)
        indent: Leading whitespace from the first line
        marker: Comment marker (e.g., "#", "//", "/*") or docstring quote
        end_marker: End marker for block comments/docstrings (e.g., "*/" or triple quotes)
        raw_text: Inner text content without markers
    """
    file_path: Path
    segment_type: CommentSegmentType
    start_line: int
    end_line: int
    indent: str
    marker: str | None
    end_marker: str | None
    raw_text: str
