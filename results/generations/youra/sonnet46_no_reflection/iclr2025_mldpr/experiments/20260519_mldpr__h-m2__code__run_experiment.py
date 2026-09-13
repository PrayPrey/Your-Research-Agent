"""H-M2: Entry Point — Domain-Specific Degradation Signal Leading Indicator Analysis."""
import argparse
import os
import sys
import numpy as np

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_HM2_DIR = os.path.dirname(_CODE_DIR)

CONFIG = {
    "hm1_code_path": os.path.abspath(os.path.join(_CODE_DIR, "..", "..", "h-m1", "code")),
    "dataset_id": "pwc-archive/evaluation-tables",
    "min_submissions": 20,
    "min_quarters": 8,
    "domains": ["cv", "nlp", "tabular"],
    "domain_thresholds": {"cv": 0.5, "nlp": 0.3, "tabular": 0.90},
    "bootstrap_iters": 100,
    "seed": 42,
    "tau_threshold": 0.90,
    "min_consecutive": 2,
    "r1_tau_threshold": 0.85,
    "min_collapse_events": 20,
    "min_lead_months": 12,
    "gate_fraction_threshold": 0.60,
    "gate_min_domains": 2,
    "rolling_quarters": 4,
    "significance_level": 0.05,
    "output_dir": os.path.join(_HM2_DIR, "figures"),
    "results_json": os.path.join(_HM2_DIR, "results.json"),
    "results_csv": os.path.join(_CODE_DIR, "outputs", "results.csv"),
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {"cv": "#2196F3", "nlp": "#FF5722", "tabular": "#4CAF50"},
    "ablation_variants": ["A1", "A2", "A3", "A4", "A5"],
}


def parse_args(config: dict, args=None) -> dict:
    parser = argparse.ArgumentParser(description="H-M2: Signal Timing Analysis")
    parser.add_argument("--seed", type=int, default=config["seed"])
    parser.add_argument("--min_submissions", type=int, default=config["min_submissions"])
    parser.add_argument("--min_quarters", type=int, default=config["min_quarters"])
    parser.add_argument("--tau_threshold", type=float, default=config["tau_threshold"])
    parser.add_argument("--output_dir", type=str, default=config["output_dir"])
    parser.add_argument("--results_json", type=str, default=config["results_json"])
    parser.add_argument("--results_csv", type=str, default=config["results_csv"])
    parsed, _ = parser.parse_known_args(args)
    merged = config.copy()
    merged.update(vars(parsed))
    return merged


