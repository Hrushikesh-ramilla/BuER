"""Asymmetric Macro F0.5 utility maximization and threshold optimization."""
import numpy as np
from typing import Dict, List, Set, Tuple


class ExpectedUtilityOptimizer:
    """Optimizes decision thresholds and variable-length candidate set selection for Macro F0.5."""

    @staticmethod
    def select_optimal_prefix(candidate_ids: List[str], probabilities: List[float], alpha: float = 1.5) -> List[str]:
        """Selects the prefix of ranked candidates maximizing expected Macro F0.5.
        
        Args:
            candidate_ids: Pool IDs sorted by decreasing probability
            probabilities: Array of predicted match probabilities
            alpha: Weighting multiplier for the value of empty singleton prediction
        """
        probs = np.asarray(probabilities, dtype=np.float64)
        if len(probs) == 0:
            return []
            
        best_k = 0
        # Expected value of predicting empty singleton
        best_score = float(np.prod(1.0 - probs)) * alpha
        expected_gold = float(probs.sum())
        expected_tp = 0.0
        
        for k, p in enumerate(probs, 1):
            expected_tp += p
            score = 1.25 * expected_tp / (0.25 * expected_gold + k)
            if score > best_score:
                best_score = score
                best_k = k
                
        return candidate_ids[:best_k]
