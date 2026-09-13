"""
Jaccard Analyzer for H-M3: Top-k influential example disagreement.
Implements the gate metric: min(pairwise Jaccard) < 0.70.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Any

from config import H3Config


class JaccardAnalyzer:
    """Analyzes top-k influential example disagreement between attribution methods."""

    def __init__(self, cfg: H3Config):
        self.cfg = cfg

    def get_topk_indices(self, scores: np.ndarray, k: int = 50) -> List[Set[int]]:
        """
        Extract top-k influential training indices for each test sample.

        Args:
            scores: [n_test, n_train] attribution scores
            k: Number of top influential examples

        Returns:
            List of sets, one per test sample, containing top-k train indices
        """
        n_test = scores.shape[0]
        topk_sets = []
        for i in range(n_test):
            topk_idx = np.argsort(-scores[i])[:k]  # descending order
            topk_sets.append(set(topk_idx.tolist()))
        return topk_sets

    def compute_pairwise_jaccard(
        self,
        scores_dict: Dict[str, np.ndarray],
        k: int = 50,
    ) -> Tuple[np.ndarray, float, float]:
        """
        Compute pairwise Jaccard similarity between methods.

        Args:
            scores_dict: {method_name: [n_test, n_train] scores}
            k: Number of top-k examples to consider

        Returns:
            jaccard_matrix: [n_methods, n_methods] mean Jaccard per test sample
            min_jaccard: Minimum off-diagonal Jaccard (gate metric)
            mean_jaccard: Mean off-diagonal Jaccard
        """
        methods = list(scores_dict.keys())
        n_methods = len(methods)

        # Get top-k sets for each method
        topk_sets = {m: self.get_topk_indices(scores_dict[m], k) for m in methods}

        n_test = scores_dict[methods[0]].shape[0]
        jaccard_matrix = np.zeros((n_methods, n_methods))

        for i, m1 in enumerate(methods):
            for j, m2 in enumerate(methods):
                per_test_jaccard = []
                for t in range(n_test):
                    set1 = topk_sets[m1][t]
                    set2 = topk_sets[m2][t]
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    jac = intersection / union if union > 0 else 1.0
                    per_test_jaccard.append(jac)
                jaccard_matrix[i, j] = np.mean(per_test_jaccard)

        # Min/mean Jaccard (excluding diagonal)
        mask = ~np.eye(n_methods, dtype=bool)
        off_diagonal = jaccard_matrix[mask]
        min_jaccard = off_diagonal.min()
        mean_jaccard = off_diagonal.mean()

        return jaccard_matrix, min_jaccard, mean_jaccard

    def compute_jaccard_by_budget(
        self,
        results_dict: Dict[int, Dict[str, np.ndarray]],
        budgets: List[int],
        k: int = 50,
    ) -> Dict[int, Dict[str, Any]]:
        """
        Compute Jaccard analysis for each budget level.

        Args:
            results_dict: {budget: {method: [n_test, n_train] scores}}
            budgets: List of compute budgets
            k: Number of top-k examples

        Returns:
            {budget: {'matrix': ndarray[n_m, n_m], 'min': float, 'mean': float}}
        """
        jaccard_by_budget = {}
        for budget in budgets:
            if budget in results_dict:
                matrix, min_jac, mean_jac = self.compute_pairwise_jaccard(
                    results_dict[budget], k
                )
                jaccard_by_budget[budget] = {
                    'matrix': matrix,
                    'min': min_jac,
                    'mean': mean_jac,
                }
        return jaccard_by_budget

    def check_gate(self, min_jaccard: float) -> bool:
        """
        Check if the gate condition is satisfied.

        Returns True if min_jaccard < jaccard_threshold (0.70).
        """
        return min_jaccard < self.cfg.jaccard_threshold

    def get_method_pair_with_min_jaccard(
        self,
        jaccard_matrix: np.ndarray,
        methods: List[str],
    ) -> Tuple[str, str, float]:
        """Find the method pair with minimum Jaccard similarity."""
        n_methods = len(methods)
        min_val = float('inf')
        min_pair = (methods[0], methods[1])

        for i in range(n_methods):
            for j in range(i + 1, n_methods):
                if jaccard_matrix[i, j] < min_val:
                    min_val = jaccard_matrix[i, j]
                    min_pair = (methods[i], methods[j])

        return min_pair[0], min_pair[1], min_val
