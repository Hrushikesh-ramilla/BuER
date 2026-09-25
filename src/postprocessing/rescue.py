"""Multi-national precision rescue engine for edge-case recovery."""
from typing import Dict, List, Set, Tuple
from ..normalization.clean_pipeline import MultiPassTextCleaner
from ..features.geo_verifier import StructuralAddressComparator
from ..transliteration.indic_aligner import CrossLingualIndicMapper


class MultiNationalRescueEngine:
    """Recovers high-confidence true links across Indic transliterations and missing address edge cases."""

    def __init__(self, transliterator: CrossLingualIndicMapper):
        self.transliterator = transliterator

    def evaluate_indic_pair(
        self,
        s1_name: str,
        s1_addr: str,
        pool_name: str,
        pool_addr: str,
        assigned_pool_ids: Set[str],
        pool_id: str
    ) -> bool:
        """High-precision validation rule for native Indic script candidates."""
        if pool_id in assigned_pool_ids:
            return False

        # Transliterate native script to Latin
        trans_name = self.transliterator.transliterate_string(pool_name)
        trans_addr = self.transliterator.transliterate_string(pool_addr)

        clean_s1_name = MultiPassTextCleaner.clean(s1_name)
        clean_cand_name = MultiPassTextCleaner.clean(trans_name)

        s1_core = MultiPassTextCleaner.extract_core_tokens(clean_s1_name)
        cand_core = MultiPassTextCleaner.extract_core_tokens(clean_cand_name)

        # Require identical core business name
        if not s1_core or s1_core != cand_core:
            return False

        # Numeric compatibility check
        compat = StructuralAddressComparator.evaluate_number_compatibility(s1_addr, trans_addr)
        if compat == 0.0:  # Conflicting house numbers
            return False

        return True
