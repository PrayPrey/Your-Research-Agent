"""Integration test: full pipeline smoke test with synthetic data."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from run_experiment import generate_synthetic_data
from src.accessible_prep import compute_12m_run_counts, compute_accessible_score, validate_preconditions
from src.matching_accessible import run_accessible_matching
from src.mwu_analysis import run_mwu_unadjusted, run_mwu_matched, run_ols_standardized, run_mechanism_check
from src.serialize import build_results_dict, save_gate_result
import config


def test_full_pipeline_smoke():
    """Complete pipeline smoke test with n=200 synthetic cohort."""
    datasets_df, runs_df, fair_scores_df = generate_synthetic_data(n=200, seed=42)

    # Step 1: build analysis df
    analysis_df = compute_12m_run_counts(datasets_df, runs_df, window_days=365)
    analysis_df = compute_accessible_score(analysis_df, fair_scores_df)
    for col in config.FAIR_SUB_CRITERIA_COLS:
        if col not in analysis_df.columns and col in fair_scores_df.columns:
            analysis_df = analysis_df.merge(fair_scores_df[["did", col]], on="did", how="left")
    validate_preconditions(analysis_df, min_pairs=30)

    # Step 2: unadjusted
    unadj = run_mwu_unadjusted(analysis_df)
    assert unadj["n_high"] > 0
    assert unadj["n_low"] > 0

    # Step 3: matching
    matched_df, smd_df, meta = run_accessible_matching(
        analysis_df, caliper_factor=0.8, seed=42, min_pairs=30
    )
    assert meta["n_matched_pairs"] > 0

    # Step 4: matched MWU
    primary = run_mwu_matched(matched_df)
    assert "p_value" in primary
    assert "effect_size_r" in primary

    # Step 5: OLS
    ols = run_ols_standardized(analysis_df, config.FAIR_SUB_CRITERIA_COLS)
    assert "accessible_beta" in ols

    # Step 6: build results
    results = build_results_dict(primary, unadj, ols, meta, {})
    assert results["hypothesis"] == "h-m2"

    # Step 7: mechanism check
    mech_input = {**meta, "high_mean": primary.get("high_mean", 0)}
    checks = run_mechanism_check(mech_input)
    assert isinstance(checks["all_pass"], bool)
