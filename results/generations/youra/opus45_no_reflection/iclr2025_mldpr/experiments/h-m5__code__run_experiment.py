#!/usr/bin/env python3
"""H-M5 End-to-End Orchestration: Modality Divergence Analysis"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from data_loader import load_pwc_dataset, extract_modality, build_monthly_counts
from gini import compute_modality_gini_series
from baseline import compute_overall_gini_series
from correlation import period_correlation, rolling_correlation, fisher_z_test, modality_pair_correlations
from gate import evaluate_gate, failure_pivot
from visualize import plot_gate_metrics, plot_rolling_correlation, plot_gini_trajectories, plot_correlation_heatmap


def main() -> dict:
    """Run full H-M5 pipeline."""
    print("=" * 60)
    print("H-M5: Modality Divergence (Phase Transition Effect)")
    print("=" * 60)

    os.makedirs(CONFIG.output_dir, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    print("\n[1/8] Loading PWC dataset...")
    raw_df = load_pwc_dataset()
    print(f"  Loaded {len(raw_df)} records")

    print("\n[2/8] Building monthly counts with modality classification...")
    monthly_df = build_monthly_counts(raw_df)

    print("\n[3/8] Computing modality Gini time series...")
    gini_df = compute_modality_gini_series(monthly_df)

    print("\n[4/8] Computing baseline overall Gini series...")
    overall_gini = compute_overall_gini_series(monthly_df)

    print("\n[5/8] Computing period correlations and Fisher z-test...")
    r_pre, n_pre = period_correlation(gini_df, "CV", "NLP", end=CONFIG.pre_cutoff)
    r_post, n_post = period_correlation(gini_df, "CV", "NLP", start=CONFIG.post_cutoff)
    z_stat, p_value = fisher_z_test(r_pre, n_pre, r_post, n_post)

    print(f"  Pre-2020:  r = {r_pre:.4f} (n = {n_pre})")
    print(f"  Post-2021: r = {r_post:.4f} (n = {n_post})")
    print(f"  Fisher z-test: z = {z_stat:.4f}, p = {p_value:.6f}")

    print("\n[6/8] Evaluating gate...")
    result = evaluate_gate(r_pre, r_post, p_value, n_pre, n_post)
    print(f"  Gate: {'PASS' if result['gate_pass'] else 'FAIL'}")

    pivot_df = None
    if not result["gate_pass"]:
        print("\n[6b/8] Running failure pivot analysis...")
        pivot_df = failure_pivot(gini_df)
        print(pivot_df.to_string(index=False))

    print("\n[7/8] Computing rolling correlation...")
    rolling = rolling_correlation(gini_df, "CV", "NLP")

    print("\n[8/8] Generating visualizations...")
    pre_matrix = modality_pair_correlations(gini_df, "pre")
    post_matrix = modality_pair_correlations(gini_df, "post")

    plot_gate_metrics(result, CONFIG.gate_metrics_path)
    plot_rolling_correlation(rolling, CONFIG.rolling_correlation_path)
    plot_gini_trajectories(gini_df, CONFIG.gini_trajectories_path)
    plot_correlation_heatmap(pre_matrix, post_matrix, CONFIG.correlation_heatmap_path)

    results = {
        "hypothesis_id": "h-m5",
        "timestamp": datetime.now().isoformat(),
        "gate_result": "PASS" if result["gate_pass"] else "FAIL",
        "metrics": {
            "r_pre": float(r_pre),
            "r_post": float(r_post),
            "n_pre": int(n_pre),
            "n_post": int(n_post),
            "z_stat": float(z_stat) if not (z_stat != z_stat) else None,
            "p_value": float(p_value) if not (p_value != p_value) else None,
            "correlation_drop": float(r_pre - r_post) if not (r_pre != r_pre or r_post != r_post) else None,
        },
        "thresholds": {
            "r_pre_min": CONFIG.gate_r_pre_min,
            "r_post_max": CONFIG.gate_r_post_max,
            "p_value_max": CONFIG.gate_p_value_max,
        },
        "sample_info": {
            "total_records": len(raw_df),
            "time_points": len(gini_df),
            "modalities": list(gini_df.columns),
        },
        "figures": [
            CONFIG.gate_metrics_path,
            CONFIG.rolling_correlation_path,
            CONFIG.gini_trajectories_path,
            CONFIG.correlation_heatmap_path,
        ],
    }

    if pivot_df is not None:
        results["failure_pivot"] = pivot_df.to_dict(orient="records")

    results_path = "outputs/results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    gini_df.to_csv("outputs/gini_series.csv")
    rolling.to_csv("outputs/rolling_correlation.csv")

    print("\n" + "=" * 60)
    print(f"H-M5 GATE: {'PASS' if result['gate_pass'] else 'FAIL'}")
    print(f"  Pre-2020 r = {r_pre:.4f} (threshold > 0.6): {'OK' if r_pre > 0.6 else 'FAIL'}")
    print(f"  Post-2021 r = {r_post:.4f} (threshold < 0.4): {'OK' if r_post < 0.4 else 'FAIL'}")
    print(f"  p-value = {p_value:.6f} (threshold < 0.05): {'OK' if p_value < 0.05 else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
