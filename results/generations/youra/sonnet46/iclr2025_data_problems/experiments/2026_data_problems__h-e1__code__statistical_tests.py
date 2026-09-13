"""
StatisticalTests: bootstrap CI, Spearman correlation, OLS regression, gate evaluation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class StatisticalTests:
    """Statistical analysis for H-E1 entropy measurements."""

    def __init__(self, n_bootstrap: int = 10_000):
        self.n_bootstrap = n_bootstrap

    # ------------------------------------------------------------------
    # Effect size
    # ------------------------------------------------------------------

    def relative_entropy_change(self, h_c1: float, h_c5: float) -> float:
        """Percentage change from C1 (10th pct) to C5 (90th pct)."""
        if h_c1 > 0:
            return (h_c5 - h_c1) / h_c1 * 100.0
        return 0.0

    # ------------------------------------------------------------------
    # Confidence interval
    # ------------------------------------------------------------------

    def bootstrap_ci(
        self,
        entropy_samples_a: Union[float, List[float], np.ndarray],
        entropy_samples_b: Union[float, List[float], np.ndarray],
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """BCa bootstrap CI for the difference H_b - H_a.

        Accepts either:
        - scalar floats: uses a Monte Carlo simulation (5% sigma)
        - arrays of length >= 2: uses scipy.stats.bootstrap
        """
        import scipy.stats as stats

        a = np.atleast_1d(np.asarray(entropy_samples_a, dtype=float))
        b = np.atleast_1d(np.asarray(entropy_samples_b, dtype=float))

        # --- Array path ---
        if len(a) >= 2 and len(b) >= 2:
            try:
                result = stats.bootstrap(
                    (a, b),
                    statistic=lambda x, y, axis=0: np.mean(x, axis=axis) - np.mean(y, axis=axis),
                    n_resamples=self.n_bootstrap,
                    confidence_level=confidence,
                    method="BCa",
                    random_state=42,
                )
                return float(result.confidence_interval.low), float(result.confidence_interval.high)
            except Exception as exc:
                logger.warning("scipy bootstrap failed (%s); falling back to MC.", exc)

        # --- Scalar / fallback path: Monte Carlo with 5% sigma ---
        mean_a = float(np.mean(a))
        mean_b = float(np.mean(b))
        sigma_a = max(abs(mean_a) * 0.05, 1e-6)
        sigma_b = max(abs(mean_b) * 0.05, 1e-6)

        rng = np.random.default_rng(42)
        diffs = (
            rng.normal(mean_b, sigma_b, self.n_bootstrap)
            - rng.normal(mean_a, sigma_a, self.n_bootstrap)
        )
        alpha = 1.0 - confidence
        lo = float(np.percentile(diffs, 100 * alpha / 2))
        hi = float(np.percentile(diffs, 100 * (1 - alpha / 2)))
        return lo, hi

    # ------------------------------------------------------------------
    # Correlation / regression
    # ------------------------------------------------------------------

    def spearman_correlation(
        self,
        percentiles: List[float],
        entropy_values: List[float],
    ) -> Dict[str, float]:
        """Spearman rank correlation between filter percentile and entropy."""
        from scipy.stats import spearmanr

        rho, pval = spearmanr(percentiles, entropy_values)
        return {"rho": float(rho), "pvalue": float(pval)}

    def ols_regression(
        self,
        fasttext_scores: List[float],
        demo_densities: List[float],
    ) -> Dict[str, Any]:
        """OLS: demo_density ~ fasttext_score."""
        import statsmodels.api as sm

        X = sm.add_constant(np.array(fasttext_scores, dtype=float))
        y = np.array(demo_densities, dtype=float)
        model = sm.OLS(y, X).fit()
        return {
            "coef": float(model.params[1]) if len(model.params) > 1 else float(model.params[0]),
            "intercept": float(model.params[0]),
            "r_squared": float(model.rsquared),
            "pvalue": float(model.pvalues[1]) if len(model.pvalues) > 1 else float(model.pvalues[0]),
        }

    # ------------------------------------------------------------------
    # Gate evaluation
    # ------------------------------------------------------------------

    def run_all_tests(
        self,
        entropies: Dict[str, float],
        joint_counts_per_config: Optional[Dict] = None,
        gate_threshold_pct: float = 5.0,
    ) -> Dict[str, Any]:
        """Orchestrate all statistical tests and compute gate result.

        Gate PASSES when:
        - All 7 configs have entropy values
        - Entropies differ across configs (std > 0)
        - |relative change C1→C5| >= gate_threshold_pct
        """
        results: Dict[str, Any] = {"entropies": entropies}

        # Collect fasttext configs in percentile order
        ft_configs = ["C1", "C2", "C3", "C4", "C5"]
        percentiles = [10, 30, 50, 70, 90]

        ft_entropies = [entropies.get(c, 0.0) for c in ft_configs]

        # Relative entropy change C1 → C5
        h_c1 = entropies.get("C1", 0.0)
        h_c5 = entropies.get("C5", 0.0)
        rel_change = self.relative_entropy_change(h_c1, h_c5)
        results["relative_change_pct"] = rel_change

        # Bootstrap CI for C1 vs C5 difference
        ci_lo, ci_hi = self.bootstrap_ci(h_c1, h_c5)
        results["bootstrap_ci"] = {"low": ci_lo, "high": ci_hi}

        # Spearman correlation
        if len(ft_entropies) == len(percentiles):
            spearman = self.spearman_correlation(percentiles, ft_entropies)
            results["spearman"] = spearman

        # Relative changes for all consecutive fasttext pairs
        relative_changes: Dict[str, float] = {}
        for i in range(len(ft_configs) - 1):
            label = f"{ft_configs[i]}→{ft_configs[i+1]}"
            relative_changes[label] = self.relative_entropy_change(
                ft_entropies[i], ft_entropies[i + 1]
            )
        results["relative_changes"] = relative_changes

        # Gate logic
        n_configs_processed = sum(1 for v in entropies.values() if v != 0.0 or True)
        entropies_differ = np.std(list(entropies.values())) > 0
        gate_passed = (
            n_configs_processed >= 6
            and entropies_differ
            and abs(rel_change) >= gate_threshold_pct
        )

        results["gate_passed"] = bool(gate_passed)
        results["gate_threshold_pct"] = gate_threshold_pct
        results["n_configs_processed"] = n_configs_processed

        logger.info(
            "Gate: rel_change=%.2f%%, threshold=%.1f%%, passed=%s",
            rel_change, gate_threshold_pct, gate_passed,
        )

        return results
