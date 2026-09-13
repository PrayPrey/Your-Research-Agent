"""Correlation analysis for h-c1 (ported from h-m1, threshold adjusted)."""

import numpy as np
from scipy.stats import pearsonr, spearmanr, norm
from config import CONFIG


class CorrelationAnalyzer:
    """Correlation analysis with bootstrap CI for small samples."""

    def __init__(self, n_bootstrap: int = None, seed: int = None):
        self.n_bootstrap = n_bootstrap or CONFIG["n_bootstrap"]
        self.seed = seed or CONFIG["seed"]

    def analyze(self, dnsi: np.ndarray, gap: np.ndarray) -> dict:
        """Run full correlation analysis with |r|>0.3 threshold."""
        n = len(dnsi)
        r_p, p_p = pearsonr(dnsi, gap)
        r_s, p_s = spearmanr(dnsi, gap)

        boot_r = self._bootstrap_correlation(dnsi, gap)
        ci_lo, ci_hi = np.percentile(boot_r, [2.5, 97.5]) if len(boot_r) > 0 else (np.nan, np.nan)

        thr = CONFIG["success_r_abs_threshold"]
        supported = (abs(r_p) > thr and r_p < 0) or (abs(r_s) > thr and r_s < 0)

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


def fisher_z_test(r_a: float, n_a: int, r_b: float, n_b: int) -> dict:
    """Fisher z-transformation test comparing two correlations."""
    r_a_c = np.clip(r_a, -0.9999, 0.9999)
    r_b_c = np.clip(r_b, -0.9999, 0.9999)
    z_a = np.arctanh(r_a_c)
    z_b = np.arctanh(r_b_c)

    denom_a = max(n_a - 3, 1)
    denom_b = max(n_b - 3, 1)
    se = np.sqrt(1.0 / denom_a + 1.0 / denom_b)
    z_diff = (z_a - z_b) / se
    p_diff = 2 * (1 - norm.cdf(abs(z_diff)))
    consistent = np.sign(r_a) == np.sign(r_b)

    result = {
        "z_difference": float(z_diff),
        "p_difference": float(p_diff),
        "consistent_direction": bool(consistent),
    }
    if n_a <= 3 or n_b <= 3:
        result["low_n_warning"] = True
    return result
