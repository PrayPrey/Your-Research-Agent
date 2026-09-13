"""Statistical tests for error signature comparison."""

from scipy.stats import ttest_ind
import numpy as np
from typing import Dict, List
import json


class StatisticalAnalyzer:
    """Perform statistical tests for error signature comparison."""

    def __init__(self):
        """Initialize statistical analyzer."""
        pass

    def independent_ttest(
        self,
        group1: List[float],
        group2: List[float]
    ) -> Dict[str, float]:
        """
        Perform independent samples t-test.

        Args:
            group1: List[float] - First group scores (100 samples)
            group2: List[float] - Second group scores (100 samples)

        Returns:
            Dict with keys: 't_statistic', 'p_value', 'mean1', 'mean2'
        """
        # Perform t-test
        t_stat, p_val = ttest_ind(group1, group2)

        return {
            't_statistic': float(t_stat),
            'p_value': float(p_val),
            'mean1': float(np.mean(group1)),
            'mean2': float(np.mean(group2)),
            'std1': float(np.std(group1)),
            'std2': float(np.std(group2))
        }

    def evaluate_gate(
        self,
        diversity_test: Dict[str, float],
        threshold: float = 0.05
    ) -> bool:
        """
        Evaluate SHOULD_WORK gate condition.

        Args:
            diversity_test: Dict with t-test results
            threshold: float - Significance threshold (default 0.05)

        Returns:
            bool - True if (p < 0.05) AND (mean_nq > mean_tqa)
        """
        p_value = diversity_test['p_value']
        mean_nq = diversity_test['mean1']
        mean_tqa = diversity_test['mean2']

        # Gate condition: statistically significant AND correct direction
        gate_pass = (p_value < threshold) and (mean_nq > mean_tqa)

        return gate_pass

    def save_results(self, results: Dict, output_path: str):
        """Save statistical results to JSON."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_path}")
