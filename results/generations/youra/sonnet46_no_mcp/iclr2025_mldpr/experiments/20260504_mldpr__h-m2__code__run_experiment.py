"""H-M2 run_experiment.py — CLI entry point for Accessible → 12m run count analysis."""
import sys
import os
import logging
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import config

from src.ingest import load_he1_scores, fetch_all_run_records, fetch_dataset_metadata
from src.accessible_prep import compute_12m_run_counts, compute_accessible_score, build_analysis_df, validate_preconditions
from src.matching_accessible import run_accessible_matching
from src.mwu_analysis import run_mwu_unadjusted, run_mwu_matched, run_ols_standardized, run_mechanism_check
from src.ablation import run_ablation_caliper, run_ablation_ratio
from src.serialize import build_results_dict, save_results, save_gate_result
from src.visualize import generate_all_figures

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    args = config.parse_args()

    if args.dry_run:
        logger.error("--dry-run is not supported: synthetic data must not be used. "
                     "Run without --dry-run to load the real OpenML dataset.")
        sys.exit(2)

    results_dir = args.results_dir
    figures_dir = args.figures_dir
    cache_dir = args.cache_dir
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    logger.info("=== PRODUCTION MODE ===")

    # Load H-E1 FAIR scores
    logger.info("Loading H-E1 scores...")
    fair_scores_df = load_he1_scores(args.h_e1_scores_csv)
    dids = fair_scores_df["did"].tolist()
    logger.info(f"Loaded {len(dids)} datasets from H-E1 scores")

    # Fetch real dataset metadata (upload_date, task_type, NumberOfInstances)
    logger.info("Fetching dataset metadata from OpenML API...")
    metadata_df = fetch_dataset_metadata(dids)
    logger.info(f"Fetched metadata for {len(metadata_df)} datasets")

    # Merge metadata into datasets_df
    datasets_df = fair_scores_df.merge(metadata_df, on="did", how="inner")
    logger.info(f"After metadata merge: {len(datasets_df)} datasets")

    # Filter to post-2018 tabular cohort using real upload_date
    datasets_df["upload_date"] = pd.to_datetime(datasets_df["upload_date"], errors="coerce")
    pre_filter = len(datasets_df)
    datasets_df = datasets_df[datasets_df["upload_date"] >= pd.Timestamp(config.OPENML_UPLOAD_DATE_MIN)].copy()
    logger.info(f"Post-2018 cohort: {len(datasets_df)} datasets (from {pre_filter})")

    if len(datasets_df) == 0:
        logger.error("No datasets remain after post-2018 filter — check upload_date availability")
        sys.exit(1)

    # Compute matching covariates from real metadata
    datasets_df["creation_year_quartile"] = pd.qcut(
        datasets_df["upload_date"].dt.year + datasets_df["upload_date"].dt.month / 12,
        4, labels=False, duplicates="drop"
    )
    if "task_type" not in datasets_df.columns:
        datasets_df["task_type"] = "supervised_classification"
    datasets_df["task_type_encoded"] = (datasets_df["task_type"] == "supervised_classification").astype(int)
    n_instances = datasets_df.get("NumberOfInstances", pd.Series(dtype=float))
    if n_instances.isna().all():
        datasets_df["size_decile"] = 5
    else:
        datasets_df["size_decile"] = pd.qcut(
            n_instances.fillna(n_instances.median()), 10, labels=False, duplicates="drop"
        )

    # Fetch real per-run records from OpenML API (individual run timestamps)
    cohort_dids = datasets_df["did"].tolist()
    logger.info(f"Fetching individual run records for {len(cohort_dids)} datasets from OpenML API...")
    runs_df = fetch_all_run_records(cohort_dids, cache_dir)
    logger.info(f"Loaded {len(runs_df)} individual run records")

    caliper_factor = config.CALIPER_FACTOR
    min_pairs = config.MIN_MATCHED_PAIRS

    # Step 1: Build analysis DataFrame
    logger.info("Step 1: Building analysis DataFrame...")
    window_days = config.OBSERVATION_WINDOW_DAYS
    analysis_df = compute_12m_run_counts(datasets_df, runs_df, window_days=window_days)
    analysis_df = compute_accessible_score(analysis_df, fair_scores_df)
    # Merge all FAIR cols
    for col in config.FAIR_SUB_CRITERIA_COLS:
        if col not in analysis_df.columns and col in fair_scores_df.columns:
            analysis_df = analysis_df.merge(fair_scores_df[["did", col]], on="did", how="left")
    validate_preconditions(analysis_df, min_pairs)
    logger.info(f"Analysis DF: {len(analysis_df)} rows, {analysis_df['high_accessible'].sum()} high, {(analysis_df['high_accessible']==0).sum()} low")

    # Step 2: Unadjusted MWU
    logger.info("Step 2: Unadjusted MWU...")
    unadjusted_mwu = run_mwu_unadjusted(analysis_df)
    logger.info(f"Unadjusted MWU: p={unadjusted_mwu['p_value']:.4f}, high_mean={unadjusted_mwu['high_mean']:.2f}, low_mean={unadjusted_mwu['low_mean']:.2f}")

    # Step 3: PS Matching
    logger.info("Step 3: Propensity score matching...")
    matched_df, smd_df, matching_meta = run_accessible_matching(
        analysis_df, caliper_factor=caliper_factor, seed=config.SEED, min_pairs=min_pairs
    )
    logger.info(f"Matching: {matching_meta['n_matched_pairs']} pairs, smd_max={matching_meta['smd_max']:.3f}")

    # Add propensity scores to analysis_df for visualization
    from src.matching import fit_propensity_model
    covariate_cols = [c for c in ["creation_year_quartile", "task_type_encoded", "size_decile"] if c in analysis_df.columns]
    if covariate_cols:
        _, ps = fit_propensity_model(analysis_df, covariate_cols, "high_accessible", config.SEED)
        analysis_df["propensity_score"] = ps

    # Step 4: Matched MWU
    logger.info("Step 4: Matched MWU...")
    primary_mwu = run_mwu_matched(matched_df)
    logger.info(f"Matched MWU: p={primary_mwu['p_value']:.4f}, r={primary_mwu['effect_size_r']:.3f}, direction_pass={primary_mwu['direction_pass']}")

    # Step 5: OLS
    logger.info("Step 5: OLS standardized regression...")
    ols_results = run_ols_standardized(analysis_df, config.FAIR_SUB_CRITERIA_COLS)
    logger.info(f"OLS: accessible_beta={ols_results['accessible_beta']:.3f}, R2={ols_results['r_squared']:.3f}")

    # Step 6: Ablations
    logger.info("Step 6: Ablation studies...")
    caliper_abl = run_ablation_caliper(analysis_df, fair_scores_df)
    ratio_abl = run_ablation_ratio(analysis_df, fair_scores_df)
    ablations = {
        "caliper": caliper_abl.to_dict(orient="records"),
        "ratio": ratio_abl.to_dict(orient="records"),
    }

    # Step 7: 6-month window sensitivity
    logger.info("Step 7: Window sensitivity (6m)...")
    analysis_6m = compute_12m_run_counts(datasets_df, runs_df, window_days=180)
    analysis_6m = compute_accessible_score(analysis_6m, fair_scores_df)
    matched_6m, _, _ = run_accessible_matching(analysis_6m, caliper_factor=caliper_factor, seed=config.SEED, min_pairs=10)
    results_6m = run_mwu_matched(matched_6m) if len(matched_6m) > 0 else {}

    # Step 8: Build results
    logger.info("Step 8: Saving results...")
    results = build_results_dict(primary_mwu, unadjusted_mwu, ols_results, matching_meta, ablations)
    save_results(results, os.path.join(results_dir, "results.json"))
    gate = save_gate_result(results, os.path.join(results_dir, "gate_result.json"),
                            mwu_alpha=config.MWU_ALPHA, beta_gate=config.ACCESSIBLE_BETA_GATE)

    # Step 9: Figures
    logger.info("Step 9: Generating figures...")
    generate_all_figures(results, matched_df, analysis_df, smd_df, ols_results, results_6m, figures_dir)

    # Step 10: Mechanism check
    logger.info("Step 10: Mechanism check...")
    mech_input = {**matching_meta, "high_mean": primary_mwu.get("high_mean", 0)}
    mech = run_mechanism_check(mech_input)
    logger.info(f"[MECHANISM CHECK] {mech}")

    logger.info(f"=== EXPERIMENT COMPLETE === gate_passed={gate['gate_passed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
