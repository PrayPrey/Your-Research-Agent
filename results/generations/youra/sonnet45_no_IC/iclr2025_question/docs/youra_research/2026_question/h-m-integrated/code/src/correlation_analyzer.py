"""Correlation analysis between consistency and conformal signals."""

import numpy as np
from scipy.stats import pearsonr


class CorrelationAnalyzer:
    """Analyze correlation between C and I signals."""

    def __init__(self):
        """Initialize analyzer."""
        pass

    def compute_correlation(
        self,
        consistency_scores: list[float],
        interval_indicators: list[int]
    ) -> tuple[float, float]:
        """
        Compute Pearson correlation ρ(C, I).

        Args:
            consistency_scores: List of consistency scores C
            interval_indicators: List of binary interval indicators I

        Returns:
            tuple: (correlation, p_value)
        """
        C = np.array(consistency_scores)
        I = np.array(interval_indicators)

        rho, p_value = pearsonr(C, I)

        return float(rho), float(p_value)

    def validate_gate_condition(
        self,
        correlation: float,
        p_value: float,
        lower_bound: float = 0.3,
        upper_bound: float = 0.7,
        significance_level: float = 0.05
    ) -> bool:
        """
        Validate gate condition: 0.3 ≤ ρ ≤ 0.7 and p < 0.05.

        Returns:
            bool: True if gate condition satisfied
        """
        correlation_valid = lower_bound <= correlation <= upper_bound
        significance_valid = p_value < significance_level

        return correlation_valid and significance_valid
