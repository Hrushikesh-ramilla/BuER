"""Country-partitioned multi-channel candidate blocker."""
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class DualInvertedIndexBlocker:
    """Scalable candidate generation using token inverted index with frequency thresholds."""

    def __init__(self, max_postings_per_token: int = 1500, min_token_len: int = 3):
        self.max_postings = max_postings_per_token
        self.min_len = min_token_len
        self.index: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    def index_pool_records(self, pool_records: List[Tuple[str, str, str, str]]) -> None:
        """Build postings lists per country partition.
        
        Args:
            pool_records: List of (entity_id, norm_name, norm_addr, country)
        """
        for pid, name, addr, country in pool_records:
            country_norm = country.strip().lower()
            name_tokens = {t for t in name.split() if len(t) >= self.min_len}
            for tok in name_tokens:
                self.index[country_norm][tok].append(pid)

    def retrieve_candidates(self, s1_id: str, norm_name: str, norm_addr: str, country: str, max_candidates: int = 40) -> List[str]:
        """Query the inverted index for matching candidate IDs."""
        country_norm = country.strip().lower()
        postings = self.index.get(country_norm, {})
        if not postings:
            return []

        counts: Dict[str, int] = defaultdict(int)
        query_tokens = [t for t in norm_name.split() if len(t) >= self.min_len]

        for tok in query_tokens:
            posting_list = postings.get(tok, [])
            if 0 < len(posting_list) <= self.max_postings:
                for pid in posting_list:
                    counts[pid] += 1

        if not counts:
            return []

        # Sort by posting overlap count descending
        sorted_cands = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [pid for pid, _ in sorted_cands[:max_candidates]]
