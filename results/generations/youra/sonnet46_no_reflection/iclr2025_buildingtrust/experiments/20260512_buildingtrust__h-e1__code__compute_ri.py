"""
compute_ri.py — FR-2, FR-3: Capability-PC1 + OLS Residual Instability for H-E1.

Implements PCA on capability benchmarks, OLS residualization of AdvGLUE_drop,
and VIF multicollinearity check.
"""

from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

import config


class RIComputer:
    def __init__(self, seed: int = config.SEED) -> None:
        self.seed = seed
        self._scaler: Optional[StandardScaler] = None
        self._pca: Optional[PCA] = None
        self._ols: Optional[LinearRegression] = None
        self._ols_baseline: Optional[LinearRegression] = None

    def compute_pc1(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """Fit PCA on 5 capability cols; add PC1 column.

        Returns (df_with_PC1, pc1_explained_variance_ratio).
        Input shape: (N, 11), Output shape: (N, 12).
        """
        df = df.copy()
        X = df[config.CAP_COLS].values.astype(float)

        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._pca = PCA(n_components=1, random_state=self.seed)
        pc1_values = self._pca.fit_transform(X_scaled).flatten()
        pc1_var = float(self._pca.explained_variance_ratio_[0])

        if pc1_var < config.PC1_VAR_THRESHOLD:
            import warnings
            warnings.warn(
                f"PC1 explains only {pc1_var:.1%} variance "
                f"(threshold: {config.PC1_VAR_THRESHOLD:.1%}). "
                "Continuing as sensitivity note."
            )

        df["PC1"] = pc1_values
        print(f"  PC1 variance explained: {pc1_var:.3f}")
        return df, pc1_var

    def fit_ols(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """OLS: advglue_drop ~ PC1 + mean_confidence; add RI column.

        Returns (df_with_RI, r2).
        Input shape: (N, 12), Output shape: (N, 13).
        """
        df = df.copy()
        X = df[["PC1", "mean_confidence"]].values.astype(float)
        y = df["advglue_drop"].values.astype(float)

        self._ols = LinearRegression()
        self._ols.fit(X, y)
        y_pred = self._ols.predict(X)
        r2 = float(self._ols.score(X, y))

        df["RI"] = y - y_pred
        print(f"  R²_residualization: {r2:.4f}")
        return df, r2

    def fit_ols_baseline(self, df: pd.DataFrame) -> float:
        """OLS baseline: advglue_drop ~ PC1 only.

        Returns r2_baseline float.
        """
        X_base = df[["PC1"]].values.astype(float)
        y = df["advglue_drop"].values.astype(float)

        self._ols_baseline = LinearRegression()
        self._ols_baseline.fit(X_base, y)
        r2_baseline = float(self._ols_baseline.score(X_base, y))
        print(f"  R²_baseline (PC1 only): {r2_baseline:.4f}")
        return r2_baseline

    def check_vif(self, df: pd.DataFrame) -> float:
        """Compute VIF for PC1 in [PC1, mean_confidence].

        Returns vif_pc1 float (should be < 5.0).
        """
        X = df[["PC1", "mean_confidence"]].values.astype(float)
        vif_pc1 = float(variance_inflation_factor(X, 0))
        if vif_pc1 >= config.VIF_THRESHOLD:
            import warnings
            warnings.warn(
                f"VIF(PC1) = {vif_pc1:.2f} >= {config.VIF_THRESHOLD} "
                "(multicollinearity concern)"
            )
        print(f"  VIF(PC1): {vif_pc1:.3f}")
        return vif_pc1

    def compute(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """Run full pipeline: PC1 → OLS → VIF → stats dict.

        Returns (df_with_PC1_and_RI, stats_dict).
        """
        print("Computing Residual Instability...")

        df, pc1_var = self.compute_pc1(df)
        df, r2 = self.fit_ols(df)
        r2_baseline = self.fit_ols_baseline(df)
        vif = self.check_vif(df)

        sd_drop = float(df["advglue_drop"].std())  # type: ignore[arg-type]
        gate_sd = sd_drop > config.SD_THRESHOLD
        gate_r2 = r2 < config.R2_THRESHOLD

        stats = {
            "pc1_var": pc1_var,
            "r2_residualization": r2,
            "r2_baseline": r2_baseline,
            "sd_advglue_drop": sd_drop,
            "vif": vif,
            "gate_sd_passed": gate_sd,
            "gate_r2_passed": gate_r2,
            "gate_passed": gate_sd and gate_r2,
        }

        print(
            f"  SD(advglue_drop): {sd_drop:.4f} "
            f"({'✓ PASS' if gate_sd else '✗ FAIL'} > {config.SD_THRESHOLD})"
        )
        print(
            f"  Gate SD: {'PASS' if gate_sd else 'FAIL'}, "
            f"Gate R²: {'PASS' if gate_r2 else 'FAIL'}"
        )
        return df, stats


def compute_residual_instability(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Top-level entry point for RI computation.

    Returns (enriched_df, stats_dict).
    """
    computer = RIComputer(seed=config.SEED)
    return computer.compute(df)
