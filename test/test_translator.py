# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_l10n.translator import (
    EchoTranslator, InternalSimpleTranslator, ExternalApiTranslator,
    build_translator_from_config, TranslationError
)
from code_l10n.config import CodeL10nConfig
from code_l10n.enums import Language


class TestTranslator(unittest.TestCase):
    
    def test_echo_translator(self):
        """Test that EchoTranslator returns text unchanged."""
        translator = EchoTranslator()
        text = "Hello world"
        result = translator.translate(text, Language.ENGLISH, Language.FRENCH)
        
        self.assertEqual(result, text)
    
    def test_internal_translator_ukrainian(self):
        """Test InternalSimpleTranslator with Ukrainian."""
        translator = InternalSimpleTranslator()
        text = "привіт світ"
        result = translator.translate(text, Language.UKRAINIAN, Language.ENGLISH)
        
        # Should translate known words
        self.assertIn("hello", result.lower())
        self.assertIn("world", result.lower())
    
    def test_internal_translator_unknown_word(self):
        """Test InternalSimpleTranslator with unknown words."""
        translator = InternalSimpleTranslator()
        text = "unknown неизвестный"
        result = translator.translate(text, Language.UKRAINIAN, Language.ENGLISH)
        
        # Unknown words should be preserved
        self.assertIn("unknown", result)
    
    def test_internal_translator_no_dictionary(self):
        """Test InternalSimpleTranslator with unsupported language pair."""
        translator = InternalSimpleTranslator()
        text = "test"
        # French to German has no dictionary
        result = translator.translate(text, Language.FRENCH, Language.GERMAN)
        
        # Should return original text
        self.assertEqual(result, text)
    
    def test_build_echo_translator(self):
        """Test building EchoTranslator from config."""
        config = CodeL10nConfig(
            source_paths=[Path(".")],
            translation_engine="echo"
        )
        translator = build_translator_from_config(config)
        
        self.assertIsInstance(translator, EchoTranslator)
    
    def test_build_internal_translator(self):
        """Test building InternalSimpleTranslator from config."""
        config = CodeL10nConfig(
            source_paths=[Path(".")],
            translation_engine="internal"
        )
        translator = build_translator_from_config(config)
        
        self.assertIsInstance(translator, InternalSimpleTranslator)
    
    def test_build_external_translator(self):
        """Test building ExternalApiTranslator from config."""
        config = CodeL10nConfig(
            source_paths=[Path(".")],
            translation_engine="external",
            translation_engine_options={
                "base_url": "https://api.example.com/translate",
                "api_key": "test_key"
            }
        )
        translator = build_translator_from_config(config)
        
        self.assertIsInstance(translator, ExternalApiTranslator)
    
    def test_build_external_translator_missing_url(self):
        """Test that building ExternalApiTranslator without URL raises error."""
        config = CodeL10nConfig(
            source_paths=[Path(".")],
            translation_engine="external",
            translation_engine_options={}
        )
        
        with self.assertRaises(ValueError):
            build_translator_from_config(config)
    
    def test_build_unknown_engine(self):
        """Test that unknown engine name raises error."""
        config = CodeL10nConfig(
            source_paths=[Path(".")],
            translation_engine="unknown"
        )
        
        with self.assertRaises(ValueError):
            build_translator_from_config(config)


if __name__ == '__main__':
    unittest.main()
