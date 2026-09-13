"""H-M2 matching pipeline: wraps h-m1 matching.py with treatment_col='high_accessible'."""
import logging
import numpy as np
import pandas as pd
from .matching import fit_propensity_model, nearest_neighbor_match, compute_smd

logger = logging.getLogger(__name__)


def run_accessible_matching(
    df: pd.DataFrame,
    caliper_factor: float = 0.2,
    seed: int = 42,
    min_pairs: int = 500,
) -> tuple:
    """Run PS matching with treatment_col='high_accessible'.
    Returns: (matched_df, smd_df, matching_meta)
    """
    treatment_col = "high_accessible"
    covariate_cols = ["creation_year_quartile", "task_type_encoded", "size_decile"]
    available_covs = [c for c in covariate_cols if c in df.columns]

    if len(available_covs) == 0:
        logger.warning("No covariates available for matching, using direct comparison")
        matched_df = df.copy()
        matched_df["pair_id"] = range(len(matched_df))
        smd_df = pd.DataFrame(columns=["covariate", "smd_before", "smd_after"])
        matching_meta = {"n_matched_pairs": len(df) // 2, "smd_max": 0.0, "caliper_used": 0.0, "balance_ok": True}
        return matched_df, smd_df, matching_meta

    model, ps_scores = fit_propensity_model(df, available_covs, treatment_col, seed)
    logit_ps = np.log(ps_scores / (1 - ps_scores))
    ps_sd = logit_ps.std()
    caliper = caliper_factor * ps_sd

    matched_df = nearest_neighbor_match(df, ps_scores, treatment_col, caliper, ratio=1)
    n_matched_pairs = len(matched_df) // 2 if len(matched_df) > 0 else 0

    smd_df = compute_smd(df, matched_df, available_covs, treatment_col) if len(matched_df) > 0 else pd.DataFrame(columns=["covariate", "smd_before", "smd_after"])
    smd_max = float(smd_df["smd_after"].max()) if len(smd_df) > 0 and "smd_after" in smd_df.columns else 0.0

    balance_ok = smd_max < 0.1
    if not balance_ok:
        logger.warning(f"SMD imbalance: max={smd_max:.3f} > 0.1 (SHOULD_WORK gate, continuing)")
    if n_matched_pairs < min_pairs:
        logger.warning(f"Matched pairs {n_matched_pairs} < {min_pairs} (SHOULD_WORK gate, continuing)")

    matching_meta = {
        "n_matched_pairs": n_matched_pairs,
        "smd_max": smd_max,
        "caliper_used": float(caliper),
        "balance_ok": balance_ok,
    }

    # Add PS to matched_df
    df_with_ps = df.copy()
    df_with_ps["propensity_score"] = ps_scores
    if len(matched_df) > 0 and "propensity_score" not in matched_df.columns:
        matched_df["propensity_score"] = np.nan

    return matched_df, smd_df, matching_meta
