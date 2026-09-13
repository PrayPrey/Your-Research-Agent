"""
Cohen's Kappa Calculator with Bootstrap Confidence Intervals
"""

import numpy as np
from sklearn.metrics import cohen_kappa_score
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class KappaCalculator:
    """Cohen's kappa with bootstrap confidence intervals"""

    def __init__(self, config):
        """Initialize with bootstrap configuration."""
        self.n_bootstrap = config.bootstrap_iterations
        self.confidence_level = config.confidence_level
        self.random_seed = config.random_seed
        np.random.seed(self.random_seed)

        logger.info(f"KappaCalculator initialized: {self.n_bootstrap} bootstrap iterations")

    def compute_cohens_kappa(self, coder_a: np.ndarray, coder_b: np.ndarray) -> float:
        """
        Compute Cohen's kappa.
        Args:
            coder_a, coder_b: [n] binary arrays
        Returns:
            κ ∈ [-1, 1]
        """
        return cohen_kappa_score(coder_a, coder_b)

    def bootstrap_confidence_interval(
        self,
        coder_a: np.ndarray,
        coder_b: np.ndarray
    ) -> Tuple[float, float]:
        """
        Compute bootstrap confidence interval for Cohen's kappa.
        Args:
            coder_a, coder_b: [n] binary arrays
        Returns:
            (ci_lower, ci_upper): 95% confidence interval bounds
        """
        n = len(coder_a)
        bootstrap_kappas = []

        for _ in range(self.n_bootstrap):
            # Sample with replacement
            indices = np.random.choice(n, n, replace=True)
            sample_a = coder_a[indices]
            sample_b = coder_b[indices]

            # Compute kappa for this bootstrap sample
            kappa = self.compute_cohens_kappa(sample_a, sample_b)
            bootstrap_kappas.append(kappa)

        # Compute percentile-based confidence interval
        alpha = 1 - self.confidence_level
        ci_lower = np.percentile(bootstrap_kappas, alpha / 2 * 100)
        ci_upper = np.percentile(bootstrap_kappas, (1 - alpha / 2) * 100)

        return ci_lower, ci_upper
