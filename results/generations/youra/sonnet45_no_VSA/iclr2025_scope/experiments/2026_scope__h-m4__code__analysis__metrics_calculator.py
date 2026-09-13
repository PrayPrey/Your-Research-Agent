"""Calculate experiment evaluation metrics."""

import numpy as np
from scipy import stats
from typing import List, Dict, Tuple


class MetricsCalculator:
    """Calculate experiment evaluation metrics."""

    def calculate_median_ttff(self, ttff_list: List[float]) -> float:
        """Calculate median TTFF."""
        if not ttff_list:
            return None
        return np.median(ttff_list)

    def calculate_ttff_reduction(
        self,
        ci_only: List[float],
        ci_contracts: List[float]
    ) -> float:
        """Calculate TTFF reduction."""
        median_ci_only = np.median(ci_only)
        median_ci_contracts = np.median(ci_contracts)
        reduction = median_ci_only - median_ci_contracts
        return reduction

    def mann_whitney_test(
        self,
        ci_only: List[float],
        ci_contracts: List[float]
    ) -> Tuple[float, float]:
        """Perform Mann-Whitney U test."""
        if len(ci_only) < 2 or len(ci_contracts) < 2:
            return (None, None)

        u_stat, p_value = stats.mannwhitneyu(
            ci_only,
            ci_contracts,
            alternative='greater'
        )
        return (u_stat, p_value)

    def calculate_marginal_detection(
        self,
        ci_only_count: int,
        ci_contracts_count: int
    ) -> float:
        """Calculate marginal detection improvement."""
        if ci_only_count == 0:
            return 0.0
        improvement = (ci_contracts_count - ci_only_count) / ci_only_count * 100
        return improvement

    def calculate_stage_distribution(
        self,
        results: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate stage-of-failure distribution."""
        distribution = {}

        for result in results:
            arm = result['arm']
            stage = result['stage']

            if arm not in distribution:
                distribution[arm] = {'environment': 0, 'training': 0, 'unknown': 0}

            distribution[arm][stage] = distribution[arm].get(stage, 0) + 1

        # Convert to proportions
        for arm in distribution:
            total = sum(distribution[arm].values())
            if total > 0:
                for stage in distribution[arm]:
                    distribution[arm][stage] = (distribution[arm][stage] / total) * 100

        return distribution
