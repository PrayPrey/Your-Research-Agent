"""Statistical analysis for CCP experiments."""

from scipy.stats import mannwhitneyu, pearsonr
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
import numpy as np
from typing import List, Dict, Tuple


class StatisticalAnalyzer:
    """Perform statistical tests for hypothesis validation."""

    def mann_whitney_test(
        self,
        factual_rho: List[float],
        creative_rho: List[float],
        alternative: str = "greater"
    ) -> Dict:
        """Perform Mann-Whitney U test.

        Args:
            factual_rho: ρ_j values for factual domain
            creative_rho: ρ_j values for creative domain
            alternative: 'greater' tests if factual > creative

        Returns:
            Dict with statistic, p_value, and delta_rho_j
        """
        if not factual_rho or not creative_rho:
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "delta_rho_j": 0.0,
                "median_factual": 0.0,
                "median_creative": 0.0
            }

        # Compute medians
        median_factual = float(np.median(factual_rho))
        median_creative = float(np.median(creative_rho))
        delta_rho_j = median_factual - median_creative

        # Mann-Whitney U test
        statistic, p_value = mannwhitneyu(
            factual_rho,
            creative_rho,
            alternative=alternative
        )

        return {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "delta_rho_j": delta_rho_j,
            "median_factual": median_factual,
            "median_creative": median_creative
        }

    def pearson_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> Dict:
        """Compute Pearson correlation.

        Args:
            x: First variable (e.g., ρ_j values)
            y: Second variable (e.g., ROC-AUC values)

        Returns:
            Dict with r_squared, correlation coefficient, and p_value
        """
        if not x or not y or len(x) != len(y):
            return {
                "r_squared": 0.0,
                "correlation": 0.0,
                "p_value": 1.0
            }

        # Remove NaN/inf values
        x_clean = []
        y_clean = []
        for xi, yi in zip(x, y):
            if np.isfinite(xi) and np.isfinite(yi):
                x_clean.append(xi)
                y_clean.append(yi)

        if len(x_clean) < 2:
            return {
                "r_squared": 0.0,
                "correlation": 0.0,
                "p_value": 1.0
            }

        # Pearson correlation
        correlation, p_value = pearsonr(x_clean, y_clean)
        r_squared = correlation ** 2

        return {
            "r_squared": float(r_squared),
            "correlation": float(correlation),
            "p_value": float(p_value),
            "n_samples": len(x_clean)
        }

    def compute_roc_auc(
        self,
        y_true: List[int],
        y_scores: List[float]
    ) -> Dict:
        """Compute ROC-AUC and PR-AUC.

        Args:
            y_true: Binary labels (0 or 1)
            y_scores: Prediction scores

        Returns:
            Dict with roc_auc and pr_auc
        """
        if not y_true or not y_scores or len(y_true) != len(y_scores):
            return {
                "roc_auc": 0.0,
                "pr_auc": 0.0
            }

        # Remove NaN/inf scores
        y_true_clean = []
        y_scores_clean = []
        for yt, ys in zip(y_true, y_scores):
            if np.isfinite(ys):
                y_true_clean.append(yt)
                y_scores_clean.append(ys)

        if len(y_true_clean) < 2 or len(set(y_true_clean)) < 2:
            return {
                "roc_auc": 0.0,
                "pr_auc": 0.0
            }

        # ROC-AUC
        try:
            roc_auc = roc_auc_score(y_true_clean, y_scores_clean)
        except ValueError:
            roc_auc = 0.0

        # PR-AUC
        try:
            precision, recall, _ = precision_recall_curve(y_true_clean, y_scores_clean)
            pr_auc = auc(recall, precision)
        except ValueError:
            pr_auc = 0.0

        return {
            "roc_auc": float(roc_auc),
            "pr_auc": float(pr_auc),
            "n_samples": len(y_true_clean)
        }
