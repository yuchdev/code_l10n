# -*- coding: utf-8 -*-
"""
Translation interfaces and implementations.
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict
import urllib.request
import urllib.error
import json
from .enums import Language
from .config import CodeL10nConfig


logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Raised when translation fails."""
    pass


class Translator(ABC):
    """
    Abstract base class for translation engines.
    """
    
    @abstractmethod
    def translate(self, text: str, source: Language, target: Language) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source: Source language
            target: Target language
            
        Returns:
            Translated text
            
        Raises:
            TranslationError: If translation fails
        """
        pass


class EchoTranslator(Translator):
    """
    Simple translator that returns text unchanged.
    Useful for testing and development.
    """
    
    def translate(self, text: str, source: Language, target: Language) -> str:
        """Return the text unchanged."""
        return text


class InternalSimpleTranslator(Translator):
    """
    Simple dictionary-based translator for testing.
    
    Contains a small set of common words for demonstration.
    """
    
    # Simple dictionary: (source_lang, target_lang) -> {word: translation}
    DICTIONARIES = {
        (Language.UKRAINIAN, Language.ENGLISH): {
            'привіт': 'hello',
            'світ': 'world',
            'функція': 'function',
            'клас': 'class',
            'метод': 'method',
            'змінна': 'variable',
            'коментар': 'comment',
            'код': 'code',
            'файл': 'file',
            'програма': 'program',
            'помилка': 'error',
            'тест': 'test',
        },
        (Language.RUSSIAN, Language.ENGLISH): {
            'привет': 'hello',
            'мир': 'world',
            'функция': 'function',
            'класс': 'class',
            'метод': 'method',
            'переменная': 'variable',
            'комментарий': 'comment',
            'код': 'code',
            'файл': 'file',
            'программа': 'program',
            'ошибка': 'error',
            'тест': 'test',
        },
    }
    
    def translate(self, text: str, source: Language, target: Language) -> str:
        """
        Translate using simple word substitution.
        """
        dictionary = self.DICTIONARIES.get((source, target), {})
        
        if not dictionary:
            logger.warning(f"No dictionary for {source.value} -> {target.value}")
            return text
        
        # Simple word-by-word translation
        words = text.split()
        translated = []
        
        for word in words:
            # Try lowercase match
            lower_word = word.lower()
            if lower_word in dictionary:
                translated.append(dictionary[lower_word])
            else:
                translated.append(word)
        
        return ' '.join(translated)


class ExternalApiTranslator(Translator):
    """
    Generic wrapper for HTTP-based translation APIs.
    
    Requires configuration of API endpoint and authentication.
    """
    
    def __init__(self, base_url: str, api_key: str = None, timeout: float = 10.0):
        """
        Initialize external API translator.
        
        Args:
            base_url: API endpoint URL
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
    
    def translate(self, text: str, source: Language, target: Language) -> str:
        """
        Translate text via external API.
        
        This is a generic implementation that may need to be customized
        for specific translation services.
        """
        # Prepare request
        data = {
            'text': text,
            'source': source.value,
            'target': target.value,
        }
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            req = urllib.request.Request(
                self.base_url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Try common response formats
                if 'translation' in result:
                    return result['translation']
                elif 'translated_text' in result:
                    return result['translated_text']
                elif 'result' in result:
                    return result['result']
                else:
                    raise TranslationError(f"Unexpected response format: {result}")
        
        except urllib.error.HTTPError as e:
            raise TranslationError(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise TranslationError(f"URL error: {e.reason}")
        except json.JSONDecodeError as e:
            raise TranslationError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise TranslationError(f"Translation failed: {e}")


def build_translator_from_config(config: CodeL10nConfig) -> Translator:
    """
    Build a Translator instance from configuration.
    
    Args:
        config: CodeL10nConfig with translation engine settings
        
    Returns:
        Configured Translator instance
        
    Raises:
        ValueError: If engine name is unknown
    """
    engine = config.translation_engine.lower()
    options = config.translation_engine_options
    
    if engine == "echo":
        return EchoTranslator()
    
    elif engine == "internal":
        return InternalSimpleTranslator()
    
    elif engine == "external":
        # Extract options for external API
        base_url = options.get('base_url')
        if not base_url:
            raise ValueError("External translator requires 'base_url' in translation_engine_options")
        
        api_key = None
        api_key_env = options.get('api_key_env')
        if api_key_env:
            api_key = os.environ.get(api_key_env)
            if not api_key:
                logger.warning(f"Environment variable {api_key_env} not set for API key")
        elif 'api_key' in options:
            api_key = options['api_key']
        
        timeout = options.get('timeout', 10.0)
        
        return ExternalApiTranslator(base_url, api_key, timeout)
    
    else:
        raise ValueError(f"Unknown translation engine: {engine}. Use 'echo', 'internal', or 'external'")
