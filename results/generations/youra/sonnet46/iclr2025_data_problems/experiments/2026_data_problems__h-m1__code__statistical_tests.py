"""
Statistical Tests for H-M1: Spearman rank correlation gate and supporting tests.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Config ID to filtering intensity mapping for C1-C5
CONFIG_TO_INTENSITY = {"C1": 10, "C2": 30, "C3": 50, "C4": 70, "C5": 90}


class StatisticalTests:
    """Run statistical tests for H-M1 Spearman gate and supporting analyses."""

    def __init__(self, n_bootstrap: int = 1000, seed: int = 42):
        self.n_bootstrap = n_bootstrap
        self.seed = seed

    # ------------------------------------------------------------------
    # Core tests
    # ------------------------------------------------------------------

    def spearman_correlation(
        self,
        filtering_intensities: List[float],
        mean_log_odds: List[float],
    ) -> Dict[str, float]:
        """
        Compute Spearman rank correlation between filtering intensities and mean log-odds.

        Returns:
            {"rho": float, "pvalue": float}
        """
        from scipy import stats

        rho, pvalue = stats.spearmanr(filtering_intensities, mean_log_odds)
        return {"rho": float(rho), "pvalue": float(pvalue)}

    def bootstrap_spearman_ci(
        self,
        filtering_intensities: List[float],
        mean_log_odds: List[float],
    ) -> Tuple[float, float]:
        """
        Compute bootstrap 95% CI for Spearman correlation.

        Handles both old and new scipy API.

        Returns:
            (ci_low, ci_high)
        """
        from scipy import stats

        x = np.array(filtering_intensities)
        y = np.array(mean_log_odds)

        if len(x) < 2:
            return (-np.inf, np.inf)

        rng = np.random.default_rng(self.seed)

        try:
            # New scipy API (>=1.7)
            def spearman_stat(x, y):
                r, _ = stats.spearmanr(x, y)
                return r

            result = stats.bootstrap(
                (x, y),
                spearman_stat,
                n_resamples=self.n_bootstrap,
                random_state=self.seed,
                paired=True,
            )
            ci_low = float(result.confidence_interval.low)
            ci_high = float(result.confidence_interval.high)
        except Exception:
            # Fallback: manual bootstrap
            rhos = []
            n = len(x)
            for _ in range(self.n_bootstrap):
                idx = rng.integers(0, n, size=n)
                r, _ = stats.spearmanr(x[idx], y[idx])
                if not np.isnan(r):
                    rhos.append(r)
            if not rhos:
                return (-np.inf, np.inf)
            ci_low = float(np.percentile(rhos, 2.5))
            ci_high = float(np.percentile(rhos, 97.5))

        return (ci_low, ci_high)

    def ols_regression(
        self,
        filtering_intensities: List[float],
        mean_log_odds: List[float],
    ) -> Dict[str, float]:
        """
        Fit OLS regression of mean_log_odds ~ filtering_intensities.

        Returns:
            {"coef": float, "intercept": float, "r_squared": float, "pvalue": float}
        """
        import statsmodels.api as sm

        x = np.array(filtering_intensities, dtype=float)
        y = np.array(mean_log_odds, dtype=float)

        X = sm.add_constant(x)
        model = sm.OLS(y, X).fit()

        return {
            "coef": float(model.params[1]),
            "intercept": float(model.params[0]),
            "r_squared": float(model.rsquared),
            "pvalue": float(model.pvalues[1]),
        }

    def mann_whitney_u(
        self,
        log_odds_c5: np.ndarray,
        log_odds_c6: np.ndarray,
    ) -> Dict[str, float]:
        """
        Mann-Whitney U test between C5 and C6 log-odds distributions.

        Returns:
            {"statistic": float, "pvalue": float}
        """
        from scipy import stats

        # Filter out non-finite values
        c5 = np.array(log_odds_c5)
        c6 = np.array(log_odds_c6)
        c5 = c5[np.isfinite(c5)]
        c6 = c6[np.isfinite(c6)]

        if len(c5) == 0 or len(c6) == 0:
            return {"statistic": float("nan"), "pvalue": float("nan")}

        stat, pvalue = stats.mannwhitneyu(c5, c6, alternative="two-sided")
        return {"statistic": float(stat), "pvalue": float(pvalue)}

    def ks_test(
        self,
        log_odds_c1: np.ndarray,
        log_odds_c5: np.ndarray,
    ) -> Dict[str, float]:
        """
        Kolmogorov-Smirnov test between C1 and C5 log-odds distributions.

        Returns:
            {"statistic": float, "pvalue": float}
        """
        from scipy import stats

        c1 = np.array(log_odds_c1)
        c5 = np.array(log_odds_c5)
        c1 = c1[np.isfinite(c1)]
        c5 = c5[np.isfinite(c5)]

        if len(c1) == 0 or len(c5) == 0:
            return {"statistic": float("nan"), "pvalue": float("nan")}

        stat, pvalue = stats.ks_2samp(c1, c5)
        return {"statistic": float(stat), "pvalue": float(pvalue)}

    def per_pair_spearman(
        self,
        log_odds_df: pd.DataFrame,
        filtering_intensities: List[float],
    ) -> pd.DataFrame:
        """
        Compute Spearman correlation per (demographic, occupation) pair across C1-C5.

        Maps config_id to filtering intensity: C1→10, C2→30, C3→50, C4→70, C5→90

        Returns:
            DataFrame with columns: [demographic, occupation, rho, pvalue]
        """
        from scipy import stats

        # Filter to C1-C5 only
        c1_c5 = log_odds_df[log_odds_df["config_id"].isin(CONFIG_TO_INTENSITY.keys())].copy()

        if c1_c5.empty:
            return pd.DataFrame(columns=["demographic", "occupation", "rho", "pvalue"])

        c1_c5["intensity"] = c1_c5["config_id"].map(CONFIG_TO_INTENSITY)

        rows = []
        for (demo, occ), group in c1_c5.groupby(["demographic", "occupation"]):
            group_sorted = group.sort_values("intensity")
            x = group_sorted["intensity"].values.astype(float)
            y = group_sorted["log_odds"].replace([np.inf, -np.inf], np.nan).values.astype(float)

            # Drop NaN pairs
            mask = np.isfinite(y)
            x_clean = x[mask]
            y_clean = y[mask]

            if len(x_clean) < 2:
                rows.append({"demographic": demo, "occupation": occ, "rho": float("nan"), "pvalue": float("nan")})
                continue

            rho, pval = stats.spearmanr(x_clean, y_clean)
            rows.append({"demographic": demo, "occupation": occ, "rho": float(rho), "pvalue": float(pval)})

        return pd.DataFrame(rows)

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
        bootstrap_ci: Tuple[float, float],
        alpha_level: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Evaluate Spearman gate: |rho| > 0 AND pvalue < alpha_level.

        Returns:
            dict with gate_passed, rho, pvalue, bootstrap_ci_low, bootstrap_ci_high
        """
        rho = spearman_result["rho"]
        pvalue = spearman_result["pvalue"]

        gate_passed = bool(abs(rho) > 0 and pvalue < alpha_level)

        return {
            "gate_passed": gate_passed,
            "rho": rho,
            "pvalue": pvalue,
            "bootstrap_ci_low": bootstrap_ci[0],
            "bootstrap_ci_high": bootstrap_ci[1],
        }

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_all_tests(
        self,
        log_odds_df: pd.DataFrame,
        mean_log_odds_per_config: Dict[str, float],
        filtering_intensities: List[float],
    ) -> Dict[str, Any]:
        """
        Run all statistical tests and return unified results dict.

        Uses C1-C5 for Spearman, C5 vs C6 for Mann-Whitney, C1 vs C5 for KS.

        Returns:
            dict with keys: spearman, bootstrap_ci, ols, mann_whitney, ks, per_pair_spearman, gate
        """
        fasttext_config_ids = ["C1", "C2", "C3", "C4", "C5"]

        # Build ordered mean log-odds for C1-C5 using filtering_intensities order
        mean_lo_c1_c5 = []
        for cid in fasttext_config_ids:
            mean_lo_c1_c5.append(mean_log_odds_per_config.get(cid, 0.0))

        # Spearman
        logger.info("Running Spearman correlation (C1-C5)")
        spearman = self.spearman_correlation(filtering_intensities, mean_lo_c1_c5)

        # Bootstrap CI
        logger.info("Running bootstrap Spearman CI")
        bootstrap_ci = self.bootstrap_spearman_ci(filtering_intensities, mean_lo_c1_c5)

        # OLS regression
        logger.info("Running OLS regression")
        ols = self.ols_regression(filtering_intensities, mean_lo_c1_c5)

        # Extract per-config log-odds arrays
        def get_log_odds_array(config_id: str) -> np.ndarray:
            if log_odds_df.empty:
                return np.array([])
            subset = log_odds_df[log_odds_df["config_id"] == config_id]["log_odds"]
            return subset.values

        c5_vals = get_log_odds_array("C5")
        c6_vals = get_log_odds_array("C6")
        c1_vals = get_log_odds_array("C1")

        # Mann-Whitney U (C5 vs C6)
        logger.info("Running Mann-Whitney U test (C5 vs C6)")
        mann_whitney = self.mann_whitney_u(c5_vals, c6_vals)

        # KS test (C1 vs C5)
        logger.info("Running KS test (C1 vs C5)")
        ks = self.ks_test(c1_vals, c5_vals)

        # Per-pair Spearman
        logger.info("Running per-pair Spearman correlations")
        per_pair_df = self.per_pair_spearman(log_odds_df, filtering_intensities)
        per_pair_spearman = per_pair_df.to_dict(orient="records")

        # Gate evaluation
        gate = self.evaluate_gate(spearman, bootstrap_ci)
        logger.info("Gate evaluation: %s (rho=%.4f, p=%.4f)", gate["gate_passed"], gate["rho"], gate["pvalue"])

        return {
            "spearman": spearman,
            "bootstrap_ci": bootstrap_ci,
            "ols": ols,
            "mann_whitney": mann_whitney,
            "ks": ks,
            "per_pair_spearman": per_pair_spearman,
            "gate": gate,
        }


# Type hint for evaluate_gate
from typing import Any  # noqa: E402 (already imported above)
