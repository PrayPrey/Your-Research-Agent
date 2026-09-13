"""
evaluate.py — FR-4: Gate Condition Evaluation and Statistical Validation for H-E1.

Checks SD(AdvGLUE_drop) > 5% and R² < 0.80, computes bootstrap CIs,
and exports results to CSV/YAML/JSON.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression

import config


class GateEvaluator:
    def __init__(
        self,
        sd_threshold: float = config.SD_THRESHOLD,
        r2_threshold: float = config.R2_THRESHOLD,
        n_bootstrap: int = config.N_BOOTSTRAP,
        seed: int = config.SEED,
    ) -> None:
        self.sd_threshold = sd_threshold
        self.r2_threshold = r2_threshold
        self.n_bootstrap = n_bootstrap
        self.seed = seed

    def check_gate(self, df: pd.DataFrame, stats: dict) -> dict:
        """Evaluate gate conditions from stats dict.

        Returns gate_results dict.
        """
        gate_sd = stats["sd_advglue_drop"] > self.sd_threshold
        gate_r2 = stats["r2_residualization"] < self.r2_threshold
        gate_passed = gate_sd and gate_r2

        ci = self.bootstrap_ci(df)

        gate = {
            "gate_passed": gate_passed,
            "gate_sd_passed": gate_sd,
            "gate_r2_passed": gate_r2,
            "sd_advglue_drop": float(stats["sd_advglue_drop"]),
            "sd_ci_lower": float(ci["sd_ci"][0]),
            "sd_ci_upper": float(ci["sd_ci"][1]),
            "r2_residualization": float(stats["r2_residualization"]),
            "r2_ci_lower": float(ci["r2_ci"][0]),
            "r2_ci_upper": float(ci["r2_ci"][1]),
            "n_models": int(len(df)),
            "n_families": int(df["model_family"].nunique()),
            "n_scales": int(df["scale"].nunique()),
            "n_regimes": int(df["training_regime"].nunique()),
            "pc1_var": float(stats.get("pc1_var", 0.0)),
            "r2_baseline": float(stats.get("r2_baseline", 0.0)),
            "vif": float(stats.get("vif", 0.0)),
        }

        print(
            f"  Gate result: {'✓ PASS' if gate_passed else '✗ FAIL'} "
            f"(SD={gate['sd_advglue_drop']:.4f} {'>' if gate_sd else '<='} "
            f"{self.sd_threshold}, R²={gate['r2_residualization']:.4f} "
            f"{'<' if gate_r2 else '>='} {self.r2_threshold})"
        )
        return gate

    def bootstrap_ci(
        self,
        df: pd.DataFrame,
        alpha: float = 0.05,
    ) -> dict:
        """Bootstrap 95% CIs (10,000 samples) for SD(advglue_drop) and R²_residualization.

        Returns {"sd_ci": (lower, upper), "r2_ci": (lower, upper)}.
        """
        rng = np.random.default_rng(self.seed)
        n = len(df)
        advglue = df["advglue_drop"].values.astype(float)

        # Need PC1 and mean_confidence for R² bootstrap
        has_ri_cols = "PC1" in df.columns and "mean_confidence" in df.columns
        X_full = df[["PC1", "mean_confidence"]].values.astype(float) if has_ri_cols else None

        sd_samples = np.empty(self.n_bootstrap)
        r2_samples = np.empty(self.n_bootstrap)

        for i in range(self.n_bootstrap):
            idx = rng.choice(n, size=n, replace=True)
            sd_samples[i] = advglue[idx].std()
            if X_full is not None:
                X_s = X_full[idx]
                y_s = advglue[idx]
                try:
                    r2_s = LinearRegression().fit(X_s, y_s).score(X_s, y_s)
                except Exception:
                    r2_s = 0.0
                r2_samples[i] = r2_s
            else:
                r2_samples[i] = 0.0

        lo, hi = (alpha / 2) * 100, (1 - alpha / 2) * 100
        sd_ci = (float(np.percentile(sd_samples, lo)), float(np.percentile(sd_samples, hi)))
        r2_ci = (float(np.percentile(r2_samples, lo)), float(np.percentile(r2_samples, hi)))

        return {"sd_ci": sd_ci, "r2_ci": r2_ci}

    def verify_mechanism_activated(
        self,
        df: pd.DataFrame,
        stats: dict,
    ) -> Tuple[bool, dict]:
        """Check both gates + bootstrap CIs.

        Returns (gate_passed: bool, full_gate_dict).
        """
        gate = self.check_gate(df, stats)
        return gate["gate_passed"], gate

    def export_results(
        self,
        df: pd.DataFrame,
        stats: dict,
        gate: dict,
        output_dir: str,
    ) -> None:
        """Write model_matrix.csv, gate_results.yaml, stats_summary.json.

        Outputs: {output_dir}/model_matrix.csv, gate_results.yaml, stats_summary.json
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # model_matrix.csv
        df.to_csv(out / "model_matrix.csv", index=False)
        print(f"  Saved: {out / 'model_matrix.csv'}")

        # gate_results.yaml
        gate_out = {k: (bool(v) if isinstance(v, (bool, np.bool_)) else
                        float(v) if isinstance(v, (float, np.floating)) else
                        int(v) if isinstance(v, (int, np.integer)) else v)
                    for k, v in gate.items()}
        with open(out / "gate_results.yaml", "w") as f:
            yaml.dump(gate_out, f, default_flow_style=False)
        print(f"  Saved: {out / 'gate_results.yaml'}")

        # stats_summary.json
        summary = {
            "hypothesis_id": "h-e1",
            "gate": gate_out,
            "stats": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else
                          float(v) if isinstance(v, (float, np.floating)) else v)
                      for k, v in stats.items()},
            "n_models": int(len(df)),
            "model_families": df["model_family"].value_counts().to_dict(),
        }
        with open(out / "stats_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"  Saved: {out / 'stats_summary.json'}")

        # ri_scores.csv (RI per model if available)
        if "RI" in df.columns:
            ri_df = df[["model_id", "model_family", "scale", "training_regime", "advglue_drop", "PC1", "RI"]]
            ri_df.to_csv(out / "ri_scores.csv", index=False)
            print(f"  Saved: {out / 'ri_scores.csv'}")


def run_evaluation(
    df: pd.DataFrame,
    stats: dict,
    output_dir: str,
) -> dict:
    """Top-level entry point: gate check + bootstrap CI + export.

    Returns gate_results dict.
    """
    evaluator = GateEvaluator()
    print("Running gate evaluation...")
    gate_passed, gate = evaluator.verify_mechanism_activated(df, stats)
    evaluator.export_results(df, stats, gate, output_dir)
    return gate
