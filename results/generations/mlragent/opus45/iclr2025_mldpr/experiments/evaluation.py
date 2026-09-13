"""
Evaluation metrics for DDHS experiments.
Includes deprecation prediction, user alignment, and efficiency metrics.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, average_precision_score,
    f1_score, precision_score, recall_score, confusion_matrix
)
from scipy.stats import kendalltau, spearmanr, pearsonr
import time


class DeprecationPredictor:
    """
    Evaluate ability of health scores to predict dataset deprecation.
    Uses ROC-AUC as primary metric.
    """

    def evaluate(
        self,
        scores: List[float],
        is_deprecated: List[bool]
    ) -> Dict[str, float]:
        """
        Evaluate deprecation prediction performance.

        Args:
            scores: Health scores (higher = healthier, so we invert for deprecation)
            is_deprecated: Ground truth deprecation labels

        Returns:
            Dictionary of evaluation metrics
        """
        y_true = np.array(is_deprecated).astype(int)
        y_score = 1 - np.array(scores)  # Invert: low health -> high deprecation risk

        # Handle edge cases
        if len(np.unique(y_true)) < 2:
            return {
                'auc_roc': 0.5,
                'avg_precision': 0.0,
                'precision_at_10': 0.0,
                'recall_at_10': 0.0,
                'f1_at_optimal': 0.0,
                'n_deprecated': int(np.sum(y_true)),
                'n_total': len(y_true)
            }

        # ROC-AUC
        auc_roc = roc_auc_score(y_true, y_score)

        # Average Precision (PR-AUC)
        avg_precision = average_precision_score(y_true, y_score)

        # Precision/Recall at top 10%
        threshold_idx = int(len(y_score) * 0.1)
        top_indices = np.argsort(y_score)[-threshold_idx:]
        y_pred_top10 = np.zeros_like(y_true)
        y_pred_top10[top_indices] = 1

        precision_at_10 = precision_score(y_true, y_pred_top10, zero_division=0)
        recall_at_10 = recall_score(y_true, y_pred_top10, zero_division=0)

        # F1 at optimal threshold
        precision_curve, recall_curve, thresholds = precision_recall_curve(y_true, y_score)
        f1_scores = 2 * (precision_curve * recall_curve) / (precision_curve + recall_curve + 1e-8)
        f1_at_optimal = np.max(f1_scores)

        return {
            'auc_roc': float(auc_roc),
            'avg_precision': float(avg_precision),
            'precision_at_10': float(precision_at_10),
            'recall_at_10': float(recall_at_10),
            'f1_at_optimal': float(f1_at_optimal),
            'n_deprecated': int(np.sum(y_true)),
            'n_total': len(y_true)
        }


class UserAlignmentEvaluator:
    """
    Evaluate alignment between computed scores and expert rankings.
    Uses Kendall's tau and Spearman correlation.
    """

    def evaluate(
        self,
        computed_scores: List[float],
        expert_scores: List[float]
    ) -> Dict[str, float]:
        """
        Evaluate alignment between computed and expert scores.

        Returns:
            Dictionary of correlation metrics
        """
        computed = np.array(computed_scores)
        expert = np.array(expert_scores)

        # Kendall's tau
        kendall_tau, kendall_p = kendalltau(computed, expert)

        # Spearman correlation
        spearman_rho, spearman_p = spearmanr(computed, expert)

        # Pearson correlation
        pearson_r, pearson_p = pearsonr(computed, expert)

        # Mean absolute error
        mae = np.mean(np.abs(computed - expert))

        # Root mean squared error
        rmse = np.sqrt(np.mean((computed - expert) ** 2))

        # Rank correlation (how well rankings match)
        computed_ranks = np.argsort(np.argsort(-computed))  # Higher score = lower rank
        expert_ranks = np.argsort(np.argsort(-expert))
        rank_mae = np.mean(np.abs(computed_ranks - expert_ranks))

        return {
            'kendall_tau': float(kendall_tau),
            'kendall_p': float(kendall_p),
            'spearman_rho': float(spearman_rho),
            'spearman_p': float(spearman_p),
            'pearson_r': float(pearson_r),
            'pearson_p': float(pearson_p),
            'mae': float(mae),
            'rmse': float(rmse),
            'rank_mae': float(rank_mae)
        }


class EfficiencyEvaluator:
    """
    Evaluate computational efficiency of health score computation.
    """

    def __init__(self):
        self.timing_results = []

    def time_evaluation(
        self,
        method,
        datasets,
        name: str,
        n_runs: int = 3
    ) -> Dict[str, float]:
        """
        Time the evaluation of a method.

        Returns:
            Dictionary of timing metrics
        """
        times = []

        for _ in range(n_runs):
            start = time.time()
            method.evaluate_repository(datasets)
            end = time.time()
            times.append(end - start)

        mean_time = np.mean(times)
        std_time = np.std(times)
        time_per_dataset = mean_time / len(datasets)

        result = {
            'method': name,
            'total_time_mean': float(mean_time),
            'total_time_std': float(std_time),
            'time_per_dataset': float(time_per_dataset),
            'n_datasets': len(datasets),
            'n_runs': n_runs
        }

        self.timing_results.append(result)
        return result

    def get_all_results(self) -> List[Dict]:
        """Get all timing results"""
        return self.timing_results


class ScalabilityBenchmark:
    """
    Benchmark scalability across different repository sizes.
    """

    def __init__(self, sizes: List[int] = None):
        self.sizes = sizes or [50, 100, 200, 500, 1000]
        self.results = []

    def benchmark(
        self,
        method_factory,
        data_generator,
        method_name: str
    ) -> List[Dict]:
        """
        Benchmark method across different sizes.

        Args:
            method_factory: Function that creates method instance
            data_generator: SyntheticDataGenerator instance
            method_name: Name of the method

        Returns:
            List of benchmark results
        """
        results = []

        for size in self.sizes:
            # Generate datasets of this size
            datasets = data_generator.generate_repository(num_datasets=size)

            # Create fresh method instance
            method = method_factory()

            # Time evaluation
            times = []
            for _ in range(3):
                start = time.time()
                method.evaluate_repository(datasets)
                end = time.time()
                times.append(end - start)

            result = {
                'method': method_name,
                'n_datasets': size,
                'mean_time': float(np.mean(times)),
                'std_time': float(np.std(times)),
                'time_per_dataset': float(np.mean(times) / size)
            }
            results.append(result)

        self.results.extend(results)
        return results


def compute_comprehensive_evaluation(
    method_name: str,
    scores: List[float],
    expert_scores: List[float],
    is_deprecated: List[bool],
    computation_time: float,
    n_datasets: int
) -> Dict:
    """
    Compute comprehensive evaluation metrics for a method.
    """
    deprecation_evaluator = DeprecationPredictor()
    alignment_evaluator = UserAlignmentEvaluator()

    deprecation_metrics = deprecation_evaluator.evaluate(scores, is_deprecated)
    alignment_metrics = alignment_evaluator.evaluate(scores, expert_scores)

    return {
        'method': method_name,
        'deprecation': deprecation_metrics,
        'alignment': alignment_metrics,
        'efficiency': {
            'total_time': computation_time,
            'time_per_dataset': computation_time / n_datasets,
            'n_datasets': n_datasets
        }
    }


if __name__ == "__main__":
    # Test evaluation metrics
    from data_generator import SyntheticDataGenerator
    from health_scores import DDHSCalculator

    # Generate test data
    generator = SyntheticDataGenerator(seed=42)
    datasets = generator.generate_repository(num_datasets=100)

    # Compute DDHS scores
    calculator = DDHSCalculator()
    ddhs_scores, _ = calculator.evaluate_repository(datasets)

    # Get ground truth
    expert_scores = [ds.quality_score_expert for ds in datasets]
    is_deprecated = [ds.is_deprecated for ds in datasets]

    # Evaluate
    deprecation_evaluator = DeprecationPredictor()
    alignment_evaluator = UserAlignmentEvaluator()

    deprecation_results = deprecation_evaluator.evaluate(ddhs_scores, is_deprecated)
    alignment_results = alignment_evaluator.evaluate(ddhs_scores, expert_scores)

    print("Deprecation Prediction Metrics:")
    for k, v in deprecation_results.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    print("\nUser Alignment Metrics:")
    for k, v in alignment_results.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
