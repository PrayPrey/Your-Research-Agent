#!/usr/bin/env python3
"""Main entrypoint for H-E1 benchmark correlation experiment.

This is an EXISTENCE PoC: evaluate base Llama-2-7B on TruthfulQA, HHH-helpful,
HHH-harmless, then compute pairwise correlations. Gate: all |r| < 0.5.
"""

import os
import sys
import json
import numpy as np

# Add code dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RESULTS_PATH, CORR_THRESHOLD, FIGURES_DIR
from data import load_truthfulqa, load_hhh
from evaluate import load_model, run_all_evaluations
from correlate import compute_pairwise_correlations, check_gate
from visualize import plot_correlation_heatmap, plot_gate_status, plot_score_distributions


def main():
    print("=" * 60)
    print("H-E1: Benchmark Independence Verification")
    print("=" * 60)

    # 1. Load datasets
    print("\n[1/5] Loading datasets...")
    truthfulqa_ds = load_truthfulqa()
    hhh_helpful_ds = load_hhh("helpful")
    hhh_harmless_ds = load_hhh("harmless")
    print(f"  TruthfulQA: {len(truthfulqa_ds)} samples")
    print(f"  HHH-helpful: {len(hhh_helpful_ds)} samples")
    print(f"  HHH-harmless: {len(hhh_harmless_ds)} samples")

    # 2. Load model
    print("\n[2/5] Loading model...")
    model, tokenizer = load_model()
    print("  Model loaded successfully")

    # 3. Run evaluations
    print("\n[3/5] Running evaluations...")
    scores = run_all_evaluations(model, tokenizer, truthfulqa_ds, hhh_helpful_ds, hhh_harmless_ds)

    # 4. Compute correlations
    print("\n[4/5] Computing correlations...")
    correlations = compute_pairwise_correlations(scores)
    for pair, stats in correlations.items():
        print(f"  {pair}: r={stats['r']:.4f}, p={stats['p']:.4f}")

    gate_passed = check_gate(correlations)

    # 5. Generate figures
    print("\n[5/5] Generating figures...")
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plot_correlation_heatmap(correlations)
    plot_gate_status(correlations)
    plot_score_distributions(scores)

    # Save results
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    results = {
        "scores": {k: v.tolist() for k, v in scores.items()},
        "accuracies": {k: float(v.mean()) for k, v in scores.items()},
        "correlations": correlations,
        "gate_threshold": CORR_THRESHOLD,
        "gate_passed": gate_passed,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")

    # Final gate check
    print("\n" + "=" * 60)
    if gate_passed:
        print("GATE PASSED: All |r| < 0.5")
        print("Benchmarks measure distinct alignment dimensions.")
    else:
        print("GATE FAILED: Some |r| >= 0.5")
        print("Benchmarks too correlated. Pipeline STOPS.")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    sys.exit(main())
