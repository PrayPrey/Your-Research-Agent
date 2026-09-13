"""H-M1: Entry point — Submission Count → Score Compression Causal Mechanism."""
import argparse
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Set working directory to code folder for relative imports
_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

from data_pipeline import load_panel
from sigma_estimation import get_sigma_map
from compression_detector import flag_compression, summarize_compression
from spearman_baseline import compute_spearman_baseline
from granger_causality import run_granger_panel, aggregate_granger_panel
from evaluate import verify_mechanism_activated, check_gate_condition, save_results
from visualize import generate_all_figures

CONFIG = {
    "seed": 42,
    "min_submissions": 20,
    "min_history_years": 2,
    "min_quarters": 8,
    "date_start": "2018-01-01",
    "date_end": "2025-12-31",
    "domains": ["cv", "nlp", "tabular"],
    "compression_threshold": 1.5,
    "min_consecutive": 2,
    "top_k_scores": 10,
    "granger_max_lag": 4,
    "granger_primary_lag": 2,
    "adf_significance": 0.05,
    "spearman_rho_target": 0.4,
    "granger_p_target": 0.05,
    "significance_level": 0.05,
    "min_panel_rows": 200,
    "min_granger_benchmarks": 30,
    "output_dir": os.path.join(os.path.dirname(_CODE_DIR), "figures"),
    "results_json": os.path.join(os.path.dirname(_CODE_DIR), "results.json"),
    "results_csv": os.path.join(os.path.dirname(_CODE_DIR), "code", "outputs", "results.csv"),
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"},
}


def parse_args(config: dict, args=None) -> dict:
    parser = argparse.ArgumentParser(
        description="H-M1: BCBHS Causal Mechanism — Submission Count → Score Compression"
    )
    parser.add_argument("--seed", type=int, default=config["seed"])
    parser.add_argument("--min-submissions", type=int, default=config["min_submissions"],
                        dest="min_submissions")
    parser.add_argument("--min-quarters", type=int, default=config["min_quarters"],
                        dest="min_quarters")
    parser.add_argument("--compression-threshold", type=float,
                        default=config["compression_threshold"], dest="compression_threshold")
    parser.add_argument("--granger-max-lag", type=int, default=config["granger_max_lag"],
                        dest="granger_max_lag")
    parser.add_argument("--output-dir", type=str, default=config["output_dir"],
                        dest="output_dir")
    parser.add_argument("--results-csv", type=str, default=config["results_csv"],
                        dest="results_csv")
    parser.add_argument("--results-json", type=str, default=config["results_json"],
                        dest="results_json")
    parsed = parser.parse_args(args if args is not None else [])
    cfg = dict(config)
    cfg.update({k: v for k, v in vars(parsed).items() if v is not None})
    return cfg


