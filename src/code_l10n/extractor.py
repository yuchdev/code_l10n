# -*- coding: utf-8 -*-
"""
Comment and docstring extraction from source files.
"""
import ast
import logging
from pathlib import Path
from typing import List
from .segments import CommentSegment
from .comment_styles import CommentStyle


logger = logging.getLogger(__name__)


class CommentExtractor:
    """
    Extracts comment and docstring segments from source files.
    """
    
    def extract_segments(self, path: Path, style: CommentStyle) -> List[CommentSegment]:
        """
        Read file and extract all comment/docstring segments.
        
        Args:
            path: Path to the source file
            style: CommentStyle defining comment syntax for this file
            
        Returns:
            List of CommentSegment objects
            
        Raises:
            IOError: If file cannot be read
        """
        # Special handling for Python files with docstrings
        if path.suffix == '.py' and style.docstring_markers:
            try:
                return self._extract_python_segments(path, style)
            except Exception as e:
                logger.warning(f"Failed to parse {path} as Python (AST), falling back to text parsing: {e}")
        
        # General text-based extraction for all other files
        return self._extract_text_segments(path, style)
    
    def _extract_python_segments(self, path: Path, style: CommentStyle) -> List[CommentSegment]:
        """
        Extract Python comments and docstrings using AST.
        
        Combines line comments (via text parsing) and docstrings (via AST).
        """
        segments = []
        
        # Get line comments first
        line_segments = self._extract_line_comments(path, style)
        segments.extend(line_segments)
        
        # Get docstrings via AST
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(path))
            docstring_segments = self._extract_docstrings_from_ast(path, tree, source)
            segments.extend(docstring_segments)
        except SyntaxError as e:
            logger.warning(f"Syntax error in {path}: {e}")
        
        # Sort by start_line
        segments.sort(key=lambda s: s.start_line)
        return segments
    
    def _extract_docstrings_from_ast(self, path: Path, tree: ast.AST, source: str) -> List[CommentSegment]:
        """
        Extract docstrings from AST nodes.
        """
        segments = []
        lines = source.splitlines(keepends=True)
        
        for node in ast.walk(tree):
            docstring = ast.get_docstring(node, clean=False)
            if docstring is None:
                continue
            
            # Get the position of the docstring
            # For module, class, and function docstrings, they are the first statement in the body
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.body and isinstance(node.body[0], ast.Expr):
                    expr = node.body[0]
                    if isinstance(expr.value, ast.Constant) and isinstance(expr.value.value, str):
                        start_line = expr.lineno
                        end_line = expr.end_lineno if expr.end_lineno else start_line
                        
                        # Determine the quote style used
                        line_text = lines[start_line - 1] if start_line <= len(lines) else ""
                        indent = len(line_text) - len(line_text.lstrip())
                        indent_str = line_text[:indent]
                        
                        # Detect quote style
                        quote_style = '"""'
                        if "'''" in line_text:
                            quote_style = "'''"
                        elif '"""' in line_text:
                            quote_style = '"""'
                        
                        segments.append(CommentSegment(
                            file_path=path,
                            segment_type="docstring",
                            start_line=start_line,
                            end_line=end_line,
                            indent=indent_str,
                            marker=quote_style,
                            end_marker=quote_style,
                            raw_text=docstring
                        ))
        
        return segments
    
    def _extract_text_segments(self, path: Path, style: CommentStyle) -> List[CommentSegment]:
        """
        Extract comments using text-based parsing.
        
        Handles:
        - Line comments (grouping consecutive lines)
        - Block comments
        """
        segments = []
        
        # Extract line comments
        if style.line_markers:
            segments.extend(self._extract_line_comments(path, style))
        
        # Extract block comments
        if style.block_markers:
            segments.extend(self._extract_block_comments(path, style))
        
        # Sort by start_line
        segments.sort(key=lambda s: s.start_line)
        return segments
    
    def _extract_line_comments(self, path: Path, style: CommentStyle) -> List[CommentSegment]:
        """
        Extract and group consecutive line comments.
        """
        segments = []
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        current_block = None
        current_lines = []
        current_start = None
        
        for line_num, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            
            # Check if this line starts with any of the line markers
            matched_marker = None
            for marker in style.line_markers:
                if stripped.startswith(marker):
                    matched_marker = marker
                    break
            
            if matched_marker:
                # Extract indent and content
                indent = line[:len(line) - len(stripped)]
                content = stripped[len(matched_marker):]
                # Remove single space after marker if present
                if content.startswith(' '):
                    content = content[1:]
                
                # Start new block or continue existing one
                if current_block is None:
                    current_block = matched_marker
                    current_start = line_num
                    current_lines = [content.rstrip('\n\r')]
                    first_indent = indent
                elif current_block == matched_marker:
                    # Continue block
                    current_lines.append(content.rstrip('\n\r'))
                else:
                    # Different marker, save previous block and start new one
                    if current_lines:
                        segments.append(CommentSegment(
                            file_path=path,
                            segment_type="line_block",
                            start_line=current_start,
                            end_line=line_num - 1,
                            indent=first_indent,
                            marker=current_block,
                            end_marker=None,
                            raw_text='\n'.join(current_lines)
                        ))
                    
                    current_block = matched_marker
                    current_start = line_num
                    current_lines = [content.rstrip('\n\r')]
                    first_indent = indent
            else:
                # Not a comment line, save current block if any
                if current_block is not None:
                    segments.append(CommentSegment(
                        file_path=path,
                        segment_type="line_block",
                        start_line=current_start,
                        end_line=line_num - 1,
                        indent=first_indent,
                        marker=current_block,
                        end_marker=None,
                        raw_text='\n'.join(current_lines)
                    ))
                    current_block = None
                    current_lines = []
        
        # Save final block if any
        if current_block is not None:
            segments.append(CommentSegment(
                file_path=path,
                segment_type="line_block",
                start_line=current_start,
                end_line=len(lines),
                indent=first_indent,
                marker=current_block,
                end_marker=None,
                raw_text='\n'.join(current_lines)
            ))
        
        return segments
    
    def _extract_block_comments(self, path: Path, style: CommentStyle) -> List[CommentSegment]:
        """
        Extract block comments (/* ... */, <!-- ... -->, etc.).
        """
        segments = []
        
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            lines = content.splitlines(keepends=True)
        
        for start_marker, end_marker in style.block_markers:
            pos = 0
            while pos < len(content):
                # Find start of block comment
                start_pos = content.find(start_marker, pos)
                if start_pos == -1:
                    break
                
                # Find end of block comment
                end_pos = content.find(end_marker, start_pos + len(start_marker))
                if end_pos == -1:
                    # Unterminated block comment
                    break
                
                # Calculate line numbers
                start_line = content[:start_pos].count('\n') + 1
                end_line = content[:end_pos + len(end_marker)].count('\n') + 1
                
                # Extract indent from the line where block starts
                line_start = content.rfind('\n', 0, start_pos) + 1
                indent = content[line_start:start_pos]
                
                # Extract content between markers
                inner_content = content[start_pos + len(start_marker):end_pos]
                
                # Clean up common formatting (e.g., " * " in C-style block comments)
                raw_text = self._clean_block_comment(inner_content, start_marker)
                
                segments.append(CommentSegment(
                    file_path=path,
                    segment_type="block_comment",
                    start_line=start_line,
                    end_line=end_line,
                    indent=indent,
                    marker=start_marker,
                    end_marker=end_marker,
                    raw_text=raw_text
                ))
                
                pos = end_pos + len(end_marker)
        
        return segments
    
    def _clean_block_comment(self, content: str, start_marker: str) -> str:
        """
        Clean up formatting from block comment content.
        
        For C-style comments, removes leading " * " from each line.
        """
        lines = content.split('\n')
        cleaned = []
        
        for line in lines:
            stripped = line.lstrip()
            # Remove common leading markers like " * " in C-style comments
            if start_marker == "/*" and stripped.startswith('* '):
                cleaned.append(stripped[2:])
            elif start_marker == "/*" and stripped.startswith('*'):
                cleaned.append(stripped[1:].lstrip())
            else:
                cleaned.append(line.strip())
        
        # Join and strip outer whitespace
        result = '\n'.join(cleaned).strip()
        return result
