"""
Correlation Analyzer
Computes correlation metrics and gate evaluation for h-e1
"""

from typing import Tuple
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import roc_auc_score


class CorrelationAnalyzer:
    """Compute correlation metrics and gate evaluation."""

    def compute_pearson(self, derivatives: np.ndarray, outcomes: np.ndarray) -> Tuple[float, float]:
        """
        Pearson correlation.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            r: Pearson correlation coefficient
            p_value: statistical significance
        """
        if len(derivatives) < 2:
            return 0.0, 1.0

        r, p_value = pearsonr(derivatives, outcomes)
        return float(r), float(p_value)

    def compute_spearman(self, derivatives: np.ndarray, outcomes: np.ndarray) -> Tuple[float, float]:
        """
        Spearman correlation.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            rho: Spearman correlation coefficient
            p_value: statistical significance
        """
        if len(derivatives) < 2:
            return 0.0, 1.0

        rho, p_value = spearmanr(derivatives, outcomes)
        return float(rho), float(p_value)

    def compute_auc(self, derivatives: np.ndarray, outcomes: np.ndarray) -> float:
        """
        ROC-AUC score.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            auc: Area under ROC curve
        """
        if len(np.unique(outcomes)) < 2:
            return 0.5  # No discrimination possible

        try:
            auc = roc_auc_score(outcomes, derivatives)
            return float(auc)
        except Exception as e:
            print(f"WARNING: Could not compute AUC: {e}")
            return 0.5

    def evaluate_gate(self, r: float, rho: float, threshold: float = 0.3) -> bool:
        """
        Gate condition evaluation.

        Args:
            r: Pearson correlation coefficient
            rho: Spearman correlation coefficient
            threshold: minimum correlation threshold (default 0.3)

        Returns:
            True if gate passes (r > threshold OR rho > threshold)
        """
        return r > threshold or rho > threshold

    def compute_summary_statistics(self, derivatives: np.ndarray, outcomes: np.ndarray) -> dict:
        """
        Compute summary statistics by outcome group.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]

        Returns:
            dict with mean/std for success and timeout groups
        """
        success_derivatives = derivatives[outcomes == 0]
        timeout_derivatives = derivatives[outcomes == 1]

        return {
            'success': {
                'count': len(success_derivatives),
                'mean': float(np.mean(success_derivatives)) if len(success_derivatives) > 0 else 0.0,
                'std': float(np.std(success_derivatives)) if len(success_derivatives) > 0 else 0.0,
            },
            'timeout': {
                'count': len(timeout_derivatives),
                'mean': float(np.mean(timeout_derivatives)) if len(timeout_derivatives) > 0 else 0.0,
                'std': float(np.std(timeout_derivatives)) if len(timeout_derivatives) > 0 else 0.0,
            }
        }
