# -*- coding: utf-8 -*-
"""
Enumerations and helpers for the code_l10n library.
"""
from enum import Enum


class Language(Enum):
    """Supported languages for detection and translation."""
    ENGLISH = "en"
    UKRAINIAN = "uk"
    RUSSIAN = "ru"
    POLISH = "pl"
    FRENCH = "fr"
    GERMAN = "de"
    CZECH = "cs"
    SPANISH = "es"
    VIETNAMESE = "vi"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    GREEK = "el"
    TURKISH = "tr"
    ARABIC = "ar"
    HEBREW = "he"
    HINDI = "hi"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


def normalize_locale(locale_or_charset: str) -> Language:
    """
    Map locale ('uk-UA') or charset-ish ('uk') to Language enum.
    
    Args:
        locale_or_charset: A locale string like 'uk-UA', 'en-US', or just 'uk', 'en'
        
    Returns:
        Language enum corresponding to the input
        
    Raises:
        ValueError: If the locale/charset is not recognized
        
    Examples:
        >>> normalize_locale('uk-UA')
        Language.UKRAINIAN
        >>> normalize_locale('uk')
        Language.UKRAINIAN
        >>> normalize_locale('en')
        Language.ENGLISH
    """
    # Extract the language code (first part before '-')
    lang_code = locale_or_charset.lower().split('-')[0].strip()
    
    # Try to find matching Language enum by value
    for language in Language:
        if language.value == lang_code:
            return language
    
    # If not found, raise an error
    raise ValueError(
        f"Unknown locale or charset: '{locale_or_charset}'. "
        f"Supported language codes: {', '.join(lang.value for lang in Language)}"
    )
