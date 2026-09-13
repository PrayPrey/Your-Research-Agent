"""evaluate.py — Gate evaluation and secondary statistical tests for H-M1."""
from __future__ import annotations

from typing import Literal, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

import config

GateResult = Literal["PASS", "PARTIAL", "FAIL"]


class GateEvaluator:
    def __init__(
        self,
        rho_threshold: float = config.RHO_THRESHOLD,
        p_threshold: float = config.P_THRESHOLD,
        consistent_positive_threshold: int = config.FAMILY_SIGN_THRESHOLD,
        vif_threshold: float = config.VIF_THRESHOLD,
    ) -> None:
        self.rho_threshold = rho_threshold
        self.p_threshold = p_threshold
        self.consistent_positive_threshold = consistent_positive_threshold
        self.vif_threshold = vif_threshold

    def evaluate_gate(
        self,
        rho: float,
        p_value: float,
        family_results: pd.DataFrame,
    ) -> dict:
        """PASS/PARTIAL/FAIL gate logic."""
        n_consistent = int((family_results["sign_consistent"] == True).sum()) if len(family_results) > 0 else 0
        cond_rho = rho >= self.rho_threshold
        cond_p = p_value < self.p_threshold
        cond_fam = n_consistent >= self.consistent_positive_threshold
        n_met = sum([cond_rho, cond_p, cond_fam])

        if n_met == 3:
            gate: GateResult = "PASS"
        elif n_met >= 1:
            gate = "PARTIAL"
        else:
            gate = "FAIL"

        return {
            "gate": gate,
            "rho": rho,
            "p_value": p_value,
            "n_consistent_positive": n_consistent,
            "conditions_met": n_met,
            "cond_rho": cond_rho,
            "cond_p": cond_p,
            "cond_fam": cond_fam,
        }

    def baseline_corr(self, df: pd.DataFrame) -> dict:
        """Spearman ρ(PC1, ECE) — capability-only null model."""
        rho, p_val = stats.spearmanr(df["PC1"], df["ECE"])
        return {"rho": float(rho), "p_val": float(p_val)}

    def check_vif(self, df: pd.DataFrame) -> dict[str, float]:
        """VIF for [RI, PC1, mean_confidence]. Must be < 5.0."""
        cols = ["RI", "PC1", "mean_confidence"]
        X = df[cols].copy().dropna()
        X_arr = X.values
        vif_vals = {}
        for i, col in enumerate(cols):
            vif_vals[col] = float(variance_inflation_factor(X_arr, i))
        return vif_vals

    def cooks_distance(self, df: pd.DataFrame) -> dict:
        """Compute Cook's distance, flag models with D > 4/n."""
        from statsmodels.regression.linear_model import OLS
        from statsmodels.tools import add_constant

        X = add_constant(df[["RI", "PC1", "mean_confidence"]].values)
        y = df["ECE"].values
        model = OLS(y, X).fit()
        influence = model.get_influence()
        cd = influence.cooks_distance[0]
        threshold = 4.0 / len(df)
        flagged = []
        d_values = {}
        for i, (mid, d) in enumerate(zip(df["model_id"] if "model_id" in df.columns else df.index, cd)):
            d_values[str(mid)] = float(d)
            if d > threshold:
                flagged.append(str(mid))
        return {"flagged_models": flagged, "d_values": d_values, "threshold": threshold}

    def fisher_z_test(self, df: pd.DataFrame) -> dict:
        """Fisher z-test: ρ_high_PC1 vs ρ_low_PC1 split."""
        median_pc1 = df["PC1"].median()
        high = df[df["PC1"] >= median_pc1]
        low = df[df["PC1"] < median_pc1]
        rho_high, _ = stats.spearmanr(high["RI"], high["ECE"]) if len(high) >= 3 else (float("nan"), float("nan"))
        rho_low, _ = stats.spearmanr(low["RI"], low["ECE"]) if len(low) >= 3 else (float("nan"), float("nan"))

        # Fisher z-transformation
        def fisher_z(r: float) -> float:
            r = max(min(r, 0.9999), -0.9999)
            return 0.5 * np.log((1 + r) / (1 - r))

        n1, n2 = len(high), len(low)
        if np.isnan(rho_high) or np.isnan(rho_low) or n1 < 3 or n2 < 3:
            return {"z_stat": float("nan"), "p_val": float("nan"), "rho_high": float(rho_high), "rho_low": float(rho_low)}

        z1, z2 = fisher_z(rho_high), fisher_z(rho_low)
        se = np.sqrt(1.0 / (n1 - 3) + 1.0 / (n2 - 3))
        z_stat = (z1 - z2) / se
        p_val = float(2 * (1 - stats.norm.cdf(abs(z_stat))))
        return {"z_stat": float(z_stat), "p_val": p_val, "rho_high": float(rho_high), "rho_low": float(rho_low)}

    def run_all_secondary(
        self,
        df: pd.DataFrame,
        family_results: pd.DataFrame,
    ) -> dict:
        """Run all secondary tests."""
        baseline = self.baseline_corr(df)
        vif = self.check_vif(df)
        cooks = self.cooks_distance(df)
        fisher = self.fisher_z_test(df)
        return {
            "baseline_corr": baseline,
            "vif": vif,
            "cooks": cooks,
            "fisher_z": fisher,
        }


def evaluate_experiment(
    df: pd.DataFrame,
    partial_corr_results: dict,
) -> Tuple[dict, dict]:
    """Top-level entry point. Returns (gate_results, secondary_results)."""
    evaluator = GateEvaluator()
    gate_results = evaluator.evaluate_gate(
        rho=partial_corr_results["full"]["rho"],
        p_value=partial_corr_results["full"]["p_value"],
        family_results=partial_corr_results["family_df"],
    )
    secondary_results = evaluator.run_all_secondary(df, partial_corr_results["family_df"])
    return gate_results, secondary_results
