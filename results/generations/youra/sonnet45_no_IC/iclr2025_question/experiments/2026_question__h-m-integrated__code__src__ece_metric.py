"""
Expected Calibration Error (ECE) Metric & Cost Tracking (M-3)

ECE measures calibration quality by binning predictions and comparing
accuracy vs confidence in each bin.

Computational cost tracking counts forward passes for efficiency claims.

Author: Anonymous
Date: 2026-07-13
Hypothesis: h-m-integrated
"""

import numpy as np
from typing import List, Dict, Tuple
from scipy import stats


class ECEMetric:
    """
    Expected Calibration Error with 10-bin discretization.

    Formula: ECE = Σ (|B_m|/n) |acc(B_m) - conf(B_m)|
    """

    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins

    def compute_ece(
        self,
        predictions: List[int],  # 1 if in interval, 0 otherwise
        confidences: List[float],  # Confidence scores
        ground_truth: List[int]  # 1 if correct, 0 otherwise
    ) -> float:
        """
        Compute ECE.

        Args:
            predictions: Binary predictions (interval membership)
            confidences: Confidence scores [0, 1]
            ground_truth: Binary correctness

        Returns:
            ECE value [0, 1]
        """
        predictions = np.array(predictions)
        confidences = np.array(confidences)
        ground_truth = np.array(ground_truth)

        # Create bins
        bins = np.linspace(0, 1, self.n_bins + 1)
        ece = 0.0
        bin_details = []

        for i in range(self.n_bins):
            # Mask for samples in this bin
            mask = (confidences >= bins[i]) & (confidences < bins[i+1])
            n_samples = mask.sum()

            if n_samples > 0:
                # Accuracy and confidence in this bin
                bin_acc = ground_truth[mask].mean()
                bin_conf = confidences[mask].mean()

                # Weighted ECE contribution
                bin_ece = (n_samples / len(predictions)) * abs(bin_acc - bin_conf)
                ece += bin_ece

                bin_details.append({
                    'bin': i,
                    'range': (bins[i], bins[i+1]),
                    'n_samples': n_samples,
                    'accuracy': bin_acc,
                    'confidence': bin_conf,
                    'ece_contribution': bin_ece
                })

        return ece

    def compute_ece_with_stats(
        self,
        predictions: List[int],
        confidences: List[float],
        ground_truth: List[int]
    ) -> Dict:
        """
        Compute ECE with detailed statistics.

        Returns dict with:
        - ece: float
        - bin_details: list of per-bin statistics
        - max_calibration_error: float (max bin error)
        """
        predictions = np.array(predictions)
        confidences = np.array(confidences)
        ground_truth = np.array(ground_truth)

        bins = np.linspace(0, 1, self.n_bins + 1)
        ece = 0.0
        bin_details = []
        max_error = 0.0

        for i in range(self.n_bins):
            mask = (confidences >= bins[i]) & (confidences < bins[i+1])
            n_samples = mask.sum()

            if n_samples > 0:
                bin_acc = ground_truth[mask].mean()
                bin_conf = confidences[mask].mean()
                bin_error = abs(bin_acc - bin_conf)
                bin_ece = (n_samples / len(predictions)) * bin_error

                ece += bin_ece
                max_error = max(max_error, bin_error)

                bin_details.append({
                    'bin': i,
                    'range': (bins[i], bins[i+1]),
                    'n_samples': int(n_samples),
                    'accuracy': float(bin_acc),
                    'confidence': float(bin_conf),
                    'error': float(bin_error),
                    'ece_contribution': float(bin_ece)
                })

        return {
            'ece': float(ece),
            'bin_details': bin_details,
            'max_calibration_error': float(max_error),
            'n_bins': self.n_bins
        }


class ComputationalCostTracker:
    """
    Track forward passes for computational efficiency measurement.

    Cost breakdown:
    - HBC: N samples per query (5-10) + calibration passes
    - COIN: 1 sample per query + calibration
    - Expected reduction: 30-50%
    """

    def __init__(self):
        self.forward_pass_counts: Dict[str, int] = {}
        self.sample_counts: Dict[str, int] = {}

    def reset(self):
        """Reset all counters."""
        self.forward_pass_counts = {}
        self.sample_counts = {}

    def track_method(
        self,
        method_name: str,
        n_queries: int,
        samples_per_query: int,
        calibration_passes: int = 0
    ):
        """
        Track forward passes for a method.

        Args:
            method_name: e.g., "HBC", "COIN", "SelfCheckGPT"
            n_queries: Number of test queries
            samples_per_query: Samples generated per query
            calibration_passes: Additional calibration passes
        """
        total_passes = (n_queries * samples_per_query) + calibration_passes
        self.forward_pass_counts[method_name] = total_passes
        self.sample_counts[method_name] = n_queries

    def compute_reduction(self, method_a: str, method_b: str) -> float:
        """
        Compute cost reduction: (A - B) / A × 100%.

        Args:
            method_a: Baseline method (e.g., "COIN")
            method_b: Proposed method (e.g., "HBC")

        Returns:
            Reduction percentage (negative if B is more expensive)
        """
        if method_a not in self.forward_pass_counts or method_b not in self.forward_pass_counts:
            return 0.0

        cost_a = self.forward_pass_counts[method_a]
        cost_b = self.forward_pass_counts[method_b]

        if cost_a == 0:
            return 0.0

        reduction = (cost_a - cost_b) / cost_a * 100.0
        return reduction

    def get_summary(self) -> Dict:
        """Return cost tracking summary."""
        return {
            'forward_passes': dict(self.forward_pass_counts),
            'sample_counts': dict(self.sample_counts)
        }

    def get_reduction_report(self, baseline: str = "COIN") -> Dict:
        """
        Generate cost reduction report.

        Args:
            baseline: Baseline method name

        Returns:
            Dict with reduction percentages vs baseline
        """
        if baseline not in self.forward_pass_counts:
            return {}

        baseline_cost = self.forward_pass_counts[baseline]
        reductions = {}

        for method, cost in self.forward_pass_counts.items():
            if method != baseline:
                reduction = (baseline_cost - cost) / baseline_cost * 100.0
                reductions[method] = {
                    'cost': cost,
                    'baseline_cost': baseline_cost,
                    'reduction_pct': reduction
                }

        return reductions


def compute_statistical_significance(
    ece_method_a: List[float],
    ece_method_b: List[float],
    alpha: float = 0.05
) -> Dict:
    """
    Compute statistical significance between two methods via t-test.

    Args:
        ece_method_a: ECE values for method A (per-sample or per-bin)
        ece_method_b: ECE values for method B
        alpha: Significance level

    Returns:
        Dict with t-statistic, p-value, significant (bool)
    """
    t_stat, p_value = stats.ttest_rel(ece_method_a, ece_method_b)

    return {
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'significant': p_value < alpha,
        'alpha': alpha,
        'mean_difference': float(np.mean(ece_method_a) - np.mean(ece_method_b))
    }
