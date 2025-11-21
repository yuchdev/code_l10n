# -*- coding: utf-8 -*-
"""
Language detection for text fragments.
"""
import re
import logging
from dataclasses import dataclass
from typing import Sequence
from .enums import Language


logger = logging.getLogger(__name__)


@dataclass
class DetectedFragment:
    """
    A text fragment with detected language.
    
    Attributes:
        text: The fragment text
        language: Detected language (None if unknown)
        start_offset: Start position in original text
        end_offset: End position in original text
    """
    text: str
    language: Language | None
    start_offset: int
    end_offset: int


class LanguageDetector:
    """
    Detects language of text fragments using heuristics.
    
    This is a simple implementation based on character sets and patterns.
    For production use, consider integrating a library like langdetect or langid.
    """
    
    # Character ranges for different scripts
    CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]')
    LATIN_PATTERN = re.compile(r'[a-zA-Z]')
    CHINESE_PATTERN = re.compile(r'[\u4E00-\u9FFF]')
    JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')
    KOREAN_PATTERN = re.compile(r'[\uAC00-\uD7AF]')
    ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')
    HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]')
    GREEK_PATTERN = re.compile(r'[\u0370-\u03FF]')
    
    # Ukrainian-specific words and patterns
    UKRAINIAN_WORDS = {'який', 'яка', 'яке', 'якi', 'що', 'цей', 'цих', 'ці', 'він', 'вона', 'воно', 'вони'}
    RUSSIAN_WORDS = {'который', 'которая', 'которое', 'которые', 'что', 'этот', 'эти', 'он', 'она', 'оно', 'они'}
    
    def detect_fragments(self, text: str) -> Sequence[DetectedFragment]:
        """
        Split text into sentences/phrases and detect language for each.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of DetectedFragment objects
        """
        if not text or not text.strip():
            return []
        
        # Simple sentence splitting by common delimiters
        fragments = self._split_sentences(text)
        
        detected = []
        offset = 0
        
        for fragment_text in fragments:
            # Find actual position in original text
            start = text.find(fragment_text, offset)
            if start == -1:
                # Fallback if exact match not found
                start = offset
            end = start + len(fragment_text)
            offset = end
            
            # Detect language
            lang = self._detect_language(fragment_text)
            
            detected.append(DetectedFragment(
                text=fragment_text,
                language=lang,
                start_offset=start,
                end_offset=end
            ))
        
        return detected
    
    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences/phrases.
        
        Uses simple heuristics: split on '.', '!', '?', ';' followed by space or newline.
        """
        # Split on sentence endings
        pattern = r'([.!?;]+[\s\n]+)'
        parts = re.split(pattern, text)
        
        sentences = []
        current = ""
        
        for part in parts:
            current += part
            if re.match(pattern, part):
                # This is a separator, keep with previous text
                if current.strip():
                    sentences.append(current.rstrip())
                current = ""
        
        # Add any remaining text
        if current.strip():
            sentences.append(current.rstrip())
        
        # If no sentences found, treat whole text as one fragment
        if not sentences:
            return [text]
        
        return sentences
    
    def _detect_language(self, text: str) -> Language | None:
        """
        Detect language of a text fragment using character-based heuristics.
        """
        if not text or len(text.strip()) < 3:
            return None
        
        text_lower = text.lower()
        
        # Count characters from different scripts
        cyrillic_count = len(self.CYRILLIC_PATTERN.findall(text))
        latin_count = len(self.LATIN_PATTERN.findall(text))
        chinese_count = len(self.CHINESE_PATTERN.findall(text))
        japanese_count = len(self.JAPANESE_PATTERN.findall(text))
        korean_count = len(self.KOREAN_PATTERN.findall(text))
        arabic_count = len(self.ARABIC_PATTERN.findall(text))
        hebrew_count = len(self.HEBREW_PATTERN.findall(text))
        greek_count = len(self.GREEK_PATTERN.findall(text))
        
        # Determine dominant script
        total_chars = cyrillic_count + latin_count + chinese_count + japanese_count + korean_count + arabic_count + hebrew_count + greek_count
        
        if total_chars == 0:
            # No alphabetic characters
            return None
        
        # Check for specific scripts
        if chinese_count > total_chars * 0.3:
            return Language.CHINESE
        
        if japanese_count > total_chars * 0.2:
            return Language.JAPANESE
        
        if korean_count > total_chars * 0.3:
            return Language.KOREAN
        
        if arabic_count > total_chars * 0.3:
            return Language.ARABIC
        
        if hebrew_count > total_chars * 0.3:
            return Language.HEBREW
        
        if greek_count > total_chars * 0.3:
            return Language.GREEK
        
        # Distinguish Cyrillic languages (Ukrainian vs Russian)
        if cyrillic_count > total_chars * 0.3:
            # Check for Ukrainian-specific words
            words = set(text_lower.split())
            ukrainian_matches = len(words & self.UKRAINIAN_WORDS)
            russian_matches = len(words & self.RUSSIAN_WORDS)
            
            if ukrainian_matches > russian_matches:
                return Language.UKRAINIAN
            elif russian_matches > ukrainian_matches:
                return Language.RUSSIAN
            else:
                # Default to Ukrainian if we can't distinguish
                return Language.UKRAINIAN
        
        # Default to English for Latin script
        if latin_count > total_chars * 0.3:
            return Language.ENGLISH
        
        return None
