"""Analysis module for h-c1: reuses h-e1 functions, adds persistence ratio."""
import os
import sys
import numpy as np
import pandas as pd

# h-c1 config first
from config import N_BOOTSTRAP, RANDOM_SEED, FULL_SAMPLE_EFFECT_PCT, PERSISTENCE_RATIO_MIN

# Add h-e1 code to path for reusing analysis functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/code")))

# Import h-e1 functions directly - no reimplementation
import analysis as h_e1_analysis
compute_reproducibility_iqr = h_e1_analysis.compute_reproducibility_iqr
compute_quartile_effect = h_e1_analysis.compute_quartile_effect
bootstrap_ci = h_e1_analysis.bootstrap_ci


def build_early_analysis_dataset(early_runs: pd.DataFrame) -> pd.DataFrame:
    """Build analysis dataset from early runs.

    Mirrors h-e1's build_analysis_dataset but simplified:
    - early_runs already has metadata_score column from synthetic generation
    - Skips controls (not needed for quartile effect comparison)
    """
    # Compute IQR per (dataset, flow, setup) group
    iqr_df = compute_reproducibility_iqr(early_runs)

    # Get metadata scores (one per dataset)
    metadata = early_runs.groupby("data_id")["metadata_score"].first().reset_index()
    metadata.columns = ["dataset_id", "metadata_score"]

    # Merge
    iqr_df = iqr_df.rename(columns={"data_id": "dataset_id"})
    df = iqr_df.merge(metadata, on="dataset_id", how="left")

    return df


def compute_persistence_ratio(early_effect_pct: float, full_effect_pct: float = FULL_SAMPLE_EFFECT_PCT) -> float:
    """Compute effect persistence ratio: early / full."""
    if full_effect_pct == 0:
        return 0.0
    return early_effect_pct / full_effect_pct


def run_early_effect_analysis(early_analysis_df: pd.DataFrame, n_boot: int = N_BOOTSTRAP) -> dict:
    """Orchestrate B-5: compute quartile effect + bootstrap CI on early subsample."""
    effect = compute_quartile_effect(early_analysis_df)
    ci = bootstrap_ci(early_analysis_df, n_boot)

    early_effect_pct = effect["relative_reduction"] * 100 if effect["relative_reduction"] else 0

    return {
        "iqr_top": effect["iqr_top"],
        "iqr_bottom": effect["iqr_bottom"],
        "relative_reduction": effect["relative_reduction"],
        "absolute_reduction": effect["absolute_reduction"],
        "relative_reduction_pct": early_effect_pct,
        "ci_lower": ci["ci_lower"],
        "ci_upper": ci["ci_upper"],
        "n_boot": len(ci["boot_estimates"]),
    }
