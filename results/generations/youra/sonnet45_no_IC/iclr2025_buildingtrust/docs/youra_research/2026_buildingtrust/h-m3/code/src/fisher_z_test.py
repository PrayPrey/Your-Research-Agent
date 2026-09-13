"""
Fisher z-Test Implementation for Correlation Comparison
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple


class FisherZTest:
    """Fisher z-test for comparing two independent correlations."""

    def __init__(self, alpha: float = 0.05):
        """
        Initialize Fisher z-test analyzer.

        Args:
            alpha: Significance level (default: 0.05)
        """
        self.alpha = alpha

    def fisher_z_transform(self, r: float) -> float:
        """
        Apply Fisher z-transformation.

        Args:
            r: Correlation coefficient [-1, 1]

        Returns:
            z: Fisher z-transformed value
        """
        return np.arctanh(r)

    def compute_z_statistic(
        self,
        r1: float,
        n1: int,
        r2: float,
        n2: int
    ) -> Tuple[float, float]:
        """
        Compute test statistic and standard error.

        Args:
            r1: Correlation coefficient for group 1 (factual)
            n1: Sample size for group 1
            r2: Correlation coefficient for group 2 (misinformation)
            n2: Sample size for group 2

        Returns:
            (z_stat, se_diff)
        """
        # Fisher z-transformation
        z1 = np.arctanh(r1)
        z2 = np.arctanh(r2)

        # Standard error of difference
        se_diff = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))

        # Test statistic
        z_stat = (z1 - z2) / se_diff

        return float(z_stat), float(se_diff)

    def compare_correlations(
        self,
        r1: float,
        n1: int,
        r2: float,
        n2: int
    ) -> Dict:
        """
        Compare two independent correlations using Fisher z-test.

        Args:
            r1: Correlation coefficient for group 1 (factual)
            n1: Sample size for group 1
            r2: Correlation coefficient for group 2 (misinformation)
            n2: Sample size for group 2

        Returns:
            {
                "z_stat": float,
                "p_value": float,
                "se_diff": float,
                "z1": float,
                "z2": float,
                "significant": bool,
                "delta_r": float
            }
        """
        z_stat, se_diff = self.compute_z_statistic(r1, n1, r2, n2)

        # Two-tailed p-value from standard normal distribution
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        # Significance test
        significant = p_value < self.alpha

        return {
            "z_stat": float(z_stat),
            "p_value": float(p_value),
            "se_diff": float(se_diff),
            "z1": float(np.arctanh(r1)),
            "z2": float(np.arctanh(r2)),
            "significant": bool(significant),
            "delta_r": float(abs(r1 - r2))
        }

    def compute_confidence_intervals(
        self,
        r: float,
        n: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Compute CI using Fisher z-transformation.

        Args:
            r: Correlation coefficient
            n: Sample size
            confidence: Confidence level (default: 0.95)

        Returns:
            (ci_lower, ci_upper) in correlation space
        """
        # Fisher z-transform
        z = np.arctanh(r)

        # Standard error
        se = 1 / np.sqrt(n - 3)

        # Critical value
        z_crit = stats.norm.ppf((1 + confidence) / 2)

        # CI in z-space
        z_ci_lower = z - z_crit * se
        z_ci_upper = z + z_crit * se

        # Back-transform to correlation space
        r_ci_lower = np.tanh(z_ci_lower)
        r_ci_upper = np.tanh(z_ci_upper)

        return float(r_ci_lower), float(r_ci_upper)

    def compute_effect_size(self, r1: float, r2: float) -> Dict:
        """
        Compute Cohen's q effect size for correlation difference.

        Args:
            r1: Correlation coefficient 1 (factual)
            r2: Correlation coefficient 2 (misinformation)

        Returns:
            {
                "cohens_q": float,
                "z1": float,
                "z2": float,
                "magnitude": str  # "small", "medium", "large"
            }
        """
        # Cohen's q = |z1 - z2|
        z1 = np.arctanh(r1)
        z2 = np.arctanh(r2)
        cohens_q = abs(z1 - z2)

        # Effect size classification
        if cohens_q < 0.1:
            magnitude = "small"
        elif cohens_q < 0.3:
            magnitude = "medium"
        else:
            magnitude = "large"

        return {
            "cohens_q": float(cohens_q),
            "z1": float(z1),
            "z2": float(z2),
            "magnitude": magnitude
        }
