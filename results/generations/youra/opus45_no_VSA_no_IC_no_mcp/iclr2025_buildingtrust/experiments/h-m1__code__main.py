"""Main experiment runner for H-M1: Calibration moderates truthfulness-robustness correlation."""

import json
import numpy as np
import pandas as pd
from pathlib import Path

from config import MODELS, MODEL_PARAMS, H_E1_RESULTS, OUTPUT_PATH, FIGURES_PATH, SEED, THRESHOLDS
from ece import compute_all_ece
from analysis import correlate_ece_with_metrics, tertile_moderation_test
from visualize import plot_ece_vs_metrics, plot_tertile_comparison


def load_h_e1_scores() -> pd.DataFrame:
    """Load cached scores from h-e1 experiment."""
    scores_path = H_E1_RESULTS / "scores.csv"
    if scores_path.exists():
        return pd.read_csv(scores_path)
    raise FileNotFoundError(f"H-E1 scores not found at {scores_path}")


def run_experiment():
    """Run the full H-M1 experiment."""
    print("=" * 60)
    print("H-M1: Calibration Moderates Truthfulness-Robustness Correlation")
    print("=" * 60)

    # Step 1: Load h-e1 cached data
    print("\n[1/5] Loading h-e1 cached scores...")
    df = load_h_e1_scores()
    print(f"  Loaded {len(df)} models from h-e1")

    # Step 2: Compute ECE for all models
    print("\n[2/5] Computing ECE for all models...")
    ece_dict = compute_all_ece(df["model"].tolist(), seed=SEED)
    df["ece"] = df["model"].map(ece_dict)
    print(f"  ECE range: [{df['ece'].min():.4f}, {df['ece'].max():.4f}]")

    # Save ECE scores
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH / "ece_scores.json", "w") as f:
        json.dump(ece_dict, f, indent=2)
    print(f"  Saved ECE scores to {OUTPUT_PATH / 'ece_scores.json'}")

    # Step 3: Run ECE correlation analysis
    print("\n[3/5] Running ECE correlation analysis...")
    ece = df["ece"].values
    truthfulqa = df["truthfulqa_mc1"].values
    advglue = df["advglue_avg"].values
    log_params = df["log_params"].values

    corr_results = correlate_ece_with_metrics(ece, truthfulqa, advglue, log_params)
    print(f"  ECE vs TruthfulQA: r={corr_results['ece_vs_truthfulqa']['r']:.4f}, p={corr_results['ece_vs_truthfulqa']['p']:.4f}")
    print(f"  ECE vs AdvGLUE:    r={corr_results['ece_vs_advglue']['r']:.4f}, p={corr_results['ece_vs_advglue']['p']:.4f}")
    print(f"  Gate 1 (ECE-TruthfulQA): {'PASS' if corr_results['ece_vs_truthfulqa']['passes'] else 'FAIL'}")
    print(f"  Gate 2 (ECE-AdvGLUE):    {'PASS' if corr_results['ece_vs_advglue']['passes'] else 'FAIL'}")

    with open(OUTPUT_PATH / "correlations.json", "w") as f:
        json.dump(corr_results, f, indent=2)

    # Step 4: Run tertile moderation test
    print("\n[4/5] Running tertile moderation test...")
    mod_results = tertile_moderation_test(ece, truthfulqa, advglue)
    print(f"  Low-ECE tertile r:  {mod_results['low_ece_correlation']:.4f}")
    print(f"  High-ECE tertile r: {mod_results['high_ece_correlation']:.4f}")
    print(f"  Difference:         {mod_results['difference']:.4f}")
    print(f"  Fisher z-test p:    {mod_results['fisher_p']:.4f}")
    print(f"  Moderation detected: {'YES' if mod_results['moderation_detected'] else 'NO'}")

    with open(OUTPUT_PATH / "moderation.json", "w") as f:
        json.dump(mod_results, f, indent=2)

    # Step 5: Generate visualizations
    print("\n[5/5] Generating visualizations...")
    FIGURES_PATH.mkdir(parents=True, exist_ok=True)

    plot_ece_vs_metrics(
        ece, truthfulqa, advglue,
        corr_results["ece_vs_truthfulqa"]["r"],
        corr_results["ece_vs_truthfulqa"]["p"],
        corr_results["ece_vs_advglue"]["r"],
        corr_results["ece_vs_advglue"]["p"],
        FIGURES_PATH,
    )
    print(f"  Saved: ece_vs_metrics.png")

    plot_tertile_comparison(
        mod_results["low_ece_correlation"],
        mod_results["high_ece_correlation"],
        mod_results["fisher_p"],
        FIGURES_PATH,
    )
    print(f"  Saved: tertile_comparison.png")

    # Final summary
    print("\n" + "=" * 60)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 60)

    gate_1 = corr_results["ece_vs_truthfulqa"]["passes"]
    gate_2 = corr_results["ece_vs_advglue"]["passes"]
    gate_3 = mod_results["moderation_detected"]
    overall_pass = gate_1 and gate_2 and gate_3

    print(f"\nGate Conditions (threshold: r < {THRESHOLDS['ece_correlation_r']}, p < {THRESHOLDS['ece_correlation_p']}):")
    print(f"  [{'PASS' if gate_1 else 'FAIL'}] ECE-TruthfulQA correlation")
    print(f"  [{'PASS' if gate_2 else 'FAIL'}] ECE-AdvGLUE correlation")
    print(f"  [{'PASS' if gate_3 else 'FAIL'}] Moderation (Fisher p < {THRESHOLDS['fisher_p']})")
    print(f"\n*** OVERALL GATE: {'PASSED' if overall_pass else 'FAILED'} ***")

    results_summary = {
        "hypothesis_id": "h-m1",
        "gate_type": "SHOULD_WORK",
        "n_models": len(df),
        "ece_vs_truthfulqa": corr_results["ece_vs_truthfulqa"],
        "ece_vs_advglue": corr_results["ece_vs_advglue"],
        "moderation": mod_results,
        "gates": {
            "gate_1_ece_truthfulqa": gate_1,
            "gate_2_ece_advglue": gate_2,
            "gate_3_moderation": gate_3,
        },
        "overall_gate_passed": overall_pass,
    }

    with open(OUTPUT_PATH / "experiment_results.json", "w") as f:
        json.dump(results_summary, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_PATH / 'experiment_results.json'}")

    return results_summary


if __name__ == "__main__":
    results = run_experiment()
