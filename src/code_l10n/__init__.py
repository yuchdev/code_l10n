# -*- coding: utf-8 -*-
"""
code_l10n - Comment and docstring localization library.

Scans source code for comments and docstrings, detects language,
and translates them to a target language.
"""

__version__ = "0.1.0"

from .config import CodeL10nConfig
from .enums import Language, normalize_locale
from .pipeline import CodeL10nPipeline
from .translator import Translator, EchoTranslator, InternalSimpleTranslator, ExternalApiTranslator
from .segments import CommentSegment
from .comment_styles import CommentStyle, get_comment_style_for_path

__all__ = [
    'CodeL10nConfig',
    'Language',
    'normalize_locale',
    'CodeL10nPipeline',
    'Translator',
    'EchoTranslator',
    'InternalSimpleTranslator',
    'ExternalApiTranslator',
    'CommentSegment',
    'CommentStyle',
    'get_comment_style_for_path',
]
