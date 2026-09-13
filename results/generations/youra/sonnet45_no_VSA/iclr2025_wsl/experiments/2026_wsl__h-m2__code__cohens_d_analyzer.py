"""
Cohen's d Effect Size Analyzer for H-M2

Computes Cohen's d effect size between CNN and Transformer parameter-mass ratio distributions.
Validates inter-family separation criterion (d > 1.0).
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple


class CohensDAnalyzer:
    """Analyzer for Cohen's d effect size between architecture families."""

    def __init__(self, threshold: float = 1.0):
        """
        Initialize Cohen's d analyzer.

        Args:
            threshold: Minimum Cohen's d for inter-family separation (default: 1.0)
        """
        self.threshold = threshold

    def compute_cohens_d(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """
        Compute Cohen's d effect size between two groups.

        Args:
            group1: R values for group 1 (e.g., CNNs)
            group2: R values for group 2 (e.g., Transformers)

        Returns:
            Cohen's d effect size (absolute value)
        """
        n1, n2 = len(group1), len(group2)

        if n1 < 2 or n2 < 2:
            return 0.0

        mean1, mean2 = np.mean(group1), np.mean(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

        # Pooled standard deviation
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        pooled_std = np.sqrt(pooled_var)

        if pooled_std == 0:
            return 0.0

        # Cohen's d (absolute value for magnitude)
        d = abs(mean1 - mean2) / pooled_std

        return d

    def perform_ttest(self, group1: np.ndarray, group2: np.ndarray) -> Tuple[float, float]:
        """
        Perform independent t-test between two groups.

        Args:
            group1: R values for group 1
            group2: R values for group 2

        Returns:
            (t_statistic, p_value)
        """
        if len(group1) < 2 or len(group2) < 2:
            return (0.0, 1.0)

        t_stat, p_value = stats.ttest_ind(group1, group2)
        return (t_stat, p_value)

    def analyze(self, cnn_R: np.ndarray, transformer_R: np.ndarray) -> Dict:
        """
        Perform full Cohen's d analysis.

        Args:
            cnn_R: Parameter-mass ratio values for CNNs
            transformer_R: Parameter-mass ratio values for Transformers

        Returns:
            {
                'cohens_d': float,
                't_statistic': float,
                'p_value': float,
                'cnn_mean': float,
                'transformer_mean': float,
                'cnn_std': float,
                'transformer_std': float,
                'passed': bool,  # d > threshold
                'threshold': float
            }
        """
        cohens_d = self.compute_cohens_d(cnn_R, transformer_R)
        t_stat, p_value = self.perform_ttest(cnn_R, transformer_R)

        return {
            'cohens_d': cohens_d,
            't_statistic': t_stat,
            'p_value': p_value,
            'cnn_mean': np.mean(cnn_R),
            'transformer_mean': np.mean(transformer_R),
            'cnn_std': np.std(cnn_R, ddof=1),
            'transformer_std': np.std(transformer_R, ddof=1),
            'cnn_n': len(cnn_R),
            'transformer_n': len(transformer_R),
            'passed': cohens_d > self.threshold,
            'threshold': self.threshold,
            'effect_size_interpretation': self._interpret_effect_size(cohens_d)
        }

    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size magnitude."""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        elif d < 1.0:
            return "large"
        else:
            return "very_large"
