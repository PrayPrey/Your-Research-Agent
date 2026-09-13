"""Internal consistency analysis module.

This module implements Cronbach's alpha calculation and correlation analysis.
"""

import numpy as np
from typing import Dict


class InternalConsistencyAnalyzer:
    """Analyzer for internal consistency of linguistic markers."""

    def cronbachs_alpha(self, item_scores: np.ndarray) -> float:
        """Compute Cronbach's alpha.

        Args:
            item_scores: [N, k] array - N samples, k items (markers)

        Returns:
            Cronbach's alpha coefficient
        """
        k = item_scores.shape[1]  # Number of items

        if k < 2:
            raise ValueError("Cronbach's alpha requires at least 2 items")

        # Compute item variances
        item_variances = np.var(item_scores, axis=0, ddof=1)

        # Compute total variance (sum of item scores)
        total_scores = np.sum(item_scores, axis=1)
        total_variance = np.var(total_scores, ddof=1)

        if total_variance == 0:
            return 0.0

        # Cronbach's alpha formula
        alpha = (k / (k - 1)) * (1 - np.sum(item_variances) / total_variance)

        return float(alpha)

    def compute_correlation_matrix(self, features: np.ndarray) -> np.ndarray:
        """Compute correlation matrix between markers.

        Args:
            features: [N, k] array - N samples, k markers

        Returns:
            [k, k] correlation matrix
        """
        corr_matrix = np.corrcoef(features, rowvar=False)
        return corr_matrix

    def check_secondary_gate(
        self, alpha: float, threshold: float = 0.7
    ) -> bool:
        """Check secondary gate: alpha > 0.7.

        Args:
            alpha: Cronbach's alpha coefficient
            threshold: Alpha threshold

        Returns:
            True if secondary gate passed
        """
        return alpha > threshold

    def compute_statistics(
        self, difference_matrix: np.ndarray
    ) -> Dict[str, float]:
        """Compute all internal consistency statistics.

        Args:
            difference_matrix: [N, 3] array of difference scores

        Returns:
            Dictionary with alpha and correlation matrix
        """
        alpha = self.cronbachs_alpha(difference_matrix)
        corr_matrix = self.compute_correlation_matrix(difference_matrix)

        return {
            'cronbach_alpha': alpha,
            'correlation_matrix': corr_matrix.tolist(),
            'mean_correlation': float(np.mean(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        }
