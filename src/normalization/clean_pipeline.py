"""High-performance Unicode and token normalization pipeline."""
import re
import unicodedata
from typing import Optional, Set, Tuple
from .entity_lexicon import ALL_CORPORATE_FILLER, ADDRESS_EXPANSIONS

_STRIP_ZERO_WIDTH = re.compile(r"[\u200B-\u200D\uFEFF]")
_NON_ALPHANUM = re.compile(r"[^a-z0-9\s]")
_MULTI_SPACE = re.compile(r"\s+")
_PINCODE_PATTERN = re.compile(r"\b([1-9]\d{4,5})\b")
_HOUSE_NUM_PATTERN = re.compile(r"^(\d+[\w\-/]*)\b")


class MultiPassTextCleaner:
    """Production-grade string preprocessor for business entity resolution."""

    @staticmethod
    def clean(text: Optional[str]) -> str:
        """Decompose Unicode diacritics, remove punctuation, and lowercase."""
        if not text:
            return ""
        # Quick ASCII check bypass
        text_str = str(text)
        if text_str.isascii():
            cleaned = _NON_ALPHANUM.sub(" ", text_str.lower())
            return _MULTI_SPACE.sub(" ", cleaned).strip()
            
        norm = unicodedata.normalize("NFKD", text_str.lower())
        stripped = "".join(c for c in norm if not unicodedata.combining(c))
        clean_text = _STRIP_ZERO_WIDTH.sub("", stripped)
        alphanumeric = _NON_ALPHANUM.sub(" ", clean_text)
        return _MULTI_SPACE.sub(" ", alphanumeric).strip()

    @staticmethod
    def extract_core_tokens(normalized_name: str, legal_lexicon: Optional[Set[str]] = None) -> Set[str]:
        """Strip corporate designations and return core distinguishing name tokens."""
        filler = legal_lexicon if legal_lexicon is not None else ALL_CORPORATE_FILLER
        tokens = set(normalized_name.split())
        return tokens - filler

    @staticmethod
    def extract_address_components(address_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract house number and postal code from normalized address."""
        if not address_str:
            return None, None
        
        # House number from start
        house_m = _HOUSE_NUM_PATTERN.search(address_str.strip())
        h_num = house_m.group(1) if house_m else None
        
        # Postal code
        pin_m = _PINCODE_PATTERN.search(address_str)
        p_code = pin_m.group(1) if pin_m else None
        
        return h_num, p_code

    @classmethod
    def expand_address_terms(cls, address: str) -> str:
        """Standardize common street type and directional abbreviations."""
        words = address.split()
        expanded = [ADDRESS_EXPANSIONS.get(w, w) for w in words]
        return " ".join(expanded)
