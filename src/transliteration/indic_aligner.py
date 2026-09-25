"""Cross-lingual Indic script alignment engine for native-to-Latin token mapping."""
import os
import json
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

_EDGE_PUNCT = re.compile(r"^[^\w]+|[^\w]+$", re.UNICODE)
_ZERO_WIDTH = re.compile(r"[\u200B-\u200D\uFEFF]")


class CrossLingualIndicMapper:
    """Bridges non-Latin Indic scripts (Tamil, Telugu, Bengali, Devanagari, etc.) into Latin forms."""

    def __init__(self, dictionary_path: Optional[str] = None):
        default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indic_dictionary.json")
        self.dict_path = dictionary_path or default_path
        self._table: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        """Load the token translation table from disk."""
        if os.path.exists(self.dict_path):
            with open(self.dict_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._table = data.get("dictionary", data)

    def is_loaded(self) -> bool:
        return len(self._table) > 0

    @property
    def token_count(self) -> int:
        return len(self._table)

    def transliterate_string(self, text: str) -> str:
        """Transliterate text by substituting known native Indic tokens with Latin equivalents."""
        if not text or text.isascii():
            return text
        
        output_words = []
        for word in text.split():
            if word.isascii():
                output_words.append(word)
                continue
            
            clean_word = _EDGE_PUNCT.sub("", _ZERO_WIDTH.sub("", unicodedata.normalize("NFC", word)).lower())
            mapped = self._table.get(clean_word)
            if mapped:
                output_words.append(mapped)
            else:
                # Apply fallback phonetic transliterator if available
                try:
                    from unidecode import unidecode
                    output_words.append(unidecode(word))
                except ImportError:
                    output_words.append(word)
                    
        return " ".join(output_words)
