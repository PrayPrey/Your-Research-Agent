"""
Composition Metrics Calculator for h-c3
Calculates detection rate, execution time, and gate evaluation
"""
from dataclasses import dataclass
from typing import List, Tuple, Dict, Literal
import numpy as np
from scipy import stats


@dataclass
class CompositionMetrics:
    """Results container for composition contract evaluation"""
    detection_rate: float
    detection_ci_lower: float
    detection_ci_upper: float
    mean_execution_time: float
    max_execution_time: float
    version_stability_rate: float
    false_positive_rate: float
    contractable_by_type: Dict[str, int]
    gate_status: Literal["PASS", "WARNING", "FAIL"]
    baseline_improvement: float


class CompositionMetricsCalculator:
    """Calculates evaluation metrics for composition contracts"""

    def __init__(self, results: List[Tuple[bool, float]]):
        """
        Initialize metrics calculator.

        Args:
            results: List of (contractable, execution_time) from each defect
        """
        self.results = results
        self.total_defects = len(results)

    def calculate_detection_rate(self) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate detection rate with 95% confidence interval.

        Returns:
            (detection_rate, (ci_lower, ci_upper))
        """
        contractable_count = sum(1 for contractable, _ in self.results if contractable)
        detection_rate = (contractable_count / self.total_defects) * 100.0

        # Wilson score confidence interval (same as h-e1)
        ci_lower, ci_upper = self._wilson_score_ci(contractable_count, self.total_defects)

        return detection_rate, (ci_lower * 100.0, ci_upper * 100.0)

    def _wilson_score_ci(self, successes: int, total: int, alpha: float = 0.05) -> Tuple[float, float]:
        """
        Calculate Wilson score confidence interval.

        Args:
            successes: Number of contractable defects
            total: Total number of defects
            alpha: Significance level (0.05 for 95% CI)

        Returns:
            (lower_bound, upper_bound) as proportions
        """
        if total == 0:
            return (0.0, 0.0)

        p = successes / total
        z = stats.norm.ppf(1 - alpha / 2)
        denominator = 1 + z**2 / total

        center = (p + z**2 / (2 * total)) / denominator
        margin = (z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))) / denominator

        return (max(0.0, center - margin), min(1.0, center + margin))

    def calculate_execution_times(self) -> Tuple[float, float]:
        """
        Calculate mean and max execution times.

        Returns:
            (mean_time, max_time) in seconds
        """
        times = [t for _, t in self.results if t > 0]
        if not times:
            return 0.0, 0.0
        return np.mean(times), np.max(times)

    def calculate_all_metrics(
        self,
        version_stability_rate: float = 0.0,
        false_positive_count: int = 0,
        total_validation_samples: int = 100,
        baseline_rate: float = 0.0
    ) -> CompositionMetrics:
        """
        Calculate all metrics.

        Args:
            version_stability_rate: % of contracts stable across versions
            false_positive_count: Number of false positives
            total_validation_samples: Total known-good samples tested
            baseline_rate: Baseline detection rate from h-e1

        Returns:
            CompositionMetrics object
        """
        detection_rate, (ci_lower, ci_upper) = self.calculate_detection_rate()
        mean_time, max_time = self.calculate_execution_times()

        # False positive rate
        fp_rate = (false_positive_count / total_validation_samples) * 100.0 if total_validation_samples > 0 else 0.0

        # Contractable by type (simplified for PoC)
        contractable_by_type = {
            "device_placement": 0,
            "tensor_layout": 0,
            "cross_library_binding": 0
        }

        # Gate evaluation
        gate_status = self._evaluate_gate(detection_rate, version_stability_rate, fp_rate)

        # Baseline improvement
        baseline_improvement = detection_rate - baseline_rate

        return CompositionMetrics(
            detection_rate=detection_rate,
            detection_ci_lower=ci_lower,
            detection_ci_upper=ci_upper,
            mean_execution_time=mean_time,
            max_execution_time=max_time,
            version_stability_rate=version_stability_rate,
            false_positive_rate=fp_rate,
            contractable_by_type=contractable_by_type,
            gate_status=gate_status,
            baseline_improvement=baseline_improvement
        )

    def _evaluate_gate(
        self,
        detection_rate: float,
        version_stability_rate: float,
        fp_rate: float
    ) -> Literal["PASS", "WARNING", "FAIL"]:
        """
        Evaluate gate status.

        Returns:
            "PASS" if detection_rate ≥60% AND stability ≥80%
            "WARNING" if 40% ≤ detection_rate < 60%
            "FAIL" if detection_rate < 40%
        """
        # SHOULD_WORK gate: Failure doesn't block pipeline
        if detection_rate >= 60.0 and version_stability_rate >= 80.0 and fp_rate < 5.0:
            return "PASS"
        elif detection_rate >= 40.0:
            return "WARNING"
        else:
            return "FAIL"
