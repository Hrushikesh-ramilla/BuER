"""Vectorized and lexical string similarity feature extraction."""
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein, JaroWinkler
from typing import Dict, List, Tuple


class VectorizedStringSimilarity:
    """Computes multidimensional fuzzy string similarity features across names and addresses."""

    @staticmethod
    def compute_pair_features(name1: str, name2: str, addr1: str, addr2: str) -> Dict[str, float]:
        """Compute complete 12-dimensional string similarity feature vector."""
        # Name metrics
        name_ratio = fuzz.ratio(name1, name2) / 100.0
        name_partial = fuzz.partial_ratio(name1, name2) / 100.0
        name_token_sort = fuzz.token_sort_ratio(name1, name2) / 100.0
        name_token_set = fuzz.token_set_ratio(name1, name2) / 100.0
        name_jw = JaroWinkler.similarity(name1, name2)
        
        # Address metrics
        addr_ratio = fuzz.ratio(addr1, addr2) / 100.0 if addr1 and addr2 else 0.0
        addr_partial = fuzz.partial_ratio(addr1, addr2) / 100.0 if addr1 and addr2 else 0.0
        addr_token_sort = fuzz.token_sort_ratio(addr1, addr2) / 100.0 if addr1 and addr2 else 0.0
        addr_token_set = fuzz.token_set_ratio(addr1, addr2) / 100.0 if addr1 and addr2 else 0.0
        addr_jw = JaroWinkler.similarity(addr1, addr2) if addr1 and addr2 else 0.0
        
        # Token overlap metrics
        t1, t2 = set(name1.split()), set(name2.split())
        name_jaccard = len(t1 & t2) / max(len(t1 | t2), 1)
        
        a1, a2 = set(addr1.split()), set(addr2.split())
        addr_jaccard = len(a1 & a2) / max(len(a1 | a2), 1) if (a1 or a2) else 0.0
        
        return {
            "name_ratio": name_ratio,
            "name_partial": name_partial,
            "name_token_sort": name_token_sort,
            "name_token_set": name_token_set,
            "name_jw": name_jw,
            "name_jaccard": name_jaccard,
            "addr_ratio": addr_ratio,
            "addr_partial": addr_partial,
            "addr_token_sort": addr_token_sort,
            "addr_token_set": addr_token_set,
            "addr_jw": addr_jw,
            "addr_jaccard": addr_jaccard,
        }