def main(args=None) -> None:
    cfg = parse_args(CONFIG, args)
    np.random.seed(cfg["seed"])

    print("=" * 60)
    print("H-M1: Submission Count → Score Compression Causal Mechanism")
    print("=" * 60)

    # Step 1: Load panel
    print("\n[Step 1] Loading quarterly panel...")
    pwc_raw, panel_df = load_panel(
        min_submissions=cfg["min_submissions"],
        min_quarters=cfg["min_quarters"],
    )
    print(f"  Panel rows: {len(panel_df):,}, benchmarks: {panel_df['benchmark_id'].nunique()}")

    # Step 2: Sigma estimation
    print("\n[Step 2] Estimating sigma_measurement...")
    sigma_map = get_sigma_map(pwc_raw)
    print(f"  sigma_map: {len(sigma_map)} benchmarks, median={sigma_map.median():.4f}")

    # Step 3: Compression detection
    print("\n[Step 3] Detecting compression events...")
    panel_df = flag_compression(
        panel_df, sigma_map,
        threshold=cfg["compression_threshold"],
        min_consecutive=cfg["min_consecutive"],
    )
    comp_summary = summarize_compression(panel_df)
    print(f"  Compression events: {comp_summary['n_compression_events']}")
    print(f"  Qualifying benchmarks: {comp_summary['n_qualifying_benchmarks']}")

    # Step 4: Spearman baseline
    print("\n[Step 4] Computing Spearman baseline...")
    spearman_result = compute_spearman_baseline(panel_df)
    print(f"  Spearman rho={spearman_result['rho']:.4f}, p={spearman_result['p_value']:.4e}, n={spearman_result['n_obs']}")

    # Step 5: Granger causality panel
    print("\n[Step 5] Running Granger causality panel (may take a few minutes)...")
    forward_results, reverse_results = run_granger_panel(panel_df, max_lag=cfg["granger_max_lag"])
    print(f"  Forward results: {len(forward_results)} benchmarks tested")

    # Step 6: Aggregate Granger
    print("\n[Step 6] Aggregating Granger results...")
    granger_agg = aggregate_granger_panel(forward_results, target_lag=cfg["granger_primary_lag"])
    print(f"  n_significant_lag2={granger_agg['n_significant_lag2']}, "
          f"pct={granger_agg['pct_significant_lag2']:.1%}, "
          f"min_p={granger_agg.get('min_p_lag2', 'N/A')}")

    # Step 7: Mechanism verification
    print("\n[Step 7] Verifying mechanism activation...")
    activated, indicators = verify_mechanism_activated(panel_df, forward_results, spearman_result)
    for k, v in indicators.items():
        print(f"  {k}: {v}")

    # Step 8: Gate condition
    print("\n[Step 8] Checking gate condition...")
    gate_passed, gate_details = check_gate_condition(spearman_result, granger_agg)

    # Step 9: Figures
    print("\n[Step 9] Generating figures...")
    os.makedirs(cfg["output_dir"], exist_ok=True)
    generate_all_figures(
        panel_df, spearman_result, forward_results, reverse_results, granger_agg,
        cfg["output_dir"],
    )

    # Step 10: Save results
    print("\n[Step 10] Saving results...")
    results = {
        "hypothesis_id": "h-m1",
        "gate_type": "MUST_WORK",
        "gate_passed": gate_passed,
        "spearman_result": spearman_result,
        "granger_agg": granger_agg,
        "compression_summary": comp_summary,
        "gate_details": gate_details,
        "indicators": indicators,
        "activated": activated,
        "panel_shape": list(panel_df.shape),
        "n_benchmarks": int(panel_df["benchmark_id"].nunique()),
        "config": {k: v for k, v in cfg.items() if not isinstance(v, (list, dict))},
    }
    save_results(results, cfg["results_json"])

    # Save CSV
    os.makedirs(os.path.dirname(os.path.abspath(cfg["results_csv"])), exist_ok=True)
    pd.DataFrame([{
        "hypothesis_id": "h-m1",
        "gate_passed": gate_passed,
        "spearman_rho": spearman_result["rho"],
        "spearman_p": spearman_result["p_value"],
        "n_obs": spearman_result["n_obs"],
        "n_benchmarks_granger": granger_agg["n_benchmarks_tested"],
        "n_significant_lag2": granger_agg["n_significant_lag2"],
        "pct_significant_lag2": granger_agg["pct_significant_lag2"],
        "min_p_lag2": granger_agg.get("min_p_lag2"),
        "n_compression_events": comp_summary["n_compression_events"],
        "panel_rows": len(panel_df),
    }]).to_csv(cfg["results_csv"], index=False)
    print(f"CSV saved to {cfg['results_csv']}")

    print("\n" + "=" * 60)
    print(f"GATE: {'PASS' if gate_passed else 'FAIL'}")
    print("=" * 60)
    print(f"  Spearman rho={spearman_result['rho']:.4f} (target >0.4), "
          f"p={spearman_result['p_value']:.4e}")
    print(f"  Granger min_p_lag2={granger_agg.get('min_p_lag2', 'N/A')} (target <0.05)")
    print("=" * 60)


if __name__ == "__main__":
    main()
