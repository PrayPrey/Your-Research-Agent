"""partial_corr.py — Spearman partial correlation analysis for H-M1."""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import pandas as pd
import pingouin as pg
from statsmodels.stats.multitest import multipletests

import config


class PartialCorrAnalyzer:
    def __init__(
        self,
        target_families: Optional[list[str]] = None,
        min_family_size: int = config.MIN_FAMILY_SIZE,
        n_bootstrap: int = config.N_BOOTSTRAP,
        seed: int = config.SEED,
    ) -> None:
        self.target_families = target_families or config.TARGET_FAMILIES
        self.min_family_size = min_family_size
        self.n_bootstrap = n_bootstrap
        self.seed = seed

    def _get_covariates(self, df: pd.DataFrame) -> list[str]:
        """Return covariates, dropping any that are constant (would cause rank deficiency)."""
        covars = ["PC1", "mean_confidence"]
        return [c for c in covars if c in df.columns and df[c].nunique() > 1]

    def full_partial_corr(self, df: pd.DataFrame) -> dict:
        """Spearman partial ρ(RI, ECE | PC1, mean_confidence) on full N=30."""
        covars = self._get_covariates(df)
        result = pg.partial_corr(
            data=df,
            x="RI",
            y="ECE",
            covar=covars,
            method="spearman",
        )
        rho = float(result["r"].iloc[0])
        p_value = float(result["p_val"].iloc[0])
        ci = self.bootstrap_rho_ci(df)
        return {
            "rho": rho,
            "p_value": p_value,
            "ci_low": ci[0],
            "ci_high": ci[1],
            "n": len(df),
        }

    def family_partial_corr(
        self,
        df: pd.DataFrame,
        min_n: Optional[int] = None,
    ) -> pd.DataFrame:
        """Per-family Spearman partial correlation."""
        min_n = min_n if min_n is not None else self.min_family_size
        # Normalize family column name
        fam_col = "model_family" if "model_family" in df.columns else "family"
        records = []
        for fam in self.target_families:
            sub = df[df[fam_col] == fam]
            if len(sub) < min_n:
                continue
            try:
                covars = self._get_covariates(sub)
                res = pg.partial_corr(
                    data=sub,
                    x="RI",
                    y="ECE",
                    covar=covars,
                    method="spearman",
                )
                rho = float(res["r"].iloc[0])
                p_val = float(res["p_val"].iloc[0])
            except Exception:
                rho, p_val = float("nan"), float("nan")
            records.append({
                "family": fam,
                "rho": rho,
                "p_value": p_val,
                "n": len(sub),
                "sign_consistent": rho > 0,
            })
        return pd.DataFrame(records)

    def holm_correction(
        self,
        p_values: np.ndarray,
        alpha: float = 0.05,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Holm-Bonferroni correction."""
        p_values = np.asarray(p_values, dtype=float)
        reject, p_corrected, _, _ = multipletests(p_values, method="holm", alpha=alpha)
        return reject, p_corrected

    def bootstrap_rho_ci(self, df: pd.DataFrame) -> Tuple[float, float]:
        """10K bootstrap resamples on full Spearman partial rho."""
        rng = np.random.default_rng(self.seed)
        rho_samples = []
        n = len(df)
        for _ in range(self.n_bootstrap):
            idx = rng.integers(0, n, size=n)
            df_b = df.iloc[idx].reset_index(drop=True)
            try:
                covars = self._get_covariates(df_b)
                r = pg.partial_corr(
                    data=df_b,
                    x="RI",
                    y="ECE",
                    covar=covars,
                    method="spearman",
                )
                rho_samples.append(float(r["r"].iloc[0]))
            except Exception:
                continue
        if len(rho_samples) < 100:
            return (float("nan"), float("nan"))
        return (
            float(np.percentile(rho_samples, 2.5)),
            float(np.percentile(rho_samples, 97.5)),
        )

    def run_all(self, df: pd.DataFrame) -> dict:
        """Run full_partial_corr + family_partial_corr + holm + bootstrap CI."""
        full = self.full_partial_corr(df)
        family_df = self.family_partial_corr(df)

        p_vals = np.array(family_df["p_value"].values, dtype=float)
        if len(p_vals) > 0:
            _, p_holm = self.holm_correction(p_vals)
            family_df = family_df.copy()
            family_df["p_value_holm"] = p_holm
        else:
            family_df = family_df.copy()
            family_df["p_value_holm"] = np.array([], dtype=float)

        n_consistent = int(family_df["sign_consistent"].sum())

        return {
            "full": full,
            "family_df": family_df,
            "n_consistent_positive": n_consistent,
        }


def run_partial_correlation_analysis(df: pd.DataFrame) -> dict:
    """Top-level entry point."""
    analyzer = PartialCorrAnalyzer()
    return analyzer.run_all(df)
