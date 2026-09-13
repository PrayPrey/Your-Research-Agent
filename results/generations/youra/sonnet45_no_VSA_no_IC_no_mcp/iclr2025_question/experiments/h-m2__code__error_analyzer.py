"""Error analysis and statistical testing."""

import numpy as np
from scipy.stats import ttest_rel


class ErrorAnalyzer:
    """Compute prediction errors and statistical tests."""

    def compute_errors(
        self,
        predictions: np.ndarray,
        ground_truth: np.ndarray
    ) -> np.ndarray:
        """
        Relative error: |pred - truth| / truth.
        predictions: [N], ground_truth: [N] -> errors: [N]
        """
        return np.abs(predictions - ground_truth) / ground_truth

    def compute_reduction(
        self,
        errors_g1: np.ndarray,
        errors_g2: np.ndarray
    ) -> dict:
        """
        Error reduction percentage: (E_g1 - E_g2) / E_g1 * 100.
        Returns: {
            "mean_reduction": float,
            "per_hypothesis_reduction": np.ndarray [N]
        }
        """
        # Avoid division by zero: set reduction to 0 where errors_g1 is zero
        with np.errstate(divide='ignore', invalid='ignore'):
            reduction_pct = np.where(errors_g1 > 0, (errors_g1 - errors_g2) / errors_g1 * 100, 0.0)
        return {
            "mean_reduction": float(np.mean(reduction_pct)),
            "per_hypothesis_reduction": reduction_pct
        }

    def paired_ttest(
        self,
        errors_g1: np.ndarray,
        errors_g2: np.ndarray
    ) -> dict:
        """
        Paired t-test comparing Gate 1 vs Gate 2 errors.
        Returns: {
            "t_statistic": float,
            "p_value": float,
            "dof": int
        }
        """
        t_stat, p_value = ttest_rel(errors_g1, errors_g2)
        return {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "dof": len(errors_g1) - 1
        }