def main(args=None) -> None:
    cfg = parse_args(CONFIG, args)

    # Step 1: Seed + sys.path inject (h-m2 MUST be first to avoid h-m1 module shadowing)
    np.random.seed(cfg["seed"])
    # Ensure h-m2 code dir is FIRST in sys.path
    if _CODE_DIR in sys.path:
        sys.path.remove(_CODE_DIR)
    sys.path.insert(0, _CODE_DIR)

    print("=" * 60)
    print("H-M2: Domain-Specific Degradation Signal Timing Analysis")
    print("=" * 60)

    # Step 2: Load H-M1 panel
    from data_pipeline import load_hm1_panel, extend_panel_with_hd
    print("\n[Step 2] Loading H-M1 panel...")
    pwc_raw, panel_df = load_hm1_panel(
        min_submissions=cfg["min_submissions"],
        min_quarters=cfg["min_quarters"],
        hm1_code_path=cfg["hm1_code_path"],
    )
    print(f"  Panel: {len(panel_df)} rows, {panel_df['benchmark_id'].nunique()} benchmarks")

    # Step 3: Extend panel with H_d signals
    print("\n[Step 3] Computing H_d signals (CV/NLP/Tabular)...")
    panel_df = extend_panel_with_hd(panel_df)
    for col in ["hd_cv", "hd_nlp", "hd_tabular"]:
        n_valid = panel_df[col].notna().sum() if col in panel_df.columns else 0
        print(f"  {col}: {n_valid} non-null values")

    # Step 4: Detect collapse events + R1 mitigation
    from collapse_detector import detect_collapse_events, apply_r1_mitigation
    print("\n[Step 4] Detecting collapse events...")
    collapse_df = detect_collapse_events(panel_df, tau_threshold=cfg["tau_threshold"],
                                         min_consecutive=cfg["min_consecutive"])
    collapse_df, tau_used = apply_r1_mitigation(panel_df, collapse_df,
                                                  min_events=cfg["min_collapse_events"],
                                                  lower_tau=cfg["r1_tau_threshold"])
    print(f"  Collapse events: {len(collapse_df)} (tau_threshold={tau_used})")

    # Step 5: Filter compressed_ids
    print("\n[Step 5] Filtering compressed benchmarks...")
    compressed_ids = panel_df[panel_df["compression_event"] == 1.0]["benchmark_id"].unique()
    print(f"  Compressed benchmarks: {len(compressed_ids)}")

    # Step 6: Compute onset for all domains
    from temporal_analysis import compute_onset_for_all_domains, run_temporal_ordering_test
    print("\n[Step 6] Computing signal onset times per domain...")
    domain_onset_dfs = compute_onset_for_all_domains(panel_df, collapse_df, compressed_ids)

    # Step 7: Run temporal ordering test per domain
    print("\n[Step 7] Running temporal ordering tests (Kaplan-Meier)...")
    domain_km_results = {}
    for domain, onset_df in domain_onset_dfs.items():
        km_result = run_temporal_ordering_test(onset_df, min_lead_months=cfg["min_lead_months"])
        domain_km_results[domain] = km_result
        print(f"  {domain}: fraction_leading={km_result['fraction_leading']:.3f}, "
              f"n_events={km_result['n_events']}, median_lead={km_result['median_lead_months']:.1f}mo")

    # Step 8: Statistical tests
    from statistical_tests import run_all_statistical_tests
    print("\n[Step 8] Running statistical tests (MW + AUC)...")
    stat_results = run_all_statistical_tests(panel_df, collapse_df, compressed_ids)

    # Step 9: Ablation variants
    from ablation import run_all_ablations
    print("\n[Step 9] Running ablation variants A1-A5...")
    ablation_results = run_all_ablations(panel_df, collapse_df, compressed_ids)

    # Step 10: Verify mechanism + gate check
    from evaluate import verify_mechanism_activated, check_gate_condition, save_results
    print("\n[Step 10] Evaluating gate condition...")
    import pandas as pd
    all_onset = pd.concat([df for df in domain_onset_dfs.values() if len(df) > 0], ignore_index=True) \
        if any(len(df) > 0 for df in domain_onset_dfs.values()) else pd.DataFrame()

    results_summary = {
        "n_collapse_events": len(collapse_df),
        "fraction_leading": {d: domain_km_results[d].get("fraction_leading", 0.0) for d in domain_km_results},
        "domain_km_results": {d: {k: v for k, v in r.items() if k != "km_estimator"}
                               for d, r in domain_km_results.items()},
    }
    _, indicators = verify_mechanism_activated(all_onset, domain_km_results, results_summary)
    print(f"  Mechanism indicators: {indicators}")

    gate_passed, gate_details = check_gate_condition(
        domain_km_results, stat_results,
        min_fraction=cfg["gate_fraction_threshold"],
        min_domains=cfg["gate_min_domains"],
    )
    gate_result = "PASS" if gate_passed else "FAIL"
    print(f"\n  SHOULD_WORK Gate: {gate_result}")
    print(f"  Passing domains: {gate_details['passing_domains']}")

    results = {
        "hypothesis_id": "h-m2",
        "gate_result": gate_result,
        "gate_passed": gate_passed,
        "gate_details": gate_details,
        "fraction_leading": {d: domain_km_results[d].get("fraction_leading", 0.0) for d in domain_km_results},
        "mw_p_value": {d: stat_results.get(d, {}).get("mw", {}).get("mw_p_value") for d in ["cv", "nlp", "tabular"]},
        "auc_lead": {d: stat_results.get(d, {}).get("auc", {}).get("auc_lead") for d in ["cv", "nlp", "tabular"]},
        "auc_concurrent": {d: stat_results.get(d, {}).get("auc", {}).get("auc_concurrent") for d in ["cv", "nlp", "tabular"]},
        "n_collapse_events": len(collapse_df),
        "n_compressed_benchmarks": int(len(compressed_ids)),
        "tau_threshold_used": tau_used,
        "mechanism_indicators": indicators,
        "ablation_results": ablation_results,
        "domain_km_results": {d: {k: v for k, v in r.items() if k != "km_estimator"}
                               for d, r in domain_km_results.items()},
        "seed": cfg["seed"],
    }

    # Step 11: Figures + save
    from visualize import generate_all_figures
    print("\n[Step 11] Generating figures and saving results...")
    os.makedirs(cfg["output_dir"], exist_ok=True)
    generate_all_figures(panel_df, collapse_df, domain_onset_dfs, domain_km_results,
                         stat_results, ablation_results, compressed_ids, cfg["output_dir"])
    save_results(results, cfg["results_json"], cfg["results_csv"])

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE — Gate: {gate_result}")
    print(f"Passing domains: {gate_details['passing_domains']}")
    for d, km_r in domain_km_results.items():
        print(f"  {d}: fraction_leading={km_r.get('fraction_leading', 0):.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
