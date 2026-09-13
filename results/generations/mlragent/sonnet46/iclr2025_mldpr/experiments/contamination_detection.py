"""
Contamination Detection Module for the Dynamic Benchmark Renewal Framework.

Detects when a benchmark has become saturated (overfit) using:
1. Performance drift analysis via logistic growth model fitting
2. Out-of-Distribution divergence test using Mann-Kendall trend test
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import kendalltau, spearmanr


class ContaminationDetectionModule:
    def __init__(self, alpha=0.05, device=None):
        self.alpha = alpha
        self.device = device

    def logistic_growth(self, t, L, k, t0):
        """Logistic growth model for performance trajectory."""
        return L / (1 + np.exp(-k * (t - t0)))

    def fit_growth_curve(self, scores):
        """Fit logistic growth curve to benchmark score trajectory."""
        n = len(scores)
        t = np.arange(n, dtype=float)

        try:
            # Initial parameter guesses
            L_init = min(scores.max() * 1.05, 0.99)
            k_init = 0.3
            t0_init = n / 2.0

            popt, _ = curve_fit(
                self.logistic_growth, t, scores,
                p0=[L_init, k_init, t0_init],
                bounds=([0.5, 0.01, -n], [1.0, 5.0, 2*n]),
                maxfev=5000
            )
            return popt
        except RuntimeError:
            # Fallback: linear fit
            L = scores.max()
            k = 0.1
            t0 = n / 2.0
            return [L, k, t0]

    def detect_saturation(self, benchmark_scores, shadow_scores):
        """
        Detect benchmark saturation using performance drift and OOD divergence.

        Args:
            benchmark_scores: shape (n_generations, n_models)
            shadow_scores: shape (n_generations, n_models)

        Returns:
            dict with detection results and metrics
        """
        n_generations, n_models = benchmark_scores.shape

        # Use top-performing model scores per generation
        top_bench_scores = benchmark_scores.max(axis=1)
        top_shadow_scores = shadow_scores.max(axis=1)

        # === Performance Drift Analysis ===
        # Fit logistic growth on first 60% of generations
        train_end = int(n_generations * 0.6)
        t_train = np.arange(train_end, dtype=float)
        train_scores = top_bench_scores[:train_end]

        popt = self.fit_growth_curve(train_scores)
        L, k, t0 = popt

        # Compute residuals on training data
        fitted_train = self.logistic_growth(t_train, L, k, t0)
        residuals = train_scores - fitted_train
        sigma_residual = max(residuals.std(), 1e-6)

        # Predict on all generations and compute deviation
        t_all = np.arange(n_generations, dtype=float)
        fitted_all = self.logistic_growth(t_all, L, k, t0)
        deviation = top_bench_scores - fitted_all

        # Critical value for saturation detection
        z_alpha = 1.645  # 95th percentile (one-tailed)
        saturation_detected_per_gen = deviation > z_alpha * sigma_residual

        # === OOD Divergence Test ===
        # Compute divergence gap between benchmark and shadow performance
        divergence_gap = top_bench_scores - top_shadow_scores

        # Mann-Kendall trend test on the divergence gap
        tau, p_value_mk = kendalltau(np.arange(n_generations), divergence_gap)
        positive_trend = (tau > 0) and (p_value_mk < self.alpha)

        # Overall saturation determination
        saturation_detected = saturation_detected_per_gen[-1] or positive_trend

        # === Evaluate detection accuracy ===
        # Ground truth: last 40% of generations are saturated
        saturation_start = int(n_generations * 0.6)
        ground_truth = np.zeros(n_generations, dtype=bool)
        ground_truth[saturation_start:] = True

        # Binary predictions per generation
        predictions = saturation_detected_per_gen.copy()

        # Compute precision and recall
        tp = np.sum(predictions & ground_truth)
        fp = np.sum(predictions & ~ground_truth)
        fn = np.sum(~predictions & ground_truth)
        tn = np.sum(~predictions & ~ground_truth)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / n_generations

        # === Compute divergence trend ===
        # Average divergence in saturated vs unsaturated period
        mean_divergence_pre = divergence_gap[:saturation_start].mean()
        mean_divergence_post = divergence_gap[saturation_start:].mean()
        divergence_increase = mean_divergence_post - mean_divergence_pre

        return {
            'saturation_detected': bool(saturation_detected),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'accuracy': float(accuracy),
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn),
            'tn': int(tn),
            'mannkendall_tau': float(tau),
            'mannkendall_pvalue': float(p_value_mk),
            'positive_trend': bool(positive_trend),
            'mean_divergence_pre_saturation': float(mean_divergence_pre),
            'mean_divergence_post_saturation': float(mean_divergence_post),
            'divergence_increase': float(divergence_increase),
            'benchmark_scores_trajectory': top_bench_scores.tolist(),
            'shadow_scores_trajectory': top_shadow_scores.tolist(),
            'fitted_trajectory': fitted_all.tolist(),
            'divergence_gap': divergence_gap.tolist(),
            'saturation_detected_per_gen': saturation_detected_per_gen.tolist(),
            'logistic_params': {'L': float(L), 'k': float(k), 't0': float(t0)},
            'sigma_residual': float(sigma_residual),
        }
