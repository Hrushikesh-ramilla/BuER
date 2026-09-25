"""Global bipartite matching with strict 1-to-1 mutual exclusivity enforcement."""
from typing import Dict, List, Set, Tuple


class BipartiteMutualExclusivitySolver:
    """Enforces the 100% ground-truth invariant: each pool record belongs to at most one S1."""

    @staticmethod
    def resolve_conflicts(scored_candidates: List[Tuple[str, str, float]]) -> List[Tuple[str, str, float]]:
        """Greedy resolution: assign each pool_id to its highest-scoring S1.
        
        Args:
            scored_candidates: List of (s1_id, pool_id, score)
        Returns:
            Disjoint candidate list where no pool_id appears twice.
        """
        # Sort descending by prediction score
        sorted_pairs = sorted(scored_candidates, key=lambda x: x[2], reverse=True)
        assigned_pool_ids: Set[str] = set()
        exclusive_pairs: List[Tuple[str, str, float]] = []

        for sid, pid, score in sorted_pairs:
            if pid not in assigned_pool_ids:
                assigned_pool_ids.add(pid)
                exclusive_pairs.append((sid, pid, score))

        return exclusive_pairs
