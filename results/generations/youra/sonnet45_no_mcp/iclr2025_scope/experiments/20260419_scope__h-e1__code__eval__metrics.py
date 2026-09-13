"""
Oracle Gap Evaluation using Hypervolume Computation
Based on: 03_architecture.md - Module 4: EvaluationModule
Based on: 03_logic.md - A-4: Oracle Gap Evaluator
"""

import numpy as np
from typing import Dict, Tuple, List
from pymoo.indicators.hv import HV


class OracleGapCalculator:
    """Compute oracle gap between per-task optimal and fixed-rank baselines."""

    def __init__(self, ref_point: List[float] = None):
        """
        Initialize oracle gap calculator.

        Args:
            ref_point: Reference point for hypervolume [min_acc, max_flops]
                      Default: [0.0, 1e12]
        """
        if ref_point is None:
            ref_point = [0.0, 1e12]

        self.ref_point = np.array(ref_point)
        self.hv_indicator = HV(ref_point=self.ref_point)

    def compute_hypervolume(self, points: np.ndarray) -> float:
        """
        Compute hypervolume for Pareto front.

        Args:
            points: Array of shape [N, 2] with (accuracy, -flops)
                   Note: -flops because we want to minimize FLOPs

        Returns:
            Hypervolume value
        """
        if len(points) == 0:
            return 0.0

        # Normalize accuracy to [0, 1] if needed
        points = np.array(points)

        # Compute hypervolume
        hv = self.hv_indicator(points)
        return float(hv)

    def select_per_task_oracle(self, task_results: Dict[int, Dict[str, float]]) -> Tuple[int, float, int]:
        """
        Select best rank for a single task (oracle selection).

        Args:
            task_results: {rank: {'accuracy': val, 'flops': val}}

        Returns:
            Tuple of (best_rank, best_accuracy, best_flops)
        """
        # Select rank with highest accuracy (greedy oracle)
        best_rank = max(task_results.keys(), key=lambda r: task_results[r]['accuracy'])
        best_accuracy = task_results[best_rank]['accuracy']
        best_flops = task_results[best_rank]['flops']

        return best_rank, best_accuracy, best_flops

    def compute_oracle_gap(self, results: Dict[str, Dict[int, Dict[str, float]]]) -> Dict[str, float]:
        """
        Compute oracle gap from training results.

        Args:
            results: {task: {rank: {'accuracy': val, 'flops': val, ...}}}

        Returns:
            Dictionary with oracle gap results:
            {
                'oracle_hv': float,
                'best_fixed_hv': float,
                'oracle_gap': float,
                'oracle_gap_pct': float,
                'best_fixed_rank': int,
                'oracle_selections': {task: rank},
                'fixed_hvs': {rank: hv}
            }
        """
        print("\n" + "="*80)
        print("ORACLE GAP COMPUTATION")
        print("="*80)

        # Step 1: Compute per-task oracle hypervolume
        oracle_points = []
        oracle_selections = {}

        for task_name, task_results in results.items():
            best_rank, acc, flops = self.select_per_task_oracle(task_results)
            oracle_points.append([acc, -flops])  # Negative flops for minimization
            oracle_selections[task_name] = best_rank

            print(f"Oracle for {task_name}: rank={best_rank}, acc={acc:.4f}, flops={flops:,}")

        oracle_points = np.array(oracle_points)
        oracle_hv = self.compute_hypervolume(oracle_points)
        print(f"\n✓ Oracle Hypervolume: {oracle_hv:.6f}")

        # Step 2: Compute fixed-rank baseline hypervolumes
        fixed_hvs = {}
        ranks = list(next(iter(results.values())).keys())  # Get available ranks

        for rank in ranks:
            fixed_points = []
            for task_name in results.keys():
                if rank in results[task_name]:
                    acc = results[task_name][rank]['accuracy']
                    flops = results[task_name][rank]['flops']
                    fixed_points.append([acc, -flops])

            if fixed_points:
                fixed_points = np.array(fixed_points)
                hv = self.compute_hypervolume(fixed_points)
                fixed_hvs[rank] = hv
                print(f"  Fixed rank={rank}: HV={hv:.6f}")

        # Step 3: Compute oracle gap
        best_fixed_rank = max(fixed_hvs.keys(), key=lambda r: fixed_hvs[r])
        best_fixed_hv = fixed_hvs[best_fixed_rank]

        oracle_gap = oracle_hv - best_fixed_hv
        oracle_gap_pct = (oracle_gap / best_fixed_hv) * 100 if best_fixed_hv > 0 else 0

        print(f"\n✓ Best Fixed Rank: {best_fixed_rank} (HV={best_fixed_hv:.6f})")
        print(f"✓ Oracle Gap: {oracle_gap:.6f} ({oracle_gap_pct:.2f}%)")
        print("="*80)

        return {
            'oracle_hv': oracle_hv,
            'best_fixed_hv': best_fixed_hv,
            'oracle_gap': oracle_gap,
            'oracle_gap_pct': oracle_gap_pct,
            'best_fixed_rank': best_fixed_rank,
            'oracle_selections': oracle_selections,
            'fixed_hvs': fixed_hvs
        }


class TaskMetrics:
    """Compute task-specific evaluation metrics."""

    def __init__(self, task_type: str = "classification"):
        """
        Initialize task metrics calculator.

        Args:
            task_type: Type of task (classification, regression)
        """
        self.task_type = task_type

    def compute_accuracy(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute classification accuracy.

        Args:
            predictions: Predicted labels
            labels: True labels

        Returns:
            Accuracy value
        """
        correct = np.sum(predictions == labels)
        total = len(labels)
        return correct / total if total > 0 else 0.0

    def compute_f1(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute F1 score (binary classification).

        Args:
            predictions: Predicted labels
            labels: True labels

        Returns:
            F1 score
        """
        # True positives, false positives, false negatives
        tp = np.sum((predictions == 1) & (labels == 1))
        fp = np.sum((predictions == 1) & (labels == 0))
        fn = np.sum((predictions == 0) & (labels == 1))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0

        return f1

    def compute_pearson(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute Pearson correlation (for regression tasks like STS-B).

        Args:
            predictions: Predicted values
            labels: True values

        Returns:
            Pearson correlation coefficient
        """
        if len(predictions) < 2:
            return 0.0

        # Compute means
        pred_mean = np.mean(predictions)
        label_mean = np.mean(labels)

        # Compute correlation
        numerator = np.sum((predictions - pred_mean) * (labels - label_mean))
        denominator = np.sqrt(np.sum((predictions - pred_mean)**2) * np.sum((labels - label_mean)**2))

        if denominator == 0:
            return 0.0

        correlation = numerator / denominator
        return float(correlation)

    def compute_matthews_correlation(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """
        Compute Matthews Correlation Coefficient (for CoLA).

        Args:
            predictions: Predicted labels
            labels: True labels

        Returns:
            Matthews correlation coefficient
        """
        tp = np.sum((predictions == 1) & (labels == 1))
        tn = np.sum((predictions == 0) & (labels == 0))
        fp = np.sum((predictions == 1) & (labels == 0))
        fn = np.sum((predictions == 0) & (labels == 1))

        numerator = (tp * tn) - (fp * fn)
        denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

        if denominator == 0:
            return 0.0

        mcc = numerator / denominator
        return float(mcc)
