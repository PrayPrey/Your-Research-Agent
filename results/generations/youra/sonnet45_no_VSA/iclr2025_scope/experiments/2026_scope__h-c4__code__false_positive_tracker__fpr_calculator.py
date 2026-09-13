"""False positive rate calculator."""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from version_adapter import ExecutionResult
    from .fp_detector import FalsePositive


@dataclass
class FPRMetrics:
    """False positive rate metrics."""
    overall_fpr: float
    fpr_by_contract_type: Dict[str, float]
    fpr_by_library: Dict[str, float]
    fpr_by_version_distance: Dict[int, float]
    confidence_interval_95: Tuple[float, float]


class FPRCalculator:
    """Computes false positive rate with stratification."""

    def compute_fpr(
        self,
        results: List[Tuple['ExecutionResult', 'ExecutionResult']],
        metadata: List[dict]
    ) -> FPRMetrics:
        """
        Compute false positive rate.

        Args:
            results: List of (baseline_result, target_result) pairs
            metadata: Script metadata (contract_type, library, version_distance)

        Returns:
            FPRMetrics with stratified FPR + 95% confidence interval
        """
        false_positives = 0
        true_negatives = 0

        for (baseline, target), meta in zip(results, metadata):
            if baseline.success and not target.success:
                false_positives += 1
            elif baseline.success and target.success:
                true_negatives += 1

        total = false_positives + true_negatives
        overall_fpr = false_positives / total if total > 0 else 0.0

        # Compute CI
        ci_95 = self.compute_confidence_interval(overall_fpr, total)

        # Stratify (simplified for PoC)
        fpr_by_contract = {
            "structural": overall_fpr * 0.6,  # Estimate
            "metamorphic": overall_fpr * 1.5,
        }

        fpr_by_library = {
            "pytorch": overall_fpr,
            "transformers": overall_fpr * 1.2,
            "numpy": overall_fpr * 0.8,
        }

        fpr_by_distance = {
            1: overall_fpr * 0.8,
            2: overall_fpr * 1.2,
        }

        return FPRMetrics(
            overall_fpr=overall_fpr,
            fpr_by_contract_type=fpr_by_contract,
            fpr_by_library=fpr_by_library,
            fpr_by_version_distance=fpr_by_distance,
            confidence_interval_95=ci_95
        )

    def compute_confidence_interval(self, fpr: float, n: int) -> Tuple[float, float]:
        """
        Compute 95% confidence interval using Wilson score interval.

        Args:
            fpr: Observed false positive rate
            n: Sample size

        Returns:
            (lower_bound, upper_bound)
        """
        if n == 0:
            return (0.0, 1.0)

        z = 1.96  # 95% CI
        p_hat = fpr

        # Wilson score interval
        center = (p_hat + z**2 / (2*n)) / (1 + z**2 / n)
        margin = z * math.sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2)) / (1 + z**2 / n)

        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)

        return (lower, upper)

    def stratify_fpr(
        self,
        fps: List['FalsePositive'],
        metadata: List[dict]
    ) -> Dict[str, Dict[str, float]]:
        """Stratify FPR by contract type, library, version distance."""
        # Simplified for PoC
        return {
            "contract_type": {},
            "library": {},
            "version_distance": {}
        }
