"""H-M1 run_experiment.py — CLI entry point for survival analysis pipeline."""
import sys
import os
import logging
import numpy as np
import pandas as pd

# Add code dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as cfg_module
from src.ingest import load_he1_scores, fetch_run_timestamps, fetch_dataset_metadata, build_merged_cohort
from src.findable import compute_findable_score
from src.survival_prep import build_survival_df, validate_preconditions
from src.matching import run_matching
from src.km_analysis import run_km_unadjusted, run_km_matched
from src.cox_analysis import run_cox_primary
from src.ablation import run_all_ablations
from src.sensitivity import run_all_sensitivity
from src.visualize import generate_all_figures
from src.serialize import build_results_dict, save_results, save_gate_result

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    args = cfg_module.parse_args()
    paths = cfg_module.resolve_paths(args)

    np.random.seed(args.seed)

    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)
    os.makedirs(args.cache_dir, exist_ok=True)

    if args.dry_run:
        logger.error("--dry-run is not supported in production: synthetic data must not be used. "
                     "Run without --dry-run to load the real OpenML dataset.")
        sys.exit(2)

    logger.info("Loading H-E1 scores...")
    he1_scores = load_he1_scores(paths["he1_scores_csv"])
    dids = he1_scores["did"].tolist()

    logger.info(f"Fetching run timestamps for {len(dids)} datasets...")
    run_data = fetch_run_timestamps(dids, args.cache_dir)

    logger.info("Fetching dataset metadata...")
    metadata = fetch_dataset_metadata(dids)

    logger.info("Building merged cohort...")
    cohort = build_merged_cohort(he1_scores, run_data, metadata, args.min_run_count)

    logger.info(f"Cohort size after filter: {len(cohort)}")

    # Compute Findable sub-scores
    cohort = compute_findable_score(
        cohort,
        f1_weight=args.__dict__.get("f1_pid_weight", cfg_module.F1_PID_WEIGHT),
        f2_weight=args.__dict__.get("f2_metadata_weight", cfg_module.F2_METADATA_WEIGHT),
        f3_weight=args.__dict__.get("f3_search_weight", cfg_module.F3_SEARCH_WEIGHT),
    )

    # Build survival DataFrame
    survival_df = build_survival_df(cohort, args.observation_window_days)

    # Validate preconditions
    preconditions = validate_preconditions(survival_df, args)
    logger.info(f"Preconditions: {preconditions}")

    # Unadjusted baseline KM
    logger.info("Running unadjusted KM baseline...")
    unadjusted = run_km_unadjusted(survival_df)

    # Propensity matching
    logger.info("Running propensity matching...")
    # Map lowercase CLI args to uppercase attrs expected by run_matching
    import types
    cfg_proxy = types.SimpleNamespace(
        CALIPER_FACTOR=args.caliper_factor,
        CALIPER_RELAXED_FACTOR=args.caliper_relaxed_factor,
        MIN_MATCHED_PAIRS=args.min_matched_pairs,
        SMD_THRESHOLD=cfg_module.SMD_THRESHOLD,
        SEED=args.seed,
    )
    matched_df, smd_df, matching_meta = run_matching(survival_df, cfg_proxy)
    n_matched = matching_meta["n_matched_pairs"]
    logger.info(f"Matched pairs: {n_matched}, SMD max: {matching_meta['smd_max']:.3f}")

    if n_matched < args.min_matched_pairs // 2:
        logger.warning(f"Insufficient matched pairs ({n_matched} < 50) — aborting with FAIL")
        gate = {"result": "FAIL", "reason": f"Insufficient matched pairs: {n_matched}"}
        import json
        os.makedirs(args.results_dir, exist_ok=True)
        with open(paths["gate_json"], "w") as f:
            json.dump(gate, f, indent=2)
        sys.exit(1)

    # Matched KM (PRIMARY GATE)
    logger.info("Running matched KM analysis...")
    km_results = run_km_matched(matched_df)

    # Cox PH regression (SECONDARY GATE)
    logger.info("Running Cox PH regression...")
    cox_results = run_cox_primary(matched_df, predictor_col="findable_score")
    cph_model = cox_results.pop("cph_model", None)

    # Ablations
    logger.info("Running ablations...")
    ablations = run_all_ablations(survival_df, args)

    # Sensitivity analysis
    logger.info("Running sensitivity analysis...")
    sensitivity = run_all_sensitivity(survival_df, matched_df, cph_model, args)

    # Assemble results
    primary = {
        **km_results,
        **cox_results,
        "n_cohort_filtered": len(cohort),
    }

    results = build_results_dict(primary, unadjusted, matching_meta, ablations, sensitivity)
    results.update({
        "kmf_high": km_results.get("kmf_high"),
        "kmf_low": km_results.get("kmf_low"),
        "smd_df": smd_df,
        "ablations": ablations,
        "ps_before": survival_df.get("propensity_score", pd.Series(dtype=float)) if "propensity_score" in survival_df.columns else pd.Series(dtype=float),
        "ps_after": matched_df.get("propensity_score", pd.Series(dtype=float)) if "propensity_score" in matched_df.columns else pd.Series(dtype=float),
    })

    # Generate figures
    logger.info("Generating figures...")
    fig_paths = generate_all_figures(results, args.figures_dir)
    logger.info(f"Figures: {fig_paths}")

    # Save results
    save_results(results, args.results_dir)
    gate_path = save_gate_result(results, args.results_dir, args.log_rank_alpha, args.cox_hr_gate)

    # Gate evaluation
    log_rank_p = km_results.get("log_rank_p", 1.0)
    median_high = km_results.get("median_ttfr_high", float("inf"))
    median_low = km_results.get("median_ttfr_low", 0.0)
    cox_hr = cox_results.get("cox_hr", 0.0)
    gate_pass = (log_rank_p < args.log_rank_alpha and median_high < median_low)
    secondary_pass = cox_hr > args.cox_hr_gate
    logger.info(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    logger.info(f"  log_rank_p={log_rank_p:.4f} (threshold={args.log_rank_alpha}): {'PASS' if log_rank_p < args.log_rank_alpha else 'FAIL'}")
    logger.info(f"  median_high={median_high:.1f} < median_low={median_low:.1f}: {'PASS' if median_high < median_low else 'FAIL'}")
    logger.info(f"  Cox HR={cox_hr:.3f} (gate={args.cox_hr_gate}): {'PASS' if secondary_pass else 'FAIL'}")
    logger.info(f"EXPERIMENT COMPLETE")

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
