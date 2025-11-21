# -*- coding: utf-8 -*-
"""
Post-processing of translated comment segments.
"""
import logging
from .segments import CommentSegment
from .comment_styles import CommentStyle


logger = logging.getLogger(__name__)


class PostProcessor:
    """
    Applies post-processing transformations to translated comment segments.
    """
    
    def __init__(self, profile: str = "default"):
        """
        Initialize post-processor with a profile.
        
        Args:
            profile: Name of post-processing profile
                     ("default", "prefer_block_comments", "flatten_single_line")
        """
        self.profile = profile
    
    def apply(self, original: CommentSegment, translated_inner_text: str, style: CommentStyle) -> str:
        """
        Apply post-processing to generate final comment text.
        
        Args:
            original: Original comment segment
            translated_inner_text: Translated text content (without markers)
            style: CommentStyle for this file type
            
        Returns:
            Final text with markers and indentation to replace the original segment
        """
        if self.profile == "prefer_block_comments":
            return self._apply_prefer_block_comments(original, translated_inner_text, style)
        elif self.profile == "flatten_single_line":
            return self._apply_flatten_single_line(original, translated_inner_text, style)
        else:
            # Default: preserve original structure
            return self._apply_default(original, translated_inner_text)
    
    def _apply_default(self, original: CommentSegment, translated_inner_text: str) -> str:
        """
        Default profile: preserve original comment structure.
        """
        if original.segment_type == "line_block":
            return render_line_block(original.indent, original.marker, translated_inner_text)
        elif original.segment_type == "block_comment":
            return render_block_comment(original.indent, original.marker, original.end_marker, translated_inner_text)
        elif original.segment_type == "docstring":
            return render_docstring(original.indent, original.marker, translated_inner_text)
        else:
            # Fallback
            return translated_inner_text
    
    def _apply_prefer_block_comments(self, original: CommentSegment, translated_inner_text: str, style: CommentStyle) -> str:
        """
        Convert multi-line line-comment blocks to block comments if possible.
        """
        # Only convert line_block segments with multiple lines
        if original.segment_type == "line_block" and '\n' in translated_inner_text:
            # Check if style supports block comments
            if style.block_markers:
                start_marker, end_marker = style.block_markers[0]
                return render_block_comment(original.indent, start_marker, end_marker, translated_inner_text)
        
        # Otherwise use default
        return self._apply_default(original, translated_inner_text)
    
    def _apply_flatten_single_line(self, original: CommentSegment, translated_inner_text: str, style: CommentStyle) -> str:
        """
        Convert to single-line comment if text has no newlines.
        """
        if '\n' not in translated_inner_text:
            # Try to use line comment if available
            if style.line_markers:
                marker = style.line_markers[0]
                return f"{original.indent}{marker} {translated_inner_text}\n"
            # Otherwise try block comment
            elif style.block_markers:
                start_marker, end_marker = style.block_markers[0]
                return f"{original.indent}{start_marker} {translated_inner_text} {end_marker}\n"
        
        # Otherwise use default
        return self._apply_default(original, translated_inner_text)


def render_line_block(indent: str, marker: str, inner_text: str) -> str:
    """
    Render text as a line-comment block.
    
    Args:
        indent: Leading whitespace
        marker: Comment marker (e.g., "//", "#")
        inner_text: Text content
        
    Returns:
        Formatted comment text
    """
    lines = inner_text.split('\n')
    result_lines = []
    
    for line in lines:
        result_lines.append(f"{indent}{marker} {line}")
    
    return '\n'.join(result_lines) + '\n'


def render_block_comment(indent: str, start: str, end: str, inner_text: str) -> str:
    """
    Render text as a block comment.
    
    Args:
        indent: Leading whitespace
        start: Start marker (e.g., "/*")
        end: End marker (e.g., "*/")
        inner_text: Text content
        
    Returns:
        Formatted comment text
    """
    lines = inner_text.split('\n')
    
    if len(lines) == 1:
        # Single line block comment
        return f"{indent}{start} {inner_text} {end}\n"
    else:
        # Multi-line block comment with " * " prefix (C-style)
        result_lines = [f"{indent}{start}"]
        for line in lines:
            result_lines.append(f"{indent} * {line}")
        result_lines.append(f"{indent} {end}")
        return '\n'.join(result_lines) + '\n'


def render_docstring(indent: str, quotes: str, inner_text: str) -> str:
    """
    Render text as a docstring.
    
    Args:
        indent: Leading whitespace
        quotes: Quote style ('"""' or "'''")
        inner_text: Text content
        
    Returns:
        Formatted docstring text
    """
    lines = inner_text.split('\n')
    
    if len(lines) == 1:
        # Single line docstring
        return f"{indent}{quotes}{inner_text}{quotes}\n"
    else:
        # Multi-line docstring
        result_lines = [f"{indent}{quotes}"]
        for line in lines:
            result_lines.append(f"{indent}{line}")
        result_lines.append(f"{indent}{quotes}")
        return '\n'.join(result_lines) + '\n'
