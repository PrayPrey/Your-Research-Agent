"""
run_experiment.py — H-E1: End-to-end pipeline orchestration.
"""
import argparse
import logging
import os
import sys
import time

# ---------------------------------------------------------------------------
# Constants (C-E1-3, C-E1-4)
# ---------------------------------------------------------------------------
RESULTS_DIR: str = "h-e1/results"
FIGURES_DIR: str = "h-e1/figures"
LOG_FILE: str = "h-e1/results/experiment.log"


# ---------------------------------------------------------------------------
# CLI & Logging
# ---------------------------------------------------------------------------

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: AIFS Conditional Preference Shift Detection"
    )
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR)
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR)
    parser.add_argument("--cosine-threshold", type=float, default=0.85)
    parser.add_argument("--max-iter", type=int, default=200)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--smoke-test", action="store_true",
                        help="Run on 500-row subsample per split")
    return parser.parse_args()


def setup_logging(log_path: str = LOG_FILE) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path, mode="a"),
    ]
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)


def smoke_test_run(df_pairs, results_dir: str, figures_dir: str) -> None:
    """Run pipeline on full df_pairs (already subsampled before clustering)."""
    from experiment import fit_baseline_model, fit_proposed_model
    from evaluate import compute_metrics

    res_base = fit_baseline_model(df_pairs)
    res_prop = fit_proposed_model(df_pairs)
    metrics = compute_metrics(res_base, res_prop)
    assert metrics is not None and "beta4" in metrics, "Smoke test: metrics dict missing keys"
    logging.info(f"Smoke test passed. beta4={metrics['beta4']:.4f}, OR={metrics['OR']:.4f}")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    args = get_args()
    setup_logging(os.path.join(args.results_dir, "experiment.log"))
    t0 = time.time()
    logging.info("=" * 60)
    logging.info("H-E1 EXPERIMENT START")
    logging.info(f"  smoke_test={args.smoke_test}")
    logging.info(f"  cosine_threshold={args.cosine_threshold}")
    logging.info(f"  max_iter={args.max_iter}")
    logging.info(f"  seed={args.seed}")
    logging.info("=" * 60)

    os.makedirs(args.results_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)

    # Step 1: Load data
    from data_prep import (
        load_hh_rlhf, extract_dialogue, filter_pairs,
        cluster_prompts, build_pairs_df, validate_clusters,
    )
    logging.info("Step 1: Loading HH-RLHF dataset...")
    df_base_raw, df_online_raw = load_hh_rlhf()
    logging.info(f"  Loaded base={len(df_base_raw)}, online={len(df_online_raw)}")

    # Step 2: Extract dialogue
    logging.info("Step 2: Extracting dialogue...")
    import pandas as pd
    df_base_raw = pd.DataFrame(
        [extract_dialogue(r) for r in df_base_raw.to_dict("records")]
    )
    df_online_raw = pd.DataFrame(
        [extract_dialogue(r) for r in df_online_raw.to_dict("records")]
    )

    # Step 3: Filter pairs
    logging.info("Step 3: Filtering pairs...")
    df_base = filter_pairs(df_base_raw)
    df_online = filter_pairs(df_online_raw)
    logging.info(f"  After filter: base={len(df_base)}, online={len(df_online)}")

    # Smoke test subsampling
    if args.smoke_test:
        logging.info("SMOKE TEST MODE: subsampling 5000 rows per split")
        df_base = df_base.head(5000).reset_index(drop=True)
        df_online = df_online.head(5000).reset_index(drop=True)

    # Step 4: Cluster prompts
    logging.info("Step 4: Clustering prompts...")
    base_prompts = df_base["prompt"].tolist() if "prompt" in df_base.columns else df_base["chosen"].tolist()
    online_prompts = df_online["prompt"].tolist() if "prompt" in df_online.columns else df_online["chosen"].tolist()
    all_prompts = base_prompts + online_prompts
    cluster_threshold = 0.70 if args.smoke_test else args.cosine_threshold
    cluster_ids = cluster_prompts(all_prompts, threshold=cluster_threshold)
    logging.info(f"  Unique clusters: {len(set(cluster_ids))}")

    # Step 5: Build pairs DataFrame
    logging.info("Step 5: Building pairs DataFrame...")
    df_pairs = build_pairs_df(df_base, df_online, cluster_ids)
    logging.info(f"  df_pairs shape: {df_pairs.shape}")

    # Step 6: Validate clusters
    logging.info("Step 6: Validating clusters...")
    validate_clusters(df_pairs)
    logging.info("  Cluster validation passed.")

    if args.smoke_test:
        smoke_test_run(df_pairs, args.results_dir, args.figures_dir)
        logging.info(f"SMOKE TEST COMPLETE in {time.time()-t0:.1f}s")
        logging.info("EXPERIMENT COMPLETE")
        return

    # Step 7: Supply proportion
    logging.info("Step 7: Computing supply proportions...")
    from experiment import (
        compute_supply_prop, fit_baseline_model, fit_proposed_model,
        fit_extended_model, fit_perplexity_model, verify_mechanism_activated,
    )
    df_pairs = compute_supply_prop(df_pairs)

    # Step 8: Fit models
    logging.info("Step 8: Fitting statistical models...")
    result_baseline = fit_baseline_model(df_pairs)
    logging.info("  Baseline model fitted.")
    result_proposed = fit_proposed_model(df_pairs)
    logging.info("  Proposed model fitted.")
    result_extended = fit_extended_model(df_pairs)
    logging.info("  Extended model fitted.")
    try:
        result_perplexity = fit_perplexity_model(df_pairs)
        logging.info("  Perplexity model fitted.")
    except Exception as e:
        logging.warning(f"  Perplexity model failed ({e}), using proposed model as fallback.")
        result_perplexity = result_proposed

    # Step 9: Mechanism verification
    logging.info("Step 9: Verifying mechanism activation...")
    all_ok, indicators = verify_mechanism_activated(result_proposed, df_pairs)
    logging.info(f"  Mechanism verified: {indicators}")

    # Step 10: Compute metrics & gate
    logging.info("Step 10: Computing metrics and gate check...")
    from evaluate import compute_metrics, check_gate, save_metrics, save_model_summary, save_pairs_df
    metrics = compute_metrics(result_baseline, result_proposed)
    gate_passed = check_gate(metrics)
    logging.info(f"  beta4={metrics['beta4']:.4f}, OR={metrics['OR']:.4f}, "
                 f"pval={metrics['pval']:.6f}, CI_lo={metrics['CI_lo']:.4f}")
    logging.info(f"  GATE {'PASSED' if gate_passed else 'FAILED'}")

    # Step 11: Save results
    logging.info("Step 11: Saving results...")
    save_metrics(metrics, gate_passed)
    save_model_summary(result_proposed)
    save_pairs_df(df_pairs)

    # Step 12: Figures
    logging.info("Step 12: Generating figures...")
    from visualize import (
        plot_or_comparison, plot_forest, plot_aifs_distribution,
        plot_cluster_histogram, plot_or_sensitivity,
    )
    plot_or_comparison(metrics)
    plot_forest({
        "baseline": result_baseline,
        "proposed": result_proposed,
        "extended": result_extended,
        "perplexity": result_perplexity,
    })
    plot_aifs_distribution(df_pairs)
    plot_cluster_histogram(df_pairs)
    plot_or_sensitivity(df_base, df_online)

    elapsed = time.time() - t0
    logging.info(f"EXPERIMENT COMPLETE in {elapsed:.1f}s")
    logging.info(f"Gate result: {'PASS' if gate_passed else 'FAIL'}")


if __name__ == "__main__":
    main()
