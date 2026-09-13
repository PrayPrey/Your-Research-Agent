"""Experiment executor for simplified PoC validation."""

import random
import numpy as np
from typing import Dict, List
from scipy import stats


class ExperimentExecutor:
    """Run simplified PoC experiments."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)

    def run_experiment(self, hypothesis: Dict) -> Dict:
        """Execute simplified experiment for hypothesis.

        Returns: {hypothesis_id, p_value, control_mean, treatment_mean, success}
        """
        # Simplified PoC: mock experiments with realistic effect sizes
        # In real version: load actual D/B/M and run intervention

        hypothesis_id = hypothesis['id']

        # Use ground truth to simulate realistic outcomes
        # Testable hypotheses (DBM exists) should have higher success rate
        is_truly_testable = hypothesis.get('ground_truth_testable', True)

        if is_truly_testable:
            # 70% chance of significant result (p < 0.05) for truly testable
            has_effect = random.random() < 0.70
        else:
            # 30% chance of significant result for non-testable (noise)
            has_effect = random.random() < 0.30

        # Generate mock control/treatment data
        n_trials = 30  # Small sample for PoC
        control_mean = 0.75
        control_std = 0.05

        if has_effect:
            # Significant effect
            treatment_mean = control_mean + np.random.uniform(0.03, 0.10)
        else:
            # No effect (null result)
            treatment_mean = control_mean + np.random.uniform(-0.02, 0.02)

        treatment_std = 0.05

        # Generate samples
        control_results = np.random.normal(control_mean, control_std, n_trials)
        treatment_results = np.random.normal(treatment_mean, treatment_std, n_trials)

        # Two-sample t-test
        t_stat, p_value = stats.ttest_ind(treatment_results, control_results)

        return {
            "hypothesis_id": hypothesis_id,
            "p_value": float(p_value),
            "control_mean": float(np.mean(control_results)),
            "treatment_mean": float(np.mean(treatment_results)),
            "success": bool(p_value < 0.05),
        }
