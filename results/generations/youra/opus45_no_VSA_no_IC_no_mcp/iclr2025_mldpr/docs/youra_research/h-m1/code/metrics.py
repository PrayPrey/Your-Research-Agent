"""Correlation analysis for h-m1."""

import numpy as np
from scipy.stats import pearsonr, spearmanr
from config import CONFIG


class CorrelationAnalyzer:
    """Correlation analysis with bootstrap CI for small samples."""

    def __init__(self, n_bootstrap: int = None, seed: int = None):
        self.n_bootstrap = n_bootstrap or CONFIG["n_bootstrap"]
        self.seed = seed or CONFIG["seed"]

    def analyze(self, dnsi: np.ndarray, gap: np.ndarray) -> dict:
        """Run full correlation analysis.

        Returns dict with n, r_pearson, p_pearson, r_spearman, p_spearman,
        ci_95_lower, ci_95_upper, bootstrap_r, hypothesis_supported.
        """
        n = len(dnsi)
        r_p, p_p = pearsonr(dnsi, gap)
        r_s, p_s = spearmanr(dnsi, gap)

        boot_r = self._bootstrap_correlation(dnsi, gap)
        ci_lo, ci_hi = np.percentile(boot_r, [2.5, 97.5]) if len(boot_r) > 0 else (np.nan, np.nan)

        supported = r_p < CONFIG["success_r_threshold"] or r_s < CONFIG["success_r_threshold"]

        return {
            "n": n,
            "r_pearson": float(r_p),
            "p_pearson": float(p_p),
            "r_spearman": float(r_s),
            "p_spearman": float(p_s),
            "ci_95_lower": float(ci_lo),
            "ci_95_upper": float(ci_hi),
            "bootstrap_r": boot_r,
            "hypothesis_supported": bool(supported),
        }

    def _bootstrap_correlation(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Resample pairs with replacement and compute Pearson r."""
        rng = np.random.default_rng(self.seed)
        n = len(x)
        results = []
        for _ in range(self.n_bootstrap):
            idx = rng.integers(0, n, size=n)
            xi, yi = x[idx], y[idx]
            if np.std(xi) == 0 or np.std(yi) == 0:
                continue
            r, _ = pearsonr(xi, yi)
            if np.isfinite(r):
                results.append(r)
        return np.array(results)
